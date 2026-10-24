#!/usr/bin/env python3
"""Gera catalogo/catalogo.csv e catalogo/catalogo.json a partir de catalogo/listagem_bruta.txt.

A listagem bruta é a cópia fiel dos cartões da Biblioteca de Operações Competitivas da Riot
(https://competitiveops.riotgames.com/pt-BR/library). Este script acrescenta uma classificação
analítica (jogo, competição, região, nível, tipo de documento, temporada, versão, status).

A classificação é automática (regras sobre o título) e foi revisada manualmente em 2026-10-24.
Correções pontuais ficam em OVERRIDES, indexadas pela chave do arquivo (hash da URL), e não pela
posição, para sobreviverem às atualizações da listagem.

Uso: python scripts/gerar_catalogo.py [--raiz .]
"""
import argparse, csv, json, re, unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

CDN = "https://cdn.sanity.io/files/dsfx7636/"
MESES = {m: i for i, m in enumerate(["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO",
                                     "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"], 1)}

# ---------------------------------------------------------------- correções manuais
# chave do arquivo -> campos a sobrescrever
OVERRIDES = {
    # Documentos de LoL que o site rotula como "VCT EMEA" (EMEA Masters / ERLs são do LoL)
    "29cfda2ba883": {"jogo": "LoL", "nota_classificacao": "Site rotula como VCT EMEA; EMEA Masters é competição de LoL"},
    "riotgames.enterprise.slack": {"jogo": "LoL", "temporada": "2025"},
    "e865f60487e1": {"jogo": "LoL", "temporada": "2024"},
    "9a20c12b1be4": {"jogo": "LoL"},
    "e8a76d9bde2d": {"jogo": "LoL", "nota_classificacao": "Título diz 'VCT EMEA Masters', mas a v2.2 de 28/06/2024 corresponde ao EMEA Masters de LoL; conferir no texto"},
    # Temporadas que não aparecem no título
    "3ea5d7549c28": {"temporada": "2026"}, "ba5c6c32ee02": {"temporada": "2026"},
    "ef00799f1f47": {"temporada": "2025"}, "1865561342bc": {"temporada": "2025"},
    "cc250f846cc2": {"temporada": "2025"}, "1569edbdc653": {"temporada": "2025"},
    "face14cbd248": {"temporada": "2025"}, "e69ef6bceb14": {"temporada": "2025"},
    "38aa5f4e2ab4": {"temporada": "2024"}, "143ec2815881": {"temporada": "2022"},
    "84d275e92598": {"temporada": "2021"}, "815602961147": {"temporada": "2025"},
    "cc189b5d24c0": {"temporada": "2025"}, "7224c356f9be": {"temporada": "2024"},
    "5e02c4f2436d": {"temporada": "2024"}, "44e7dc6ef628": {"temporada": "2024"},
    "ed17d56d54af": {"temporada": "2024"}, "276b32200c0c": {"temporada": "2024"},
    "cffa86644dc9": {"temporada": "2025"}, "667003e7af77": {"temporada": "2024"},
    "3290d162991a": {"temporada": "2024"}, "5bcfcb880fa2": {"temporada": "2024"},
    "16b35274e077": {"temporada": "2024"}, "811a2bc66e21": {"temporada": "2024"},
    "2faf03f9bb56": {"temporada": "contínuo"},
    "docs.google.com/spreadsheets": {"temporada": "contínuo"},
}

