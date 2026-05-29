# AI kódování - kontext vs. měření, software jako paměť, váš software se učit nebudu, OpenClaw a chytrá domácnost

META
- url: /2026/ai-code-context-feedback/
- source: interactive\source\2026\ai-code-context-feedback.article.md
- date: 2026-03-30
- thesis: software/skill/CLI jsou paměť a optimalizace agenta; low-level API je dostatečné připojení ke světu; měření a zpětná vazba rozhodují tam, kde jde smyčku uzavřít; uživatel se nemá učit software, software/agent se má učit uživatele.

STRUCTURE
- 01 Rámování domácího experimentu a hlavní myšlenky.
- 02 Evoluce projektu: vlastní software, agent spravuje software, GenUI.
- 03 Závěry: paměť, API, kontext vs. feedback, učení od uživatele.

KEY POINTS
- Home Assistant funguje, ale autor se nechce učit cizí UI/YAML pro každou změnu.
- GitHub Copilot CLI + 3-5 agentů paralelně pomohlo postavit mikroslužby, gateway, web, GitHub Actions, Docker Compose a nasazení na Orange Pi.
- Agent nemá být jen chatbot nad webem. Má přes low-level API, CLI a skill spravovat i vytvářet software.
- OpenClaw lokálně: používá nástroje, paměť, skilly a skripty; může upravovat sám sebe.
- `smarthomectl` vzniklo jako agent-friendly CLI nad REST/API: jednodušší než ruční JSON a escaping.
- CLI postupně absorbuje zkušenost: např. `--include`, `--exclude`, `--blinders-group` pro časté scénáře žaluzií.
- Kontext je zásadní, ale pokud lze měřit výsledek, největší průlom je zpětnovazební smyčka.
- GenUI: chat sám nestačí; obraz/mini-app výstup a voice input budou často ideální.

DETAILS
## Úvod
- Otázky: kontext vs. zpětná vazba; agent zlepšuje sám sebe feedbackem; coding agent vs. obecný agent; agentické UX vs. grafické UI.
- Smart home: Home Assistant, ZigBee, WiFi, cloud zařízení.
- Cíl: změna software má být prostě „říct“.
- Fáze 2 insight: nechci agenta, co kliká v software; chci agenta, který software spravuje a vytváří.
- Fáze 3: hledání správného UI/UX; plné GenUI a multimodální řešení zatím naráží na limity kanálů.

## Fáze 1: vlastní software místo učení cizího
- Home Assistant automatizace mocné, ale nutné znát parametry zařízení a YAML.
- Příklad: levé žaluzie na terasu; po sjetí nastavit natočení jako pravé; sledovat polohu místo hloupého časování.
- Copilot CLI měl SSH na Orange Pi Zero 2 a Zero 3 (2GB), četl staré Home Assistant konfigurace, tvořil mikroslužby, ladil přes SSH, dělal GitHub Actions, publikoval do container registry, nasazoval Docker Compose.
- Architektura: mikroslužba pro žaluzie přes lokální TaHoma API; další pro zigbee světla/vypínače, zigbee senzory, WiFi appliances; automatizační služba; gateway/BFF s autentizací; web.
- Copilot zjistil, že TaHoma Switch podporuje lokální API; předtím používán cloud přes Home Assistant.
- Výsledek: architektonicky čitelnější, snadnější experimenty, nastavení i software dostupné přes GitHub Copilot CLI.

## Fáze 2: agent spravuje software
- Web s přihlašováním nestačil pro rodinu; dává smysl WhatsApp/voice/chat ovládání.
- Složitější příkazy: zítřejší vstávání v 6:00 a žaluzie v 5:58/6:00; dřívější spaní a topení/žaluzie; zvedni žaluzie na minutu pro bylinky.
- Tyto scénáře nechci zadrátovat předem; agent má pochopit cíl a přes low-level API dodělat potřebné kroky.
- OpenClaw: lokálně běžící agent, tools, paměť, skilly, skripty, sebeúprava.
- Původní plán: agent využije MCP variantu gateway. Realita: lokálně běžící agent šel přirozeně přímo přes REST API a dělal chyby.
- Dohoda: OpenClaw si napíše `smarthomectl` CLI a okomentuje ho ve skillu.
- Low-level API propojuje digitálního agenta s fyzickým světem. CLI = svalová paměť. Skill = kontext/zručnost. Datová perzistence = paměť.
- „Software kolabuje do agentů“: základ řešení je API do světa + kód/skill + paměť/databáze.

