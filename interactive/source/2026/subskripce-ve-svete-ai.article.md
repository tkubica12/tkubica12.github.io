---
format_version: 1
title: "Je předplatné vhodný obchodní model pro AI produkt? Zdražuje AI? Zdražují tokeny? Nebo se jen najíždí na férový model?"
eyebrow: "Subskripce, tokeny a agenti"
subtitle: "Flat subskripce je skvělá pro adopci, ale agenti rozbíjejí přirozené limity spotřeby. Budoucnost vidím spíš v licenci jako vstupence, poolované předplacené spotřebě a férových dokupovaných jednotkách."
slug: subskripce-ve-svete-ai
date: 2026-04-27
language: cs-CZ
status: experimental
canonical_url: "/new/2026/subskripce-ve-svete-ai/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

V poslední době dochází k mnoha změnám v obchodních modelech některých AI produktů a to zejména těch kolem kódování. Myslím, že je to předzvěst změn i v dalších oblastech - jakmile uvidíme stejný fázový přechod co jsme zažili v prosinci 2025 v kódování (kdy to prostě začalo krásně spolehlivě fungovat), vznikne podobný tlak na ostatní produkty i pro ne-vývojáře. A agenti typu OpenClaw nebo Cowork tipuji na tu další službu, která půjde tímto trendem.

::: group id="predplatne" title="Proč klasické předplatné fungovalo"

::: card number="01" title="Klasické předplatné" default="open"
Pokud necháte lidi platit podle toho jak službu využívají tak je známé, že ji pak využívají málo a nedokáží realizovat plnou hodnotu - nikdy se to vlastně nenaučí, protože pořád počítají peníze a bojí se. Tohle v minulosti geniálně vyřešilo předplatné - vtáhne vás do hry, používáte, zvykáte si, nechcete o to přijít. A šíříte to všude okolo, uživatelská základna se zvyšuje. Zkrátka **flat subskripce je ideální pro adopci**.

::: reveal title="Spotify, posilovna a přirozený limit"
Jak na tom poskytovatel služby vydělává? Je jasné, že to má spočítané tak, aby měl dobrou marži na průměrném uživateli. Na těch co to používají málo vydělává ještě mnohem víc, na power userech vydělává naopak málo a u těch několika extrémních může prodělávat. Vezměme třeba Spotify. To má určitě nějaké fixní náklady na uživatele (za servery, vývoj aplikace apod.), ale velmi mnoho jich bude dáno spotřebou - poplatky autorům, poplatky za přenesená data. Průměrný uživatel konzumuje řekněme 50 hodin měsíčně. A co "power user"? Je tady přirozený limit - i pokud by nespal tak to nemůže být víc jak 730 hodin měsíčně, s nějakým spánkem řekněme 10x víc než ten průměrný (podobně přirozené limity má předplatné do posilovny nebo na MHD). Jiný typ byznysu může mít tenhle rozdíl menší (třeba nějaké předplatné elektronického magazínu - jak moc článků si power user přečte je vcelku jedno) nebo větší (třeba úložiště typu Box s neomezeným prostorem mají také neomezené náklady). Tam kde není přirozený limit (počet hodin v měsíci například), tam se poskytovatel často chrání nějakou "hvězdičkou" - je to neomezené, ale detekuje neférové využívání a dává vágní limit.
:::
:::

::: card number="02" title="Proč je to s AI problematické" default="open"
U běžného chatu samozřejmě velmi aktivní uživatel spotřebuje daleko víc tokenů a generuje tak náklady ne 10x mezi průměrem a power userem, ale určitě spíše 100x. To ale možná pořád ten obchodní model zvládne, ale můžou se tady využívat nějaká omezení:

- Limity v rámci hodiny
- Dočasné přepnutí na levnější model
- Zpomalení odpovědi (ne schválně, ale třeba díky nějaké de-prioritizaci někoho kdo přestřeluje)

Jenže to je chat - **agenti všechno mění**. Už tzv. Deep Research byl trochu problém, ale plnokrevný agent je ještě mnohem větší - a v kódování je to to jediné co dnes dává smysl. Agent může hodiny pracovat na zadané úloze, načítat si kód, dokumentaci (čili mít enormní kontext v tokenech), provolávat nástroje ve stovkách interakcí, vytvářet si kolegy subagenty a paralelně je nechat na částech problému pracovat. No a pokud váš agent pracuje na něčem hodinu, budete na něj koukat nebo otevřete jiné okno a nahodíte dalšího, který řeší něco jiného? Jasně, že to uděláte, takže těch žravých agentů a subagentů nakonec běží de facto neomezené množství. Váš poměr mezi průměrným uživatelem a Power Userem se dostává klidně do 4 řádů rozdílu a prakticky může totálně ustřelit - a vůbec ne schválně, uživatel prostě agenty naplno využil a spánek není přirozený limit.

