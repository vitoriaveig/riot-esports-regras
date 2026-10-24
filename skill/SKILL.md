---
name: "riot-esports-regras"
description: "Consulta e analisa os regulamentos de esports da Riot Games (LoL, VALORANT, TFT) da Biblioteca de Operações Competitivas: ligas, eventos, penalidades, elenco e conduta; use para dúvidas pontuais ou para levantar dados e análises para pesquisa acadêmica."
---

# Regulamentos de esports da Riot Games (LoL, VALORANT, TFT)

Esta skill tem dois modos. Escolha pelo pedido:

- **Consulta rápida**: pergunta pontual ("no CBLoL 2026, o técnico pode falar durante a pausa?", "qual a punição por atraso no VCT?"). Responda na conversa, curto e direto.
- **Análise para pesquisa**: o usuário quer dados, contagens, comparações entre ligas, evolução entre temporadas, tabelas, gráficos ou texto para artigo. Siga a seção 4.

Responda sempre no idioma do usuário.

## 1. Obter as fontes (sempre, nos dois modos)

Os regulamentos mudam a cada temporada e às vezes no meio dela. Nunca responda de memória.

**Fonte principal: corpus no GitHub** (texto extraído de todos os documentos da Biblioteca, atualizado toda semana por GitHub Actions):

- Repositório: https://github.com/vitoriaveig/riot-esports-regras
- Base para leitura: `https://raw.githubusercontent.com/vitoriaveig/riot-esports-regras/main/`
- Arquivos: `catalogo/catalogo.csv` (metadados e link oficial de cada documento), `manifest.csv` (situação da extração), `secoes.csv` (índice de seções com página), `textos/<id>.md` (texto integral com marcas `<!-- página N -->`), `scripts/buscar.py` e `scripts/comparar_versoes.py`.

Passo a passo:

1. Baixe o catálogo e o manifesto com `curl` (ou WebFetch) a partir da base raw.
2. Baixe o buscador e use-o em modo remoto, que lê e guarda em cache só os textos necessários:
   ```bash
   B=https://raw.githubusercontent.com/vitoriaveig/riot-esports-regras/main
   mkdir -p riot && cd riot && curl -sSO $B/scripts/buscar.py && curl -sSO $B/scripts/comparar_versoes.py
   python3 buscar.py --remoto vitoriaveig/riot-esports-regras --listar --jogo LoL --temporada 2026
   python3 buscar.py --remoto vitoriaveig/riot-esports-regras "coach" "pause" --competicao CBLoL
   ```
   Filtros: `--jogo`, `--competicao`, `--temporada`, `--tipo`, `--status`, `--ids`; `--regex`, `--qualquer`, `--contar`, `--max`.
3. Para ler um documento inteiro, baixe `textos/<id>.md` (a coluna `texto` do catálogo dá o caminho).
4. Confira no `manifest.csv` se o texto está `ok`. Leia a coluna `detalhe`: "link quebrado na própria Biblioteca (HTTP 404)" e "documento Google com acesso restrito" são falhas da fonte, não do corpus (relate-as como achado, se for pesquisa); "texto obtido por OCR" pede conferência no original; "planilha vinculada exportada" indica dados em `dados/`. Para documentos sem texto, peça ao usuário que anexe o PDF (o link oficial está no catálogo). Alguns PDFs são só capas com link para uma planilha (ex.: EMEA Penalty Tracker); os links ficam no fim do texto, em "Links presentes no documento".
5. Veja a data no cabeçalho de `catalogo/listagem_bruta.txt`. Se a pergunta for sobre algo muito recente, avise que a Biblioteca pode ter documento mais novo e sugira rodar o workflow (aba Actions do repositório → "Run workflow") ou conferir a página da Biblioteca.

**Restrições importantes:** os PDFs ficam em `cdn.sanity.io`, que bloqueia leitura automática; não tente contornar isso por curl, Python, espelhos ou cache. Se o repositório estiver fora do ar, use o mapa da seção 5 para dizer o que existe e peça o PDF ao usuário. Se o usuário anexar uma versão própria, compare com o corpus e avise sobre diferenças.

## 2. Como ler os regulamentos da Riot

**Camadas normativas** (da mais geral para a mais específica):

1. Código de Conduta Global de Esports: vale para todos os jogos e ligas.
2. Regras globais do jogo: Políticas Globais de Esports do LoL; Regras Oficiais da Competição do VCT e Regras de Construção de Elenco do VCT; Regras Globais e Política Global de Jogador do TFT.
3. Regulamento da liga ou do circuito (LCS, LEC, LCK, LCP, CBLoL, LTA, ERLs, NACL, Circuito Desafiante, VCT Americas/EMEA/Pacific, Challengers etc.).
4. Regras específicas de evento ou suplementares (Worlds, MSI, First Stand, Masters, Champions, Kickoff, Etapas, qualificatórias).
5. Changelogs, índices de penalidades, formulários e FAQs.