COMP_RULES = [  # (regex no título, competição, região, nível) — a primeira que casar vence
    (r"Código de Conduta|Code of Conduct", "Riot Esports (todos)", "Global", "Global"),
    (r"Políticas Globais de Esports do LoL|Global Policies|Regras Globais de League of Legends", "LoL Esports (todos)", "Global", "Global"),
    (r"Banco de Dados de Contratos|Contract Database", "Global Contract Database", "Global", "Global"),
    (r"Penalty Tracker|Relatório de Penalidades da EMEA", "EMEA (LEC, ERLs, VCT)", "EMEA", "Regional"),
    (r"Dispute Resolution|Resolução de Conflitos", "EMEA – Resolução de Conflitos", "EMEA", "Regional"),
    (r"Análise da temporada|Season Review", "EMEA (todas as ligas)", "EMEA", "Regional"),
    (r"Campeonato Mundial|World Championship|Worlds", "Worlds (LoL)", "Internacional", "Internacional"),
    (r"Mid-Season|Mid-Seasonal|MSI", "MSI (LoL)", "Internacional", "Internacional"),
    (r"First Stand", "First Stand (LoL)", "Internacional", "Internacional"),
    (r"Eventos Internacionais.*League of Legends|League of Legends Esports International Events", "Eventos internacionais (LoL)", "Internacional", "Internacional"),
    (r"TFT Pro Circuit|Regras Globais de Esports do TFT|Política Global de Jogador dos Esports do TFT|Regulamento Global e Regional do TFT", "TFT Pro Circuit", "Global", "Global"),
    (r"TFT Macao", "TFT Macao Open", "Internacional", "Internacional"),
    (r"TFT.*APAC", "TFT APAC", "APAC", "Regional"),
    (r"TFT.*EMEA", "TFT EMEA", "EMEA", "Regional"),
    (r"TFT.*Americas", "TFT Americas", "Américas", "Regional"),
    (r"Roster Construction|construção do elenco", "VCT (ligas parceiras)", "Global", "Global"),
    (r"Regras oficiais da competição do VCT|Regras Oficiais da Competição de VALORANT|VALORANT Official Competition Ruleset", "VCT (global)", "Global", "Global"),
    (r"propriedade simultânea", "VCT (global)", "Global", "Global"),
    (r"EMEA Masters|Masters EMEA|EM e das ERLs", "EMEA Masters (LoL)", "EMEA", "Tier 2 / Semipro"),
    (r"League of Legends EMEA Championship", "LEC", "EMEA", "Tier 1"),
    (r"campeonato VCT Game Changers|Game Changers Championship|VCT2\d Game Changers", "VCT Game Changers Championship", "Internacional", "Internacional"),
    (r"Masters|\bChampions\b|VCT Paris", "VCT Masters/Champions", "Internacional", "Internacional"),
    (r"Game Changers Latin America", "Game Changers LATAM", "LATAM", "Tier 2 / Semipro"),
    (r"Game Changers Pacific", "Game Changers Pacific", "Pacífico", "Tier 2 / Semipro"),
    (r"Americas Game Changers", "Game Changers Americas", "Américas", "Tier 2 / Semipro"),
    (r"EMEA Game Changers", "Game Changers EMEA", "EMEA", "Tier 2 / Semipro"),
    (r"Challengers Latin America", "VALORANT Challengers LATAM", "LATAM", "Tier 2 / Semipro"),
    (r"Challengers Brazil", "VALORANT Challengers Brasil", "Brasil", "Tier 2 / Semipro"),
    (r"Challengers APAC|Pacific Ascension", "VALORANT Challengers APAC / Ascension Pacific", "Pacífico", "Tier 2 / Semipro"),
    (r"Challengers Ascension Americas", "VALORANT Ascension Americas", "Américas", "Tier 2 / Semipro"),
    (r"Challengers.*EMEA|EMEA Challengers|Challengers Ascension EMEA", "VALORANT Challengers EMEA", "EMEA", "Tier 2 / Semipro"),
    (r"VCT.*EMEA", "VCT EMEA", "EMEA", "Tier 1 (liga parceira)"),
    (r"VCT.*Americas", "VCT Americas", "Américas", "Tier 1 (liga parceira)"),
    (r"VCT.*Pacific", "VCT Pacific", "Pacífico", "Tier 1 (liga parceira)"),
    (r"VCT.*(CN|China)", "VCT China", "China", "Tier 1 (liga parceira)"),
    (r"ERL", "ERLs – European Regional Leagues (LoL)", "EMEA", "Tier 2 / Semipro"),
    (r"empréstimo de jogadores", "LoL EMEA (LEC/ERL)", "EMEA", "Regional"),
    (r"LEC", "LEC", "EMEA", "Tier 1"),
    (r"LCK", "LCK", "Coreia", "Tier 1"),
    (r"LCP", "LCP", "Pacífico", "Tier 1"),
    (r"LCS", "LCS", "América do Norte", "Tier 1"),
    (r"CBLoL", "CBLoL", "Brasil", "Tier 1"),
    (r"LTA.*Tier 2|LATAM Tier 2", "LTA Tier 2 / LATAM Tier 2", "Américas", "Tier 2 / Semipro"),
    (r"LRN e LRS", "LRN e LRS (LTA Tier 2)", "Américas", "Tier 2 / Semipro"),
    (r"LTA", "LTA", "Américas", "Tier 1"),
    (r"Circuito Desafiante", "Circuito Desafiante", "Brasil", "Tier 2 / Semipro"),
    (r"NACL|North American Challengers", "NACL", "América do Norte", "Tier 2 / Semipro"),
    (r"LJL", "LJL", "Japão", "Tier 2 / Semipro"),
    (r"College League", "College LoL (CLOL)", "América do Norte", "Universitário"),
]


