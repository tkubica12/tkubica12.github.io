---
format_version: 1
title: "AI kódování - kontext vs. měření, software jako paměť, váš software se učit nebudu, OpenClaw a chytrá domácnost"
eyebrow: "Domácí experiment s AI agenty"
subtitle: "Domácí projekt s Home Assistantem, Copilot CLI a OpenClaw jako praktická laboratoř pro přemýšlení o kontextu, zpětné vazbě, software jako paměti a GenUI."
slug: ai-code-context-feedback
date: 2026-03-30
language: cs-CZ
status: experimental
canonical_url: "/2026/ai-code-context-feedback/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

# AI kódování - kontext vs. měření, software jako paměť, váš software se učit nebudu, OpenClaw a chytrá domácnost

Pustil jsem se do domácího experimentu, který ultimátně vede na to, že v jeho jádru je AI agent. Cestou jsem zaznamenal, že si neustále promýšlím následující koncepty a že taková zkušenost je opravdu důležitá:
- Co je důležitější - kontext nebo zpětná vazba?
- Jak už dnes reálně agent zlepšuje sám sebe zapracováním mého feedbacku?
- Dává smysl agent na kódování nebo je to prostě agent?
- V čem je agentické UX lepší než grafické UI a nahrazuje ho?

Jde o to, že chytrou domácnost mám řízenou přes Home Assistant, který je připojen na ZigBee komponenty, některé jsou ale WiFi a některé jsou velká zařízení dostupná jen přes cloud a to všechno se tam ovládá a automatizuje. Cílem bylo zkusit nahradit hotový software, v kterém se stále musím učit věci dělat, řešením na míru s využitím AI kódování a tím pádem při požadavku na změny software je prostě "říct". Jenže pak přišla druhá fáze - automatizace i web je fajn, bylo by dobré tam přidat agentický interface (například "zavři všechny žaluzie kromě pracovny"). Jenže v této fázi mi došlo, že o tom přemýšlím opačně - nechci přece agenta co umí "klikat" v software (to se dělalo před rokem), ale agenta, který mimo jiné spravuje a vytváří software. Teď se nacházím ve fázi 3 a zkoumám, jak má vypadat to správné UI/UX - jednoznačně chci plné GenUI a multimodální řešení, ale zatím narážím na limity použitých kanálů (např. WhatsApp leda přes Business Platform a to stejně jsou jen tlačítka, ne plné mini-apps).

Než se vrhnu do většího detailu, tak aby to vaši agenti nemuseli číst celé, tak tady jsou hlavní myšlenky:

::: summary-grid
- **Software a skill jsou paměť**: Je to energetická a výkonnostní optimalizace vedoucí k lepší šanci na přežití v budoucnu. Svalová paměť a umění číst hru vzniklé tréninkem.
- **Low-level API připojuje agenta do reálného světa**: Není potřeba aby bylo komplexní a mělo abstrakce. Ty si agent implementuje sám jako CLI/skill případně je nabízí dále kolegům přes A2A.
- **Kontext vs. zpětná vazba**: Kontext je zásadní, ale hlavní průlom vzniká s uzavřením zpětnovazební smyčky, která ve finále vede i k vytváření kontextu. Pokud lze něco dobře změřit, je lepší investovat 80% snahy do měření a jen 20% na kontext (zejména v podobě konstituce a konceptů). Pokud se něco špatně posuzuje, je potřeba investovat 80% snahy do kontextu.
- **Uživatelé se nebudou učit používat váš software**: Tohle musí být naopak.
:::

::: group id="evoluce" title="Evoluce mého domácího projektu"

Zkusím popsat jak jsem postupoval a vřele doporučuji si něco takového vyzkoušet - je to zábavné.

::: sequence title="Tři fáze domácího experimentu"
1. **Vlastní software** — nahradit části Home Assistantu řešením na míru, které umím měnit přes AI kódování.
2. **Agent spravuje software** — nepřidávat jen chat nad web, ale dát agentovi low-level API, CLI, skill a možnost zlepšovat vlastní schopnosti.
3. **GenUI místo pevného webu** — zkoumat, kdy stačí chat, kdy je potřeba obraz a kdy se UI má přizpůsobit uživateli.
:::

