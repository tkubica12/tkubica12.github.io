# Otevřený AI model má mnoho výhod. Většina z nich nevyžaduje vlastní hardware.

META
- Datum: 2026-09-14; jazyk: cs-CZ; experimental; published: true; dostupný EN strojový překlad.
- URL: /2026/vlastni-model-vlastni-server/
- Source: interactive\source\2026\vlastni-model-vlastni-server.article.md; veřejná kopie: [source.md](./source.md).
- source-sha256: 8d4bcb653240b8bf8a6a3fce671aa57b68ccdef84a54964ef5fa17bcd3bc3515
- Teze: otevřené váhy ≠ vlastní inference ≠ vlastní hardware. Kontrola, menší lock-in, legitimní použití, data, latence a cena jsou různé otázky. Většinu výhod získám bez nákupu serveru.
- Struktura: 12 karet; první část očekávání (01–06), druhá měření a ekonomika stejného modelu (07–12).

## První část: co od otevřeného modelu vlastně čekám

### 01 Oddělme model od místa, kde běží
- Stejný model přes tokenové API, na vlastní Azure GPU VM nebo na vlastním serveru. Mění se provozní odpovědnost a plátce nevyužité kapacity.
- Open weights = stažitelné váhy, provoz podle licence; ne automaticky plně open-source AI dle [OSI](https://opensource.org/ai/open-source-ai-definition). Trénovací data nemusí být otevřená; důležité pro bezpečnost.

### 02 Kontrola a závislost na dodavateli
- Podržení verze, vlastní runtime, kvantizace, cache, adaptér; nemusím čekat na funkci poskytovatelova API.
- Plán B po vypnutí API: další poskytovatelé nebo stažené váhy a GPU jinde.
- Konec vývojového týmu: dnešní schopnosti zůstanou, budoucí inovace ne. Migrace modelu mění tool calling, formát, kvalitu; není jen výměnou URL.
- Stejný model u velkých, menších i lokálních providerů nebo vlastní inference na VM; relativně snadný přesun, flexibilita změnit poskytovatele, typ železa, region. Není nutný nákup serveru.
- [Fable 5 vypnutí/obnovení](https://www.anthropic.com/news/redeploying-fable-5): Anthropic 12. 6. 2026 po americké exportní direktivě vypnul všem, globální přístup obnovil 1. 7. Nedokázal v reálném čase ověřovat státní příslušnost pro selektivní omezení; ne běžný výpadek. Stažené váhy snižují závislost na vypnutí služby, **nejsou výjimkou ze zákonů/exportních pravidel**.
- Dostupnost vah na internetu nezaručuje možnost plného použití. Firmy/stát mohou smluvně zakázat čínské modely v zakázkách; stát omezit zdravotnictví/práci s dětmi. Model může zbýt jen pro „osobní potřebu“.

### 03 Legitimní práce a guardrails
- Autorizovaný pentest / analýza incidentu potřebují útočné techniky; i výzkum AI/biologie může filtr blokovat či omezit přepnutím na slabší model.
- Open weights nezaručují absenci odmítání ve vahách; zůstává aplikace, licence, pravidla infrastruktury a odpovědnost.
- [Fable 5/5.1 → Opus](https://support.claude.com/en/articles/15363606-why-claude-switched-models-in-your-conversation-with-fable-5-or-fable-5-1): Anthropic popisuje blokování/fallback pro některé ofenzivní techniky a úzké úlohy frontier LLM vývoje (distribuovaný trénink, návrh ML akcelerátorů, kernely nestandardních čipů).
- Ne zákaz veškeré obrany/AI vývoje. Kontroly zahrnují soubory i kontext, false positives existují. Opus má ochrany; fallback nezaručuje odpověď. Některé obranné scénáře mají ověřovací program; app/API se liší.
- Otevřená alternativa pro laboratoř/výzkum: ověřit kvalitu, neztratit odpovědnost; API jako služba nebo cloudová VM může stačit.

### 04 Data a bezpečnost
- Vlastní inference dává kontrolu toku, přístupů, ukládání; API neznamená automaticky cizí přístup k datům, cloud neznamená nutný přístup provozovatele dovnitř VM.
- [Zero retention policy](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention): omezení uchovávání u podporovaných funkcí a sjednaných podmínek; **neznamená absenci zpracování dat při inference**.
- Confidential computing chrání paměť i před privilegovaným provozovatelem infrastruktury; jiná ochrana než ZDR. Liší se vlastní nastavení/odpovědnost, ne automatické pořadí bezpečnosti variant.
- Otevřené váhy neodhalují původ trénovacích dat a nedokazují absenci nežádoucího/skrytě podmíněného chování (např. spící agent). Umístění serveru nevyřeší důvěru v model.
- Region + privátní přístup + smlouva mohou vyhovět citlivým datům bez nutnosti on-prem.
- [Confidential computing včetně GPU VM](https://learn.microsoft.com/en-us/azure/confidential-computing/confidential-vm-overview): ochrana za běhu vyžaduje podporovanou platformu, konfiguraci, attestation.
- Neřeší chyby aplikace/oprávněný export; evropský region sám neřeší jurisdikci. Definovat hrozbu a obranu, ne nálepku.

### 05 Latence a offline
- Vlastní inference: rezervace kapacity a parametry pro rychlost jednoho požadavku na úkor celku. Typicky menší batch size → rychlejší odpověď, potenciálně výrazně dražší token.
- [Claude fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode): stejné váhy, rychlejší inference za vyšší cenu, ne chytřejší model. Anthropic implementaci nepopisuje jako pouhé zmenšení batch size; zrychlení hlavně generování, ne TTFT.
- Latence = síť + fronta + prefill + generování. Dobré API může předběhnout malý server; round tripy důležitější u hlasu/mnoha krátkých agentních kroků.
- Pro kontrolu latence může stačit cloudová VM; pro práci bez internetu ne. Pak zařízení/místní server.
- Offline AI ≠ nutně LLM: např. útočný dron může používat computer vision, nepotřebuje jazykovou diskusi.
- Menší model může zvládat extrakci/klasifikaci. **Autorův osobní verdikt pro očekávaný coding agent: cokoli běžícího na notebooku naprosto nepoužitelné.** Ne univerzální tvrzení, že malý model nenapíše užitečnou funkci.
- [GLM 5.3](https://huggingface.co/zai-org/GLM-5.3) ~753 miliard parametrů vs. [Kimi K3](https://huggingface.co/moonshotai/Kimi-K3) 2,8 bilionu: úžasné otevřené modely, ne notebooková liga, ne stejná velikost/nároky. Velké multi-GPU sestavy, u největších cluster.
- U největších modelů cluster v desítkách milionů Kč; hardware doporučený Moonshot AI pro Kimi K3 téměř 100 milionů Kč (cenová ilustrace níže).

**Hardware pro 2T: paměťová dolní mez, ne návrh nasazení**
- 2 biliony parametrů: pouze váhy ~4 TB BF16 / 2 TB 8bit / 1 TB 4bit. Bez cache, aktivací, kvantizačních metadat/režie. MoE používá část expertů na token, ostatní váhy stále musí někde být.
- [Thinkmate konfigurátor](https://www.thinkmate.com/system/gigabyte-g894-sd1-aax5): celý server 8× B200, 1,44 TB HBM, 538 120 USD. Ilustrativní kurz 22 Kč/USD → ~11,8 mil. Kč; ne aktuální kurz/závazná nabídka s českou DPH.

| 2T reprezentace | Jen váhy | Min. 8× B200 serverů dle součtu HBM | Orientační cena |
|---|---:|---:|---:|
| 4bit | 1 TB | 1 | 11,8 mil. Kč |
| 8bit | 2 TB | 2 | 23,7 mil. Kč |
| BF16 | 4 TB | 3 | 35,5 mil. Kč |

- **Ne doporučené konfigurace/změřený výkon.** Runtime, režie, podporované rozdělení modelu, kontext, batch size a rychlost mohou vyžadovat více GPU. Navíc propojení, napájení, chlazení, provoz. RAM/disk offload může snížit HBM, ale změní cenu i rychlost.
- [Moonshot: 2,8T Kimi K3 supernode ≥64 akcelerátorů](https://www.kimi.com/news/kimi-k3) pro efektivitu a rychlou komunikaci. 8 uvedených serverů = 64 B200 ≈94,7 mil. Kč bez další clusterové infrastruktury.
- 8 HGX serverů automaticky netvoří jeden NVLink supernode; pouze cenová ilustrace počtu GPU, ne ověřený Kimi deployment.

### 06 Chci model, který bude levnější
- Levnější model ≠ levnější provoz stejného modelu.
- Menší model s levným API může ušetřit bez GPU, pokud zvládne práci. Licence úsporu negarantuje: sazby, kvalita, opakování, lidské dodělávky.
- Pareto-optimální hranice: nejlepší poměr ceny/výkonu. Autor uvádí levnou GPT 5.6 Luna na hranici; closed source neznamená špatný poměr. Aktuální otevřené Mistral modely podle textu daleko od hranice: horší výsledky vůči hardwarové náročnosti.
- Dále pouze ekonomika stejné práce: tokenové API vs. vlastní IaaS inference vs. vlastnictví. Server neobhajovat jinými už rozebranými výhodami.

## Druhá část: stejný model, tři způsoby placení

### 07 Co běželo na A100
- Testován Mistral i Nemotron; zde pouze **NVIDIA Nemotron 3.5 Lightning 30B-A3B BF16**. Princip přenositelný, naměřený výkon/break-even ne.
- Azure `Standard_NC24ads_A100_v4`, 1× A100 80 GB PCIe, vLLM 0.28.0.
- Požadavek: 16 384 input + 512 output. Concurrency 1/5/10/20/50/100 × společný/unikátní prefix × 3 opakování = 36 měření, 4 017 úspěšných požadavků.
- Společný prefix simuluje opakované instrukce/nástroje/kontext coding agenta: velký podíl cached tokenů. Bez sdíleného začátku více nového vstupu = un-cached scénář.
- [Prefix cache](https://docs.vllm.ai/en/v0.28.0/features/automatic_prefix_caching/): reuse stavu zpracovaného vstupu, ne hotové odpovědi; oba scénáře mají stejný počet input/output tokenů.
- Logicky sdíleno 12 288 tokenů = 75 % vstupu. Hybridní attention/Mamba runtime blok 2 096 → 5 celých bloků = 10 480 tokenů. Hity ~63,96 % při c5–100; 62,75 % při c1 včetně počátečních misses. Unikátní prefix: 0 %.
- Lokální reuse ≠ API billing hit. API granularita, routing, TTL, skutečný hit ratio neměřeny. Výkon a předpoklad účtování voleny zvlášť.
- Raw completions bez chat template; syntetický kód; vynuceno 512 output s ignorováním EOS. Příjem nové práce 120 s + dokončení rozpracovaných; throughput zahrnuje doběh; klient hned opakuje.
- Váhy 58,93 GiB; BF16, připnutá revize i vLLM image, bez speculative decoding.
- API přesnost/kvalita/rychlost neznámé; pouze nacenění stejného objemu tokenů. Koupenému serveru přisouzen výkon Azure A100, ne druhé fyzické měření.
- A100 starší karta, jiná nebyla k dispozici. Autor očekává použitelnost pro řádové srovnání malého modelu a podobný trend u větších modelů/novějších GPU; nejde o přenos konkrétního výkonu/break-even.

### 08 Batch size, concurrency, latence
- Batch size: společně zpracovaná dávka, lepší využití stejných vah. Continuous batching průběžně přidává/odebírá požadavky.
- Měřený parametr = klientská concurrency, ne pevná interní dávka ani registrovaní uživatelé.
- Output tok/s = celá GPU, ne jeden člověk; TTFT = první token; průměry 3 opakování.

| Souběh | Prefix: output tok/s | TTFT | Celá odpověď | Unikátní: output tok/s | TTFT | Celá odpověď |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 148,2 | 0,39 s | 3,45 s | 132,2 | 0,81 s | 3,87 s |
| 5 | 294,3 | 1,35 s | 8,70 s | 228,2 | 2,70 s | 11,21 s |
| 10 | 398,2 | 2,24 s | 12,86 s | 289,6 | 3,12 s | 17,67 s |
| 20 | 591,9 | 3,16 s | 17,29 s | 371,2 | 4,20 s | 27,17 s |
| 50 | 820,1 | 4,73 s | 31,17 s | 409,4 | 17,72 s | 59,90 s |
| 100 | 788,2 | 15,83 s | 60,58 s | 389,6 | 64,48 s | 109,97 s |

- Cached c1→c50 ~5,5× kapacita, delší odpověď jednotlivci. c100 throughput klesá. Kalkulovat jen bod s přijatelnou latencí; noční batch ≠ interaktivní asistent.

### 09 Vytížení a výhoda providera
- Concurrency = kolik současně; časové využití = jak dlouho mám práci při tomto bodu. 100 % času c1 ≠ objem c50. `nvidia-smi` není ekonomické využití.
- 8 h × 5 dní = 23,8 % kalendáře, ještě před schůzkami, čekáním agentů, kolísáním. 60 % >100 h/týden: více pásem, aplikací, noční fronta.
- Provider skládá zákaznickou poptávku; vlastní server si frontu nevytvoří. Odstranění jeho marže nezíská jeho náklady.
- Výhodnější nákup, datacentrum, specialisté ve velkém. PUE = energie DC / IT; PUE 2 přidává 100 % energetické režie, ne stejné procento celé ceny inference.
- Batching/cache/routing ke vhodnému kontextu; sdílená kapacita neznamená sdílení soukromých dat.
- Oddělený prefill/decode: různé nároky, samostatné pooly/clustery a škálování. [Dynamo](https://docs.nvidia.com/dynamo/v1.0.0/design-docs/disaggregated-serving): přenos KV cache má náklad, není univerzální výhra.
- Speculative decoding: levný drafter navrhne tokeny, hlavní model společně ověří. Dobré návrhy zrychlí, nevhodný drafter může škodit.
- CUDA/Triton kernely, paměť, kvantizace, specializovaný hardware: podmínka podpora modelu a kvalita. [Fireworks inference](https://fireworks.ai/inference), [speculative decoding](https://docs.fireworks.ai/deployments/speculative-decoding).
- Techniky dostupné i self-hostingu, ale vývoj/provoz stojí práci. Není tvrzeno, že konkrétní endpoint vše používá; žádný domyšlený výkonový násobek.

### 10 Kalkulačka: předpoklady pěti let

| Varianta | Cena |
|---|---|
| API input / cached input / output | 0,06 / 0,01 / 0,22 USD/milion tokenů |
| Azure PAYG | 4,775 USD/alokovaná hodina |
| 3letá rezervace | 46 567 USD; extrapolace stejné sazby na 5 let = 77 611,67 USD |
| Vlastní server | 45 000 USD CAPEX; při trvalé práci 5letý součet = 64 834,80 USD |

- [Fireworks on Foundry sazby](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/fireworks/): veřejná reference, snapshot 3. 9. 2026.
- On-prem náskok před rezervací 12 776,87 USD/5 let ≈2 555 USD/rok; tolik prostoru pro další rozdílové náklady.
- [Huang/H100 nájemné](https://stocktwits.com/news-articles/markets/equity/nvda-rises-overnight-after-strong-week-ceo-jensen-huang-pumps-nvidia-chips-as-highly-rentable-money-minting-assets/cZt3ZqARJxw): pokračující poptávka; ~3,28 USD/h **per GPU**, ne celý 8GPU server. [Ornn metodika](https://ornn.com/product/ornn-data).
- Nájemné ≠ prodejní cena/odpis. 5 let plánovací horizont, ne důkaz životnosti/návratnosti. Bez zůstatkové hodnoty, konstantní ceny/výkon; ne tržní predikce.

### 11 Kdy vlastní provoz zlevní
- Výchozí lokální společný prefix; **předpoklad 64 % vstupu účtovaných API jako cached**, zbytek běžná sazba, výstup zvlášť. Dvě osy: využití placeného času a souběh.

**Časové využití při c50; USD / 1 000 stejných požadavků**
- VM alokovaná až do dokončení práce; platím mezery. Využití = produktivní podíl placeného času, během práce stále c50; nejde o pomalejší GPU. 1 000 požadavků = jednotka srovnání; rezervace/on-prem rozpočtené z pětiletých nákladů a práce.

| Využití placeného času | API, 64 % vstupu cached | Rezervace | On-prem | PAYG včetně čekání |
|---|---:|---:|---:|---:|
| 100 % | 0,5714 | 0,3073 | 0,2567 | 0,8281 |
| 90 % | 0,5714 | 0,3415 | 0,2828 | 0,9201 |
| 60 % | 0,5714 | 0,5122 | 0,4133 | 1,3802 |
| 40 % | 0,5714 | 0,7683 | 0,6090 | 2,0703 |
| 20 % | 0,5714 | 1,5365 | 1,1962 | 4,1406 |
| 10 % | 0,5714 | 3,0731 | 2,3705 | 8,2812 |

- Plné využití: rezervace/on-prem levnější; 40 % obě dražší. Rovnost rezervace 53,78 %, on-prem 42,74 %.
- API stejné tokeny → stejná cena. Rezervace stále placená, on-prem mimo práci idle, PAYG platí každou alokovanou hodinu.
- Při c50 tisíc požadavků ~10,4 min produktivního běhu. 100% využití → PAYG ~0,83 USD; 10% využití → ~104 min alokace a ~8,28 USD. Start/načtení modelu nezapočtené, přidaly by další placený čas.

**Souběh; USD / 1 000 požadavků při 100% časovém využití, lokální prefix + 64 % vstupu účtovaných API jako cached**

| Souběh | API | Rezervace | On-prem | PAYG |
|---|---:|---:|---:|---:|
| 1 | 0,5714 | 1,7005 | 1,4206 | 4,5826 |
| 5 | 0,5714 | 0,8563 | 0,7154 | 2,3076 |
| 10 | 0,5714 | 0,6329 | 0,5287 | 1,7056 |
| 20 | 0,5714 | 0,4258 | 0,3557 | 1,1473 |
| 50 | 0,5714 | 0,3073 | 0,2567 | 0,8281 |
| 100 | 0,5714 | 0,3197 | 0,2671 | 0,8616 |

- Z měřených bodů první levnější on-prem při c10, rezervace při c20; PAYG nikdy. Obrat pořadí on-prem mezi c5/c10, rezervace c10/c20; přesná rovnost/batch size nezměřená. Nutná práce pořád i najednou.
- c100 horší ekonomika než c50 (throughput klesá); TTFT 15,83 vs. 4,73 s.

- Sleva za cached tokeny ovlivňuje výsledek: levnější API → více práce potřebné pro výhodnost vlastní inference.
- Bez prefixu na obou stranách, uncached c50: práh rezervace 56,18 %, on-prem 44,73 %; jiná kapacita, TTFT 17,72 s.
- VM alokovaná 48 h, cached c50, 100% využití: PAYG compute 229,20 USD vs. API 158,15 USD při 64 % vstupu účtovaných jako cached. Při 50% využití téhož okna polovina práce a API ceny, VM stále 229,20 USD.
- PAYG neporazí API ani při 100% využití v měřených soubězích. Dealokace po dávce odstraní zbytek měsíce, ne placené mezery během práce. Start/načtení také stojí čas; disky mohou stát i po dealokaci.
- PAYG vs. rezervace: PAYG dražší při alokaci >37,1 % kalendáře, včetně čekání. Ne produktivní využití ani break-even proti API.

```text
H = 43 800 hodin za pět let
u = produktivní podíl kalendáře
R = naměřené output tok/s × 3600 / 512
h = předpokládaný podíl vstupních tokenů účtovaných API jako cached
p = [16384 × ((1 − h) × 0,06 + h × 0,01) + 512 × 0,22] / 1 000 000
API = H × u × R × p
PAYG po celé srovnávané období alokované = H × 4,775 USD
rezervace = 77 611,67 USD
on-prem = 59 316 USD + H × u × 0,126 USD
```

- On-prem fix = pořízení + údržba + idle energie; aktivita přidá jen active−idle. Jednotková cena = náklad / počet požadavků. Nad dosažitelným prahem fixní varianta levnější; >100 % nesplnitelné.
- ~54 % c50 ≈90 h práce/týden při tomto výkonu, ne GPU monitor. Různé souběhy sčítat po bodech; průměr concurrency nedává lineární výkon.

### 12 Co si z toho beru
- Otevřené modely: kontrola, verze, chování, alternativa po konci služby; většina bez vlastního serveru.
- Tento model/workload: malý souběh/nepravidelná práce → levné API. Hodně souběžné práce dlouho → vlastní inference může vyhrát.
- Pak rezervovaná VM vs. úplný on-prem rozpočet, ne cena karty vs. nonstop PAYG.
- Cached c50, předpoklad API hitu 64 %: ~54 % času rezervace / ~43 % on-prem. Náskok on-prem jen ~2,6 tisíce USD/rok na další rozdílové náklady, snadno převáží provoz.
- Pořadí: model zvládající práci → potřebná kontrola/odezva → kdo provozuje GPU. Odstranit marži poskytovatele ≠ neplatit vlastní idle server.

ZÁVĚR
- Otevřené váhy: kontrola, flexibilita, řešení nestandardních situací včetně politické nestability. Autor doporučuje API od důvěryhodného poskytovatele, jako je Microsoft; vlastní server podle něj pro naprostou většinu případů nedává smysl, je nesmyslně drahý.
