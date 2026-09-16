---
format_version: 1
title: "Otevřený AI model má mnoho výhod. Většina z nich nevyžaduje vlastní hardware."
eyebrow: "Open weights, vlastní inference a peníze"
subtitle: "Otevřené váhy dávají kontrolu. Ale kdo zaplatí GPU, když nemá práci? Pojďme projít výhody open-weight modelů, vyzkoušet jejich provoz a propočítat náklady na vlastní server, cloudovou VM i hotové API."
slug: vlastni-model-vlastni-server
date: 2026-09-14
language: cs-CZ
status: experimental
published: true
canonical_url: "/2026/vlastni-model-vlastni-server/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

Proč bych mohl chtít používat otevřený model? Větší kontrola nad tím, co provozuju a kam posílám data. Méně omezení při autorizované kyberbezpečnostní práci nebo vývoji AI. Menší závislost na dodavateli. Možnost dostat se na nižší latenci. A nakonec to, co zní asi nejlákavěji: **nemohlo by to být levnější?**

Za mě jsou to dobré otázky. Jen se z nich občas udělá jeden velký závěr: potřebujeme vlastní server. Ten ale podle mě ve většině případů neplatí a to dnes rozebereme. Některé výhody získám volbou modelu, jiné vlastní inferencí a jen část z nich opravdu vyžaduje železo u mě.

Pojďme nejdřív projít ta očekávání. Kde otevřený model pomůže a co z toho předpokládá i nějaký konkrétní způsob provozování modelu? A co jsou naopak univerzální výhody open-weight modelu bez ohledu na to, jak ho získám? Je levnější mít model na vlastním hardwaru doma, na pronajatém hardwaru v cloudu s rezervací, zapínat si hardware (VM) dávkově podle potřeby, nebo jít do token-as-a-service, platby podle tokenů? To si zkusme změřit a dobře propočítat — zásadní bude vzít v úvahu zatíženost a využitelnost, batch size a další aspekty.

::: group id="co-od-modelu-chci" title="První část: co od otevřeného modelu vlastně čekám"

::: card number="01" title="Oddělme model od místa, kde běží"
Otevřený model můžu používat přes hotové API a platit za tokeny. Stejný model si můžu pustit na GPU virtuálce v Azure. Nebo si koupím server a provozuju ho u sebe.

**Model může být stejný. Liší se, kdo se stará o provoz a kdo platí nevyužitou kapacitu.**

