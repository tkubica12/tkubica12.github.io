# Tři cesty k GenUI a jejich výhody a nevýhody

META
- url: /new/2026/3-cesty-k-genui/
- date: 2026-01-27
- lang: cs-CZ
- source: source.md
- audience: tvůrci AI-first aplikací, produktoví a techničtí architekti
- thesis: obrazovka zůstane důležitá, ale univerzální naprogramované UI nebude stačit; GenUI má tři praktické cesty s různým poměrem bezpečí, interaktivity a flexibility.

STRUCTURE
- 01 Univerzální UI pro AI vs. AI-first UI.
- 02 Tři cesty vizuálního GenUI.
- 03 Shrnutí kompromisů.

KEY POINTS
- Vizuální modalita zůstane, i když porostou hlasové a jiné interakce; plně univerzální naprogramované UI autor nečeká.
- Dva směry: univerzální UI schránka pro AI (Copilot, Excel) vs. AI-first UI pro specifické komplexní aplikace.
- Tři GenUI cesty: statický artefakt, deklarativní UI specifikace, plně generovaný imperativní kód.

DETAILS

## Univerzální UI pro AI vs. AI-first UI
- UI schránka pro AI: Copilot nebo Excel; specifické aplikace žijí uvnitř univerzálního prostředí.
- Banka: poradenství/přehledy/události v chat aplikaci typu Copilot; finanční plánování a rozpočty spíš v Excelu.
- AI-first UI: aplikace tak jiné a složité, že Copilot/PowerPoint/Word nestačí.
- Příklad muzikanti: broukání melodií, harmonické postupy, rytmy; AI pomáhá tvořit party, přehrávat, aranžovat.

## Statické artefakty generované ad-hoc
- Od 2023; typicky grafy/diagramy z tabulkových dat.
- Code Interpreter jako nástroj: model napíše Python s Matplotlib/Seaborn, vznikne obrázek, vytáhne se ze sandboxu a zobrazí uživateli.
- Výhody:
  - Velmi bezpečné: sandbox typicky bez internetu; k uživateli jde jen JPEG/PNG; nic se nespouští.
  - Snadné uložení v historii: blob s GUID + RBAC + odkaz v historii.
- Nevýhody:
  - Nulová interaktivita: nelze manipulovat, filtrovat, zoomovat.
  - Grafická omezení, horší přizpůsobení designu aplikace.

## Deklarativní UI specifikace generované ad-hoc
- Oddělení renderovacího kódu od popisu, co zobrazit.
- AI generuje jen v mantinelech deklarativního jazyka: komponenty + atributy; žádný imperativní JavaScript.
- Příklady:
  - Adaptive Cards: https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/design-effective-cards?tabs=design
  - A2UI: https://a2ui-composer.ag-ui.com/gallery
- Adaptive Cards = JSON; AI vygeneruje celé a Teams může zobrazovat.
- A2UI = JSONL; každý element vlastní JSON řádek; streaming a postupné vykreslování.
- Výhody:
  - Bezpečné: AI negeneruje libovolný kód.
  - Interaktivní: uživatel může typicky klikat.
  - Design kontroluje klient/rendering prostředí (např. Teams).
- Nevýhody:
  - Omezené možnosti podle sady komponent.
  - Náročnější implementace: vytvořit a udržovat komponenty a rendering.

## Plně generované interaktivní UI generováním imperativního kódu ad-hoc
- AI generuje libovolný kód a zobrazí ho v iframe; mini-aplikace na míru.
- Autor dříve psal o HTMX pro server-side rendering s AI: https://tomaskubica.cz/post/2025/genui/
- Nový standard/extenze MCP pro předávání generovaného kódu zpět do agenta: MCP-Apps https://mcpui.dev/
- MCP-Apps podporován ve VS Code Insiders: https://code.visualstudio.com/blogs/2026/01/26/mcp-apps-support
- Výhody:
  - Maximální flexibilita: AI může vytvořit cokoli v daném jazyce/frameworku.
  - Plná interaktivita: uživatel pracuje s mini-aplikací.
- Nevýhody:
  - Bezpečnostní rizika: generovaný kód vyžaduje sandboxing a opatření.
  - Design může být nekonzistentní bez dostatečných instrukcí.

WARNINGS
- U imperativního generovaného UI je zásadní sandboxing.
- Deklarativní cesta vyžaduje údržbu komponent a renderingu.
- Statický artefakt je bezpečný, ale bez interaktivity.

VERDICT
- Statické artefakty: bezpečné a snadno uložené, ale bez interaktivity.
- Deklarativní specifikace: bezpečnější a interaktivní, ale omezené sadou komponent.
- Imperativní kód: maximální flexibilita a mini-aplikace, ale bezpečnostní/design rizika.
- Závěrečná otázka: mají aplikace #GenUI schopnosti a kterou cestu využijí?