Não presuma qual camada prevalece em caso de conflito: procure a cláusula de precedência no próprio documento (em geral nas seções iniciais ou finais) e cite-a. Quando a resposta depender de mais de uma camada, mostre as duas.

**Versão aplicável.** Muitos documentos têm versão (v26.1, v2.6_11Maio2026) e data. O que vale para um fato é a versão vigente na data do fato. A Biblioteca guarda documentos arquivados; use-os para perguntas históricas. "Arquivado" é um rótulo do site, não prova de revogação.

**Cuidados com a Biblioteca** (documentados no catálogo):

- Títulos aparecem traduzidos no site em português, mas o arquivo pode estar em inglês, coreano (LCK 2026) ou outro idioma. Cite o trecho original entre aspas e traduza.
- Alguns cartões apontam para o mesmo arquivo (coluna `mesmo_arquivo_que`), por exemplo LCP 2026 "Oficiais" e "Específicas do Evento"; Challengers Ascension EMEA e Americas; LCK 2025 oficial e específico. Diga ao usuário que o site pode ter um erro e confirme pelo conteúdo qual documento é de fato.
- Algumas etiquetas do site estão erradas: EMEA Masters (LoL) marcado como "VCT EMEA"; Challengers Ascension (VALORANT) marcado como "LTA". O catálogo corrige o jogo; veja `nota_classificacao`.
- Lacunas: a Biblioteca não tem LPL, Wild Rift, 2XKO nem Legends of Runeterra, e a VCT China só aparece em documentos internacionais. Se algo não está no corpus, diga "não consta na Biblioteca", nunca "não existe regra".

**Documentos que são dados empíricos, não normas:** EMEA Penalty Tracker / Relatório de Penalidades da EMEA (sanções efetivamente aplicadas: data, destinatário, equipe, tipo, motivo, liga, expiração); Global Contract Database de LoL e VALORANT (planilhas em `dados/`); Banco de Dados de Jogadores das ERLs; Escalação Ativa da NACL; Análises da temporada na EMEA (2021–2024).

**Glossário.** LCS (América do Norte), LEC (EMEA), LCK (Coreia), LCP (Pacífico), CBLoL (Brasil), LTA (Américas, 2025; LTA Norte/Sul), LRN/LRS (ligas regionais Norte/Sul), ERLs (ligas regionais europeias, Tier 2 de LoL), EMEA Masters (torneio entre ERLs), NACL (Tier 2 norte-americano), Circuito Desafiante (Tier 2 brasileiro), LJL (Japão), CLOL (universitário). VCT = VALORANT Champions Tour (ligas parceiras Americas, EMEA, Pacific, China; Kickoff, Etapas, Masters, Champions); Challengers (Tier 2 de VALORANT); Ascension (acesso ao VCT); Game Changers (circuito para mulheres e gêneros marginalizados); LCQ = Last Chance Qualifier. TFT Pro Circuit e Finais Regionais. GCD = Global Contract Database.

## 3. Modo consulta rápida

1. Identifique jogo, competição, temporada e, se houver, a data do fato.
2. Escolha os documentos pelo catálogo (camada da liga + camada global + evento, se for o caso). Use `secoes.csv` para achar a seção pelo título e `buscar.py` para achar o trecho.
3. Responda em poucas linhas: a regra; seção e página; trecho original entre aspas com tradução; versão e data do documento; ressalvas de camada ou de versão.
4. Para perguntas transversais ("quais ligas exigem X?"), liste liga, temporada, seção e regra resumida.
5. Termine com o link oficial do documento (coluna `url`) e o link do texto no GitHub.

## 4. Modo análise para pesquisa

### 4.1 Montar a base

1. Liste o recorte com `buscar.py --listar` e baixe os textos necessários (ou todos) a partir da base raw. Tente `git clone https://github.com/vitoriaveig/riot-esports-regras.git` se precisar do histórico; se falhar, baixe arquivo por arquivo.
2. Monte em Python uma tabela por documento (metadados do catálogo + manifesto) e, conforme a pergunta, uma tabela por seção (`secoes.csv`) ou por parágrafo/regra.
3. Use um arquivo por documento único (o catálogo tem cartões duplicados que apontam para o mesmo arquivo; conte pelo `texto`, não pelo cartão).
4. Classificações do catálogo (jogo, competição, nível, tipo) foram atribuídas por regras sobre o título. Trate-as como codificação do pesquisador e confira as que entrarem na análise.

### 4.2 Análises que o corpus permite