::: sequence title="Cesta od chatu k agentům"
1. **Chat** — rozdíl mezi průměrem a power userem může být spíše 100x.
2. **Deep Research** — už je trochu problém, protože běží déle a spotřebuje víc kontextu.
3. **Plnokrevný agent** — hodiny práce, stovky tool callů, subagenti a paralelní okna mohou vystřelit spotřebu o celé řády.
:::

::: callout type="verdict" title="Pointa"
Co s tím? **Flat subscription to být nemůže** - a proto tolik změn na trhu a přechod k placení podle férového využívání. Podívejme se nejdřív za co se vlastně bude platit a pak jak to může vypadat.
:::
:::

:::

::: group id="naklady" title="Dva zdroje nákladů"

::: card number="03" title="Tokeny a compute jsou měřitelné" default="open"
Řešení typicky musí zahrnovat platbu za to že existuje - někdo to vytvořil, řeší jeho bezpečnost, architekturu, compliance a také má nějaké náklady na základní provoz. To nás ale teď nezajímá - my se chceme zaměřit na dva zdroje nákladů, které jsou přímo měřitelné a přímo závislé na uživateli (bez něj nevznikají).

::: summary-grid
- **Tokeny**: vstupní, cachované vstupní a výstupní tokeny jsou přímý náklad modelu.
- **Compute**: cloudový agent potřebuje CPU, RAM a izolované prostředí; u agenta je to druhá klíčová složka.
:::

::: reveal title="Tokeny"
**Tokeny** jsou reálné náklady daného řešení. Říká se, že Anthropic má marži na tokenech 40%-50% (což zahrnuje IP modelu a inferencing, tedy GPU) a můžeme tak předpokládat že jinde to bude podobné. I když si poskytovatel model hostuje sám nebo má nějakou slevu, náklady na tokeny jsou stále velmi reálné - tohle není nějaká licence nebo něco podobného, ale skutečné elektrony přeměněné v inteligenci. Vstupní, vstupní cachované a výstupní tokeny jsou přímý náklad. Samozřejmě různé modely mají různé ceny (jsou různě velké co do náročnosti na hardware) a to musí být zahrnuto, takže se obvykle použije nějaký přepočet ve formě "AI jednotky" - střední model 1x, velký 3x a tak podobně. Někde se počítají přímo peníze, ale u služeb podporujích různé modely (například GitHub Copilot s podporou OpenAI, Anthropic i Google) je přepočet přes virtuální měnu častější.
:::

::: reveal title="Compute"
**Compute** začne být druhou klíčovou složkou, protože pro chatbota je spotřebovaný compute relativně malý, ale pro agenta je situace jiná. Ano, agent může běžet lokálně na notebooku uživatele (viz třeba GitHub Copilot CLI), ale z bezpečnostních a praktických důvodů to bude stále častěji stroj v cloudu. Agent potřebuje počítač a dát mu ho v cloudu bude dávat obrovský smysl. Pak je to ale půjčený compute - skutečné náklady za elektrony proudící v CPU a RAM. Infra cloud má nějakou marži (počítejme 30%-40%), takže zase platí, že i když má pro provoz slevu nebo si to hostuje sám, tak i tam většina ceny zůstane jako náklad.
:::
:::

:::

::: group id="cloud-model" title="Model pro cloud"

::: card number="04" title="Subskripce jako vstupenka, balíček spotřeby a dokupy" default="open"
Myslím, že tohle je model budoucnosti - subskripce, která vám odemyká vlastnosti a typicky obsahuje i nějakou **předplacenou spotřebu**, ideálně poolovanou. Pojďme si vysvětlit.

GitHub Copilot (oznámeno a v efektu od června) nebo Cursor fungují na principu, že máte předplatné, které vám umožňuje jeho funkce používat a současně obsahuje nějaké množství spotřeby. Ta může být klidně i naprosto nulová (seat-only, takhle to má Anthropic Claude Enterprise, v ceně není nic), nebo menší (za 20 USD licenci máte 10 USD v ceně), ale standard je obvykle od 1:1 nahoru (Cursor má 1:1 u 20 USD licence, ale 60 USD má v ceně 70 USD spotřeby, GitHub Copilot používá 1:1 takže v 19 USD licenci je 19 USD spotřeby).

::: tabs id="modely-spotreby"
::: tab id="seat-only" title="Seat-only"
Licence odemyká produkt, ale v ceně není žádná spotřeba. Takhle to má Anthropic Claude Enterprise: v licenci nemáte zhola nic, dokupujete všechno.
:::
::: tab id="included" title="Spotřeba v ceně"
Za licenci dostanete i nějaký balík spotřeby. Může být menší než cena licence, 1:1, nebo i vyšší - například Cursor má u 60 USD licence v ceně 70 USD spotřeby.
:::
::: tab id="pool" title="Pool"
Všechny nakoupené licence dávají pool peněz pro celou firmu, takže uživatel, který to používá málo neznamená, že jeho spotřeba je tím ztracena - využije ji někdo jiný.
:::
::: tab id="dokupy" title="Dokupy a limity"
Enterprise potřebuje řídit per-user limity a politiku dokupů podle firmy nebo organizací. To podle mě nahrazuje éru vágních limitů typu týden, hodina, výjimky a nejasné změny.
:::
:::

