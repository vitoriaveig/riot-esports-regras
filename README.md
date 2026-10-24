# Regulamentos de esports da Riot Games: corpus para pesquisa

Arquivo de pesquisa com o **catálogo** e o **texto extraído** dos documentos publicados na
[Biblioteca de Operações Competitivas da Riot Games](https://competitiveops.riotgames.com/pt-BR/library):
regulamentos de League of Legends, VALORANT e Teamfight Tactics (ligas, eventos internacionais,
circuitos semiprofissionais), códigos de conduta, políticas globais, índices de penalidades, regras de
elenco, documentos de resolução de conflitos e bases de dados públicas.

O repositório foi pensado para dois usos:

1. **Consultas rápidas** (qual regra vale, em que seção e página).
2. **Pesquisa acadêmica** (comparações entre ligas, evolução entre temporadas, análise de conteúdo).

Ele acompanha a skill `riot-esports-regras`, que lê os arquivos daqui (cópia em [`skill/SKILL.md`](skill/SKILL.md)).

## Conteúdo

| Caminho | O que é |
|---|---|
| `catalogo/listagem_bruta.txt` | Cópia fiel dos cartões da Biblioteca (data, título, etiquetas, link). |
| `catalogo/catalogo.csv` / `.json` | Catálogo classificado: jogo, competição, região, nível, tipo de documento, temporada, versão, status, URL oficial. |
| `textos/<id>.md` | Texto integral extraído de cada arquivo, com cabeçalho de metadados e marcas `<!-- página N -->`. |
| `dados/` | Planilhas públicas (ex.: Global Contract Database) exportadas em CSV, uma por aba. |
| `manifest.csv` | Situação de cada download: `ok`, `erro` ou `indisponivel`; SHA-256, páginas, palavras, idioma, data. |
| `secoes.csv` | Índice das seções numeradas de todos os documentos (documento, número, título, página). |
| `scripts/` | Coleta, extração, busca e comparação de versões. |

Os PDFs originais **não** são versionados aqui: cada texto aponta para o link oficial da Riot.
Os documentos são de autoria e propriedade da Riot Games; este repositório os reúne apenas para
fins de pesquisa, citação e acompanhamento histórico.

## Atualização automática

O workflow [`.github/workflows/atualizar.yml`](.github/workflows/atualizar.yml) roda toda segunda-feira e
também pode ser disparado à mão (aba **Actions → Atualizar corpus de regulamentos → Run workflow**). Ele:

1. relê a Biblioteca em um navegador sem interface e atualiza a listagem;
2. regenera o catálogo;
3. baixa só os documentos novos e extrai o texto;
4. grava as mudanças em um commit. O histórico do Git passa a registrar quando cada documento entrou,
   mudou de link ou foi arquivado, o que já é um dado de pesquisa por si só.

Na primeira vez, dispare o workflow manualmente para montar o corpus completo.

## Uso local

```bash
pip install -r requirements.txt          # e poppler-utils (pdftotext) no sistema
python scripts/gerar_catalogo.py
python scripts/baixar_e_extrair.py       # --forcar para baixar tudo de novo

# buscas
python scripts/buscar.py "coach" "pause" --jogo LoL --temporada 2026
python scripts/buscar.py --regex "betting|gambling|apostas" --qualquer --contar > apostas.csv
python scripts/buscar.py --listar --tipo "Índice de penalidades"

# sem clonar: lê direto do GitHub
python scripts/buscar.py --remoto vitoriaveig/riot-esports-regras "residency"

# evolução entre versões
python scripts/comparar_versoes.py regras-oficiais-da-competicao-de-valorant-2025 regras-oficiais-da-competicao-do-vct-2026
```

## Limitações (para a seção de método)

- A Biblioteca é curada pela Riot e pode retirar ou substituir documentos; o catálogo reflete a data da última leitura.
- Títulos aparecem traduzidos no site em português; o arquivo pode estar em inglês, coreano etc. (coluna `idioma` no manifesto).
- Algumas etiquetas do site estão inconsistentes (ex.: EMEA Masters de LoL marcado como "VCT EMEA"; cartões distintos que apontam para o mesmo arquivo). As correções estão documentadas em `scripts/gerar_catalogo.py` e na coluna `nota_classificacao`.
- A classificação (jogo, competição, nível, tipo) é do pesquisador, feita por regras sobre o título; confira antes de usar como variável.
- A extração de texto de PDF pode quebrar tabelas e colunas; cite sempre conferindo a página no original.
- Ligas sem documentos na Biblioteca (ex.: LPL) não estão cobertas.

## Como citar

> RIOT GAMES. *Título do documento*. Versão X. [S. l.]: Riot Games, ano. Disponível em: URL oficial. Acesso em: data.
> Corpus organizado em: SOBRENOME, Nome. *riot-esports-regras*. GitHub, 2026. Disponível em: https://github.com/vitoriaveig/riot-esports-regras (commit `<hash>`).

Scripts sob licença MIT. Os textos dos regulamentos pertencem à Riot Games.
