---
format_version: 1
title: "Spirální čtení, poslech a pokec - moje AI workflow pro nasání knihy do mozku"
subtitle: "Jak si z PDF dělám několik vrstev čtení a poslechu, abych mohl kdykoli skončit, pokračovat hlouběji nebo se doptat AI."
slug: spiralni-cteni
date: 2026-03-11
language: cs-CZ
status: experimental
eyebrow: "Spirální čtení"
canonical_url: "/2026/spiralni-cteni/"
tags:
  - audioknihy
  - AI
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
---

::: group id="proc" title="Proč to řeším"
::: card number="01" title="Cesta znalostí z knihy do mozku" default="open"
Chci dnes nasdílet svoje workflow a s ním spojené skripty a zároveň se poptat, jak to řešíte vy. Jaké triky a nápady s AI používáte, aby byla cesta znalostí z knihy do mozku co nejefektivnější?

Řeším to z několika důvodů. Někdy chci číst, spíš krátce, ale intenzivně. Jindy chci poslouchat při procházce nebo v autě. Ne vždy ke knize existuje namluvená verze, ne vždy mi sedí hlas interpreta a často ani nejde o klasickou knihu, ale o delší eseje nebo vědecké práce z ArXivu. Zároveň nechci po několika investovaných hodinách zjistit, že mě to vlastně moc nezajímá.
:::

::: card number="02" title="Nechci pro stromy nevidět les" default="open"
Další problém je, že při čtení detailů člověk snadno ztratí celek. Nechci pro stromy nevidět les. Když už do pětihodinového materiálu investuji neurčený čas, chci, aby informační hodnota s časem rostla. Ne aby prvních třicet minut byl detail, který mi je po přerušení procesu vlastně k ničemu. Chci něco jako princip Matryoshka: začít přehledem a pak se postupně nořit do detailů, ale vždy s vědomím toho, jak to zapadá do celku. Někdy se tomu říká spirální učení, progressive disclosure nebo anytime algoritmus. A do toho všeho chci mít kdykoli možnost přerušit a doptat se AI na cokoli, co mi není jasné.
:::
:::

::: group id="vrstvy" title="Vrstvy ze stejného zdroje"
::: card number="03" title="Jedno PDF, několik otáček spirály" default="open"
Proto mi jako ideální postup vyšlo vzít PDF a nechat z něj automaticky vytvořit několik vrstev obsahu, vždy anglicky i česky. Záleží na tématu, co preferuji, ale hlavně mi to dává možnost kombinace. V některé otáčce spirály si dám jiný jazyk, což je za mě mimochodem výborný trik. Přijde mi, že to aktivuje trochu jiné synapse.

Z jednoho zdroje si nechávám generovat:

::: summary-grid
- **2 minuty**: velmi krátké shrnutí na 2 minuty
- **5 minut**: shrnutí na 5 minut
- **20 minut**: podrobnější sumář na 20 minut
- **60 minut**: hluboký technický podcast jako rozhovor dvou hostitelů na 60 minut
- **Plný poslech**: namluvený celý text, ale upravený pro účely poslechu
- **Markdown**: extrahovaný text v Markdown podobě jako kvalitní vstup do kontextu LLM
:::

::: reveal title="Proč plná verze není slepé čtení PDF"
U té plné verze nejde o slepé čtení dokumentu od začátku do konce. Když je v PDF graf, obrázek nebo tabulka, chci slovní interpretaci, ne mechanické čtení buňky po buňce. Cílem je poslouchat něco, co je použitelné pro člověka, ne jen exportované pro stroj.
:::
:::
:::

::: group id="pipeline" title="Pipeline a nástroje"
::: card number="04" title="Velké dávky bez klikání" default="open"
Určitě se k něčemu podobnému dá dostat v nástrojích jako Copilot nebo NotebookLM, ale ne úplně v té podobě, kterou chci. Hlavně to chci dělat ve velkém. Naházet tam PDFka, spustit a vrátit se pro hotový výsledek. Nechci nikde klikat a ručně to skládat.
:::