Co mi přijde velmi férové, a má to pokud vím jen GitHub Copilot a Cursor, je **pool**. Všechny nakoupené licence dávají pool peněz pro celou firmu, takže uživatel, který to používá málo neznamená, že jeho spotřeba je tím ztracena - využije ji někdo jiný. Ideální pro AI infusing do organizace - mají to mít všichni! Tohle je dobrá incentiva, nikdo není "neperspektivní" a proto bez AI, mají všichni a pokud někdo nevyužije naplno, spotřebuje někdo jiný. Je samozřejmě důležité pak mít dobré možnosti řízení případných per-user limitů a politiku dokupů podle firmy nebo jejích organizací - tohle má GitHub Copilot výborně zpracované.

Claude Code je velmi čitelný v Enterprise verzi - **v licenci nemáte zhola nic, dokupujete všechno**. Myslím, že éra vágních limitů (týden, hodina, nikdy neřekneme přesně, řekneme ale pak to pořád měníme a dáváme výjimky) skončí a to zejména pro enterprise, protože takové mlžení pro firmy není dobré. OpenAI Codex ale v tomhle aktuálně ještě jede.
:::

:::

::: group id="zbytek-ai" title="Za kódováním"

::: card number="05" title="To je kódování, co zbytek?" default="open"
Aktuálně se tohle všechno týká kódovacích agentů, ale ostatní AI služby jako je M365 Copilot, Gemini, OpenAI, Claude, stále typicky běží na klasičtější subskripci s podivnými limity. Výjimkou je ale Claude Enterprise - ani pro běžné povídání není v ceně nic, je to seat only. Tipuji, že je to předzvěst toho, že i ostatní služby pro enterprise se jednoho dne dostanou do jiného modelu a tipuji nějaký model dost podobný kódovacím agentům - poplatek za hodinu propůjčeného počítače (například pro Cowork), poplatek za tokeny.

A co vy? Preferujete svět flat subscription s podivnými a nejasnými limity, nenápadným snižováním kvality (viz některé Claude aféry z posledních pár dní), ale potenciálně lepší cenovou předvídatelností a možnost z toho dostat o několik řádů víc, pokud jste power user? Nebo se vám líbí víc model podle skutečné spotřeby s odděleným poplatkem za vstupenku? Já osobně, protože jsem odchován Azure a platbu dle skutečného použití považuji za nejpřirozenější a férovou, mám rád ten model co teď má GitHub Copilot - subskripce něco stojí, ale její hodnotu dostáváte zpět v tokenech a to poolovaně, takže se nemusíte bát dát subskripci i těm, co ještě neumí tolik využívat.
:::

::: card number="06" title="Zdražuje AI?" default="open"
Takže zdražuje AI? Nemyslím - tokeny jsou na celém trhu naceněny velmi férově s rozumnou marží a nikdy se nezdražují pro konkrétní generaci/kvalitu. Spíše přichází nové modely a reálně dnešní mini model v cloudu vám udělá za 5x nižší cenu podobnou službu jako high-end model před rokem, poplatek za jednotku inteligence se tedy naprosto dramaticky snižuje a to víc než u jakékoli jiné IT technologie za posledních 50 let. Jenže - dnes vám kódovací agent za hodinu napíše celou aplikaci, před rokem vám AI asistent navrhl novou třídu a když jste ji spustili, tak jste řešili, že nefunguje a vraceli jste mu to. Jestli vám stačí žít v minulosti, použijte 5x levnější model a užijte si, že šetříte - AI se brutálně zlevnilo. Já raději pojedu na jiné vlně - za velmi podobné peníze jako před rokem či dvěma dnes mám řešení podstatně kvalitnější a užitečnější. Preferuju inteligenci a růst před úsporami. Ale každý to může mít jinak a je to v pořádku - **ale AI se nezdražilo**. Nicméně narazilo se na limit obchodního modelu, který je v této éře neudržitelný. Podle mě potřebujeme model kdy za předvídatelné náklady zavedeme AI všem a díky poolu nepřijdeme o nevyužité tokeny a budeme si řídit rozumně limity dokupování třeba podle organizací nebo individuálně.

::: summary-grid
- **Adopce**: flat subskripce lidi vtáhne do používání.
- **Limit**: agenti nemají přirozený strop spotřeby jako hodiny poslechu nebo návštěvy posilovny.
- **Náklady**: tokeny a cloud compute jsou skutečné a měřitelné náklady.
- **Férovost**: ideální je předvídatelná licence, poolovaná spotřeba a řízené dokupy.
:::

Mám připravené a otestované tipy jak na tokenech šetřit - na to se podíváme v příštím článku!
:::

:::
