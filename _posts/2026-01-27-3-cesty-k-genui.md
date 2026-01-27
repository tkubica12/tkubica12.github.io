---
layout: post
title: Tři cesty k GenUI a jejich výhody a nevýhody
tags:
- AI
---
Oblast ad-hoc automaticky generovaného UI mě fascinuje a považuji ji za klíčovou pro moderní aplikace zrozené v AI světě. Nepochybně uvidíme aplikace využívající jiné než vizuální modality, například hlas (spekuluje se, že první consumer AI zařízení z rýsovacího prkna tvůrce iPhonu pracujícího v OpenAI Jony Ive bude právě chytrý repráček), nicméně obrazovka s námi nějaký čas zůstane a v nějaké formě bude součástí uživatelského rozhraní dokud nepřejdeme plně na brain-computer rozhraní typu Neuralink. Ale aby bylo UI naprogramované a univerzální v nějaké aplikaci nemyslím, že bude pravděpodobné. 

# Univerzální UI pro AI vs. AI-first UI
Očekávám dva přístupy:
- **UI schránka pro AI**: To bude například **Copilot** nebo **Excel**. Univerzální způsob interakce s AI a moje specifické aplikace budou žít uvnitř. Tak například pokud jsem banka, tak moje poradenství, přehledy, aktuální události, to budu chtít přístupné ve své "chat" aplikaci, například Copilotovi. Nicméně pokud jde o nějaké finanční plánování, rozpočty a tak podobně, chat není vhodný formát a Excel je na to výborný. Banka by tedy měla mít podporu v mém Excelu - musí být schopna mi tam natáhnout výdaje, pomoci s finančním zdravím, nabídnout konsolidaci úvěrů nebo různé optimalizace.
- **AI-first UI**: Některé aplikace budou natolik jiné a složité, že jejich odběr z univerzálního UI typu Copilot nebo PowerPoint nebude vhodný. Tak například AI-first řešení pro muzikanty, kde budete schopni broukat jednotlivé melodie, harmonické postupy, rytmy a AI vám bude pomáhat je přetvářet v party, přehrávat jak to zní a společně budete váš výtvor aranžovat. Nemyslím, že tohle je na chat nebo Word, co myslíte?

# Tři cesty k vytvoření vizuálního GenUI a jejich porovnání
Objevují se tři cesty k vytváření generovaného vizuálního uživatelského rozhraní (GenUI):
- Statické artefakty generované ad-hoc
- Deklarativní UI specifikace generované ad-hoc
- Plně generované interaktivní UI generováním imperativního kódu ad-hoc

Podívejme se na ně blíže a porovnejme jejich výhody a nevýhody.

## Statické artefakty generované ad-hoc
Tohle se rozmohlo už v roce 2023, pár měsíců po spuštění ChatGPT a později přibylo přímo do API. Používá se to typicky pro generování grafů a diagramů z nějakých tabulkových dat. Přidáte Code Interpreter jako nástroj a pokud model vidí, že jsou na vstupu tabulková data a je dobré udělat graf, napíše kód v Pythonu s využitím knihovny Matplotlib nebo Seaborn a tím vznikne obrázek s výstupem. Ten si vytáhne ze sandboxu a zobrazí uživateli.

**Výhody:**
- Velmi bezpečné - sandbox typicky nemůže na internet (takže data nemůžou odejít pryč) a k uživateli se dostává pouze JPEG/PNG obrázek, nic se nikde nespouští
- Snadno lze uložit v historii a vyvolat zpět, stačí soubor držet v nějakém blobu s GUID a RBAC pro uživatele a do historie k němu dát odkaz

**Nevýhody:**
- Nulová interaktivita - s grafem nelze nijak manipulovat, filtrovat, zoomovat
- Grafická omezení a horší přizpůsobitelnost hlavnímu designu aplikace 

## Deklarativní UI specifikace generované ad-hoc
Druhá varianta spočívá v rozdělení kódu pro zobrazení od toho, jak říct, co se má zobrazit. Myšlenka je, že vytvoříte deklarativní jazyk - seznam možných komponent a nějaké jejich atributy, například tlačítko, obrázek, seznam a tak podobně a AI bude mít možnost generovat pouze v mantinelech toho deklarativního jazyka. Nedělá žádný imperativní kód typu JavaScript, pouze vybírá z nějakého pole možností, co tam chce a jak to chce poskládat. Typickým příkladem jsou [Adaptive Cards](https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/design-effective-cards?tabs=design) od Microsoftu pro Teams, které jsou odladěné a používané už před příchodem AI. Další zajímavou možností je [A2UI](https://a2ui-composer.ag-ui.com/gallery) primárně od Google, které jsou více zaměřené na web a Android a tím, že jsou novější, mají i některé optimalizace pro GenUI (například to, že Adaptive Cards jsou JSON, takže AI vygeneruje celé a může začít Teams zobrazovat, zatímco A2UI jsou JSONL, kdy každý element je vlastní JSON řádek, a lze tak použít streaming a postupné vykreslování).

**Výhody:**
- Bezpečné - AI nemůže generovat libovolný kód, pouze předem dané komponenty
- Interaktivní - uživatel má typicky možnost na některé věci klikat
- Design má pod kontrolou klient - rendering je na klientovi, například Teams, takže grafické provedení je plně v jeho moci

**Nevýhody:**
- Omezené možnosti - pokud AI potřebuje něco, co není v sadě komponent, nemůže to udělat
- Náročnější na implementaci - je potřeba vytvořit a udržovat sadu komponent a jejich rendering

## Plně generované interaktivní UI generováním imperativního kódu ad-hoc
Co dát AI volnou ruku generovat si jakýkoli kód a ten uživateli v iframe zobrazit? Tato maximální flexibilita umožňuje vytvářet doslova mini-aplikace na míru, ad-hoc a je to velmi dobrá varianta. Už jsem si s tím hrál, v květnu jsem tady [psal](https://tomaskubica.cz/post/2025/genui/) o využití HTMX standardu pro server-side rendering s AI. Tím, jak se možnosti AI v kódování stále zlepšují, to dnes lze posunout ještě mnohem dál. Novinkou je, že se objevil nový standard (extenze MCP), jak předávat vygenerovaný kód zpět do agenta - [MCP-Apps](https://mcpui.dev/). Novinkou je, že MCP-Apps je ode dneška podporován ve [VS Code Insiders](https://code.visualstudio.com/blogs/2026/01/26/mcp-apps-support).

**Výhody:**
- Maximální flexibilita - AI může vytvořit cokoliv, co je možné v daném jazyce a frameworku
- Plná interaktivita - uživatel může s UI plně interagovat, jde doslova o mini-aplikace

**Nevýhody:**
- Bezpečnostní rizika - spouštění generovaného kódu může představovat bezpečnostní hrozby, je potřeba mít sandboxing a další opatření
- Design může být nekonzistentní - pokud AI nemá dostatečné pokyny, může generovat UI, které neodpovídá celkovému designu aplikace


Tak co, už mají vaše aplikace #GenUI schopnosti? Kterou z cest plánujete využít? 