::: card number="05" title="Co pipeline používá" default="open"
V dnešní době to ale není zásadní problém. GitHub Copilot CLI mi tohle nakódil překvapivě snadno a velmi dobře. Pro extrakci z PDF používám Azure Content Understanding. Nestačil mi MarkItDown, protože mi nejde jen o text, ale i o rozumné zpracování obrázků, grafů a celkové struktury dokumentu. Potřebuji dostat ven výstup, který je dobře použitelný pro další práci s LLM, ne jen syrový textový výtah. Na zpracování textu používám klasicky LLM a na namluvení Azure Speech text-to-speech, u mě typicky s rychlostí zhruba o 20 procent vyšší, ať to mluví svižněji.

::: steps title="Hrubý tok zpracování"
1. **PDF dovnitř** — naházím PDFka a spustím pipeline.
2. **Azure Content Understanding** — vytáhne text, obrázky, grafy a strukturu dokumentu použitelněji než syrový textový výtah.
3. **LLM a Azure Speech** — LLM připraví vrstvy a Azure Speech z nich udělá poslech, typicky rychlejší zhruba o 20 procent.
4. **OneDrive a mobil** — výstupní adresář mám na OneDrivu a na mobilu do něj kouká aplikace na audioknihy.
:::
:::

::: card number="06" title="Slabé místo: ruční nahrávání do LLM" default="open"
Prakticky to funguje tak, že nahážu PDFka, spustím pipeline a výstupní adresář mám na OneDrivu. Na mobilu do něj kouká aplikace na audioknihy, takže se k tomu dostanu hned. Pak ještě ručně nahrávám knihu do LLM, což je slabé místo celého procesu a budu to chtít dořešit automatizací. Dnes to dávám do Copilot Notebook a Perplexity Spaces, abych se mohl kdykoli doptat na obsah, a to textem i hlasem.
:::
:::

::: group id="workflow" title="Moje spirála v praxi"
::: card number="07" title="Typické rozhodování po prvních minutách" default="open"
Moje typické workflow pak vypadá tak, že si nejdřív poslechnu dvouminutovou verzi, potom pětiminutovou. Tím velmi rychle získám mapu terénu. Pak přichází rozhodování: buď dvacetiminutové shrnutí, šedesátiminutový podcast, nebo plný obsah.

::: sequence title="Tři rychlé otáčky"
1. **2 minuty** — první orientace, jestli mě téma vůbec zajímá.
2. **5 minut** — rychlá mapa terénu a lepší kontext.
3. **20 minut** — skoro vždy, pokud ta kniha není úplný propadák.
:::

Někdy jedu v tomto pořadí, někdy si dvacet nebo šedesát minut přepnu do češtiny, abych změnil režim vnímání, někdy mě dvacet minut zaujme natolik, že jdu rovnou na plnou verzi. A někdy naopak usoudím, že dvacetiminutové summary úplně stačilo.
:::

::: card number="08" title="Kdy pokračuji hlouběji" default="open"
V každém případě, pokud ta kniha není úplný propadák, tak si téměř vždy dám tři otáčky spirály: 2, 5 a 20 minut. U věcí, které jsou pro mě důležité, pokračuji dál. Tohle mi zatím vychází jako nejlepší kompromis mezi rychlostí, hloubkou a možností kdykoli změnit směr nebo se doptat na kontext.

::: callout type="source" title="Repo"
Repo je [tady](https://github.com/tkubica12/book-processing).
:::
:::
:::

::: group id="zaver" title="Otázka na vás"
::: card number="09" title="Jak to máte vy?" default="open"
A zajímá mě, jak to máte vy. Máte nějaké vlastní workflow na spirální čtení, poslech nebo práci s delšími texty přes AI?

::: arrow-list title="Co mě zajímá"
- Jaké triky a nápady s AI používáte pro delší texty?
- Kdy vám stačí summary a kdy jdete do plného obsahu?
- Jak řešíte možnost se kdykoli doptat textem nebo hlasem?
:::
:::
::: closing
Spirální čtení není zkratka kolem knihy. Je to způsob, jak **rychle získat mapu** a pak se nořit přesně tak hluboko, jak téma stojí za to.
:::
:::