::: card number="01" title="Fáze 1 - Proč se mám učit cizí software, když mít vlastní je jednodušší?" default="open"
Home Assistant je výborný kousek software, ale rozchodit v něm věci tak, jak přesně chci, jsem vlastně nikdy nedokázal. Například automatizace jsou tam mocné, ale je potřeba je znát a pochopit všechny parametry, co zařízení používají, a naučit se správně jejich YAML jazyk, a stejně to není ono. Například - když jdu na terasu, potřebuji zvednout levé žaluzie no a když je pak dám tlačítkem zpět, tak sjedou v poloze lamel v plném zastínění. Potřeboval jsem dvě věci - jednak ať se po sjetí dolů nastaví natočení tak jako u té pravé a také možná nesjíždí úplně shora, takže místo hloupého časování po vteřinách (příkaz na natočení lamel se nesmí dát, když sjíždějí, protože jinak se zastaví) sledovat, v jaké poloze jsou, a když dojedou dolů, tak je hned sklopit. V YAMLu jsem řešení nenašel a přitom je zřejmé, že to není složitý algoritmus a že vibe-coding pro něco takového nemůže být problém.

Vzal jsem tedy GitHub Copilot CLI a rozjel projekt, kde simultánně jelo vždy 3-5 agentů současně a já pár dní skákal mezi okny (tentokrát těmi v počítači) a řídil je. Popsal jsem architekturu, kdy mám jednotlivé mikroslužby pro různé typy zařízení (jednu pro žaluzie, která využívá lokální API krabičky TaHoma, jinou pro vypínače a světla na zigbee, jinou na senzory na zigbee, další pro appliance na WiFi typu pračka, sušička nebo spotřebiče v kuchyni), dále automatizační službu, gateway (de facto backend-for-frontend s přidanou autentizací) a web. Copilot běžel na mém počítači a dostal SSH přístup do původního minipočítače (Orange Pi Zero 2) a také do nového (Orange Pi Zero 3 - 2GB paměti) - koukal se do původního, aby vykradl konfigurace a názvy zařízení z Home Assistant souborů, vytvářel mikroslužby, ladil je v krátké smyčce přes SSH, udělal workflow v GitHub Actions s publikováním do container registry, rozjížděl finální verze v Docker Compose na zařízení a tak podobně. Dokázal například zjistit, že TaHoma Switch podporuje i lokální API, což jsem nevěděl. V Home Assistantu jsem využíval integraci na jejich cloud, tady se zjistilo, že žaluzie můžu ovládat lokálně. Copilot si scanoval síť, hledal a rozpoznával zařízení, koukal do dokumentace a celkově byl vývoj velká zábava.

Výsledné řešení je pro mě architektonicky čitelnější, dosáhl jsem co jsem potřeboval - v některých oblastech je to lepší, někde možná ještě ne, ale to hlavní je něco jiného. Nejsem na to sám. Popisuji co chci a jak, můžu experimentovat, nemusím studovat nějaké návody a trápit se tím. A hlavně - většinu toho co jsem v Home Assistant nastavil, jsem pak zapomněl a musel se zpětně dívat jak to vlastně funguje, když jsem přidal něco nového nebo potřeboval změnu. Tenhle software i veškeré jeho nastavení je dostupný přes GitHub Copilot CLI - tohle bych určitě nechtěl jinak. Nebo nakonec jo?
:::

::: card number="02" title="Fáze 2 - Proč jen přidat agenta do software, když to může být obráceně?" default="open"
V tuto chvíli jsem měl web s přihlašováním a panovala spokojenost, ale ne každý v rodině byl ochoten se na web připojovat. Bylo jasné, že nějaký agentický interface by dával smysl - aby se to dalo říct přes WhatsApp nebo něco takového, zkrátka klasické ovládání domácnosti ala Google Home, ale s moderním LLM co fakt chápe co se řeší a bez proprietárního řešení. Dává smysl nebo ne? Přidáme do toho software agenta, vlastně spíš takového chatbota a/nebo voicebota.

