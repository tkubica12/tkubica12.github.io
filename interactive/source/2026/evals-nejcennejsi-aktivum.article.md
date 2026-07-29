---
format_version: 1
title: "Nejcennější aktivum vaší firmy ve světě AI je definice toho, co je dobře."
eyebrow: "Kam se stěhuje hodnota v AI"
subtitle: "Prompt zestárl, kontext si agent najde sám, specifikaci vám napíše. Co ale musíte udělat vy?"
slug: evals-nejcennejsi-aktivum
date: 2026-07-29
language: cs-CZ
status: experimental
published: true
canonical_url: "/2026/evals-nejcennejsi-aktivum/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

# Nejcennější aktivum vaší firmy ve světě AI je definice toho, co je dobře.

Když nastoupí do firmy nový člověk, dostane přístupy, dokumentaci, data a kód. To je ta snadná část, trvá den, a přitom je důležitá - bez ní by nefungoval vůbec. Jenže pak tam sedí ještě půl roku, než začne být opravdu užitečný. V té době se učí něco, co mu nikdo neumí napsat: kdy se který proces obchází a proč je to v pořádku, který zákazník to myslí vážně, co znamená, když někdo na schůzce řekne "to zvládneme".

Přesně v téhle situaci je dneska každý AI systém, který do firmy pustíte. Tu první část mu dáte za odpoledne. Tu druhou ne.

Otázka pak zní, jak toho člověka po půl roce vlastně poznáte. Podle čeho víte, že už je dobrý? Protože dokud na tohle neumíte odpovědět, neumíte to naučit ani AI.

::: group id="o-co-jde" title="O co tady jde"

::: card number="" title="Nejen data, kód a modely" default="open"
Na Buildu letos v červnu k tomu Satya Nadella řekl větu, která podle mě trochu zapadla - že **privátní evals jsou možná to největší duševní vlastnictví (IP), které dnes firma může mít**. A přidal k tomu test: máte privátní eval, běžíte na modelu A. Dokážete přepnout na model B a stoupat dál? Jestli ano, máte to pod kontrolou.

Nejen data. Nejen kód. Nejen modely. Nejen specifikace, o kterých se poslední rok mluví jako o novém firemním zlatě. Schopnost změřit, že je výsledek dobrý.
:::

:::

::: group id="prompt-agent" title="Od promptu k agentovi"

Nejdřív byla věda se správně zeptat. Pak vyhledat ty správné informace a naservírovat je modelu. A dneska ladíme spíš nástroje a počítač pro agenta - zbytek už si vyřeší sám.

::: card number="01" title="Prompt engineering a profese, která nikdy nebyla profesí" default="closed"
Na začátku to byl jednoznačně prompt. Umění se zeptat. Vznikla kolem toho celá "profese" a existovaly propracované sady pravidel, které jsme si všichni předávali - formulovat pozitivně a ne negacemi, na konec zopakovat to nejdůležitější, dát pár příkladů, přinutit model k postupnému uvažování větou "let's think step by step", oddělovat sekce, strukturovat vstup.

A tehdy to fakt fungovalo. Rozdíl mezi dobrým a špatným promptem byl rozdíl mezi použitelným a nepoužitelným výstupem.

