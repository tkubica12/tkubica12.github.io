---
layout: post
published: true
title: Jak a kdy dělám vibe coding
tags:
- AI
---
Jak postupuji, když chci vytvořit aplikaci, která není ohraná a triviální (tzn. je mimo možnosti no-code platforem) a nebudu psát žádný kód? Kdy něco takového chci a kdy ne? Nasdílím pár triků s GitHub Copilot a podobnými platformami.

# Kdy používám čistý vibe coding a kdy "jen" AI asistenta
Vibe coding rozhodně nepoužívám vždy, většinou je to spíše AI coding agent ve formě kolegy, ale čisté programování bez programování u mě má své místo. V čem?
- **Ucelená miniaplikace**: Často potřebuji vyřešit nějaký konkrétní problém a získat tak utilitku nebo appku, která to bude dělat. Je to něco, k čemu se budu vracet a používat to, ale je to ucelené, nehodlám do toho moc sahat ani to integrovat do nějakého projektu. Typický příklad: skript, který vezme prompt a vygeneruje z něj X variací přes LLM a pro každou vygeneruje Y obrázků v gpt-image-1 a uloží do adresáře v nějakém názvosloví (používám, když chci obrázek do prezentace - nahodím prompty, od každého si nechám udělat 25 pokusů v různých variantách a vrátím se později a z 250 výsledků si vyberu ten nejpovedenější na každý slide). Podobných udělátek používám spoustu a vibe-coding je u nich otázka pár minut. Podobně jsou to i různé vzdělávací utilitky - lidem je servíruji "as a service" přes web, takže vnitřek je nemusí zajímat, a jakmile je dokončím, budu je jen používat a nikomu jejich střeva nepředhazovat (LLM next-token pravděpodobnostní vizualizace pro pochopení funkčnosti - ještě tady na blogu ukážu).
- **Prototypování**: Typicky jde o něco, co by ve finále mělo skončit jako dobře napsaná opakovatelná integrovatelná aplikace (tzn. v režimu spíše AI peer než vibe coding), nicméně ještě není rozhodnuto jestli vůbec do toho jdeme a tím méně jak vlastně. Příklad - potřebuji zjistit jak dostat obsah z SharePoint Pages do AI Search ve formátu, který má AI rádo (Markdown). Jak složitá stránka může být, abych nechal obsah extrahovat jednoduše předhozením aspx souboru LLM a ať to z toho vyhrabe (btw. pro jednoduché stránky to funguje) vs. potřebuji prototyp crawleru (Crawlee -> extrakce přes rendering v Playwright -> převod HTML do Markdown s Markitdown ... ale k tomu vyřešit autentizaci do SharePointu)? Tohle už nerad dělám "bez kódu", vibe coding mi umožní různé varianty sestavit, i když kód třeba nebude čistý, bezpečný a výkonný, ale jeho smyslem je získat prototypy pro rozhodnutí, pak se zahodí a udělá se pořádně. Zkrátka - no-code je na rapid prototyping běžných byznys aplikací (okno, tlačítka, formulář, databáze, report), ale ne na technické prototypy viz můj příklad.
- **Průzkum**: Velmi často potřebuji prozkoumat nějakou technologii, vyzkoušet jak funguje, jak ji začlenit do aplikace apod. Zjistil jsem, že než použít nějaký obecný tutoriál, který mi často nevyhovuje, nedělá co si od technologie představuji a je moc jednoduchý, tak je pro mě lepší vibe codingem postavit něco vlastního. Výsledek nemá žádnou ambici být udržitelný nebo produkční a na konci půjde do šuplíku a pravděpodobně se k němu už nevrátím. Smyslem celého procesu je získat znalosti a zkušenosti a přes praktické zprovoznění zcela vlastního scénáře se učí nejlépe. Příklady kdy jsem použil: Reflex (Python framework pro psaní frontendu), srovnání multi-agent AI frameworků (LangGraph, Autogen, Semantic Kernel, Crew), různé varianty jak vyřešit detekci sentimentu textu (vlastní BERT model, LR na embeddingy, LLM, fune-tunované LLM). To jsou scénáře, kdy vibe coding trvá i několik dní v kuse, nejsou to triviální věci.