Jenže tady mi začalo rychle docházet, že budeme mít meta-problém. Já asi nechci mít jen klasické vytažení intentu a zapnutí světla, ale chtěl bych řešit složitější věci, například:
- Ráno tentokrát musím zítra vstát v 6:00, tak otevři žaluzie v ložnici v 5:58 jen tak trochu a v 6:00 naplno
- Dnes půjdeme spát dřív, přestaň topit už v 19:00 a ve 21:00 sklop všechny žaluzie
- Jdu pro bylinky, zvedni na minutu žaluzie

Na tohle všechno by to muselo být připravené - musel bych mít promyšlené tyto příklady použití a specifické mechanismy zadrátovat. Agentický přístup je ale o tom, že AI pochopí co chci a najde cestu jak to realizovat. Agent se nebude nutně omezovat aktuálním stavem software co do UI nebo automatizační části, ale přes low-level API dokáže dodělat cokoli bude potřeba. Nechci tedy chatovadlo nad webem, ale opravdu agenta.

V ten okamžik začalo být jasné co chci na zařízení dostat - **[OpenClaw](https://github.com/openclaw/openclaw)**. Je to v mém setupu lokálně běžící agent, který umí používat nástroje, držet si paměť a průběžně si rozšiřovat vlastní schopnosti pomocí skillů a skriptů. Díky němu jsou takové úlohy dobře splnitelné a hlavně OpenClaw dokáže upravovat sám sebe. Tak například - v mé architektuře jsou mikroslužby s vlastním API a gateway (BFF), která je sdružuje a přidává třeba bezpečnost nebo MCP variantu. Za tohle tahá web a původní plán byl, že agent využije MCP. Jenže agent teď běží přímo na místě a měl spíše přirozeně snahu vrhnout se do toho rovnou přes REST API a dělal v tom chyby.

Jak to dopadlo? Dohodli jsme se, že vzhledem k tomu, že je všechno lokální, bude ideální, aby si OpenClaw napsal CLI a okomentoval si ho ve skillu. Vytvořili jsme si smarthomectl, které se LLM používá mnohem jednodušeji než snažit se montovat JSON objekty a řešit, jak správně udělat escape při spouštění. Jednoduché CLI a pěkné přepínače. Nicméně CLI postupně přidává abstrakci vycházející ze zkušenosti!

Příklad: Skupiny žaluzií, například ráno otočit všechny žaluzie kromě dvou v místnosti, kde ještě spí dítě. Místo volání API po jednom si OpenClaw po dohodě v CLI vytvořil možnost zadávat věci typu --include a --exclude a pak ještě --blinders-group. Tedy protože je to častá věc, dohodli jsme se, že dává smysl ji přidat - v podstatě tím tedy optimalizovat řešení (zrychlit a zjednodušit časté scénáře a zvýšit jejich spolehlivost).

::: callout type="rule" title="Architektura"
Architektura tedy je - low-level API propojuje agenta (svět digitální) s fyzickým světem. Agent si sám udržuje CLI ("svalová paměť") a skill (kontext, zručnost), kterými vytváří "vyšší logiku". K tomu má paměť. To je, co mají lidé na mysli, když tvrdí, že software kolabuje do agentů - základní komponenty řešení jsou API pro interakci se světem, kód a skill (výuční list agenta a možnost ho dále rozvíjet) a datová perzistence (paměť, nějaká databáze apod.).
:::
:::

::: card number="03" title="Fáze 3 - Proč mám mít webové rozhraní, když můžu mít GenUI?" default="open"
Web je fajn - pro mě přehledný, na míru, ale pro ostatní členy domácnosti možná ne. Třeba mají jinou představu co tam mít a jak to uspořádat. A navíc - kde mít agenta, jako chat na webu? Připojení OpenClaw přes WhatsApp je skvělé - nikdo si nic nemusí instalovat, zůstává ve svém workflow, jen vznikla specializovaná skupina na ovládání domácnosti a funguje to. WhatsApp je robustní, snadno se dá zpráva napsat i hlasem, funguje dost bezpečně odkudkoli i se špatným signálem. Otázkou tedy je - potřebuji web ještě vůbec? Je to přehlednější v tom, že mám ovládací prvky na jedné stránce a pokud potřebuji udělat víc akcí najednou, je to rychlé. Ale pokud agent je už dnes chytrý a chápe příkazy typu rozsviť lampu a linku (tzn. dojde mu, že kuchyňská linka je jen jedna, takže tou lampou asi myslím tu v obýváku a chci je zapnout současně), tak je to přes něj taky pohodlné. Jediné co mi vadí je velká přemýšlecí doba. Musím ještě zkoušet menší rychlejší modely, ale zase bych nerad, aby model zhloupl v okamžiku, kdy má udělat něco složitější nebo odpovídat na úrovni Copilotu na research a náročnější otázky (což samozřejmě výborně umí). Zadání typu "jestli zítra nebude pršet, pojďme dnes večer spustit zalévání x litrů" už vyžaduje vyhledání informací na Internetu a rozhodnutí podle výsledku, takže přes čisté webové UI začíná být takové ovládání zbytečně kostrbaté.

To, co bych potřeboval, je GenUI, ale v konzumerském světě se mi zatím nedaří najít vhodnou variantu. [WhatsApp Flows](https://developers.facebook.com/docs/whatsapp/flows/) umí strukturované vícekrokové formuláře a lehké UI, ale pořád to nejsou plnohodnotné mini-apps. [Telegram Mini Apps](https://core.telegram.org/bots/webapps) jsou z hlediska UI velmi schopné, ale Telegram drží end-to-end šifrování jen pro Secret Chats. Signal bohaté UI nepodporuje. [Discord](https://support.discord.com/hc/en-us/articles/25968222946071-End-to-End-Encryption-for-Audio-and-Video) už má E2E pro audio a video, ale ne pro textové zprávy. Do budoucna tedy zkusím tři cesty a uvidím, co bude nejlepší:

::: arrow-list title="Tři cesty"
- Web (to už mám a funguje to dobře)
- WhatsApp (funguje skvěle, exekuci mám v sandboxu a je to ideální pro ne-administrátorské používání)
- Vlastní chat/voicechat UI přes web s podporou mini-apps (to jdu právě teď zkoušet)
:::

Výsledek nemám, určitě se k tomu ještě vrátím - každopádně myslím, že zejména kombinace hlasu na vstupu a mini-app GenUI obrazovka na výstupu bude často ideální a doslova "jako dělaná" pro nějaké pozdější brýle s displejem.
:::

:::

::: group id="zavery" title="Závěry"

::: detail-grid title="Čtyři závěry" hint="Klikněte na kartu pro detail"
::: detail-card title="Software je paměť, optimalizace" summary="Skript, CLI nebo MCP server je způsob, jak si agent uloží natrénovaný postup."
Pokud bude agent dostatečně chytrý, bude mít přístup na všechna potřebná low-level API a data, a bude mít k dispozici potřebné nástroje (internet, databáze apod.) a bude mít kontext (nebo si ho dokáže efektivně sehnat, třeba ze znalostní báze), zvládne prakticky cokoli. Ale možná mu to dá zabrat - udělá spoustu chyb, bude načítat velké množství obsahu, třeba bude potřebovat pomoci a dát zpětnou vazbu, spotřebuje hromadu tokenů a času. Něco jako když vy děláte tu věc poprvé. Do příště to ale umíte natrénovat - získáte pro danou činnost svalovou paměť, vaše pohyby i myšlenkové postupy budou zakódované a optimalizované a současně vám učení dalo velké množství kontextu, tedy k čemu je to dobré, proč to děláte, jak to funguje. Tohle agent může udělat taky!
- **Software**, například napsaný skript či nová funkce v CLI či další MCP server, je způsob jak si agent uloží nějaký postup, business logiku, způsobem, který je opakovatelný, předvídatelný, lze ho upravovat a rozvíjet, lze ho testovat, tedy trénovat. Stejně jako váš tenisový servis.
- Kontext, například **skill** nebo jiný způsob jak ovlivnit co se dostane k modelu (třeba MCP server s pamětí), zaznamenává jak na to, k čemu je to dobré, jak to funguje. Stejně jako vaše schopnost "číst hru".
:::

::: detail-card title="API do světa, data, abstrakce jako skill" summary="Low-level API agentovi nevadí; vlastní abstrakce si může uložit do CLI nebo skillu."
Agent je schopen zvládnout komplexitu nízko-úrovňového API do světa a na rozdíl od člověka mu vyhovují víc, než abstrakce. Moduly v Terraformu děláme proto, že nejsme schopni zvládat dobře detail a abstrahované objekty nám skvěle jdou do hlavy, protože zapadají do širokého kontextu, který si držíme. LLM to má víceméně opačně. Než mu nutit naši představu abstrakcí, asi uděláme lépe, když mu dáme low-level API a přístup k datům.

Agent si možná najde vlastní abstrakce, ale ty budou opět o optimalizaci - skill nebo přidané věci do CLI či nové MCP funkce se stanou poznámkami jak rychleji a spolehlivěji provádět nějaká "vyšší" zadání uživatele.
:::

::: detail-card title="Kontext vs. zpětná vazba" summary="Když jde výsledek měřit, rozhoduje smyčka; když agent neví, co dělá, rozhoduje kontext."
Houževnatost agentů je úžasná - pokud mají možnost měřit výsledek, udělají neuvěřitelný pokrok, aby se jim to podařilo. Jsem přesvědčen, že pokud budete mít eshop, dokáže agent už velmi brzy (pokud už ne teď) převzít ladění celé aplikace s ohledem na maximalizaci zisku. Bude mít možnost pracovat s chováním klientů, tím, co a jak objednávají, a bude přicházet s nejrůznějšími nápady, které bude hned A/B testovat a měřit výsledky. V takové zpětnovazební smyčce je agent schopen dosáhnout fascinujících výsledků a kromě toho při nich bude neustále budovat nový kontext - které hypotézy se potvrzují a tak podobně. Jakmile už je eshop zaveden a funguje, tak myslím, že zpětná vazba je 80% úspěchu.

Jsou ale situace, kde tuto smyčku nejde uzavřít úplně, protože agent neví, co dělá. V takovém okamžiku je naprosto zásadní právě kontext - co má dělat, jak to funguje, porozumění byznys doméně a tak podobně. Je samozřejmě důležité mít i zpětnou vazbu ve formě zadání nějakých testů a měřitelných výstupů, ale v této chvíli bude kontext 80% úspěchu.

Za mě se tedy snažím vybudovat co nejlepší kontext, abych se co nejdříve dostal do stavu, ve kterém už to bude víceméně jen o zpětné vazbě, v ten okamžik jsem agentovi spíše na obtíž, chci aby na tom makal sám.
:::

::: detail-card title="Učení se od uživatele a GenUI" summary="Uživatel se nebude učit software; software a agent se musí učit uživatele."
Agent má skvělou schopnost pochopit co uživatel chce i když každý mu to řekne třeba nějak jinak. Pokud si agent není jist, zeptá se, uživatel upřesní, agent si zapamatuje. Agent se učí chápat uživatele, ne že se uživatel musí učit ovládat vaše řešení. Tohle je silné a lidé to budou vyžadovat.

Jenže chat interface nebude pro některé scénáře dostatečně efektivní a jeho kombinace s obrazem bude důležitá, ale čím víc pracujete s agenty, tím méně vám vyhovuje snažit se pochopit, jak to UI má fungovat. Grafické rozhraní bude muset být schopné se automaticky přizpůsobit uživateli, stejně jako to textové. Je to samozřejmě složitější, ale GenUI se musí stát standardem.
:::

:::

::: closing
Uživatelé se nebudou učit používat váš software. **Software a agent** se budou učit rozumět uživateli.
:::

:::