Mediální vrchol byl někdy na jaře 2023, kdy Anthropic inzeroval pozici "Prompt Engineer and Librarian" s kompenzací [až 335 000 dolarů ročně](https://www.washingtonpost.com/business/2023/02/25/prompt-engineers-techs-next-big-job/). Zajímavé ale je, že to nikdy nebyl skutečný trh - [analýza inzerátů na LinkedIn](https://arxiv.org/abs/2506.00058) našla pouhých 72 prompt-engineer pozic z 20 662, tedy nějakých 0,35 %. Bublina, která se ve skutečnosti nikdy nenafoukla. Jen se o ní hodně psalo.

Nebylo by ale fér říct, že prompt engineering umřel - jen se rozdělil na dvě části a ta mechanická zmizela v modelu samotném a jeho rozvinutých schopnostech uvažování. OpenAI dnes u reasoning modelů přímo doporučuje **"Avoid chain-of-thought prompts"** a **"Try zero shot first"** ([reasoning best practices](https://developers.openai.com/api/docs/guides/reasoning-best-practices)), protože model si uvažování udělá sám a vaše berlička ho spíš rozhodí. Anthropic naopak dodnes tvrdí, že příklady jsou **"one of the most reliable ways"** jak model řídit. Není to černobílé, záleží na modelové rodině a na úloze.

Ale ta obsahová část - co vlastně chci - je najednou důležitější než forma. A to je celá pointa.

::: callout type="rule" title="Verdikt"
Ty techniky nezmizely proto, že by byly špatné. Zmizely proto, že model přestal potřebovat berličku. Přestali jsme řešit, **jak** se zeptat, a začali jsme řešit, **na co** se ptáme.
:::
:::

::: card number="02" title="Context engineering, vybíráme co by si měl model přečíst" default="closed"
Jakmile přestalo záležet na formulaci, přesunula se pozornost o patro výš. Co dostane model do kontextového okna? Jaká data, jaké texty, jak je připravit, jak chunkovat, jak rerankovat. Postavil jsem na tomhle tématu [celou sérii o RAG](/2025/rag-part1/) a byla to opravdu věda.

Termín zviralizoval Tobi Lütke 19. 6. 2025 definicí **"the art of providing all the context for the task to be plausibly solvable by the LLM"** ([zdroj](https://x.com/tobi/status/1935533422589399127)). O šest dní později to Andrej Karpathy rozšířil na **"the delicate art and science of filling the context window with just the right information for the next step"** ([zdroj](https://x.com/karpathy/status/1937902205765607626)). Anthropic to pak 29. 9. 2025 [zformalizoval](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) jako strategie pro kurátorství a udržování optimální sady tokenů během inference, včetně promptu, nástrojů, MCP, historie, paměti i externích dat.

Všimněte si toho posunu. Přestali jsme ladit otázku a začali ladit to, co je v zorném poli modelu (context window). Pořád jsme ale byli my ti, kdo to zorné pole staví.
:::

::: card number="03" title="Agentický přístup, kontext si najdu sám, děkuji" default="closed"
V podobné době přišly nástroje a s nimi agentické chování. Agent se může rozhodnout, že si něco dotáhne. Zeptá se ve stávajících systémech, napíše si query do databáze, přečte si soubor, zkusí to znovu jinak. A iteruje.

Tím se ta pečlivá příprava kontextu částečně rozpustila. Nemusíme už tak úzkostlivě řešit, jak vybrat těch správných pět odstavců, protože si je agent najde sám.

RAG sice už není pupek světa, ale je stále zásadním prostředkem optimalizace nákladů, rychlosti a kvality odpovědí. Anthropic sice ukázal, že jejich multi-agent Research systém překonal single-agent Claude Opus 4 v interním evalu [o 90,2 %](https://www.anthropic.com/engineering/multi-agent-research-system), ale spotřeboval při tom zhruba **patnáctkrát víc tokenů** než běžný chat. Microsoft svůj [Agentic Retrieval](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview) popisuje explicitně jako věc určenou *pro* RAG patterny, ne jako jejich náhradu. Dobře připravený kontext pořád zvyšuje spolehlivost a snižuje náklady. Jen už není podmínkou, aby to vůbec fungovalo.

A pak přišlo to, co mě baví nejvíc - **agent si začal psát poznámky pro svou pozdější práci**. Anthropic vydal [Agent Skills](https://claude.com/blog/skills) 16. 10. 2025 a [memory tool](https://claude.com/blog/context-management) 29. 9. 2025, formát skillů se pak 18. 12. 2025 [stal otevřeným standardem](https://agentskills.io/).

Když se agent natrápí přes tři slepé uličky, než najde správný způsob dotazu do databáze, umí to dneska zobecnit a uložit jako skill. Procedurální paměť. Přemýšlecí cache. To už není retrieval, to je začátek učení. Psal jsem o tom podrobněji v článku o [software jako paměti](/2026/ai-code-context-feedback/), kde si můj domácí agent sám napsal CLI a okomentoval si ho ve skillu.

::: callout type="info" title="Kde jsme"
Kontext přestal být něco, co agentovi dodávám. Stal se něčím, co si agent staví - a co si mezi běhy pamatuje.
:::
:::

:::

::: group id="radek-zamer" title="Od řádku k záměru"

V oblasti kódování je to zase trochu jiný pohled na změny v posledních pár letech, ale stojí na stejných principech. Výsledkem je změna jednotky práce a zadání - a postupně nás to dovedlo k fenoménu spec-driven development.

::: card number="04" title="Jak rostla jednotka zadání" default="closed"
Jednotka práce v software se za tři roky posunula tak, že se to skoro nedá srovnat. Psal jsem o tom podrobněji [v samostatném článku](/2026/agenti-token-kapital-build-2026/), takže tady jen zkratka:

::: sequence title="Kus práce, který můžu předat"
1. **Řádek** — dopiš mi tenhle for cyklus. Autocomplete, který hádá další řádek.
2. **Funkce** — napiš celou funkci podle komentáře nebo signatury. A brzy nato změna napříč deseti soubory.
3. **Úloha** — kódovací agent. Sám si to sestaví, spustí, otestuje, uvidí chybu a opraví ji.
:::

Podstatné je, že **neubývalo práce, ubývalo "jak"**. Na první příčce jsem musel vědět úplně přesně, co má být na dalším řádku. Na třetí už jenom to, co má být na konci hotové.

Na té třetí příčce se poprvé objevila **zpětná vazba**. Agent si spustí testy, uvidí červenou a jde to opravit. To je zárodek celé zbývající části tohohle článku - jen se posuneme o jednu vrstvu smyček nahoru.
:::

::: card number="05" title="Spec-driven development: říkám agentovi přesně, co má dělat" default="closed"
Když jednotka zadání dorostla do "úlohy", vznikl nový problém. Agent teď pracuje hodinu bez mého dohledu. Chat, ve kterém jsem mu to řekl, je nespolehlivý, zapomíná se, nikdo si ho nepřečte podruhé. Potřeboval jsem trvanlivý artefakt.

Tak vznikl spec-driven development. AWS uvedl [Kiro](https://kiro.dev/blog/introducing-kiro/) 14. 7. 2025, GitHub vydal [Spec Kit](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/) 2. 9. 2025 s cyklem Specify → Plan → Tasks → Implement. Specifikace jako živý zdroj pravdy.

Chci zdůraznit, že to není móda, ale dobrý inženýrský nápad, a to ze tří důvodů:

::: steps title="Proč spec-driven dává smysl"
1. **Kód přestal být vstup** — stal se z něj výstupní artefakt. Můžu ho zahodit a nechat vygenerovat znovu. Specifikace je pak jediná věc, kterou opravdu vlastním.
2. **Je to čitelné pro člověka i pro stroj** — na rozdíl od kódu je specifikace srozumitelná i pro obchod, právníky nebo compliance.
3. **A hlavně: je testovatelná** — dá se podle ní zpětně ověřit, že to agent napsal tak, jak jsme chtěli.
:::

Ten třetí bod je ten důležitý a málo se o něm mluví. Spec-driven totiž do toho příběhu přinesl **nezávislého kontrolora**. Jeden agent píše kód podle specifikace, druhý agent nebo člověk nezávisle ověří, že ji dodržel. To je strašně užitečná vlastnost, je to auditní artefakt, a nechci o něj přijít ani v budoucnu.

Jenže. A tady je ta trhlina, kvůli které tenhle článek vlastně píšu.

::: callout type="warning" title="Trhlina"
Specifikace popisuje, **jak něco udělat**. Neříká, jak poznám, že je výsledek dobrý.
:::
:::

:::

::: group id="smycka" title="Uzavírání smyček u kódování"

Až sem to bylo o tom, jak dobře agentovi zadat práci. Teď přijde obrat: nejzajímavější věci se začaly dít ve chvíli, kdy jsme přestali zadávat a začali stavět smyčku, která si výsledek sama hodnotí.

::: card number="06" title="Pokračuj, dokud to nebude tak dobré jako Call of Duty" default="closed"
Matt Shumer zveřejnil 25. 7. 2026 [post](https://x.com/mattshumer_/status/2081054356405731740) se slovy "Claude Opus 5 one-shotted this game" a ukázkou first-person střílečky. Internet se zbláznil. Metodiku pak o dva dny později popsal pod názvem [Gauntlet Loop](https://somethingbig.ai/gauntlet-loop).

Ten prompt stojí za přečtení celý, protože je to hezky čistá esence toho přístupu.

::: reveal title="Celé znění Shumerova promptu"
```text label="mshumer/Claude-of-Duty - prompt.md"
I want you to build a first-person shooter at the level of the most recent
Call of Duty games. It should be utterly perfect, visually beautiful, with
every single thing done at AAA quality—from textures to physics to anything
you could think of.

Fan out sub-agents and have sub-agents tackle each one individually so that
the game is utterly perfect. You should /loop on each item and have a separate
sub-agent check it visually to ensure it looks triple A. That separate
sub-agent should be a really harsh critic, and if it doesn't look triple A,
it should keep going.

Don't stop until each sub-agent is utterly wowed with the quality when compared
with the actual Call of Duty game. It should literally compare them side by
side blind and say which one looks better. Do this in ThreeJS. /loop until it's
utterly perfect. Fan out sub-agents and ultracode.
```
:::

Podstatné na tom není zadání hry. Podstatné je, že tam vůbec není napsáno, **jak** to udělat. Je tam napsáno, **jak se pozná, že je to hotové**: oddělený subagent, nemilosrdný kritik, slepé porovnání vedle sebe se skutečnou hrou, a smyčka běží dál, dokud kritik neřekne dost.

Shumer to o dva dny později upřesnil: *"I gave Claude Code one prompt, then left it alone. It spent many hours working, spawned a massive fleet of subagents, wrote roughly 55,000 lines of code... I did not sit there steering it, at all."* Jeden prompt, žádné doptávání, mnoho hodin autonomní práce a zhruba 55 tisíc řádků kódu.

Ten kritik navíc neměl referenční bod jen v paměti modelu. Shumer to popsal doslova: *"For the game, I used actual Call of Duty screenshots. The critic was supposed to look at the two side by side, decide which was better, and keep going whenever ours lost."*

Technicky to fungovalo tak, že Playwright pustil vytvářenou hru v headless Chromiu, odchytil jedenáct předem definovaných pohledů ve full HD - prostředí, světlo, materiály, zbraň v ruce, zaměřování, dopady, HUD - a ty pak šly kritikovi proti skutečným snímkům z Call of Duty. Naslepo, aby nevěděl, který obrázek je čí.

::: callout type="rule" title="Klíčový moment"
Ta smyčka nefungovala jen proto, že byla chytře napsaná. Fungovala proto, že měla k dispozici hotovou, veřejnou, sdílenou definici toho, co je dobře - a to doslova ve formě obrázků, které si kdokoli stáhne.
:::
:::

::: card number="07" title="Vaše firma není Call of Duty" default="closed"
Když si otevřete [jeho repozitář](https://github.com/mshumer/Claude-of-Duty), najdete tam něco, co se do virálních postů nedostalo:

> **"The goal was to match a modern Call of Duty. It does not."**

Skóre se během těch smyček posunulo z 3,59 přes 4,14 a 4,05 na konečných 5,05 z deseti - všimněte si, že jedno kolo bylo dokonce horší než předchozí. Dva z jedenácti pohledů se dostaly na hodnocení "CLOSE", zbytek zůstal na "AMATEUR". A ve **všech** slepých A/B srovnáních vyhrálo skutečné Call of Duty.

Ta smyčka udělala přesně to, k čemu byla postavená. Poctivě změřila, že cíle nedosáhla, a napsala to nahlas. To je mnohem cennější než naleštěná ukázka bez čísla - protože z čísla se dá pokračovat.

A tady je ta nepříjemná zpráva pro vás.

::: callout type="warning" title="Zásadní zjištění"
Váš referenční bod nikde neleží. Neexistuje složka se snímky, které by kritik položil vedle vašeho procesu a řekl "tady to zaostává". A pokud model zná vaši firmu dokonale, máte mnohem větší problém než pomalou adopci AI - jste komodita a míříte k nulové marži. Jinak řečeno: pokud jste zajímavá firma, model **nezná** naprostou většinu toho, co vás dělá vámi.
:::

Což znamená, že tu část, kterou Shumer dostal zadarmo, si musíte vyrobit sami. A to je ta nejtěžší práce v celém řetězci.
:::

::: card number="08" title="Loop engineering a 70 USD do koše" default="closed"
Ten posun od zadávání práce k navrhování smyček dostal v červnu 2026 i jméno. [Addy Osmani](https://addyosmani.com/blog/loop-engineering/) ho 7. 6. definoval jako **"replacing yourself as the person who prompts the agent. You design the system that does it instead."** Peter Steinberger, autor [OpenClaw](https://github.com/openclaw/openclaw), řekl tentýž den totéž jinak: **"You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents."**

Já si to překládám takhle. Přestal jsem mluvit s agentem a začal jsem mluvit s **předákem**. Neříkám mu, jak a co má naprogramovat. Říkám mu, čeho chci dosáhnout. Předák si to rozseká na dílčí úlohy, sám napíše specifikace, rozdá práci ostatním agentům a pak je bičuje tak dlouho, dokud výsledek neodpovídá záměru. Já do toho v mezičase nesahám.

Zní to skvěle. Tak jsem si takovou smyčku postavil.

Cílem byl jednodenní workshop na Microsoft Foundry - kombinace krátké prezentace, demo ukázek a krátkých hands-on labů pro účastníky. Měl jsem agendu, měl jsem plán. Vytvořil jsem ekosystém subagentů úplně v Mattově duchu: jeden se na to díval očima pedagoga, druhý očima studenta, třetí očima grafika, čtvrtý očima inženýra. A makali na tom.

O sedmdesát dolarů později mi představili výsledek. Dokonale naleštěné materiály. Krásné, detailní, fakticky naprosto správné, pedagogicky výborně vystavěné.

**Nebyl tam žádný Azure.**

Já chtěl skutečná dema a skutečné laby, kde si účastník sáhne na reálný zdroj. Oni to pojali jako teoretické cvičení, kde praktičnost spočívala v interaktivních formulářích, ve kterých se krásně skládala AI architektura. Výborné. Ale ne to, co jsem chtěl. Letělo to celé do koše.

Chyba byla samozřejmě u mě. Moje smyčka kontrolovala témata, strukturu, vizuál a pedagogickou návaznost. Nikdy nesáhla na reálný zdroj v Azure. **Vybičoval jsem model k dokonalosti v disciplíně, která nebyla pro výsledek to zásadní.** Model nemá uvnitř představu, co je výsledek, není to Call of Duty - a moje definice dobrého výsledku byla mizerně připravená.

::: callout type="rule" title="Verdikt"
Loop engineering neposouvá tu těžkou práci pryč. Jen ji přesouvá jinam. Místo "napiš mi, jak to má vypadat" je otázka "napiš mi, podle čeho poznáš, že je to dobře". A to je mnohem těžší otázka, protože na ni většina firem nemá odpověď ani pro své lidi.
:::
:::

:::

::: group id="firma" title="Hill-climbing a enterprise smyčky"

Zatím jsme byli u kódu, kde se výsledek dá spustit a otestovat. Teď to samé zkusme ve firmě, kde se většina práce spustit nedá - a přesto se u ní musí poznat, jestli je dobrá.

::: card number="09" title="Víme víc, než říkáme" default="closed"
Představte si, že tyhle principy chcete posunout do lidské práce ve firmě plné unikátních znalostí. Často nevyřčených. Často fungujících jinak, než je napsané - a přitom dobře a flexibilně, protože ta firma prostě funguje.

Pomáhá mi na to koukat přes tři vrstvy:

::: steps title="Z čeho se skládá to, co vaši firmu dělá firmou"
1. **Explicitní znalost** — data. Dokumenty, databáze, čísla, dokumentace. Tohle všichni znají a dvacet let se to označovalo za firemní zlato.
2. **Institucionální a procedurální znalost** — postupy, procesy, pravidla. Často zabetonovaná v aplikačním kódu, často nikde nepopsaná celá.
3. **Implicitní znalost** — to, co mají zaměstnanci v hlavách. To, co si nový člověk musí za těch šest měsíců nasbírat, protože mu to nikdo neumí napsat.
:::

Michael Polanyi to v roce 1966 shrnul větou, kterou nikdo nepřekonal: **"we can know more than we can tell."**

Nechci tvrdit, že první vrstva je bezcenná, to by byla hloupost - bez dat nefunguje nic. Chci říct něco jiného: **je to jediná vrstva, kterou umíte předat za odpoledne.** A co předáte, to se dá zkopírovat.

Pokud výrobci modelu předáte svoje data, aby je použil na trénink, je to výhoda spíš pro něj než pro vás. A pokud mu necháte poslouchat i lidské interakce a ukládat si je k analýze, může odtéct i to nevyřčené. Mít data v cloudu problém není, odevzdat kontrolu nad nimi problém je. Chci v cloudu použít svoji firemní unikátnost k získání AI na míru - ale chci ten výsledek vlastnit.

Zatím to nevnímám jako problém. Trochu se ale obávám doby, kdy někteří výrobci budou v zájmu "bezpečnosti" ten výsledek vlastnit za vás. A za rok bude vaše unikátnost náhodou v nabídce "as a service" pro všechny.

Satya Nadella tomu v [textu z 12. 7. 2026](https://x.com/satyanadella/article/2076323181154230284) dal jméno: **Reverse Information Paradox**. Ekonom Kenneth Arrow kdysi popsal, že hodnotu informace kupující nezná, dokud mu ji neodhalíte - jenže jakmile ji odhalíte, má ji zadarmo. AI ten problém podle Nadelly otočila: teď musí svoje know-how odhalit **kupující**, aby pro něj ta inteligence byla vůbec užitečná. Platíte tedy dvakrát. Jednou penězi, podruhé znalostí. A čím lepší výsledek chcete, tím víc té znalosti musíte dát.

> **"Models learn from exhaust, the prompts people write, the tools agents use, and especially the corrections people make when the model is wrong. Every correction is distilled into institutional know-how. It's the kind of knowledge a competitor could never buy, and the kind that leaks almost imperceptibly: trace by trace, correction by correction, eval by eval."**

Všimněte si toho konce. Trace by trace, correction by correction, **eval by eval**.

::: callout type="rule" title="Verdikt"
Co je univerzální, to bude v modelu. Co je vaše, si musíte umět nechat - a platí to pro všechny tři vrstvy, data nevyjímaje.
:::
:::

::: card number="10" title="Hill-climbing machine a učení při práci" default="closed"
Když víme, že rozhoduje smyčka, a víme, že u firemních věcí nemáme hotovou definici úspěchu, kudy dál? Za mě je odpověď continuous learning, respektive on-the-job learning. Zkušenost nasbíraná při skutečném provádění práce a v interakci s ostatními je pro naprostou většinu ekonomicky důležitých činností nenahraditelná. Pokud má AI opravdu násobit schopnosti lidí, musí se učit i z nejasných signálů.

Microsoft pro to má hezký název. V oznámení nových MAI modelů z 2. 6. 2026 tým píše, že cílem je postavit **"what we think of as a hill-climbing machine: an organization that can continuously improve, cycle after cycle"** ([zdroj](https://microsoft.ai/news/building-a-hillclimbing-machine-launching-seven-new-mai-models/)).

Z opačného konce to popisuje Thinking Machines Lab: **"Most AI in use today is trained in a handful of places and then frozen"** ([manifest z 10. 7. 2026](https://thinkingmachines.ai/blog/the-future-worth-building-is-human/)). Jejich [Inkling](https://thinkingmachines.ai/news/introducing-inkling/) z 15. 7. 2026 je pro můj argument obzvlášť pěkný - je to ukázka modelu, který si sám připraví evaly, nasbírá data a přes Tinker se dotrénuje. Řízený experiment, ne magie, ale směr je jasný.

Kde reálně jsme dnes? Za mě ve čtyřech vrstvách, které se překrývají:

::: sequence title="Čtyři vrstvy dnešní adopce"
1. **Pomocník na chatu** — ptám se, dostávám odpovědi. Nejrozšířenější a nejmíň zajímavé.
2. **Auditovatelné automatizační workflow** — zpracování faktur a podobné procesy. Deterministické mantinely, jasný výstup.
3. **Osobní pracant s dopadem do reálného světa** — sáhne do kalendáře, něco vytvoří, pošle to mailem, počká na odpovědi, posbírá data, analyzuje je a založí lead do CRM nebo doplní poznámku ze zápisu schůzky.
4. **Digitální pracovník** — už to není můj nástroj, ale entita v organizaci. Má vlastní schránku, je na Teamsech, má přidělené přístupy a učí se z toho, jak jeho práce dopadla.
:::

Ta třetí vrstva je dneska nejzajímavější prakticky, protože si takového pracanta můžete **vychovávat**. Mění si vlastní skilly a učí se od vás. Prakticky to jde třeba přes [Microsoft 365 Copilot Cowork](https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/), který je od června 2026 v GA a pracuje napříč Outlookem, Teams, Office a SharePointem se schvalováním citlivých akcí.

Čtvrtá vrstva je ta, kvůli které tenhle článek píšu, a věnuju jí celou další kapitolu.

Zajímavý kousek skládačky je ale ve Foundry. [Agent Optimizer](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview) vezme baseline konfiguraci agenta a eval dataset a automaticky vylepší jeho instrukce, obsah skillů, popisy nástrojů i volbu modelu. A [Observability](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset) k tomu umí z produkčních traces vyrobit ten eval dataset. Dohromady je to smyčka: reálné běhy → dataset → optimalizace → lepší agent.
:::

::: card number="11" title="Autopiloti a agent jako člen týmu" default="closed"
Aby se agent mohl učit z práce, musí být její součástí. Ne nástroj, který si otevřu, ale kolega, kterému něco přijde.

Na Buildu 2026 k tomu Microsoft představil novou produktovou kategorii, a to docela explicitně: **"Today we are introducing a new category of agents called Autopilots. Autopilots are always-on agents that work autonomously, with their own identity, and act on your behalf."** ([oznámení](https://www.microsoft.com/en-us/microsoft-365/blog/2026/06/02/introducing-microsoft-scout-your-always-on-personal-agent/)). Prvním zástupcem je [Microsoft Scout](https://learn.microsoft.com/en-us/microsoft-scout/overview). Copilot sedí vedle vás a čeká, až se ozvete. Autopilot běží, i když u toho nejste. Nejsou to konkurenti, jsou to souběžné kategorie - ale ten směr je podle mě jednoznačný.

Firemně použitelné je to až se správou. [Microsoft Agent 365](https://learn.microsoft.com/en-us/microsoft-agent-365/overview) je od 1. 5. 2026 v GA jako enterprise control plane: registr agentů, lifecycle, přístupy, Purview, Defender, identita v Entra. Licencovaný "agent user" má vlastní mailbox, OneDrive, UPN a dá se zmínit v Teams.

Že to nemusí být jen Microsoft, je snad jasné - [Hermes Agent](https://github.com/NousResearch/hermes-agent) od Nous Research se popisuje jako agent, který *"creates skills from experience, improves them during use"*, [OpenClaw](https://github.com/openclaw/openclaw) používám doma. A není to buď-anebo: tyhle systémy můžou běžet v Azure, napojit se na Microsoft 365 a být spravované přes Agent 365 stejně jako Scout.

::: callout type="warning" title="Pozor na slovo self-improving"
U všech těchhle systémů dnes "self-improving" znamená zápis do paměti a úpravu lokálních instrukcí nebo skillů. **Zatím** to neznamená automatickou změnu vah modelu - ale směr, kterým jde Microsoft i ostatní, je jasný: nejen optimalizace skillů, ale i reinforcement learning environments a doladěné váhy.
:::

::: callout type="info" title="Na jindy"
Dalším krokem je koordinované kolektivní učení agentů - jeden se něco naučí a ostatní to dostanou. To je ale téma na samostatný článek.
:::
:::

::: card number="12" title="Definici dobrého výsledku musíte umět spustit" default="closed"
Tady je moje hlavní doporučení. Firma by měla systematicky budovat a formalizovat definici toho, co je dobrý výsledek. Evaluations, reward funkce, reward model, testy, akceptační kritéria, user stories - říkejte tomu jakkoli. Podstatné je, že to musí být **spustitelné**, ne jen napsané.

Nejsem v tom naštěstí sám. Kromě citované Satyovy věty o privátních evalech jako největším IP ([celý rozhovor](https://www.latent.space/p/satya-2026)) říká Mustafa Suleyman na MAI keynote něco, co tu myšlenku posouvá ještě dál: **"So with us, the RLEs and the models you build inside of them become your moat."** ([přepis](https://microsoft.ai/news/microsoft-build-2026-mai-keynote-transcript/)). Tedy že moat tvoří reinforcement learning environments a modely, které v nich vytrénujete. To je hezká gradace - evals jsou první krok, prostředí druhý, vlastní model třetí.

Mimo Microsoft to zní stejně. Greg Brockman už v prosinci 2023 napsal **"evals are surprisingly often all you need"** ([zdroj](https://x.com/gdb/status/1733553161884127435)), Garry Tan z Y Combinatoru v roce 2025 **"Evals are emerging as the real moat for AI startups"** ([zdroj](https://x.com/garrytan/status/1892952656940880036)) a Anthropic v [Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) upozorňuje, že jejich *"value compounds over the lifecycle of an agent"*.

Co dobré evals odemknou:

::: arrow-list title="Co získáte, když umíte změřit kvalitu"
- Otestujete modely různých výrobců i open source proti **své** definici kvality, ne proti cizímu benchmarku.
- Můžete dotrénovat menší specializovaný model pro konkrétní firemní roli.
- Můžete ladit skilly, kontext i nástroje proti měřitelnému výsledku místo dojmu.
- Získáte schopnost **přepnout** řešení i model, aniž byste letěli naslepo.
:::

Ta poslední položka je podle mě nejpodceňovanější a Satya na ni míří tím svým testem s modelem A a B. Prostředí se mění technologicky, politicky i strategicky a nebude to jen souboj OpenAI versus Anthropic. xAI se [2. 2. 2026 spojilo se SpaceX](https://x.ai/news/xai-joins-spacex) a vydalo [Grok 4.5](https://x.ai/news/grok-4-5). V Evropě je Mistral s open modely pod Apache 2.0. A open source je dnes fakt kvalitní - [Kimi K3](https://www.kimi.com/blog/kimi-k3) se v nezávislém [Artificial Analysis indexu](https://artificialanalysis.ai/models/kimi-k3) drží nad GPT-5.5 i nad Claude Opus 4.8, tedy nad modely, které ještě před dvěma měsíci byly extratřída světa. [GLM-5.2](https://z.ai/blog/glm-5.2) je celkově o kus níž, ale na dlouhých kódovacích úlohách se s touhle třídou měří taky. Jestli to platí i pro *vaši* úlohu, zjistíte jedině vlastními evaly.
:::

::: card number="13" title="Chci zaměstnance, ne najaté konzultanty" default="closed"
Nejde o to, jestli cloud ano nebo ne. Cloud rozhodně ano. Výnosy z rozsahu jsou v téhle hře naprosto zásadní a netýkají se jen infrastruktury - týkají se hlavně platforem, orchestrace, bezpečnostních a compliance systémů, evaluačních nástrojů a rychlosti, s jakou přibývají nové modely. Tohle si sami doma nepostavíte a nemá myslím smysl se o to pokoušet.

Jde o něco jiného: **komu se to učení připíše.**

::: tabs id="dva-modely"
::: tab id="zamestnanec" title="Zaměstnanec (chci)"
Zaměstnanec se u vás půl roku učí a ta zkušenost zůstává ve firmě. Ví, kdy se který proces obchází. Zná vaše zákazníky. A když si tuhle znalost zapíše, zapíše si ji do vašich systémů.

Tohle chci od AI. Od dodavatele beru stavební bloky - flexibilní výběr modelů, izolované prostředí, šifrovanou storage, evaluační nástroje, správu identit agentů a řízení jejich životního cyklu. Na tom si postavím svoje AI, ať už je to Scout, Copilot Cowork, Hermes, nebo vlastní řešení ve Foundry řízené přes Agent 365.

Moje evals, moje skilly, moje případně dotrénované váhy. Všechno v mém tenantu, izolovaně, šifrovaně. Když se rozhodnu přepnout model nebo odejít, beru si to s sebou.
:::

::: tab id="konzultant" title="Najatý konzultant (nechci)"
Konzultant přijde, vyřeší problém a je vidět hned. Jenže to nejcennější, co si odnáší, je zkušenost s vaším prostředím - a tu si odnáší **k sobě**. Příští čtvrtletí ji prodá někomu jinému. Ve vašem odvětví. Možná přímo vaší konkurenci.

Přeloženo do AI: předám někomu to, co je pro mě unikátní, a on mi to "přidá do modelu". Ten model ale pak použije i jinde.

Fungovalo by to skvěle - první rok. Pak by se moje unikátnost stala součástí obecné schopnosti, kterou má i konkurence. Efektivně bych zaplatil za to, aby ze mě někdo odsál důvod mojí existence. Přesně tomu Satya říká Reverse Information Paradox.
:::
:::

Satya to pojmenoval přesně takhle - firemní stopy z reálné práce mají trénovat *"not a generalist model, but... the company veteran agent"*. A z toho plyne, co po dodavateli chtít: **skutečnou hranici důvěry**, uvnitř které se vaše data, traces, evals, doladěné váhy a paměť hromadí a zlepšují dohromady. Mluví o ní jako o místě, kde se skládá lidský a token kapitál - a o [token kapitálu jsem psal samostatně](https://tomaskubica.cz/2026/agenti-token-kapital-build-2026/). Shrnul to jednou větou, kterou bych si dal na zeď:

> **"In consuming intelligence, you are creating intelligence. And what you create should belong to you."**

Ta hranice nevede mezi cloudem a onprem. Vede mezi **schopností, kterou si kupuji**, a **schopností, kterou si vychovávám**.

To první je naprosto v pořádku a budu to dělat pořád - když chci Copilota, který rozumí Excelu, nechci ho učit Excel. To druhé je pracant, kterému dáte firemní nástroje, pustíte ho k reálné práci a budete ho učit. Může to být klidně taky od Microsoftu: Copilot Cowork, Scout, nebo vlastnoručně postavené řešení ve Foundry napojené do Microsoft 365 a řízené přes Agent 365. Není to o tom, jestli si to napíšete sami. Je to o tom, jestli si necháte to, co se naučí.
:::

:::

::: group id="zavery" title="Závěry"

::: detail-grid title="Tři věci, které si z toho odnést" hint="Klikněte na kartu pro detail"
::: detail-card title="Hodnota se stěhuje k měření" summary="Prompt, kontext i specifikaci vám dnes napíše AI sama. Definici úspěchu ne."
Každá zastávka na té cestě byla chvíli tím nejdůležitějším a pak se vsákla do modelu nebo do nástrojů. Prompt engineering se rozpustil ve schopnostech modelů. Context engineering z velké části převzalo agentické chování. Specifikaci vám dneska napíše agent, když mu popíšete záměr.

Co se nevsakuje, je definice toho, co je dobrý výsledek. Ta se nedá odvodit z veřejných dat, protože je specifická pro vás.
:::

::: detail-card title="Model zná obecné věci, vaši firmu ne" summary="Call of Duty si kritik pustí vedle. Váš proces ne."
Shumerova smyčka fungovala hlavně proto, že měla zadarmo dokonalý referenční bod. Vaše firma taková není a být nemá - pokud model dokonale zná vaše postupy, jste komodita mířící k nulové marži.

Takže to, že model nezná vaši procedurální a implicitní znalost, není problém k vyřešení. Je to vaše konkurenční výhoda, kterou musíte umět převést do měřitelné podoby, aniž byste ji rozdali.
:::

::: detail-card title="Bez evalů není hill-climbing" summary="Jen náhodná procházka, která vypadá jako pokrok."
Další fáze adopce není lepší chatbot, ale digitální pracovník, který se učí z toho, jak jeho práce dopadla. Nejdřív ladění skillů a kontextu, později prostředí a doladěné modely pro konkrétní firemní role.

Obojí ale potřebuje totéž: signál, podle kterého se dá stoupat do kopce. A ten signál si musíte vyrobit sami - a nechat si ho.
:::
:::

::: arrow-list title="Co s tím prakticky"
- U každého AI use case si nejdřív napište, jak poznáte, že je výsledek dobrý. Teprve pak řešte prompt a nástroje.
- Zkontrolujte, jestli vaše smyčka měří **výsledek**, ne jen formu. Moje neměřila a stálo mě to sedmdesát dolarů.
- Sbírejte evals jako firemní aktivum, ne jako vedlejší produkt projektu. Jejich hodnota v čase roste.
- Udělejte si Satyův test: dokážete vyměnit model a stoupat dál? Jestli ne, nemáte to pod kontrolou vy.
:::

:::

::: closing
Kdo neumí změřit, co je dobrý výsledek, **nemá vlastní AI**. Má předplatné.
:::
