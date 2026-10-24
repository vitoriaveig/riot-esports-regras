#!/usr/bin/env python3
"""Compara dois documentos do corpus (ex.: Regulamento do CBLoL 2025 × 2026) seção a seção.

Uso:
  python scripts/comparar_versoes.py <id_antigo> <id_novo> [--remoto owner/repo] [--csv saida.csv]

Alinha as seções pelo número (ex.: 7.2.1) e, quando a numeração muda, pelo título mais parecido.
Classifica cada seção em: igual, alterada (com % de similaridade), incluída, removida.
É uma ajuda exploratória: confirme no texto integral antes de afirmar uma mudança no artigo.
"""
import argparse, csv, difflib, io, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from buscar import abrir  # noqa: E402

RX = re.compile(r"^\s{0,14}((?:\d{1,2}\.){1,5}\d{0,2})\s+([A-ZÀ-Ý][^.\n]{2,80}?)(?:\.\s|\.$|\s*$)")


def secoes(txt):
    corpo = re.sub(r"<!-- página \d+ -->", "", txt.split("\n---\n", 1)[-1])
    out, atual, buf = {}, ("0", "Preâmbulo"), []
    for l in corpo.splitlines():
        m = RX.match(l)
        if m and not re.search(r"(\.{4,}|\s{3,})\s*\d{1,3}\s*$", l):
            out[atual[0]] = (atual[1], "\n".join(buf).strip())
            atual, buf = (m.group(1).rstrip("."), m.group(2).strip()), [l[m.end():].strip()]
        else:
            buf.append(l.strip())
    out[atual[0]] = (atual[1], "\n".join(buf).strip())
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("antigo"); ap.add_argument("novo")
    ap.add_argument("--remoto"); ap.add_argument("--cache", default=".cache_corpus"); ap.add_argument("--csv")
    a = ap.parse_args(); cache = Path(a.cache)
    cat = {d["id"]: d for d in csv.DictReader(io.StringIO(abrir(a.remoto, "catalogo/catalogo.csv", cache)))}
    A = secoes(abrir(a.remoto, cat[a.antigo]["texto"], cache)); B = secoes(abrir(a.remoto, cat[a.novo]["texto"], cache))
    linhas, usados = [], set()
    for num, (tit, txt) in A.items():
        alvo = num if num in B else None
        if alvo is None:
            melhor = max(B, key=lambda k: difflib.SequenceMatcher(None, tit.lower(), B[k][0].lower()).ratio(), default=None)
            if melhor and difflib.SequenceMatcher(None, tit.lower(), B[melhor][0].lower()).ratio() > 0.85: alvo = melhor
        if alvo is None:
            linhas.append([num, tit, "", "", "removida", ""]); continue
        usados.add(alvo)
        n1, n2 = " ".join(txt.split()), " ".join(B[alvo][1].split())
        r = difflib.SequenceMatcher(None, n1, n2).ratio()
        igual = n1 == n2 and tit == B[alvo][0]
        linhas.append([num, tit, alvo, B[alvo][0], "igual" if igual else "alterada", f"{r:.2f}"])
    for num, (tit, _) in B.items():
        if num not in usados: linhas.append(["", "", num, tit, "incluída", ""])
    cab = ["secao_antiga", "titulo_antigo", "secao_nova", "titulo_novo", "situacao", "similaridade"]
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as f: w = csv.writer(f); w.writerow(cab); w.writerows(linhas)
    resumo = {s: sum(1 for l in linhas if l[4] == s) for s in ["igual", "alterada", "incluída", "removida"]}
    print(f"{cat[a.antigo]['titulo']}  →  {cat[a.novo]['titulo']}\n{resumo}\n")
    for l in linhas:
        if l[4] != "igual": print(" | ".join(l))


if __name__ == "__main__":
    main()