V ostatních případech naopak vibe coding, tedy situaci kdy si kód ani moc nečtete a spíše řídíte high-level směr a iterativně s AI jdete kupředu, spíše nedoporučuji. Jsou to typicky věci, které jsou produkční a mají zásadní "integrační" aspekty, což trochu šířeji chápu jako:
- **Aplikační integrace**: Je to součást většího systému a i pokud je to co do byznys logiky oddělená mikroslužba, stále má vliv na okolí - její děravost může poškodit celkovou bezpečnost systému, problém s výkonem či škálováním může způsobit degradaci a kaskádovité efekty v celém systému apod.
- **Časová integrace**: Je to něco, co navazuje na minulost a bude součástí budoucnosti. Musí se tedy integrovat na historické, ale i budoucí komponenty, bude mít nějakou evoluci - změny, rozšíření, vylepšení, opravy. Pokud bude budoucí přizpůsobitelnost obtížná, protože kód není napsaný tak, aby umožňoval efektivní evoluci (modularizace, dobré vrstvy abstrakce, čitelnost, dokumentace, testy), tak to bude problém.
- **Lidská integrace**: Je to něco, kde střeva zajímají větší či menší skupinu lidí, vývojářů, něco, kde si často někdo řekne "Bude dobré podívat se, jak je tahle služba vlastně napsaná, ať to dobře chápeme". Vibe coding bude mít tendenci (byť se tomu dá bránit) nedodržovat nějaký váš firemní styl, ale hlavně - LLM jsou přes Reinforcement Learning trénované pro automatizované zvládání úloh a tak postupují velmi "robustně". To totiž typicky vedlo k dosažení výsledku, nicméně je to trochu jiná incentiva, než psát kód elegantně, čitelně a úsporně. Jinak řečeno reasoning modely typu o3, Sonnet 4 a Gemini Pro 2.5 často volí komplexnější cestu na hranici překomplikovanosti.