V textu budu používat hlavně označení **open weights**: váhy si můžu stáhnout a za podmínek licence provozovat. Není to automaticky totéž co plně open-source AI podle [definice OSI](https://opensource.org/ai/open-source-ai-definition). Například nemusí být otevřená data, na kterých se model trénoval — to nás bude zajímat později při posuzování bezpečnosti. Pro naši debatu je podstatná právě možnost vlastního provozu.
:::

::: card number="02" title="Chci kontrolu a nechci být závislý na jednom dodavateli"
Tady otevřenému modelu fandím. Můžu si podržet konkrétní verzi, měnit runtime, kvantizaci, cache nebo přidat vlastní adaptér. Nemusím čekat, jestli mi poskytovatel takovou možnost vystaví v API.

A když dodavatel API vypne? Buď je tu mnoho dalších, nebo se staženými vahami můžu nastartovat GPU kdekoli jinde.

Když skončí tým, který model vyvíjí, uchovám si dnešní schopnosti. **Nezískám tím automaticky jeho budoucí inovace.** A ani přechod na jiný model není jen výměna URL: jinak může fungovat tool calling, formát odpovědí nebo kvalita na mojí úloze.

Kvůli tomu všemu ovšem nemusím kupovat server. Stejný model nabízí jak velcí provideři, tak ti menší i lokální, nebo můžu rozjet inferenci na vlastní VM — máme tedy možnost relativně snadno přejít jinam a udržuju si flexibilitu kdykoli cokoli změnit (poskytovatele, typ železa, region).

12. června 2026 Anthropic po **americké exportní direktivě** vypnul Fable 5 všem uživatelům; globální přístup obnovil 1. července. [Sám popisuje](https://www.anthropic.com/news/redeploying-fable-5), že nedokázal v reálném čase ověřovat státní příslušnost uživatelů, aby mohl omezení uplatnit selektivně. Nebyl to běžný výpadek serveru. Stažené otevřené váhy snižují závislost na podobném vypínači konkrétní služby, neplatí ale jako výjimka ze zákonů nebo exportních pravidel.

Přestože váhy, co už jsou na internetu, těžko někdo zamaskuje, neznamená to, že přístup k nim vám dá možnost je plně použít. Firmy i stát mohou smluvně zakázat používání čínských modelů ve svých zakázkách, stát může omezit použití třeba ve zdravotnictví nebo při práci s dětmi. Může se tak stát, že vám model zbyde jen pro „osobní potřebu“.
:::

::: card number="03" title="Chci, aby mě model při legitimní práci zbytečně nezastavoval"
Představme si, že dělám autorizovaný penetrační test nebo rozebírám logy napadeného systému. Potřebuju pracovat i s útočnými technikami, jinak tomu incidentu těžko porozumím. Případně pracuji na výzkumu v oblasti AI nebo biologie. Filtr může vidět nebezpečné téma a práci zastavit nebo mě přepnout na méně schopný model a to může být omezující.

**Otevřený model ale neznamená automaticky model bez guardrails.** Odmítání může mít naučené ve vahách. Další omezení přidává aplikace, licence nebo provozovatel infrastruktury.

::: reveal title="Fable, Opus a některé úlohy vývoje AI"
[Anthropic u Fable 5 a 5.1 přímo popisuje](https://support.claude.com/en/articles/15363606-why-claude-switched-models-in-your-conversation-with-fable-5-or-fable-5-1) blokování nebo fallback na Opus u některých ofenzivních kyberbezpečnostních technik. Zmiňuje také úzkou skupinu úloh vývoje frontier LLM: distribuovanou trénovací infrastrukturu, návrh ML akcelerátorů nebo kernely pro některé nestandardní čipy.

Nejde o zákaz veškerého AI vývoje ani obranné bezpečnosti. Kontroly ale posuzují i načtené soubory a další kontext, takže problém nemusí být jen v tom, co jsem napsal do posledního promptu. Poskytovatel přiznává false positives; i Opus má vlastní ochrany a fallback nezaručuje odpověď. Pro některé legitimní obranné scénáře existuje ověřovací program. Chování a nastavení fallbacku se navíc liší mezi aplikací a API.

Pro bezpečnostní laboratoř nebo výzkumný tým může být vhodný otevřený model důležitá alternativa. Nezmizí tím odpovědnost ani potřeba ověřit jeho kvalitu. A znovu: API jako služba nebo vlastní serving na cloudové VM může stačit.
:::
:::

::: card number="04" title="Chci mít data pod kontrolou. Je to u mě bezpečnější?"
Vlastní inference mi umožní rozhodnout, kam data tečou, kdo je uvidí a co se ukládá. To je skutečná výhoda, ale neznamená to, že při používání per-token API automaticky někdo získá přístup k mým datům nebo že provozovatel cloudu musí vidět dovnitř mého VM. API může mít [zero retention policy](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention), která pro podporované funkce a za sjednaných podmínek omezuje uchovávání dat. **Confidential computing** zase umožňuje chránit data v paměti i před privilegovaným provozovatelem infrastruktury. Jsou to různé ochrany — samotné zero retention neznamená, že služba data při inference vůbec nezpracovává.

Liší se míra toho, co nastavuji a za co odpovídám sám. To ale neříká, která varianta je bezpečná více nebo méně, záleží na detailech.

A vrátím se i k trénovacím datům: otevřené váhy samy neodhalují jejich původ a nejsou důkazem, že model nemá nežádoucí nebo skrytě podmíněné chování (například tzv. spící agent). Umístění serveru tuhle důvěru v model samo nevyřeší.

Pokud mi vyhoví vhodný region, privátní přístup a smluvní podmínky služby, nemusím kvůli citlivým datům automaticky do on-prem.

::: reveal title="A co confidential computing a jurisdikce?"
[Confidential computing včetně GPU VM](https://learn.microsoft.com/en-us/azure/confidential-computing/confidential-vm-overview) může chránit data i za běhu. Potřebuju ale podporovanou platformu, správné nastavení a attestation.

Ani tahle technologie neodstraní chyby aplikace nebo oprávněný export dat. A evropský region sám nevyřeší všechny otázky jurisdikce. Za mě je lepší popsat konkrétní hrozbu a obranu než se přít o to, která nálepka je bezpečnější.
:::
:::

::: card number="05" title="Chci nižší latenci. Nebo fungovat úplně bez internetu"
Vlastní provozování modelu mi dovolí rezervovat kapacitu pro moji aplikaci a ladit ho na rychlou odpověď, ne na maximální počet tokenů za den. Jinak řečeno můžu ovlivnit inferencing parametry a prioritizovat vyšší počet tokenů za vteřinu pro jeden požadavek na úkor celkové kapacity. Typicky snížím batch size: jednotlivý požadavek běží rychleji, ale náklady na token mohou výrazně narůst.

Podobnou volbu nabízejí i komerční poskytovatelé. Například [Claude fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) používá stejné váhy a rychlejší nastavení inference za vyšší cenu. Není to jiný, chytřejší model. Konkrétní implementaci ale Anthropic nepopisuje jako pouhé snížení batch size a zrychlení se týká hlavně generování tokenů, ne času do prvního tokenu.

Vedle sítě totiž čekám také ve frontě, na zpracování vstupu a na generování odpovědi. Dobře provozované vzdálené API může malý lokální server předběhnout. U hlasu nebo mnoha krátkých agentních kroků naopak síťové round tripy poznám víc než u jedné dlouhé odpovědi.

**Když chci kontrolovat latenci, může stačit vlastní cloudová VM. Když musím fungovat bez internetu, tak nestačí.** Tam už dává smysl model na zařízení nebo místní server.

Jenže tam, kde běží systém, který nesmí mít přístup k internetu, často nepotřebuju žádné LLM. Útočný dron může používat „AI“ ve formě computer vision; pro tuhle úlohu nepotřebuje diskutovat rozdíly mezi přístupy Platóna a Sókrata. Offline AI tedy není automaticky argument pro lokální velký jazykový model.

U notebooku bych si nejdřív ověřil, že menší model vůbec zvládne moji úlohu. Na extrakci nebo klasifikaci může být výborný; složitý coding agent je jiné zadání. **Za mě je pro kódování, které od agenta očekávám, cokoli, co dokáže běžet na notebooku, naprosto nepoužitelné.** To je moje laťka pro tenhle způsob práce, ne tvrzení, že malý model nenapíše užitečnou funkci.

Otevřené modely jako [GLM 5.3](https://huggingface.co/zai-org/GLM-5.3) nebo [Kimi K3](https://huggingface.co/moonshotai/Kimi-K3) jsou podle mě úžasné, ale notebooková liga to není. Ani oba nejsou stejně velké: zveřejněné váhy GLM 5.3 mají přibližně 753 miliard parametrů, Kimi K3 má 2,8 bilionu. Na efektivní provoz potřebuju velké vícenásobné GPU sestavy, u největších modelů cluster, jehož cena se bude pohybovat v desítkách milionů korun. Hardware doporučený firmou Moonshot AI pro provoz Kimi K3 vychází na téměř 100 milionů korun.

::: reveal title="Kolik tedy řádově stojí hardware pro 2T model?"
Pro orientaci vezmu model se dvěma biliony parametrů, tedy 2T. Samotné váhy potřebují přibližně **4 TB v BF16, 2 TB v osmibitové a 1 TB ve čtyřbitové reprezentaci**. Je to hrubá paměťová aritmetika bez cache, aktivací, kvantizačních metadat a další režie. U MoE se sice při jednom tokenu používá jen část expertů, ale ostatní váhy musím také někde mít.

Konkrétní [konfigurátor Thinkmate](https://www.thinkmate.com/system/gigabyte-g894-sd1-aax5) ukazuje celý server s **8× B200 a 1,44 TB HBM za 538 120 USD**. Při čistě ilustrativním kurzu 22 Kč/USD je to asi 11,8 milionu korun. Nejde o aktuální kurz ani závaznou nabídku s českou DPH.

| Reprezentace 2T vah | Jen váhy | Nejméně osmigrafikových B200 serverů podle součtu HBM | Jejich orientační cena |
|---|---:|---:|---:|
| 4bit | 1 TB | 1 | 11,8 mil. Kč |
| 8bit | 2 TB | 2 | 23,7 mil. Kč |
| BF16 | 4 TB | 3 | 35,5 mil. Kč |

**Tohle nejsou doporučené konfigurace ani změřený výkon.** Počty jsou jen dolní mez z paměti. Konkrétní runtime může potřebovat víc GPU kvůli režii, podporovanému rozdělení modelu, kontextu, batch size a požadované rychlosti. Další položkou je propojení serverů, napájení, chlazení a provoz. Offload do RAM nebo na disk zase může snížit potřebnou HBM, ale cenu a rychlost pak musím počítat úplně jinak.

Pro srovnání: [Moonshot u 2,8T Kimi K3 doporučuje supernode se 64 nebo více akcelerátory](https://www.kimi.com/news/kimi-k3) kvůli efektivitě inference a vysokorychlostní komunikaci. Osm výše uvedených serverů, tedy 64 B200, stojí v prostém součtu asi **94,7 milionu Kč**, ještě bez dodatečné clusterové infrastruktury. Osm HGX serverů navíc samo o sobě nevytvoří jeden NVLink supernode; je to cenová ilustrace stejného počtu GPU, ne ověřený návrh nasazení Kimi.

:::
:::

::: card number="06" title="Chci model, který bude levnější"
Tady bych nejdřív oddělil dvě úspory. **Vybrat levnější model není totéž jako levněji provozovat stejný model.**

Pro řadu úloh můžu místo drahého frontier modelu vzít menší otevřený model s levným API a ušetřit. Pokud úlohu zvládá, proč ne? Úsporu mám hned, bez nákupu GPU. Jen ji nezaručuje samotná licence: záleží na ceníku, kvalitě, počtu pokusů a tom, kolik práce nakonec musí dodělat člověk. Typicky mluvíme o tzv. pareto-optimální hranici, tedy modelech, které leží na nejlepším poměru ceny a výkonu. Například velmi levná GPT 5.6 Luna je na této hranici — closed source model neznamená nutně, že má špatný poměr ceny a výkonu. Stejně tak aktuální modely Mistral mají od této hranice dost daleko — jsou sice otevřené, ale na náročnost hardwaru nedávají tak dobré výsledky jako ostatní.

Druhá otázka už je jiná: když jsem si model vybral, bude levnější kupovat jeho tokeny jako službu, provozovat ho na IaaS, nebo koupit vlastní železo?

A přesně to chci ve druhé části propočítat. Kontrolu, bezpečnost a omezení už máme rozebrané. Teď nebudu obhajovat server jinými výhodami — zajímá mě **cena stejné práce**.
:::

:::

::: group id="kolik-stoji-provoz" title="Druhá část: stejný model, tři způsoby placení"

::: card number="07" title="Co jsem si pustil na A100"
Testoval jsem Mistral i Nemotron, ale dál budu komentovat jen **NVIDIA Nemotron 3.5 Lightning 30B-A3B v BF16**. Princip srovnání platí i pro další modely; konkrétní rychlost a hranice návratnosti se samozřejmě přenášet nedají.

Použil jsem Azure VM `Standard_NC24ads_A100_v4` s jednou **A100 80 GB PCIe** a vLLM 0.28.0. Každý požadavek měl 16 384 vstupních a 512 výstupních tokenů. Zkoušel jsem 1, 5, 10, 20, 50 a 100 souběžných požadavků, vždy s opakovaným prefixem a bez něj. Každou kombinaci třikrát — celkem 36 měření a 4 017 úspěšných požadavků.

Varianta se společným prefixem simuluje opakovanou práci coding agenta v jednom projektu: instrukce, nástroje a část kontextu posílám znovu (takže jde o test s velkou částí cached tokenů). Bez sdíleného začátku model víc pracuje na novém vstupu (un-cached scénář).

::: reveal title="Cache: stejný vstup neposílám zadarmo"
V obou scénářích posílám stejný počet input tokenů a generuju stejný počet output tokenů. S [prefix cache](https://docs.vllm.ai/en/v0.28.0/features/automatic_prefix_caching/) se znovu použije stav už zpracovaného začátku. **Není to hotová odpověď z cache; výstup se pořád generuje.**

Společný prefix má 12 288 tokenů, tedy 75 % vstupu. Tenhle hybridní attention/Mamba runtime ale ukládá cache po blocích 2 096 tokenů. Znovu použije pět celých bloků, tedy 10 480 tokenů. Naměřil jsem proto přibližně **63,96 % tokenových hitů** při souběhu 5 až 100 a 62,75 % při jednom streamu včetně počátečních misses. Bez společného prefixu byly hity nulové.

Tohle je lokální reuse. **Kolik tokenů mi levněji vyúčtuje API, je samostatná otázka.** Jeho granularitu, routing, TTL a reálný hit ratio jsem neměřil. V penězích proto zvlášť vybírám naměřený výkon a zvlášť předpoklad API účtování.
:::

::: reveal title="Metodika a hranice srovnání"
Používám raw completions bez chat template, syntetický kódový obsah a vynucených 512 output tokenů s ignorováním EOS. Nové požadavky se spouštějí 120 sekund, potom se čeká na dokončení rozpracovaných; throughput zahrnuje i tento doběh. Každý klient po dokončení hned posílá další požadavek.

Váhy zabraly 58,93 GiB GPU paměti. Běžel BF16 model s připnutou revizí a vLLM image; speculative decoding jsem nezapínal. Interní přesnost, kvalitu ani rychlost skutečného API neznám. Na jeho straně jen oceňuju stejný objem tokenů. Výkon případného koupeného serveru níže odvozuju od naměřené Azure A100, nejde o druhé fyzické měření.
:::

A100 je karta poměrně stará, jinou jsem neměl k dispozici — myslím ale, že pro řádové srovnání na malém modelu to není problém a trend, který navnímáme zde, bude podobný i u větších modelů a novějších karet.
:::

::: card number="08" title="Batch size: víc práce najednou, ale ne zadarmo"
Pojďme si představit, že GPU obsluhuje jen mě. Načítá váhy a postupně generuje tokeny. Když obsluhuje víc požadavků společně, může práci nad stejnými vahami lépe využít. **Batch size je velikost takové společně zpracovávané dávky.**

Moderní serving používá *continuous batching*: hotové požadavky odcházejí a nové průběžně přibývají. Já zvenku nastavuju **souběh klientů, tedy concurrency**, ne pevnou velikost každé interní dávky. Souběh 50 také neznamená 50 registrovaných uživatelů, ale 50 současně rozpracovaných požadavků.

Co to udělalo s cenově použitelnou kapacitou? V tabulkách je **souhrnný output tok/s celé karty**, ne rychlost jednoho člověka. TTFT je čas do prvního tokenu; všechna čísla jsou průměry tří opakování.

::: tabs id="nemotron-vykon"
::: tab id="vykon-cache" title="Společný prefix"
| Souběh | Output tok/s | TTFT | Doba celé odpovědi |
|---|---:|---:|---:|
| 1 | 148,2 | 0,39 s | 3,45 s |
| 5 | 294,3 | 1,35 s | 8,70 s |
| 10 | 398,2 | 2,24 s | 12,86 s |
| 20 | 591,9 | 3,16 s | 17,29 s |
| 50 | 820,1 | 4,73 s | 31,17 s |
| 100 | 788,2 | 15,83 s | 60,58 s |
:::
::: tab id="vykon-bez-cache" title="Unikátní vstupy"
| Souběh | Output tok/s | TTFT | Doba celé odpovědi |
|---|---:|---:|---:|
| 1 | 132,2 | 0,81 s | 3,87 s |
| 5 | 228,2 | 2,70 s | 11,21 s |
| 10 | 289,6 | 3,12 s | 17,67 s |
| 20 | 371,2 | 4,20 s | 27,17 s |
| 50 | 409,4 | 17,72 s | 59,90 s |
| 100 | 389,6 | 64,48 s | 109,97 s |
:::
:::

S cache jsem se z jednoho na padesát streamů dostal na přibližně **5,5násobek celkové kapacity**. Ale odpověď jednotlivci trvá déle. Při stovce už throughput dokonce klesá. „Přidám větší batch a budu levnější“ tedy neplatí donekonečna.

Za mě z toho plyne jednoduché pravidlo pro kalkulačku: **počítat můžu jen s kapacitou, jejíž latence mi ještě vyhovuje.** Noční dávka a interaktivní asistent jsou jiné scénáře a je pro ně vhodná jiná batch size.
:::

::: card number="09" title="Vytížení: kdo na tom bude pracovat v neděli večer?"
Teď ta druhá osa. **Souběh říká, kolik práce dělám najednou. Časové využití říká, jak dlouho tu práci vůbec mám.**

Sto procent času při jednom streamu není stejný objem jako sto procent při padesáti. A údaj z `nvidia-smi` není odpověď na žádnou z těchto ekonomických otázek. Zajímá mě dokončená užitečná práce, na kterou rozpočítám náklady.

Osm hodin pět dní v týdnu je jen **23,8 % kalendáře**. A to bych uvnitř pracovní doby musel držet zvolený souběh nepřetržitě. Lidé ale chodí na schůzky, agenti čekají na nástroje a poptávka kolísá. Šedesátiprocentní využití znamená přes sto hodin práce týdně. K tomu už potřebuju třeba více časových pásem, více aplikací nebo frontu úloh na noc.

Tady má velký provider praktickou výhodu: skládá poptávku mnoha zákazníků. Když já končím, někdo jiný začíná. Můj vlastní server takovou frontu práce sám od sebe nedostane.

Poskytovatel díky výnosům z rozsahu může mít podstatně nižší náklady: levnější hardware, efektivnější datacentrum, custom kernely či inferencing čipy nebo lépe vyladěná řešení (například disagregace prefill a decode či spekulativní decoding). Více níže.

::: reveal title="Proč provider nemusí být jen drahý překupník GPU"
Když odstraním jeho marži, ještě nezískám jeho náklady. Může nakupovat hardware výhodněji, provozovat datacentrum s nižším PUE a rozložit práci specialistů přes velký objem. **PUE je poměr energie celého datacentra k energii IT**: při PUE 2 stojí energetická režie dalších 100 % spotřeby serveru. Nižší PUE tuto režii snižuje, ne celou cenu inference stejným poměrem.

Vedle toho má prostor ladit samotný serving:

- **Batching, cache a routing.** Seskupí vhodné požadavky a pošle je tam, kde už existuje použitelný kontext. Více zákazníků neznamená sdílet jejich soukromá data; přínos je už ve společné kapacitě.
- **Oddělený prefill a decode.** Zpracování dlouhého vstupu a postupné generování mají jiné nároky. Mohou běžet na oddělených poolech či clusterech a škálovat nezávisle, místo aby se přetahovaly o stejné prostředky.
- **Speculative decoding.** Malý draft model nebo jiný levný mechanismus navrhne několik tokenů dopředu. Hlavní model je společně ověří. Když návrhy často sedí, může generování zrychlit; když nesedí, přidaná práce může i škodit.
- **Optimalizace blízko hardwaru.** Vlastní CUDA/Triton kernely pro NVIDIA GPU, lepší práce s pamětí, kvantizace nebo specializovaný inference hardware. Podmínkou je pořád podpora konkrétního modelu a přijatelná kvalita.

[NVIDIA Dynamo popisuje disaggregated serving](https://docs.nvidia.com/dynamo/v1.0.0/design-docs/disaggregated-serving) včetně přenosu KV cache mezi prefill a decode enginy. Přenos něco stojí, takže to není automatická výhra pro každý workload. [Fireworks uvádí vlastní kernely a oddělené serving pooly](https://fireworks.ai/inference) a [dokumentuje speculative decoding](https://docs.fireworks.ai/deployments/speculative-decoding), včetně rizika nevhodného drafteru.

Část těchto technik si můžu nasadit také. Nejsou to kouzla vyhrazená cloudům. Rozdíl je v tom, jestli je pro jeden server umím a chci vyvíjet, provozovat a zaplatit. Netvrdím, že je konkrétní Nemotron endpoint všechny používá, ani mu z nich nepřidávám vymyšlený násobek výkonu.
:::
:::

::: card number="10" title="Co dávám do kalkulačky"
Srovnávám pět let a tři způsoby provozu stejného modelu. U VM ještě rozliším, jestli ji zapínám jen na dávku, nebo si kapacitu držím dlouhodobě.

| Varianta | Cenový předpoklad |
|---|---|
| API, platba za tokeny | 0,06 / 0,01 / 0,22 USD za milion běžných input / cached input / output tokenů |
| Azure VM PAYG | 4,775 USD za každou alokovanou hodinu |
| Azure VM, tříletá rezervace | 46 567 USD za tři roky; stejnou sazbu extrapoluju na pět let: **77 611,67 USD** |
| Vlastní server | Pořízení 45 000 USD + pět let údržby a energie: při trvalé práci **64 834,80 USD** |

API sazba je [veřejná reference Fireworks on Foundry](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/fireworks/) ze snapshotu z 3. 9. 2026.

Cloudová rezervace a vlastnictví tady nejsou řádově od sebe. Rozdíl vychází na **12 776,87 USD za pět let**, tedy asi **2 555 USD ročně**. Tolik prostoru zbývá na další náklady on-prem navíc proti VM, než se modelový náskok vytratí.

::: reveal title="Proč zůstávám u pěti let"
Starší GPU nemusí být za tři roky bezcenná. [Zpráva o Huangově reakci na rostoucí nájemné H100](https://stocktwits.com/news-articles/markets/equity/nvda-rises-overnight-after-strong-week-ceo-jensen-huang-pumps-nvidia-chips-as-highly-rentable-money-minting-assets/cZt3ZqARJxw) je zajímavý signál pokračující poptávky. Cena kolem 3,28 USD/h v ní ale patří per-GPU nájemnému, ne celému osmigrafikovému serveru; metodiku takových indexů popisuje [Ornn Data](https://ornn.com/product/ornn-data).

Nájemné není totéž co prodejní cena použitého serveru nebo účetní odpis. Pět let beru jako plánovací horizont, ne dokázanou životnost či návratnost. Zůstatkovou hodnotu nezapočítávám a po celé období držím stejné sazby i výkon. Je to srovnávací model, ne předpověď trhu.
:::
:::

::: card number="11" title="Kdy mi vlastní provoz vyjde levněji?"
Pojďme měnit vždycky jednu věc: **jak dobře využiju zaplacený čas a kolik požadavků zpracovávám najednou**. V obou scénářích používám lokální společný prefix a předpokládám, že API vyúčtuje **64 % vstupních tokenů jako levnější cached tokeny**. Zbytek vstupu platím běžnou sazbou, výstup se generuje a platí zvlášť.

::: tabs id="nemotron-penize"
::: tab id="penize-vyuziti" title="1. Využití v čase"
V tomto scénáři srovnávám náklady na **1 000 stejných požadavků při souběhu 50 během zpracování** a dívám se, co s cenou udělá míra využití zaplaceného času. **VM spustím a nechám ji alokovanou až do dokončení práce. Platím tedy i mezery, kdy na další práci čeká.**

Při 100% využití na sebe práce navazuje bez mezer. Při 10% využití server produktivně pracuje jen desetinu alokovaného času — dokončení stejné práce zabere desetkrát delší placený čas. Když pracuje, držím stejné naměřené tempo při souběhu 50. Neměním tedy batch size ani nepředpokládám, že samotná GPU počítá desetkrát pomaleji.

U rezervace a vlastního serveru rozpočítávám pětileté náklady na všechnu práci za toto období a výsledek převádím na stejných 1 000 požadavků. Je to jednotková cena při daném využití, ne nákup serveru jen kvůli tisíci požadavkům.

| Využití zaplaceného času | API, 64 % vstupu cached | Rezervovaná VM | Modelový on-prem | PAYG VM včetně čekání |
|---|---:|---:|---:|---:|
| 100 % | 0,5714 | 0,3073 | 0,2567 | 0,8281 |
| 90 % | 0,5714 | 0,3415 | 0,2828 | 0,9201 |
| 60 % | 0,5714 | 0,5122 | 0,4133 | 1,3802 |
| 40 % | 0,5714 | 0,7683 | 0,6090 | 2,0703 |
| 20 % | 0,5714 | 1,5365 | 1,1962 | 4,1406 |
| 10 % | 0,5714 | 3,0731 | 2,3705 | 8,2812 |

Vše v USD. **Při plném využití vychází rezervace i on-prem levněji. Při 40 % už jsou obě varianty dražší než API.** Rezervace se vyrovná API při 53,78 %, modelový on-prem při 42,74 %.

Konkrétně: tisíc požadavků potřebuje přibližně **10,4 minuty produktivního běhu**. Při 100% využití za PAYG zaplatím asi **0,83 USD**. Při 10% využití je VM alokovaná přibližně **104 minut** a zaplatím asi **8,28 USD**. Start a načtení modelu by přidaly další placený čas, který tu ještě nezapočítávám.

**API stojí za stejné tokeny pořád stejně. Vlastní inference zdražuje, když platím čas, ve kterém nedělá užitečnou práci.** Rezervaci platím stále, vlastní server mám mimo práci zapnutý v idle a PAYG účtuje každou alokovanou hodinu.
:::
::: tab id="penize-soubeh" title="2. Souběh požadavků"
V tomto scénáři opět srovnávám cenu **1 000 stejných požadavků**, ale držím **100% využití v čase** a měním souběh. Zkoumám tím vliv batch size na cenovou výhodnost vlastní inference oproti API. Server má práci nepřetržitě; liší se, kolik požadavků obsluhuje najednou a jak rychle je celkově dokončí.

Lokální prefix cache zůstává zapnutá. U API pořád předpokládám, že **64 % vstupních tokenů dostane levnější sazbu za cached tokeny**.

| Souběh | API, 64 % vstupu cached | Rezervovaná VM | Modelový on-prem | PAYG VM |
|---|---:|---:|---:|---:|
| 1 | 0,5714 | 1,7005 | 1,4206 | 4,5826 |
| 5 | 0,5714 | 0,8563 | 0,7154 | 2,3076 |
| 10 | 0,5714 | 0,6329 | 0,5287 | 1,7056 |
| 20 | 0,5714 | 0,4258 | 0,3557 | 1,1473 |
| 50 | 0,5714 | 0,3073 | 0,2567 | 0,8281 |
| 100 | 0,5714 | 0,3197 | 0,2671 | 0,8616 |

Vše v USD za 1 000 požadavků při nepřetržité práci. **Z měřených bodů poprvé poráží API modelový on-prem při souběhu 10 a rezervovaná VM při souběhu 20. PAYG ho neporazí v žádném z nich.** Přesný bod rovnosti změřený nemám: u on-prem se pořadí obrací mezi souběhem 5 a 10, u rezervace mezi 10 a 20. Z těchto několika bodů nechci vymýšlet přesnou batch size.

**Nestačí tedy mít práci pořád. Potřebuju i dost práce najednou.** A stovka není ekonomicky lepší než padesát, protože už klesá naměřený throughput. Navíc při souběhu 50 čekám na první token 4,73 s, při souběhu 100 už 15,83 s.
:::
:::

Stručně: **vlastní inference potřebuje dost práce v čase i najednou.** Výsledek ovlivňuje i sleva za cached tokeny v API: čím levnější API díky ní je, tím víc práce potřebuju pro výhodný vlastní provoz.

Bez společného prefixu na obou stranách vychází při naměřeném souběhu 50 potřebné využití rezervace **56,18 %** a on-prem **44,73 %**. Podobná procenta, ale jiná kapacita a výrazně horší latence: první token až za 17,72 s.

::: reveal title="Jen dva dny za měsíc: má smysl zapnout PAYG virtuálku?"
Pokud VM zapnu na 48 hodin a celou dobu ji dokážu zásobovat prací při souběhu 50 se společným prefixem, stojí compute **229,20 USD**. API za stejnou práci při předpokládaných 64 % vstupu účtovaných jako cached stojí **158,15 USD**. Při polovičním využití uvnitř těchto 48 hodin udělám polovinu práce, ale za VM zaplatím pořád 229,20 USD; API vyjde jen na polovinu.

V našem scénáři tedy PAYG neporazí API ani při plném využití v žádném z měřených souběhů. Dealokace po dokončení dávky odstraní účet za zbytek měsíce, ne placené mezery během jejího zpracování. Start a načtení modelu také stojí čas a disky mohou stát peníze i po dealokaci.

Pokud porovnám jen obě VM sazby, PAYG přestává být levnější než rezervace při alokaci po více než **37,1 % kalendáře**. Tady rozhoduje placený čas, včetně čekání, ne jen produktivní práce. To je jiný break-even než VM proti API.
:::

::: reveal title="Stručně matematika"
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

Fixní část on-prem obsahuje pořízení, údržbu a idle energii. Aktivní hodina přidává rozdíl active−idle, ne znovu celou energii. Jednotková cena je celkový náklad dělený počtem požadavků. Nad dosažitelným break-even prahem vychází daná fixní varianta levněji; nad 100 % už je práh nesplnitelný.

Přibližně 54 % při c50 znamená kolem 90 hodin týdně práce při kapacitě tohoto bodu, ne 54 % na GPU monitoru. Pokud aplikace střídá různé souběhy, objem musím sčítat po těchto bodech. Nemůžu zprůměrovat concurrency a předpokládat lineární výkon.
:::

:::

::: card number="12" title="Co si z toho beru já"
Otevřené modely chci mít ve výběru. Kvůli kontrole, možnosti podržet verzi, vlastnímu chování i tomu, abych měl kam jít, když mi služba přestane vyhovovat. **Kvůli většině těchto výhod ale nepotřebuju kupovat server.**

A peníze? U tohoto modelu a workloadu mi při malém souběhu nebo nepravidelné práci vychází lépe levné API. Když mám dost souběžné práce po velkou část týdne, může vyjít vlastní inference. Pak bych porovnával především rezervovanou cloudovou VM s opravdu úplným on-prem rozpočtem, ne nákupní cenu karty s nekonečně běžícím PAYG.

Naše pracovní varianta s 64 % vstupu účtovaných API jako cached potřebuje při souběhu 50 zhruba **54 % času pro rezervaci a 43 % pro on-prem**. On-prem má přitom před rezervací modelový náskok jen asi 2,6 tisíce dolarů ročně na další rozdílové náklady. To už se provozním odhadem otočí docela snadno.

Za mě tedy nejdřív vybrat model, který práci zvládne. Potom říct, jakou kontrolu a odezvu potřebuju. A teprve nakonec se ptát, kdo bude provozovat GPU. **Neplatit marži poskytovateli je příjemná představa. Platit vlastní nevyužitý server už méně.**
:::

:::

::: closing
Otevřené váhy přináší mnoho výhod jako je míra kontroly, flexibilita, schopnost řešit nestandardní situace včetně politické nestability. Využívejte je přes API od důvěryhodného poskytovatele jako je Microsoft. Používat je na vlastním serveru myslím pro naprostou většinu případů nedává vůbec smysl - je to nesmyslně drahé.
:::