- **Comparação entre ligas** sobre um tema: idade mínima, residência e jogadores importados, tamanho de elenco e transferências, técnico durante pausas e no palco, pausas e remakes, uso de patch e restrições de campeões/agentes, apostas e patrocinadores vetados, streaming e conteúdo, regras financeiras (Regulamento Financeiro Esportivo da LEC), escala de penalidades.
- **Evolução temporal** com `comparar_versoes.py <id_antigo> <id_novo>` (situação de cada seção: igual, alterada, incluída, removida). Séries disponíveis, entre outras: Código de Conduta 2024–2026; Políticas Globais do LoL 2025–2026; Regras do VCT 2024–2026; Construção de Elenco do VCT 2024–2026; Worlds 2024–2026; MSI 2024–2025; First Stand 2025–2026; ERL 2024–2026 (várias versões); LTA v25.5→v25.7; LCP 2025–2026; VCT EMEA e VCT Americas 2024–2026; NACL 2023–2026. Changelogs são evidência direta de mudança; prefira-os quando existirem.
- **Análise de conteúdo normativo**: contagem de marcadores deônticos (shall/must = obrigação; shall not/may not = proibição; may = permissão) por 1.000 palavras; cláusulas de discricionariedade ("sole discretion", "reserves the right", "at any time") como indicador de centralização da governança; frequência de termos com `buscar.py --contar`.
- **Dados de sanções e contratos**: estatística descritiva das penalidades aplicadas (tipo, motivo, liga, período) e dos contratos da GCD.

### 4.3 Rigor e entrega

- Todos os números saem de código, nunca de estimativa. Toda afirmação sobre uma regra cita documento, seção e página.
- A base codificada vai como planilha (artifact do tipo Sheets, se disponível; .xlsx só se o usuário pedir). Gráficos calculados em código.
- Nota metodológica curta, pronta para o artigo: fonte (Biblioteca de Operações Competitivas da Riot Games e URL), repositório e hash do commit (`git ls-remote https://github.com/vitoriaveig/riot-esports-regras HEAD`), data de acesso, recorte, esquema de codificação e limitações: acervo curado pela própria Riot e sujeito a remoções; títulos traduzidos pelo site; erros de rótulo; extração de PDF que pode quebrar tabelas; classificação atribuída pelo pesquisador. Sugira dupla codificação e concordância (kappa de Cohen) se o artigo exigir.
- Referência no estilo que o usuário indicar (ABNT, APA etc.); se não indicar, pergunte. Modelo ABNT: RIOT GAMES. *Título do documento*. Versão X. [S. l.]: Riot Games, ano. Disponível em: URL oficial. Acesso em: data.

### 4.4 Texto acadêmico

Se o usuário pedir texto para artigo ou revisão de um texto dele: use registro acadêmico adequado a periódicos internacionais de alto impacto, melhore ortografia, coesão e fluidez, e preserve a forma de escrita da autora (vocabulário, ritmo, estrutura de argumento). Não acrescente afirmações que o corpus não sustente; números e citações de regras devem vir da análise feita.

## 5. Mapa do acervo (leitura de 24/10/2026: 147 cartões, 140 arquivos únicos)

Use só para orientar; o catálogo no GitHub é a referência (com títulos completos, versões e links). "(arq.)" = arquivado no site.

**Multijogo**
- EMEA (LEC, ERLs, VCT): Registro de penalidades aplicadas contínuo
- EMEA (todas as ligas): Relatório de temporada 2024; Relatório de temporada 2023; Relatório de temporada 2022; Relatório de temporada 2021
- EMEA – Resolução de Conflitos: Resolução de conflitos 2025; Resolução de conflitos 2025; Resolução de conflitos 2024; Formulário/anexo 2024; Resolução de conflitos 2024; Formulário/anexo 2024; Resolução de conflitos 2024
- Riot Esports (todos): Código de Conduta 2026; Código de Conduta 2025; Código de Conduta 2024 (arq.)

