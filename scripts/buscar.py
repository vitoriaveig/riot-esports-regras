#!/usr/bin/env python3
"""Busca no corpus de regulamentos da Riot (textos/*.md), localmente ou direto do GitHub.

Exemplos:
  python scripts/buscar.py "coach" "pause"                      # todas as palavras, mesmo parágrafo/janela
  python scripts/buscar.py --regex "remake|re-?make" --jogo LoL --temporada 2026
  python scripts/buscar.py "betting|gambling" --regex --contar > contagem.csv   # matriz documento × termo
  python scripts/buscar.py --remoto vitoriaveig/riot-esports-regras "residency"  # sem clonar o repositório
  python scripts/buscar.py --listar --jogo VALORANT --tipo "Regras de elenco"

Saída padrão: documento, página, seção mais próxima e trecho, para citação.
"""
import argparse, csv, io, re, sys, urllib.request
from pathlib import Path

RX_PAG = re.compile(r"<!-- página (\d+) -->")
RX_SEC = re.compile(r"^\s{0,14}((?:\d{1,2}\.){1,5}\d{0,2})\s+([A-ZÀ-Ý][^.\n]{2,80}?)(?:\.\s|\.$|\s*$)")


def abrir(remoto, rel, cache):
    if not remoto:
        return Path(rel).read_text(encoding="utf-8")
    alvo = cache / rel
    if alvo.exists(): return alvo.read_text(encoding="utf-8")
    url = f"https://raw.githubusercontent.com/{remoto}/main/{rel}"
    with urllib.request.urlopen(url, timeout=60) as r: txt = r.read().decode("utf-8")
    alvo.parent.mkdir(parents=True, exist_ok=True); alvo.write_text(txt, encoding="utf-8")
    return txt


def filtrar(docs, a):
    def ok(d):
        if a.jogo and d["jogo"].lower() != a.jogo.lower(): return False
        if a.competicao and a.competicao.lower() not in d["competicao"].lower(): return False
        if a.temporada and d["temporada"] != a.temporada: return False
        if a.tipo and a.tipo.lower() not in d["tipo_documento"].lower(): return False
        if a.status and a.status.lower() not in d["status_biblioteca"].lower(): return False
        if a.ids and d["id"] not in a.ids.split(","): return False
        return True
    vistos, out = set(), []
    for d in docs:  # um texto por arquivo
        if ok(d) and d["texto"] not in vistos:
            vistos.add(d["texto"]); out.append(d)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("termos", nargs="*")
    ap.add_argument("--regex", action="store_true", help="cada termo é uma expressão regular")
    ap.add_argument("--qualquer", action="store_true", help="basta um dos termos (padrão: todos)")
    ap.add_argument("--janela", type=int, default=6, help="linhas de contexto")
    ap.add_argument("--max", type=int, default=40, help="máximo de trechos exibidos")
    ap.add_argument("--contar", action="store_true", help="CSV com ocorrências por documento e termo")
    ap.add_argument("--listar", action="store_true", help="só lista os documentos filtrados")
    ap.add_argument("--remoto", help="owner/repo no GitHub (lê via raw.githubusercontent.com)")
    ap.add_argument("--cache", default=".cache_corpus")
    for f in ["jogo", "competicao", "temporada", "tipo", "status", "ids"]: ap.add_argument("--" + f)
    a = ap.parse_args()
    cache = Path(a.cache)

    docs = list(csv.DictReader(io.StringIO(abrir(a.remoto, "catalogo/catalogo.csv", cache))))
    try:
        man = {r["texto_id"]: r for r in csv.DictReader(io.StringIO(abrir(a.remoto, "manifest.csv", cache)))}
    except Exception:
        man = {}
    docs = filtrar(docs, a)

    if a.listar or not a.termos:
        w = csv.writer(sys.stdout)
        w.writerow(["id", "titulo", "jogo", "competicao", "temporada", "tipo_documento", "status_biblioteca", "texto", "status_texto", "idioma", "paginas"])
        for d in docs:
            m = man.get(Path(d["texto"]).stem, {})
            w.writerow([d["id"], d["titulo"], d["jogo"], d["competicao"], d["temporada"], d["tipo_documento"],
                        d["status_biblioteca"], d["texto"], m.get("status", "?"), m.get("idioma", ""), m.get("paginas", "")])
        return

    pads = [re.compile(t if a.regex else re.escape(t), re.I) for t in a.termos]
    if a.contar:
        w = csv.writer(sys.stdout); w.writerow(["id", "titulo", "jogo", "competicao", "temporada", "status_texto"] + a.termos)
    exibidos = 0
    for d in docs:
        tid = Path(d["texto"]).stem
        if man and man.get(tid, {}).get("status") != "ok":
            if a.contar: w.writerow([d["id"], d["titulo"], d["jogo"], d["competicao"], d["temporada"], man.get(tid, {}).get("status", "?")] + [""] * len(pads))
            continue
        try:
            txt = abrir(a.remoto, d["texto"], cache)
        except Exception as e:
            print(f"# sem texto para {tid}: {e}", file=sys.stderr); continue
        corpo = txt.split("\n---\n", 1)[-1]
        if a.contar:
            w.writerow([d["id"], d["titulo"], d["jogo"], d["competicao"], d["temporada"], "ok"] + [len(p.findall(corpo)) for p in pads])
            continue
        linhas = corpo.splitlines(); pag, sec = "", ""
        marcas = []
        for i, l in enumerate(linhas):
            m = RX_PAG.search(l)
            if m: pag = m.group(1); continue
            s = RX_SEC.match(l)
            if s and not re.search(r"(\.{4,}|\s{3,})\s*\d{1,3}\s*$", l): sec = f"{s.group(1)} {s.group(2).strip()}"
            bloco = "\n".join(linhas[max(0, i - a.janela // 2): i + a.janela // 2 + 1])
            hit = [bool(p.search(l)) for p in pads]
            if any(hit) and ((a.qualquer) or all(p.search(bloco) for p in pads)):
                if marcas and i - marcas[-1][0] <= a.janela: continue
                marcas.append((i, pag, sec, bloco))
        for i, pg, sc, bloco in marcas:
            if exibidos >= a.max: break
            exibidos += 1
            print(f"=== {d['titulo']}  [{d['id']}]  p. {pg or '?'}  | seção: {sc or '?'}\n{d['url']}\n{bloco.strip()}\n")
    if not a.contar and exibidos >= a.max:
        print(f"# limite de {a.max} trechos atingido; use --max ou filtros", file=sys.stderr)


if __name__ == "__main__":
    main()
