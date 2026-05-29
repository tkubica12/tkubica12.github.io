# Spirální čtení, poslech a pokec - moje AI workflow pro nasání knihy do mozku

META
- url: /2026/spiralni-cteni/
- source: interactive\source\2026\spiralni-cteni.article.md
- date: 2026-03-11
- language: cs-CZ
- thesis: Z PDF udělat několik vrstev čtení/poslechu, aby šlo rychle získat mapu, postupně se nořit do detailů a kdykoli se doptat AI.

STRUCTURE
- 01 Proč to řeším
- 02 Vrstvy ze stejného zdroje
- 03 Pipeline a nástroje
- 04 Moje spirála v praxi
- 05 Otázka na čtenáře

KEY POINTS
- Důvody: někdy krátké intenzivní čtení, jindy poslech při procházce/autě; často není audiokniha, nesedí hlas, nebo jde o eseje/vědecké práce z ArXivu.
- Nechce po hodinách zjistit, že ho téma nezajímá.
- Problém detailů: snadno se ztratí celek. Chce Matryoshka/princip spirálního učení/progressive disclosure/anytime algoritmus.
- Cíl: informační hodnota roste s časem; možnost kdykoli přerušit a doptat se AI.
- Trik: generovat vrstvy anglicky i česky; střídání jazyka aktivuje trochu jiné synapse.

DETAILS
## Vrstvy
- Ze zdroje generuje:
  - velmi krátké shrnutí na 2 minuty
  - shrnutí na 5 minut
  - podrobnější sumář na 20 minut
  - hluboký technický podcast jako rozhovor dvou hostitelů na 60 minut
  - namluvený celý text, upravený pro poslech
  - extrahovaný Markdown jako kvalitní vstup do kontextu LLM
- Plná verze není slepé čtení dokumentu: grafy/obrázky/tabulky mají slovní interpretaci, ne mechanické čtení buněk.
- Cíl plné verze: použitelné pro člověka, ne jen export pro stroj.

## Pipeline
- Podobné jde částečně v Copilot nebo NotebookLM, ale autor chce vlastní podobu a velké dávky: naházet PDFka, spustit, vrátit se pro hotový výsledek; bez klikání a ručního skládání.
- GitHub Copilot CLI mu pipeline nakódil překvapivě snadno a dobře.
- Extrakce z PDF: Azure Content Understanding.
- MarkItDown nestačil: nejde jen o text, ale i zpracování obrázků, grafů a celkové struktury dokumentu.
- Zpracování textu: klasicky LLM.
- Namluvení: Azure Speech text-to-speech, typicky rychlost zhruba +20 %, aby to mluvilo svižněji.
- Výstupní adresář: OneDrive; na mobilu ho používá aplikace na audioknihy.
- Slabé místo: ruční nahrávání knihy do LLM; chce automatizovat.
- Dnes dává knihu do Copilot Notebook a Perplexity Spaces, aby se mohl doptat textem i hlasem.

## Workflow
- Nejdřív 2min verze, potom 5min verze => rychlá mapa terénu.
- Pak rozhodnutí: 20min shrnutí, 60min podcast, nebo plný obsah.
- Variace:
  - někdy jede v pořadí 2 -> 5 -> 20 -> 60/plný obsah
  - někdy 20 nebo 60 minut přepne do češtiny pro změnu režimu vnímání
  - někdy po 20 minutách jde rovnou na plnou verzi
  - někdy 20min summary stačí
- Pokud kniha není propadák, téměř vždy dá tři otáčky: 2, 5 a 20 minut.
- U důležitých věcí pokračuje dál.
- Verdikt: nejlepší kompromis mezi rychlostí, hloubkou a možností kdykoli změnit směr nebo se doptat na kontext.

LINKS
- Repo: https://github.com/tkubica12/book-processing

OPEN QUESTION
- Jaké vlastní workflow mají čtenáři pro spirální čtení, poslech nebo práci s delšími texty přes AI?

VERDICT
- Spirální čtení není zkratka kolem knihy. Je to rychlá mapa a řízené noření do hloubky podle hodnoty tématu.