**LoL**
- CBLoL: Regulamento 2026 v26.1
- Circuito Desafiante: Regras de evento/suplementares 2026 v26.2; Regras de evento/suplementares 2026 v26.0; Índice de penalidades 2025
- College LoL (CLOL): Regulamento 2024 v1.01 (arq.)
- EMEA Masters (LoL): Changelog 2025 v3.2 (arq.); Regulamento 2025 v2.1.1; FAQ 2024; Changelog 2024 (arq.); Regulamento 2024 v2.2 (arq.)
- ERLs – European Regional Leagues (LoL): Regulamento 2026 v2.6_11Maio2026; Regulamento 2026 v2.3_17/11/2025; Formulário/anexo 2025; Regulamento 2025 v2.2 (arq.); Regulamento 2025 v2.0 (arq.); Changelog 2025 v2.0 (arq.); Regulamento 2024 v0.3 (arq.); Base de dados 2024; Formulário/anexo 2024; Changelog 2024 v1.3 (arq.)
- Eventos internacionais (LoL): Regulamento 2026 v1.1; Regulamento 2026
- First Stand (LoL): Regras de evento/suplementares 2026; Regulamento 2025
- Global Contract Database: Base de dados contínuo
- LCK: Regulamento 2026; Regras de evento/suplementares 2026; Regulamento 2025
- LCP: Regulamento 2026; Regulamento 2025; Regras de evento/suplementares 2025
- LCS: Regulamento 2026 v2.2
- LEC: Changelog 2026 v3.1; Regulamento 2025 v2.6; Política/diretriz 2025 v1.2; Formulário/anexo 2024; Changelog 2024 (arq.); Regulamento 2024 v2.6; Formulário/anexo 2024
- LJL: Regulamento 2025 v2.3; Formulário/anexo 2025; Regulamento 2025 (arq.)
- LRN e LRS (LTA Tier 2): Índice de penalidades 2025
- LTA: Regulamento 2025 v25.7; Regulamento 2025 v25.5; Índice de penalidades 2025; Índice de penalidades 2025 v11.11.24
- LTA Tier 2 / LATAM Tier 2: Regulamento 2026 v26.4; Regulamento 2025 v25.10 (arq.); Regulamento 2025 v25.6
- LoL EMEA (LEC/ERL): Política/diretriz 2024
- LoL Esports (todos): Política/diretriz 2026; Política/diretriz 2025 (arq.); Regulamento 2020
- MSI (LoL): Regulamento 2025 (arq.); Regulamento 2024
- NACL: Regulamento 2026 v26.6; Índice de penalidades 2025; Base de dados 2024; Índice de penalidades 2024 (arq.); Regulamento 2024 v24.3 (arq.); Regulamento 2023 v23.0
- Worlds (LoL): Regras de evento/suplementares 2026; Regulamento 2025 v1.0 (arq.); Regulamento 2024

**VALORANT**
- Game Changers Americas: Regulamento 2024 v1.0 (arq.)
- Game Changers EMEA: Regulamento 2022 v10 (arq.)
- Game Changers LATAM: Regras de evento/suplementares 2025 v1.01
- Game Changers Pacific: Regulamento 2025 (arq.)
- Global Contract Database: Base de dados contínuo
- VALORANT Ascension Americas: Regulamento 2025 v25.2 (arq.)
- VALORANT Challengers APAC / Ascension Pacific: Regulamento 2025 (arq.); Regras de evento/suplementares 2025 (arq.)
- VALORANT Challengers Brasil: Regras de evento/suplementares 2025 v25.2
- VALORANT Challengers EMEA: Regulamento 2026 v1.0_10May2026; Regulamento 2026; Regulamento 2025 v1.0; Regulamento 2025 v2.0_17.02.2025; Regulamento 2024 v1.0; Regulamento 2024 v1.3
- VALORANT Challengers LATAM: Regras de evento/suplementares 2025 v25.2
- VCT (global): Regulamento 2026; Regulamento 2025; Regulamento 2024 (arq.); Política/diretriz 2021
- VCT (ligas parceiras): Regras de elenco 2026; Regras de elenco 2025 (arq.); Regras de elenco 2024 (arq.)
- VCT Americas: Regras de evento/suplementares 2026; Regras de evento/suplementares 2026 v26.2; Regras de evento/suplementares 2025 v25.3; Política/diretriz 2024; Índice de penalidades 2024 v1.1 (arq.); Regras de evento/suplementares 2024 v24.2 (arq.)
- VCT EMEA: Regulamento 2026 v1.5_20/01/2026; Changelog 2026; Regulamento 2025 v1.3; Changelog 2025 v1.3; Regulamento 2024 (arq.)
- VCT Game Changers Championship: Regulamento 2025 (arq.); Regulamento 2024 (arq.); Regulamento 2022 (arq.)
- VCT Masters/Champions: Regras de evento/suplementares 2026; Regras de evento/suplementares 2026; Regras de evento/suplementares 2025 (arq.); Regras de evento/suplementares 2025 (arq.); Regras de evento/suplementares 2025 (arq.); Regras de evento/suplementares 2024; Regras de evento/suplementares 2024; Regras de evento/suplementares 2024 (arq.)
- VCT Pacific: Regras de evento/suplementares 2026 (arq.); Regras de evento/suplementares 2026

**TFT**
- TFT APAC: Regulamento 2026; Regulamento 2025 (arq.)
- TFT Americas: Regulamento 2026; Regulamento 2025
- TFT EMEA: Regulamento 2026; Regulamento 2025 (arq.); Regulamento 2024; Regulamento 2024; Regulamento 2024
- TFT Macao Open: Regulamento 2024 (arq.)
- TFT Pro Circuit: Regulamento 2026; Regulamento 2026; Política/diretriz 2025

