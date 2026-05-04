---
layout: post
published: true
title: Jak ušetřit na tokenech v kódovacích agentech typu GitHub Copilot
tags:
- AI
- GitHub
---
V dnešní době, kdy kódovací agenti postupně přecházejí z divných metod licencování nebo z vágních rate limitů na platbu za skutečně spotřebované tokeny, například s GitHub Copilot (ale podobně i s Cursor nebo Claude Enterprise), dává smysl podívat se na pár technik, jak s tokeny šetřit.

U GitHub Copilot dostáváte od 1. 6. 2026 v ceně subskripce identický budget na tokeny (takže například s GitHub Copilot Business máte za 19 USD nabito na 19 USD v enterprise poolu, první tři měsíce dokonce promo kredity navíc) a jak jejich utrácení tak dokupy jsou na základě ceníků, které přímo odpovídají cenám za API. Aktuální ceny jsou [tady](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing). Podrobné testy úspor v modelových příkladech mám na svém [GitHubu](https://github.com/tkubica12/gh-copilot-demo/blob/main/tools/copilot-token-lab/suite-example-analysis.md)

# Výběr modelu
Nějaké kombinování subagentů na slabších modelech apod. ještě rozebereme dál, ale začněme jen samotným výběrem modelu versus jeho cena. Nebudu teď řešit jestli je lepší nejnovější GPT 5.5 nebo Opus 4.7, protože za mě jsou oba skvělé a osobně teď preferuji 5.5 na všechno kromě frontendů, ale to si rozhodněte každý za sebe. První důležitá věc - koukejte do telemetrie nebo si průběžně vypisujte spotřebu (`/usage`) a asi jako já zjistíte, že při agentickém kódování budete mít obrovské množství cache input, dost input a relativně málo output (samotné výstupy modelu a reasoning tokeny). Tady příklad pár odhadů:
- "One-shot" session bez nějaké diskuse, například nasazení do cloudu (automatické spouštění a úprava skriptů dokud se to nepovede nasadit) -> 85% input, 0% cached, 15% output
- Standardní dlouhá multi-turn session -> 10% input, 85% cached, 5% output
- Zapnutí extra high thinking effort -> 10% input, 60% cached, 30% output

Z toho plyne pár zajímavostí:
- GPT 4.1 šetří? Jasně, input tokeny má levnější než 5.5, výrazně levnější na output, navíc nepřemýšlí, takže negeneruje reasoning tokeny, ale podívejte se na cached input - tam GPT 4.1 stojí stejně jako dramaticky lepší 5.5. V dlouhých konverzacích s převahou cached input finanční rozdíl nebude tak velký a přitom kvalita je nesrovnatelná.
- Thinking effort se může prodražit a nemůžete dopředu odhadnout kolik reasoning tokenů se vygeneruje. Automaticky dávat velmi vysoký reasoning nemusí být ekonomická volba. Můžete začít s málem a později v konverzaci nastavení změnit pokud se začne ukazovat, že by bylo lepší se zamyslet víc.
- GPT 5.5 je dražší než Opus 4.7, ale pouze u output tokenů a těch máte obvykle relativně málo. Pokud nemáte velmi vysoké nastavení přemýšlení, tak jejich cenový rozdíl není moc poznat. Jen pozor, Anthropic modely mají navíc cache write cost, tedy poplatek za první uložení části kontextu do cache.
- Gemini 3.1 Pro je docela levný na to co dokáže, takže třeba na dokumentaci nebo research je to dobrá volba (špičková obecná inteligence, ale horší v kódování), protože za cenu menší jak Sonnet nebo GPT 5.4 nabízí to nejlepší, co Google dokáže
- Cached tokeny jsou většinou na desetině ceny. Pokud máte tendenci startovat novou session pro každou úlohu, byť jsou si podobné a potřebují podobný kontext (stejné "načtené" dokumenty, kód, skilly), obvykle se to prodraží. Lépe v konverzaci pokračovat, ale samozřejmě když se dostanete do masivních kontextů, tak i desetinová cena nemusí stát za to. Zkrátka různé kompaktování kontextu "preventivně" může spíše propláchnout cache, než vyvolat úsporu za input.

K tomu ještě jedna věc - osobně jsem zastáncem chytrého modelu co si dá na čas a nerad používám něco jiného, než GPT 5.5 nebo Opus 4.7. Pokud slabší model udělá chybu nebo řešení co není optimální, budu to muset předělat (utratit další tokeny), ale hlavně mě to bude stát další čas. Podívejte se na svou výplatní pásku a spočítejte si kolik firmu vaše hodina stojí - přílišná šetřivost v tokenech se podle mě prostě nevyplatí. Ano - nepoužívat vysoký reasoning zbytečně, pracovat efektivně s kontextem a používat techniky, které si za chvíli rozebereme, sáhnout po menším rychlém modelu když se řeší něco triviálního, to chápu. Ale kódovat s GPT 5.4 mini mi nepřijde produktivní.

# Skilly místo instrukcí v AGENTS.md
Když před časem přišla možnost mít instrukce pro agenta na úrovni repozitáře a dokonce ve standardizovaném souboru, který pak funguje s různými výrobci, [AGENTS.md](https://agents.md/), byl jsem nadšen. Tohle bylo přesně to co dokázalo zvýšit kvalitu pro celý tým pracující v repozitáři. Postupně jsem takhle přidával nejen nějakou strategii v kódování a jaké knihovny a postupy chci používat, ale i vysvětloval agentovi jak chci pracovat - například, že má do souboru ImplementationLog.md zapisovat co kdy udělal, do CommonErrors.md si poznamenávat zkušenosti když se mu něco delší dobu nedařilo a pak až na to přišel, nebo vytváření plánu před exekucí a tak podobně. Později některé věci z toho začal řešit harness samotný, v mém případě GitHub Copilot CLI, ale i tak byl AGENTS.md pro mě důležitý a obsáhlý.

Jenže když zrovna řešíte deployment Terraformem, nedává smysl mít zaplácaný kontext vysvětlováním Pythonu. AGENTS.md se načítá pokaždé a vždy celý. Při první otázce se tak protočí přes metriku input tokenů, ale v kontextu zůstává a při každé další návazné otázce v session se vám znova protočí jako cached input.

Skill funguje tak, že do kontextu se dostane jen jejich seznam s krátkým popisem a agent si přečte kompletní kontext skillu pouze když má pocit, že se mu bude hodit. 

V mém testu extrémně velký AGENTS.md versus témata nasekaná do skills tak, že pro daný dotaz byl potřeba vlastně jen jeden, se skutečně dosáhlo úspory kolem 70%. Bylo trochu víc output tokenů (hlavně kvůli nástrojům pro načítání), ale mnohem méně input tokenů.

# MCP nástroje s search tool
Některé MCP servery, třeba Azure, mají stovky funkcí a pokud máte takových MCP serverů víc snadno se dostane třeba i k tisícovce nástrojů. Jejich definice a popis je v kontextu a platíte za ně input při první interakci a cached input při každé další interakci. To může být docela dost tokenů. 

Jedna z velmi zajímavých technik je na MCP serveru implementovat jeden nástroj - search_tool. Agent tak neví jaké tooly na tom serveru jsou (například je tam informace typu, že pro ovládání Azure je možné použít tenhle server), ale má možnost říct co by chtěl, například "Potřeboval bych založit resource group a v ní storage account". Na straně MCP serveru je implementované nějaké vyhledávání (od obyčejného regex přes BM25 až po embedding a vektorové vyhledání, což je relativně levné a pro tento účel se dá volit i velmi malý embedding model běžící open source na serveru a hledání jen v paměti třeba s FAISS) a server vrátí agentovi seznam "vhodných" nástrojů pro jeho situaci.

Další varianta může být vystavení nástrojů typu get_azure_tools_ai_services, který agent zavolá v okamžiku, kdy chce v Azure vytvářet nějaké AI zdroje. Tedy místo jednotlivých nástrojů rovnou dostane model kategorie a může si říct o detaily. Pokud vím zatím tohle není přímo součástí MCP standardu, ale lze toho dosáhnout.

V mém pokusu jsem viděl snížení tokenů z 60k na 40k, tedy redukce poměrně významná.

# Explicitní doporučení zdrojů
Pokud zadáte něco poměrně širokého, bude se model snažit zjistit si toho hodně z repozitáře a bude zkoušet různé soubory. Pravděpodobně jich přečte víc, než je nutné, protože dopředu neví jak se v repo zorientovat a kde bude něco zajímavého. Pouhá změna promptu tak, že poradíte modelu jaké soubory jsou ideální pro pochopení kontextu zadání, můžete hodně input/cache tokenů ušetřit. Například:
- Přečti si README.md a dále docs/ARCHITECTURE.md, všechno najdeš tam, další Markdown soubory nepotřebuješ.
- Seznam se s datovými typy z příkladových JSON souborů, ale nenačítej je zbytečně celé - použij jq a přečti si jen první dva objekty, to ti bude stačit.
- Nová mikroslužba, na které budeš pracovat, má přímou vazbu hlavně na mikroslužby X a Y - s těmi se seznam, ostatní nejsou relevantní.

V mém testu tohle vedlo na 70% úsporu přes všechny kategorie - méně input, protože se toho méně načítá, méně cached, protože při dalších obrátkách je méně kontextu a i méně output, protože se protočí méně nástrojů tím, jak se méně souborů otvírá.

# Komprese kontextu
Tohle je ošemetné a kontroverzní, pozor na to. V GitHub Copilot můžete použít funkci `/compact` a vezme kontext a udělá z něj sumarizaci, kratší verzi. Ale to znamená, že vygenerujete poměrně dost output tokenů (a ty jsou nejdražší) a propláchnete cache, takže kontext půjde zase do input tokenů (10x dražší, než cache). Může to pomoct, pokud je redukce kontextu opravdu velká, ale dělat to preventivně po každém větším kroku podle mě ekonomicky nedává smysl.

Kdy to dává smysl? Zejména pokud chcete udělat fork nebo nějakou jinou formu přepoužití. Například v konverzaci vybudujete základ služby a teď bude vhodné na některých implementacích pracovat paralelně nebo je předat kolegům - komprese té původní session může být výborný startovací bod pro nějaký fork. Současně také můžete poučení ze session chtít zpracovat do formy dokumentu, který se stane možným kontextem pro budoucí session. Pokud je to dokumentační věc, přidal bych ke specifikacím, pokud spíše věc prováděcí a o zkušenosti, pak z toho udělejte skill. Oboje ale znamená, že vytvoříte komprimovaný kontext pro budoucí použití.

# Jeskynní muž a stručnost výstupů
Na vstupu je většina tokenů kontext ze souborů a dává určitě smysl v dokumentaci nemít rozvleklé nesmysly a jít cestou stručného a jasného popisu. To dává velký smysl, ale dá se jít ještě dál - a hlavně s ohledem na výstup, protože ten je finančně náročnější. Myšlenka je říct agentovi, aby byl ve svých výstupech velmi stručný (například aby se zdržel nějakého rozsáhlého výkladu nebo konverzačních věcí kdy žoviálně popisuje co všechno dělal), například udělal maximálně 5 bulletů a tak podobně. No a jak jít ještě dál? Pak je tu varianta caveman nebo dokonce Wenyan.

Caveman instruuje agenta, aby mluvil jako technicky zdatný jeskynní muž. Žádné úvody, opakování zadání, shrnutí a zdravice, používej běžné zkratky a symboly jako jsou > < = nebo šipky typu →, závorky a tak podobně. Musí to zůstat lidsky srozumitelné, ale velmi kondenzované. Wenyan jde ještě dál, je to ještě extrémnější komprese, která už pro běžného člověka ztrácí srozumitelnost, ale agent ji stále dobře chápe.

Příklad. Běžný text (603 tokenů):

> Ahoj, až přijdeš ze školy, prosím tě nezapomeň udělat pár věcí doma.
>
> Nejdřív si dej batoh do pokoje, ať zase nezůstane uprostřed chodby jako past na dospěláky. Potom se podívej do kuchyně, jestli je plný koš. Pokud je víko už podezřele nadzvednuté nebo z něj kouká obal od jogurtu jako bílá vlajka kapitulace, vynes ho prosím do popelnice. Nový pytel je ve skříňce pod dřezem.
>
> Pak zkontroluj želvu Boba. Podívej se, jestli je venku z domečku, nebo jestli se zase tváří jako kámen s názorem. Pokud je venku, dej mu pár listů salátu z lednice. Salát je v dolním šuplíku, ale nedávej mu ten zvadlý kraj, ten už vypadá smutně i na želvu. Stačí dva nebo tři menší listy. Kdyby spal nebo byl zalezlej, nebuď ho, Bob má svůj manažerský režim a nerad je vyrušován.
>
> Podívej se taky, jestli má vodu v mističce. Pokud je tam pilina, kousek salátu nebo něco, co vypadá jako biologický experiment, vodu vylij, mističku opláchni a dej mu čistou.
>
> Potom prosím zavři dveře na balkon, pokud jsou otevřené. Ne proto, že by Bob uměl utéct po schodech, ale protože kočka od sousedů si o sobě myslí, že je inspektor domácnosti, a nemusí nám chodit kontrolovat koberec.
>
> Jestli máš hlad, v lednici je polévka. Ohřej si ji v mikrovlnce, ale dej na ni poklop, protože minule to vypadalo, jako kdyby čočková sopka vybuchla v keramické komoře. Talíř potom dej do myčky, ne vedle myčky, ne na myčku, ne do geografické blízkosti myčky — opravdu dovnitř.
>
> Nakonec se podívej na úkoly. Když žádné nemáš, napiš mi jen krátkou zprávu „hotovo“. Když nějaké máš, udělej nejdřív ty, které nejsou kreativně odložitelné na zítřek. A prosím, než zapneš počítač, udělej aspoň tyhle domácí věci, protože počítač má schopnost vytvářet časovou černou díru.
>
> Díky!

Caveman (394 tokenů):

> Přijdeš ze školy → udělej domácí mise.
>
> 1. Batoh
> - Dej do pokoje.
> - Ne chodba.
> - Chodba + batoh = past na rodiče.
>
> 2. Koš
> - Kouknout kuchyně.
> - Koš plný? Víko zvedá? Obaly lezou ven?
> - Ano → vynést.
> - Nový pytel = skříňka pod dřezem.
>
> 3. Želva Bob
> - Kouknout, jestli Bob venku z domečku.
> - Bob venku → dát salát.
> - Salát = lednice, dolní šuplík.
> - Dát 2–3 malé listy.
> - Nedávat hnusný zvadlý kraj.
> - Bob zalezlej/spí → nebudit.
> - Bob = kámen s plánem.
>
> 4. Voda
> - Miska čistá?
> - Bordel ve vodě? Pilina? Salát? Divná věc?
> - Ano → vylít, opláchnout, dát čistou vodu.
>
> 5. Balkon
> - Dveře otevřené?
> - Zavřít.
> - Sousedovic kočka nesmí dělat audit bytu.
>
> 6. Jídlo
> - Hlad? Polévka v lednici.
> - Ohřát v mikrovlnce.
> - Použít poklop.
> - Bez poklopu = čočkový vulkán.
> - Talíř potom do myčky.
> - Ne vedle. Ne na. Do.
>
> 7. Úkoly
> - Kouknout na školu.
> - Úkoly jsou? Udělat.
> - Žádné? Napsat „hotovo“.
> - Počítač až po misích.
> - Počítač = časová černá díra.
>
> Konec.

Wenyan (228 tokenů)

> Po škole:
>
> batoh → pokoj
> ne chodba = rodič past
>
> koš?
> plný / víko↑ / obaly ven ⇒ vynést
> pytel nový: pod dřezem
>
> Bob check:
> venku ⇒ salát 2–3 listy
> salát: lednice/dolní šuplík
> zvadlý kus ✗
> Bob spí/zalezlý ⇒ nerušit
>
> voda:
> miska špinavá ⇒ vylít → oplach → čistá voda
> pilina/salát/divno ve vodě = reset
>
> balkon:
> otevřeno ⇒ zavřít
> kočka soused audit ✗
>
> hlad:
> polévka lednice
> mikro + poklop
> bez poklopu ⇒ čočková exploze
> talíř ⇒ myčka dovnitř
> vedle/na myčku ✗
>
> škola:
> úkoly? ⇒ udělat
> bez úkolů ⇒ SMS „hotovo“
>
> PC:
> až po misích
> PC = čas díra

Úspora jak vidno poměrně viditelná. Za mě pro handoff mezi agenty (já jim to číst nebudu) může být na Wenyan. Co výstupy v chatu? Caveman nepoužívám - rád si nechám věci dobře vysvětlit, abych chápal co se dělo a jasně, můžu si o to přece kdykoli říct, jenže to je nový turn a tím pádem celý kontext protočený z cache. Poměr cache a output je 1:60 - takže pokud mám aktuálně 60k kontextu tak říct si o vysvětlení v délce 1k vyjde stejně, jako si ho nechat napsat rovnou. Ve finále tak spíše preferuji výstupy, které mi vysvětlují a odhalují proč, ale nepotřebuji tam sumář zadání ani dlouhé romány o procesu jak se k tomu dostal, nicméně výsledek s detailnějším popisem co konkrétně udělal, jak to funguje a proč, to mi vyhovuje. Na druhou stranu - pokud je to coding agent v cloudu a jeho povídání mě nezajímá, budu si číst až Pull Request, tak ať jede Cavemana celou dobu.

# Multiagent aneb opatrně s tím
Častý nápad je, že nechme hlavního agenta na lepším modelu a ten ať si pro jednotlivé dílčí úlohy vyvolá subagenta na levnějším modelu - předá mu ohraničený kontext a užije si levnějších tokenů. Bohužel v tomhle je situace výrazně složitější a v praxi to může situaci prodražit a výkon zhoršit. Proč?

Nezapomínejme na několik bodů, které ovlivňují náklady:
- Pokud je pointou subagenta, že pracuje s ohraničeným kontextem na ohraničené úloze, kde ten kontext vezme?
  - Můžeme to udělat tak, že hlavní chytrý agent popíše problém, udělá pro subagenta dobře koncipované a detailní "Issue". Dobrý nápad, ale tohle jsou přece drahé output tokeny hlavního agenta. Vyplatí se to?
  - Proto bude výhodnější, když hlavní agent bude hodně stručný a dá seznam doporučené četby - co si má subagent načíst do kontextu sám ze souborů. To je určitě lepší a ušetříme na drahých output tokenech, ale pak subagent nemá hezky připravený komprimovaný kontext, spoustu si musí dočíst sám. Jasně, jeho input tokeny jsou relativně levné. Ale input GPT 5.4 mini je stále dražší, než cached GPT 5.5 takže načtení kontextu znova je levnější pouze pokud je ho méně než kontextu hlavního modelu. Navíc je to malý hloupější model, zvládne se v kontextu zorientovat sám nebo jeho výsledky nebudou kvalitní?
  - Tohle je opravdu dilema - perfektně připravený komprimovaný kontext, který dává malému agentovi dobrou šanci uspět ale stojí nejdražší output tokeny vs. necháme malého agenta kontext vybudovat samotného a riskovat, že spotřebuje hodně input tokenů a stejně to nepochopí?
- Duplikování kontextu vede na duplikátní náklady. Představme si (ať se to dobře počítá tak řády přeženeme), že máme 100k kontextu už načtené (analýza problému a tak) a pět úloh, které náš dobrý agent vyřeší na 5k output tokenů. Těch pět úloh může být jediný turn, takže 100k cached a k tomu 5k output, to je 0,05 USD + 0,15 USD s GPT 5.5, tedy 0,2 USD. Pokud uděláme 5 subagentů a každý potřebuje načíst 50k kontextu (beru to tak, že třeba nepotřebuje úplně všechno) a vyprodukuje výstup za 1k output, kolik to vyjde s GPT 5.4-mini? 5x (0,0375 USD + 0,0045 USD), tedy asi 0.21 USD. V takovém případě jsem neušetřil a dost možná jsem snížil kvalitu. A tady vidíme - záleží na množství kontextu potřebného pro dobrou kvalitu, možná hodně ušetřím, možná vůbec, je to riziko.
- Co mi dává u subagenta velký smysl je side-quest nebo fork - smyslem není nutně ušetřit na tokenech subagenta, ale zmenšit input kontext hlavního agenta. Pokud side-quest znamená načíst si hromadu kontextu, který ale není potřeba pro pozdější část konverzace, tak to že se v kontextu usadí není výhodné (input a následné cached). Tohle například používám s příkazem `/ask`, což de facto fork aktuální session (= udrží se cache) jejíž průběh se ale nepřidává do kontextu aktuální session - tímhle se rád doptávám na věci k implementaci, když nejde o to, že chci něco měnit, ale spíše pochopit co se dělo.
- Pozor na paralelizaci ve stylu `/fleet`, která dává Copilotu incentivu paralelizovat a používat subagenty. To v kontextu této kapitoly sice chceme, ale bývá dobré mu i říct (slovně) na co jak velký model použít. Například dává smysl mu říct, že na backendy použijeme GPT 5.5, na frontend Opus 4.7 a na dokumentaci, unit testy, nasazovací skripty a tak podobně ať použije malý model, například GPT 5.4 mini. Pokročilejší variantou je použít custom agents a referencovat ty (tzn. dopředu připravené "role") - výhodou je, že u subagenta musí zadání připravit hlavní agent (= output tokeny), zatímco u custom agenta máte custom system prompt, ve kterém mohou být větší detaily chování agenta (například pravidla pro psaní dokumentace), čímž možná pro roli zajistíte větší kvalitu, ale tím, že je system prompt statický, platíte za něj jen input tokeny, ne výstup drahého modelu.

Je to tedy ošemetné a moje strategie je spíše:
- Subagent na jasnou a omezenou úlohu ve formě custom agenta mi dává smysl - věci, co se řešily loni, tedy dokumentace, unit test apod.
- Pro složitější věci stejně modelům typu Haiku nebo GPT mini nevěřím, ale střední model typu 5.3 CODEX nebo Sonnet proč ne.
- Přemýšlím, jestli nechat paralelní zpracování řídit dynamicky nebo použít agenta pro zpracování kontextu a zadání - vytvoření Issues pořádně a ty pak přiřadit cloudovému agentovi. Přijde mi to trackovatelnější, přehlednější.
- Často zjišťuji, že se mi do toho rizika nechce - vím, že nejlepší model v jedné konverzaci odvede vynikající práci, spolehlivě a také poměrně rychle (o rychlost mi vlastně nejde - stejně mám jiná okna, kde se řeší jiné úlohy nebo projekty, takže o zábavu mám postaráno jinde). Jasně, můžu ušetřit, ale alespoň zatím mi přijde, že tím zvyšuju riziko. Není pro mě nic horšího, než ušetřit dolar na tokenech a ztratit hodinu opravami.

# Co tedy reálně používám a co ne?
- Pokud vím co bude agent potřebovat načíst, rád mu to explicitně řeknu a snažím se udržovat v repozitáři dobrý kontext. Dokumentaci, která je stručná (ne úplně Caveman, ale snažím se limitovat rozvleklé texty, které AI obvykle generuje).
- Když dělám menší kroky vhodné pro subagenty, tak se buď spolehnu na harness (GitHub Copilot CLI), že to správně a optimálně zvolí a nebo si nechám připravit zadání pro tyto úlohy do textu nebo Issue a to použiji jako kontext a zadání (pro lokálního nebo cloudového agenta).
- Občas použiji nějakou formu forku, typicky třeba `/ask` pro diskusi bez vtlačení odpovědí do stávajícího kontextu.
- Rád nechám agenta pracovat na skillu nebo AGENTS.md - věci typu `Zamysli se nad celou touto session. Je něco co můžeme přidat do AGENTS.md, nějakého existujícího nebo nového skillu, aby nám to příště šlo rychleji, spolehlivěji a s menším množstvím kontextu a obrátek?`
- Když se mi zdá, že "je to na malý model", použiji režim `Auto` - možná se pletu a automatika mě zachrání od nepěkného výsledku a pokud se nepletu, rád si užiji 10% slevu, která z toho plyne.
- Jsou k dispozici i modely s nižší latencí za násobně vyšší cenu (fast mode) - nepoužívám, paralelizuji se, okno vedle a to další vedle má taky práci.
- Nepoužívám high reasoning až dokud to není nutné, většinou mi přijde, že výsledky nemusí být lepší (překomplikované).
- Pro většinu úloh pro agenta používám model `gpt-5.5` nebo `opus-4.7` s normálním reasoningem, protože nechci riskovat neoptimální výsledky, které za tu úsporu nemusí stát. 