def chave_arquivo(href):
    m = re.search(r"([0-9a-f]{40})", href)
    if m: return m.group(1)[:12]
    m = re.search(r"/d/(?:e/)?([\w-]{20,})", href) or re.search(r"%22ids%22%3A%5B%22([\w-]{20,})", href)
    if m: return "g-" + m.group(1)[:16]
    m = re.search(r"/files/[\w]+/([\w]+)/", href)
    if m: return "slack-" + m.group(1)
    return slug(href)


def overrides_para(chave, href):
    d = {}
    for k, v in OVERRIDES.items():
        if k == chave or k in href: d.update(v)
    return d


def iso(d):
    p = d.replace(" DE ", " ").split()
    if len(p) == 3: return f"{p[2]}-{MESES[p[1]]:02d}-{int(p[0]):02d}"
    if len(p) == 2: return f"{p[1]}-{MESES[p[0]]:02d}"
    return d


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"^(arquivado|archived)\s*:\s*", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:70] or "documento"


def jogo(r):
    T = r["titulo"].upper()
    if "TFT" in T: return "TFT"
    if re.search(r"VCT|VALORANT|CHALLENGERS EMEA|CHALLENGERS ASCENSION|GAME CHANGERS|MASTERS SANTIAGO|\bCHAMPIONS\b", T) and "LEAGUE OF LEGENDS" not in T:
        return "VALORANT"
    if re.search(r"CÓDIGO DE CONDUTA|CODE OF CONDUCT|DISPUTE RESOLUTION|RESOLUÇÃO DE CONFLITOS|PENALTY TRACKER|RELATÓRIO DE PENALIDADES|ANÁLISE DA TEMPORADA", T):
        return "Multijogo"
    if r["badge"] == "val": return "VALORANT"
    return "LoL"


def competicao(t):
    for rx, c, reg, niv in COMP_RULES:
        if re.search(rx, t, re.I): return c, reg, niv
    return "a verificar", "a verificar", "a verificar"


def tipo(t):
    regras = [
        (r"Registro de alterações|Changelog", "Changelog"),
        (r"Índice de Penalidades|Penalty Index", "Índice de penalidades"),
        (r"Penalty Tracker|Relatório de Penalidades", "Registro de penalidades aplicadas"),
        (r"Código de Conduta|Code of Conduct", "Código de conduta"),
        (r"Políticas Globais|Política Global|Política de propriedade|Diretriz|Diretrizes|Regulamento Financeiro|Policies", "Política / diretriz"),
        (r"Roster Construction|construção do elenco", "Regras de elenco"),
        (r"\bForm\b|Formulário|Exhibit|Anexo|Template|Application|Acordo de Isenção|Summary Sheet", "Formulário / anexo"),
        (r"Dispute Resolution|Resolução de Conflitos", "Resolução de conflitos"),
        (r"Banco de Dados|Database|Escalação Ativa", "Base de dados / lista"),
        (r"Análise da temporada|Season Review", "Relatório de temporada"),
        (r"Perguntas Frequentes|FAQ", "FAQ"),
        (r"Específic|Specific|Supplementary|Complementares|Carta Regra|대회별", "Regras específicas de evento / suplementares"),
    ]
    for rx, v in regras:
        if re.search(rx, t, re.I): return v
    return "Regulamento de competição"


