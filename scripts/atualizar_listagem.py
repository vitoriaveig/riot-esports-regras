#!/usr/bin/env python3
"""Relê a Biblioteca da Riot no navegador (Playwright) e regrava catalogo/listagem_bruta.txt.

Abre https://competitiveops.riotgames.com/pt-BR/library, clica em "Ver mais" até a lista parar
de crescer e copia cada cartão (data, título, descrição, etiquetas, link, selo do jogo).
Se algo falhar ou a lista vier muito menor que a anterior, mantém a listagem antiga.

Uso: python scripts/atualizar_listagem.py [--raiz .] [--min-proporcao 0.8]
"""
import argparse, re, sys, time
from datetime import date
from pathlib import Path

URL = "https://competitiveops.riotgames.com/pt-BR/library"
BOILERPLATE = re.compile(r"(Este (documento|material|recurso)|O recurso|This (document|material)).{0,40}(arquiv|archiv).*?(assistência|auxílio|ajuda|assistance|day-to-day use|decisions?\.|dia a dia\.)", re.I | re.S)

JS = r"""
() => {
  const filtro = [...document.querySelectorAll('main button')].find(b => /filtro|filter/i.test(b.innerText));
  return [...document.querySelectorAll('main a')].map(a => {
    const c = a.querySelector('div[class*="bg_game"]');
    const badge = c ? ((c.className.match(/bg_game\.([\w-]+)/) || [])[1] || '') : '';
    const fixado = filtro ? !!(a.compareDocumentPosition(filtro) & Node.DOCUMENT_POSITION_FOLLOWING) : false;
    return {badge, href: a.href, fixado, linhas: a.innerText.split('\n').map(s => s.trim()).filter(Boolean)};
  });
}
"""


def coletar():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(locale="pt-BR")
        pg.goto(URL, wait_until="networkidle", timeout=120000)
        anterior, parado = -1, 0
        for _ in range(80):
            n = pg.locator("main a").count()
            parado = parado + 1 if n == anterior else 0
            if parado >= 3: break
            anterior = n
            btn = pg.get_by_role("button", name=re.compile("ver mais", re.I))
            if btn.count() == 0: break
            btn.first.scroll_into_view_if_needed(); btn.first.click(); time.sleep(1.5)
        cards = pg.evaluate(JS); b.close()
    return cards


def para_linha(i, c):
    ls = c["linhas"]
    data, titulo, resto = ls[0], ls[1] if len(ls) > 1 else "", ls[2:]
    tags = [s for s in resto if s == s.upper() and len(s) < 45 and not re.search(r"[a-z]", s)]
    desc = " ".join(s for s in resto if s not in tags).replace("\\n", " ")
    desc = re.sub(r"\s+", " ", BOILERPLATE.sub("", desc)).strip()[:220]
    href = c["href"].replace("https://cdn.sanity.io/files/dsfx7636/", "")
    nota = ("FIXADO" if c["fixado"] else "") + ((". " if c["fixado"] and desc else "") + desc)
    return "|".join([str(i), c["badge"], data, titulo.replace("|", "/"), ",".join(tags), href, nota.replace("|", "/")])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raiz", default="."); ap.add_argument("--min-proporcao", type=float, default=0.8)
    a = ap.parse_args(); alvo = Path(a.raiz) / "catalogo" / "listagem_bruta.txt"
    antigas = [l for l in alvo.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")] if alvo.exists() else []
    try:
        cards = coletar()
    except Exception as e:
        print("Falha ao ler a Biblioteca; listagem mantida:", e); return 0
    if len(cards) < a.min_proporcao * len(antigas):
        print(f"Só {len(cards)} cartões (antes {len(antigas)}); listagem mantida."); return 0
    # preserva notas escritas à mão na listagem antiga (mesmo título + link)
    notas = {tuple(l.split("|")[3:6:2]): l.split("|", 6)[6] for l in antigas}
    linhas = []
    for i, c in enumerate(cards):
        l = para_linha(i, c).split("|", 6)
        manual = notas.get((l[3], l[5]))
        if manual and len(manual) > len(l[6]): l[6] = manual
        linhas.append("|".join(l))
    cab = [f"# Extraído de {URL} em {date.today().isoformat()} ({len(cards)} cartões, {sum(c['fixado'] for c in cards)} fixados)",
           "# idx|game_badge|data_publicacao|titulo|tags|href|nota"]
    alvo.write_text("\n".join(cab + linhas) + "\n", encoding="utf-8")
    novos = len({tuple(l.split('|')[3:6:2]) for l in linhas} - set(notas))
    print(f"{len(cards)} cartões; {novos} novos ou alterados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