## Fáze 3: web vs. GenUI
- WhatsApp pro OpenClaw je dobrý: bez instalace, v existujícím workflow, specializovaná skupina, hlasové diktování, bezpečně odkudkoli i se špatným signálem.
- Web je pořád rychlý pro více akcí a přehled ovládacích prvků.
- Agent je pohodlný pro přirozené příkazy typu „rozsviť lampu a linku“, ale vadí přemýšlecí doba.
- Menší modely mohou být rychlejší, ale riziko horšího výkonu při složitějších úkolech a research.
- Příkaz „jestli zítra nebude pršet, pojďme dnes večer spustit zalévání x litrů“ vyžaduje internet a rozhodnutí; čisté webové UI je kostrbaté.
- Kanály: WhatsApp Flows = vícekrokové formuláře, ne plné mini-apps; Telegram Mini Apps = schopné UI, ale E2E jen Secret Chats; Signal bez bohatého UI; Discord E2E audio/video, ne text.
- Zkusit tři cesty: Web; WhatsApp v sandboxu pro ne-admin použití; vlastní chat/voicechat web UI s mini-apps.
- Pravděpodobný ideál: voice input + mini-app GenUI obrazovka; vhodné i pro budoucí brýle s displejem.

## Závěry
### Software je paměť, optimalizace
- Chytrý agent s low-level API, daty, tools, internetem/databází a kontextem zvládne prakticky cokoli, ale první průchod stojí chyby, tokeny, čas, feedback.
- Trénink do příště: svalová paměť + zakódované/optimalizované postupy + kontext.
- Software (skript, CLI funkce, MCP server) ukládá postup/business logiku opakovatelně, předvídatelně, testovatelně, upravitelně.
- Kontext/skill/paměťový MCP říká jak na to, proč, k čemu, jak to funguje.

### API do světa, data, abstrakce jako skill
- Agent zvládne komplexitu low-level API lépe než člověk; člověk chce abstrahované objekty, LLM často naopak.
- Lepší dát low-level API a data než nutit lidské abstrakce.
- Agentovy abstrakce vzniknou jako optimalizace: skill, CLI nebo MCP funkce pro rychlejší a spolehlivější vyšší zadání.

### Kontext vs. zpětná vazba
- Pokud agent může měřit výsledek, je houževnatý a výrazně se zlepší.
- Eshop příklad: agent může brzy ladit aplikaci na maximalizaci zisku přes chování klientů, objednávky, nápady, A/B testy a měření.
- Zavedený eshop: zpětná vazba podle autora cca 80% úspěchu.
- Kde smyčku nejde plně uzavřít, protože agent neví co dělá, je kontext cca 80% úspěchu: doména, co má dělat, jak věci fungují.
- Autor chce vybudovat kontext co nejrychleji, aby pak práce byla hlavně feedback loop a agent mohl makat sám.

### Učení od uživatele a GenUI
- Agent chápe různé formulace uživatele, doptá se, zapamatuje si upřesnění.
- Agent se učí chápat uživatele; uživatel se nemá učit ovládat řešení.
- Chat interface nebude pro všechno efektivní; kombinace s obrazem je důležitá.
- Grafické UI se má automaticky přizpůsobit uživateli stejně jako textové; GenUI se musí stát standardem.

COMMANDS / CODE / TERMS
- GitHub Copilot CLI
- OpenClaw: https://github.com/openclaw/openclaw
- Home Assistant, ZigBee, TaHoma Switch lokální API, Orange Pi Zero 2, Orange Pi Zero 3 (2GB)
- `smarthomectl`, `--include`, `--exclude`, `--blinders-group`
- Gateway/BFF, MCP, REST API, Docker Compose, GitHub Actions, container registry
- WhatsApp Flows: https://developers.facebook.com/docs/whatsapp/flows/
- Telegram Mini Apps: https://core.telegram.org/bots/webapps
- Discord E2E audio/video: https://support.discord.com/hc/en-us/articles/25968222946071-End-to-End-Encryption-for-Audio-and-Video

WARNINGS / CAVEATS
- Autor výsledek GenUI zatím nemá; chce se k tomu vrátit.
- WhatsApp zatím limit: Business Platform a tlačítka/formuláře, ne plné mini-apps.
- Telegram UI schopné, ale E2E omezené na Secret Chats.
- Discord E2E pro audio/video, ne text.
- Rychlejší menší modely mohou zhloupnout při složitějších úkolech.

VERDICT
- Software a skill jsou paměť a optimalizace agenta.
- Low-level API + data + agentovy vlastní abstrakce jsou lepší než předem vnucené lidské abstrakce.
- Poměr kontext/feedback závisí na měřitelnosti: měřitelné = více feedback; nejasná doména = více kontext.
- Uživatelé se nebudou učit používat váš software. Software a agent se budou učit rozumět uživateli.