def temporada(t):
    m = re.search(r"(?<!\d)(20\d\d)(?!\d)", t)
    if m: return m.group(1)
    m = re.search(r"VCT(2\d)", t)
    if m: return "20" + m.group(1)
    if "Lore & Legends" in t: return "2026"
    return ""


def versao(texto):
    m = re.search(r"(?:(?<![A-Za-z])v\.?|Versão |Version:? )\s?([0-9][^\s),]*)", texto)
    return m.group(1).rstrip(".") if m else ""


def status(r):
    s = (r["titulo"] + " " + r["tags"] + " " + r["nota"]).upper()
    return "Arquivado" if re.search(r"ARQUIVADO|ARCHIVED", s) else "Ativo na biblioteca"


def fonte(h):
    if h.startswith("news"):
        return CDN + h, ("DOCX" if h.endswith(".docx") else "PDF"), "Direto (CDN Sanity)"
    if "docs.google.com/spreadsheets" in h: return h, "Google Sheets", "Google (público)"
    if "docs.google.com/document" in h: return h, "Google Docs", "Google (público)"
    if "drive.google.com" in h: return h, "Google Drive (PDF)", "Google (público)"
    if "documentcloud.adobe.com" in h: return h, "Google Drive via Adobe", "Google (público)"
    if "slack.com" in h: return h, "PDF (Slack interno)", "Indisponível ao público"
    return h, "outro", "a verificar"


def ler_listagem(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"): continue
        idx, badge, data, titulo, tags, href, nota = line.split("|", 6)
        rows.append(dict(idx=int(idx), badge=badge, data=data, titulo=titulo, tags=tags, href=href, nota=nota))
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raiz", default=".")
    a = ap.parse_args(); raiz = Path(a.raiz)
    lst = raiz / "catalogo" / "listagem_bruta.txt"
    rows = ler_listagem(lst)
    extraido = re.search(r"em (\d{4}-\d{2}-\d{2})", lst.read_text(encoding="utf-8").splitlines()[0])

    ids, out, por_arquivo = set(), [], defaultdict(list)
    for r in rows:
        sid = slug(r["titulo"])
        while sid in ids: sid += "-b"
        ids.add(sid); r["id"] = sid
        por_arquivo[chave_arquivo(r["href"])].append(sid)

    for r in rows:
        k = chave_arquivo(r["href"])
        c, reg, niv = competicao(r["titulo"])
        url, fmt, acesso = fonte(r["href"])
        texto_id = por_arquivo[k][0]  # o texto extraído é salvo uma vez por arquivo
        d = {
            "id": r["id"], "titulo": r["titulo"], "jogo": jogo(r), "competicao": c, "regiao": reg, "nivel": niv,
            "tipo_documento": tipo(r["titulo"]), "temporada": temporada(r["titulo"]),
            "versao": versao(r["titulo"] + " " + r["nota"]), "status_biblioteca": status(r),
            "data_publicacao_biblioteca": iso(r["data"]), "fixado": "sim" if r["nota"].startswith("FIXADO") else "",
            "formato": fmt, "acesso": acesso, "url": url, "chave_arquivo": k,
            "mesmo_arquivo_que": ";".join(i for i in por_arquivo[k] if i != r["id"]),
            "texto": f"textos/{texto_id}.md", "tags_site": r["tags"],
            "nota": "" if r["nota"] == "FIXADO" else r["nota"], "nota_classificacao": "",
            "ordem_listagem": r["idx"],
        }
        d.update(overrides_para(k, r["href"]))
        out.append(d)

    (raiz / "catalogo").mkdir(exist_ok=True)
    with open(raiz / "catalogo" / "catalogo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    meta = {"fonte": "https://competitiveops.riotgames.com/pt-BR/library",
            "listagem_extraida_em": extraido.group(1) if extraido else "",
            "catalogo_gerado_em": date.today().isoformat(),
            "n_cartoes": len(out), "n_arquivos_unicos": len(por_arquivo), "documentos": out}
    (raiz / "catalogo" / "catalogo.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} cartões, {len(por_arquivo)} arquivos únicos")


if __name__ == "__main__":
    main()