Pro tyto případy, kde nejedu vibe-coding, vnímám dva základní režimy:
- **AI kolega**: Používám jednak pro diskusi, rozmyšlení a přípravu architektury a dalších zásadních rozhodnutí, ale i psaní kódu a dnes už většinou v agent režimu. Nicméně snažím se o velmi krátké iterace, kdy se dostávám do smyčky a každý kód musím chápat a přijmout. Commit je moje odpovědnost, za kreténa budu já, ne AI. V tomto režimu mu do toho velmi často hrábnu (přepíšu si výsledek trochu podle sebe a vrátím mu zpět, že takhle to chci a ať mou změnu doreplikuje do zbytku) nebo ho přeruším (sleduji co dělá a zmáčknu pauzu a řeknu "Hele, ty se snažíš na to založit novou třídu, ale to bude bordel - pojďme rozšířit tuhle stávající).
- **Bug fixer**: Vnímám jako výborný use case použití autonomního režimu (například GitHub Coding Agent co reaguje na Issue a vytvoří Pull Request) pro jednoduché a dobře popsané bugy nebo drobounká vylepšení. Věci, kde vím celkem přesně co je potřeba změnit, ale je to poměrně triviální práce, která mě nebaví. Ono změnit je jedna věc, ale sjet testy, prohnat CI/CD, pročíst a opravit nálezy, ono to čas rozhodně zabere. Není to jen, že změním pár řádku u sebe v počítači a tím je hotovo. Zásadní je, že jde o něco, co má ohraničený scope (není to hledání duchařského bugu přes deset mikroslužeb) a je to dobře otestovatelné (přesně tak jsou totiž reasoning modely trénované a jsou v tom velmi dobré).

# Instrukce, dokumenty, postup na příkladu GitHub Copilot
V projektu obvykle začínám definicí základních instrukcí. To budete mít každý jiné, ale pro mě, protože většinou jde o něco v Pythonu, se hodí tohle:

```markdown
---
applyTo: '**'
---
- Use uv as package manager to manage dependencies and virtual environments in Python.
- Run app with `uv run main.py` or similar, never do .env or pip directly
- Use docstrings to document functionality. 
- Comments only for things that are not obvious, not based on comments of progress, just to explain non-obvious lines worth extra documentation.
- Do not try to guess latest versions of packages, if you need to add package, do not modify pyproject.toml directly, but use `uv add <package>` command.
- Prefer simplicity and readability
- Try to avoid too big files, split code if it makes sense
- Always read README.md file with architecture and business context to understand main goal of project
```

Tento soubor je uložený v `.github/instructions/general.instructions.md`. Kromě toho tam mám soubory specifické pro konkrétní typ souboru, například:

```markdown
---
applyTo: '**/*.tf,**/*.tfvars'
---
- Variables define external interfaces of modules and should be stable. Therefore, avoid using variables directly in resources and rather create locals for them.
- Avoid explosion of variables. Use locals when you need to make it easy to change something in the future, but it is not variable that will be changed between environments or deployments.
- Always use multi-line description of variables using `description = <<EOF ... EOF` syntax. Make sure to include description as well as examples.
- Separate resources into files based on their type such as `networking.tf`, `service_bus.tf`,  `rbac.tf`,etc. If there are a lot of resources of the same type, consider adding another level of separation such as `container_app.frontend.tf`, `container_app.backend.tf`, etc.
- We are using Azure in this project. Prefer azurerm provider for typical standard resources, but use azapi provider when dealing with new, preview or less common resources to ensure full compatibility with latest Azure features. When in doubt, ask the user.
```

Podobně třeba pro Python mám základní instrukce typu "V tomto projektu používáme FastAPI, ne Flask" nebo "V tomto projektu používá striktní typování".

Teď k postupu. Pro složité projekty používám 4 zásadní dokumenty. Celý proces začíná asistovaným vytvořením dokumentu **DesignDocument.md**, ve kterém se definuje návrh celého řešení. Chci tam základní popis byznys kontextu, hlavní funkce, architektonická rozhodnutí (jazyky, frameworky, databáze, formy deploymentu apod.), strukturu projektu (mikroslužby, moduly, integrace), klíčová API, datová schémata, popis použitých patternů (sync, async, CQRS, ...), UI a UX principy a stavební bloky a tak podobně. Než vznikne první řádek kódu, tak nad tímto dokumentem u složtějšího projektu strávím hodinu a budu se k němu vracet. Samotnou formulaci nechám dělat převážně AI, ale vstupuji do toho, zadávám požadavky, žádám o varianty, ručně měním texty a pak žádám o zatřídění, doladění, odstranění duplicit a tak podobně. Jinak řečeno - tohle je základní dokument a není to "vibe", ale pevný základ projektu. Typicky jsem tak na 500-1000 řádcích.

OK, jde se kódovat? Ještě ne. Po tomhle kroku nechám vygenerovat druhý soubor - **ImplementationPlan.md**, ve kterém jsou kapitoly, podkapitoly a checklist úkolů. Tohle se samozřejmě úplně netrefí a bude se v průběhu různě měnit, ale je důležité to mít. AI vygeneruje a já připomínkuji, ručně upravuji a ladíme to. Typicky se dostanu tak na 200 kroků/bodů, ale dobře členěných.

Dobrá, jdeme tedy kódovat? Jdeme! Nicméně session vždy začíná poměrně komplexním promptem (mám jich víc podle toho co se bude dělat, ale teď mluvíme o tom, kdy se začíná něco nového kódovat). Prompty mám uložené tak, abych se k nim dostal v GitHub Copilotu přes **/** a nemusel to pořád vypisovat, ale současně to nejsou instrukce, které se připojují vždy. Berte to jako taková "makra" (ono doslova, podporuje to i variables). V `.github/prompts/` mám například `RobustVibeCoding.md` s tímto obsahem:

```markdown
Context:
- Design document contains design decisions and architecture of the application. Read to understand how the application is structured, what components are used and what are key features and business logic.
- Implementation plan document contains tasks to be completed in order to finish the application. You will typically be assigned one or few steps at a time.
- Common errors document contains common pitfalls and errors to avoid. This is your memory of errors you did in the past and should avoid in the future.
- Implementation log document keeps track of all changes and progress made during implementation. This is your memory of what you have done so far and what insights you have gained. Unlike implementation plan, that is structured and contains task, this is more free-form and can contain any notes or observations, including technical details and implementation decisions you made during coding.

Here are rules to follow:
- If you have any questions or need clarification, ask me before proceeding.
- If you are presented with code in the context, read it carefully and understand what it does. 
- Test your changes to ensure they work as expected and do not break existing functionality.
- Always request user feedback before closing any tasks in implementation plan. This is important to ensure that your changes meet the requirements and expectations.
- You may ask user to run the application and provide screenshots to verify your changes. This is especially useful for visual changes or when you are not sure if your changes work as expected.
- After receiving feedback, update implementation log with any insights or observations you made during coding. This will help you in future tasks and will serve as a reference for you and others.
- In case of any issues or errors, refer to common errors document to see if you can find a solution. Search internet to gather more insights. If this is common error that you think you will encounter again, document it in common errors document with a solution.
```

Dám tedy **/RobustVibeCoding** a řeknu, že teď budeme implementovat sadu bodů pod kapitolou 1.4 v implementačním plánu.

Okej, mluví se tady o dvou dalších souborech, tak zkusím vysvětlit. Tyto soubory jsou poznámkový blok pro Copilot a dost se mi to osvědčilo.

Soubor **CommonErrors.md** obsahuje chyby, které Copilot udělal a musel opravovat. Snažím se v průběhu session tohle i trochu řídit, ať tam nedává úplně všechno, ale všímám si, že některé chyby skutečně dělá pořád dokola. Nejvíc jsem to viděl, když jsem použil Reflex pro defacto psaní Next.js aplikace v Pythonu. Bylo vidět, že to nemá tak načtené a často používá atributy z Reactu a Reflex (dříve se to jmenovalo Pynecone) je používá jinak. To byl schopen dělat pořád dokola. Dokumentuje tedy svoje vlastní chyby, kousek z toho souboru vypadá třeba takhle:

````markdown
**Spinner Size Error - NEW:**
```python
# ❌ WRONG - Causes TypeError
rx.spinner(size="4")  # This will fail! Spinner only accepts "1", "2", "3"

# ✅ CORRECT
rx.spinner(size="2")  # Use valid spinner size
```

**Icon Size Error - CRITICAL:**
```python
# ❌ WRONG - Causes TypeError
rx.icon("zap", size="16")  # This will fail! Icon expects integer

# ✅ CORRECT
rx.icon("zap", size=16)    # Use integer for icon size
```

**VStack/HStack Spacing Error:**
```python
# ❌ WRONG - Causes TypeError
rx.vstack(
    components...,
    spacing="1rem"  # This will fail!
)

# ✅ CORRECT
rx.vstack(
    components...,
    spacing="4"     # Use string literal
)
```

**Button Size Error:**
```python
# ❌ WRONG - Causes TypeError  
rx.button(
    "Click me",
    size="lg"       # This will fail!
)

# ✅ CORRECT
rx.button(
    "Click me", 
    size="4"        # Use string literal
)
```
````

Většinou mu dávám tenhle soubor explicitně do kontextu a pomáhá to, ale někdy udělá tu chybu i tak. Proto mám připravený další prompt na **/**, ve kterém říkám "Hele, tady máme chybu. Podívej se na CommonErrors.md, třeba ji tam najdeš. Jestli ne prohledej taky Internet #websearch a hledej dokumentaci, tutoriály, příklady a také diskuse uživatelů se stejným problémem".

Čtvrtý soubor je **ImplementationLog.md**, kde chci, aby po konci kódovací session (typicky nějaká sada bodů implementačního plánu, po které po otestování a potvrzení funkčnosti následuje odškrtnutí bodů v implementačním plánu a commit) zapsal, co se dělalo, čeho se dosáhlo a jaká technická rozhodnutí udělal. Přijde mi to důležité pro udržení kontextu mezi jednotlivými kódovacími sezeními. Přibaluji do kontextu, ale někdy si i explicitně řeknu a detailnější prozkoumání promptem typu "Myslím, že barevné schéma jsme už řešili u jiného bodu a bylo by dobré to udělat konzistentně. Podívej so do implementačního logu, k čemu jsme došli a následně prostuduj už hotový kód a použij to jako základ pro další práci".

Tady je příklad obsahu:

```markdown
### 2025-07-01

**Phase 4.1 Complete!** ✅
Interactive token generation mode successfully implemented with critical temperature handling fixes:

**Core Interactive Mode Features:**
- ✅ **Unlimited Token Generation**: Removed max tokens limit - users can generate indefinitely
- ✅ **One-Token-At-A-Time**: Each API call requests exactly 1 token for educational clarity
- ✅ **Real-time Token Selection**: Immediate generation of next alternatives after token selection
- ✅ **Temperature Control**: User-configurable temperature slider (0.0 - 2.0 range)
- ✅ **Probability Visualization**: Interactive probability bars with color coding
- ✅ **Undo/Reset Functionality**: Full session management with backtracking capability

**CRITICAL Temperature Handling - IMPORTANT:**
- ✅ **Temperature 0.0 Handling**: Frontend converts 0.0 to 0.001 to prevent NaN errors
- ✅ **Backend Safety**: LLM service also enforces minimum temperature of 0.001
- ✅ **Numerical Stability**: Prevents "Out of range float values are not JSON compliant: nan" errors
- ✅ **Deterministic Behavior**: 0.001 is small enough to maintain deterministic token selection
- ✅ **Consistent Implementation**: Both frontend and backend use same minimum value
```

Občas se stane, že se práce nedaří - nefunguje to a neposouvá se to. Obvykle řeším jedním z těchto způsobů:
- **Změna modelu**: Rád používám o3 na přípravu architektury a plánování a Sonnet 4 pro samotné kódování, ale občas v alteraci s Gemini Pro 2.5. Přestože mi aktuálně Sonnet vyhovuje víc, má tendenci dělat věci komplikovaně, Gemini tolik ne. Když se situace nevyvíjí dobře, pošlu Sonnet na střídačku. Dobré je, že v GitHub Copilot jednoduše změníte model a pokračujete ve stejné session, takže se to dá použít třeba i na závěr pro získání jiného názoru. Za mě skutečně mohu říct, že různé modely vedou na jiný styl kódu a jejich občasné prostřídání pomáhá. Nicméně moje kombinace je - o3 navrhuje a přemýšlí, Sonnet 4 dře, Gemini je druhý názor a občas zaskočí, když je potřeba vystřídat brankáře, protože dostal 3 góly v řadě a sesypal se z toho.
- **Návrat zpět**: Tlačítko Undo používám samozřejmě velmi často a je to pro mě ohraničení nějakého malého kroku. Nekliknu na Keep pokud aplikace alespoň nenaběhne, takže když se opravy nedaří, dám Undo a zkusíme to znovu trochu jinak. Nicméně o dost zásadnější je pro mě správně dělat Commit. Ten ohraničuje celý proces plnění bodů implementačního plánu a jsou situace, kdy i přes "Keep" a postupné zavádění začíná model řešit, že je v háji a že to zkusí jinak a ještě jinak a v ten moment je lepší session ukončit, vrátit se k poslednímu Commitu a začít znovu. Vzkaz z budoucnosti mu předáte, například "Zdá se, že dělat to přes CCS je moc komplikované, zkusme to jinak".

Samozřejmě v průběhu vibe kódování může dojít na nečekané záseky v architektuře a je potřeba redesign a s tím změna implementačního plánu i pročištění implementačního logu. Pár takových zvratů se může objevit, ale Copilot s tím pomůže. Je dobré mít i připravený "explorativní" prompt na **/**, kde vysvětlíte, že nechcete sahat na kód, ale načíst si všechno a debatovat o možnostech v rámci designu řešení.


**Tolik k nasdílení mého postupu na vibe coding a kdy ho používám. Pro scénáře, které jsem zmínil na začátku, je to neuvěřitelně efektivní a fascinující způsob jak výrazně zrychlit učení, průzkum a prototypování. Věci, které byste v minulosti prostě udělat nemohli a spokojili byste se s povrchnějším načtením dokumentace nebo projetím ohraného tutoriálu, dnes zvládnete "prožít". Vibe coding je myslím úžasný. Udělá z vás lepšího vývojáře, ale trochu jinak, než si lidé často mylně vysvětlují. Není to tím, že to za vás vymyslí a napíše, ale tím, že sníží bariéru vstupu a umožní vám se vymáchat v tématu daleko nad rámec "hello world". Ale na produkci jste vy ten, kdo ví, AI jen dře, jinak se vraťte o lekci zpět.**