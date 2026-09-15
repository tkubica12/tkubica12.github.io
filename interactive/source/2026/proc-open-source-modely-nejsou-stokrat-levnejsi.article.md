---
format_version: 1
title: "Proč open source modely nejsou stokrát levnější? Prozkoumejme Paretovu hranici."
eyebrow: "Cena modelů, inference a Paretova hranice"
subtitle: "Levnější token není levnější práce. Otevřené váhy nejsou GPU zdarma. A malý model není totéž co velký model bez marže. Pojďme si na jednom grafu ukázat, co má při výběru skutečně smysl porovnávat."
slug: proc-open-source-modely-nejsou-stokrat-levnejsi
date: 2026-09-15
language: cs-CZ
status: experimental
published: true
canonical_url: "/2026/proc-open-source-modely-nejsou-stokrat-levnejsi/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

„Tenhle open source model je stokrát levnější než Claude nebo GPT.“ Může to být pravda? Samozřejmě. Jen bych se hned zeptal: **než který model, při jakém nastavení a na jaké práci?**

V [minulém článku o otevřených modelech a vlastním hardwaru](/2026/vlastni-model-vlastni-server/) jsem odděloval dvě věci: jaký model si vyberu a kdo ho bude provozovat. Na měření jsme si ukázali, proč vlastní GPU dává smysl jen pokud pro něj máte opravdu hodně práce - větší batch size a 24x7. Dnes se chci vrátit k té první otázce. Je samotná otevřenost vah důvodem k dramaticky nižší ceně?

Zdá se, že nižší ano, ale dramaticky ne. Otevřeným modelům fandím, ale cenové srovnání potřebuje dva pohledy. **Kolik práce model zvládne a kolik mě ta práce stojí.** A přesně k tomu se hodí Paretova hranice.

Stejně jako minule budu přesnější než v titulku: mluvím hlavně o **open-weight modelech**, jejichž váhy si můžu stáhnout a za podmínek licence provozovat. Jejich protějškem jsou modely s uzavřenými vahami, ne „komerční modely“. Komerčně se totiž poskytují obě skupiny.

::: group id="paretova-hranice" title="Nejdřív obrázek: co je dobrá koupě?"

::: card number="01" title="Paretova hranice: lepší už jen za nějaký ústupek"
Pojďme se podívat na tenhle graf od Artificial Analysis.

![Graf Artificial Analysis z 15. září 2026: na vodorovné logaritmické ose je cena benchmarkové úlohy v USD, na svislé Intelligence Index. Tečkovaná Paretova hranice spojuje nedominované varianty; mezi levnými body je GPT-5.6 Luna a GLM-5.3-Flash, nejvyššího skóre dosahují GPT-6 Astra a Claude Fable 5.1.](../../images/2026/2026-09-15-paretova-hranice-modelu.png)

*Zdroj: Artificial Analysis, snímek z 15. 9. 2026. [Otevřít interaktivní graf s tímto výběrem modelů](https://artificialanalysis.ai/?models=gemini-3-5-flash-lite%2Cglm-5-3-flash%2Cgpt-6-astra%2Cclaude-fable-5-1%2Cgpt-5-6-luna%2Cmuse-glimmer%2Cdeepseek-v4-pro%2Cgemini-3-8-flash%2Cqwen3-8-2-4t-a95b%2Cmuse-spark-1-3%2Cqwen3-8-27b%2Cclaude-opus-5%2Cgpt-5-6-terra%2Cgrok-4-6%2Cclaude-fable-5%2Cglm-5-3%2Cgpt-5-6-sol%2Cdeepseek-v4-1-flash%2Cmistral-medium-3-5%2Ckimi-k3%2Cinkling%2Cclaude-fable-5-1-low%2Cclaude-sonnet-5-high%2Cclaude-4-5-haiku-reasoning%2Cgpt-6-astra-medium%2Cgpt-5-6-luna-medium%2Cgemini-3-1-pro-preview%2Cgemini-3-8-flash-medium%2Cqwen3-8-flash-next#intelligence-comparison-tabs). Můžete si přidat další modely i varianty nastavení. Živá data se budou měnit, komentář níže patří k obrázku.*

**Nahoru je lépe, doleva je levněji.** Na svislé ose je souhrnné skóre Intelligence Index, na vodorovné cena jedné benchmarkové úlohy. Ne cena milionu tokenů. Vodorovná osa je navíc logaritmická: posun z 0,1 na 1 dolar je stejný násobek jako z 1 na 10 dolarů. Vpravo tedy peníze přibývají rychleji, než by se mohlo zdát.

Tečkovaná čára ukazuje **Paretovu hranici**, anglicky *Pareto frontier*. Formálně hranici paretovsky optimálních řešení, prakticky množinu voleb, které někdo jiný jednoduše nepřebije.

Když najdu model, který je levnější a přitom má stejné nebo lepší výsledky, dražší model je v těchto dvou kritériích **slabší**. Totéž platí, když za stejnou cenu dostanu lepší výsledek. Alespoň v jednom kritériu se zlepším a v žádném si nepohorším.

Na hranici už taková jednoznačně lepší alternativa není. Chci vyšší kvalitu? Musím si připlatit. Chci nižší cenu? Musím něco slevit z kvality. **Neexistuje jeden vítěz pro všechny rozpočty a všechna zadání.**

To je důležitý rozdíl proti hledání jednoho „nejlepšího poměru cena/výkon“. Skóre 50 také neznamená dvojnásobnou užitečnost proti skóre 25. Nejprve si potřebuju říct, jakou kvalitu vůbec vyžaduju.

A ještě jedna věc: čára mezi body není nabídka modelu, který můžu koupit někde uprostřed. Ani mi nezaručuje, že smícháním dvou modelů dostanu bod na spojnici. Je to orientace v naměřených možnostech, ne fyzikální zákon.
:::

:::

::: group id="odkud-se-bere-cena" title="Proč otevřené váhy neznamenají inference zadarmo"

::: card number="02" title="Platím za provoz a za schopnost toho modelu"
V ceně API bych si pro začátek oddělil dvě ekonomické vrstvy.

První je **provozování modelu**. GPU, paměť, propojení, energie, datacentrum, software a lidé, kteří to drží v chodu. A také odměna poskytovateli, který to celé zajišťuje a nese riziko nevyužité kapacity. V tomhle je serving modelů docela klasický cloudový byznys.

Druhá je **vývoj modelu a hodnota jeho vah**. Někdo zaplatil výzkum, data, trénink a post-training. U uzavřeného modelu si přístup k výsledku kupuju od jeho vlastníka nebo partnera. U otevřeného modelu můžu mít právo váhy používat bez průběžné licenční platby, pokud mi to jeho licence dovoluje.

Neznamená to, že vývoj otevřeného modelu nic nestál. Znamená to, že ho nemusím platit stejným způsobem. **Otevřenost může odstranit licenční platbu za váhy. Neodstraní práci, kterou musí udělat hardware při používání modelu.**

Navíc tyhle dvě vrstvy na faktuře obvykle neuvidím odděleně. API cena není povinně „náklad na generování tokenů plus marže za váhy“. Ovlivňuje ji konkurence, kapacita, obchodní strategie nebo snaha získat zákazníky. Může být dočasně i pod náklady.

Právě v provozní vrstvě podle mě budou výnosy z rozsahu hrát zásadní roli. Velký provider má poptávku z více aplikací a časových pásem. Dokáže skládat požadavky do větších dávek, lépe využívat cache a rozpočítat specialisty na serving přes obrovský objem.

V minulém měření jsme se při přechodu z jednoho na padesát souběžných požadavků dostali s cache asi na **5,5násobek souhrnné kapacity**. Jeden požadavek ale trval déle. A vedle batch size potřebuju také využití v čase: ideálně práci, která se blíží nepřetržitému provozu, ne GPU čekající každý večer na ráno.

To neznamená, že vlastní inference musí běžet přesně 24×7, jinak se nikdy nevyplatí. Znamená to, že její ekonomiku určuje **množství užitečné práce při přijatelné latenci**.

Tyhle výhody přitom může využít poskytovatel otevřených i uzavřených modelů. **Když odstraním jeho marži, automaticky tím nezískám jeho provozní náklady.**
:::

::: card number="03" title="Malý model není velký model bez marže"
Tady podle mě vzniká velká část těch stonásobných úspor. Vezmu relativně malý otevřený model a porovnám ho s drahým frontier modelem. Rozdíl v ceníku může být obrovský. Jenže jsem nezměnil pouze licenci. Změnil jsem i to, co kupuju.

Pro pořádek jednotky: **B je miliarda, T je bilion**. Model 2T tedy má dva biliony parametrů.

| Ilustrativní velikost | Česky | Poměr počtu parametrů proti 3T |
|---|---|---:|
| 3B | 3 miliardy | 1 000× méně |
| 30B | 30 miliard | 100× méně |
| 300B | 300 miliard | 10× méně |
| 3T | 3 biliony | základ srovnání |

Tohle nejsou vymyšlené velikostní kategorie mimo realitu. [Kimi K3 má podle zveřejněné modelové karty 2,8T parametrů celkem a 104B aktivních na token](https://huggingface.co/moonshotai/Kimi-K3). U **Mixture of Experts** mají aktivní parametry velký vliv na compute nároky, všechny váhy se ale musejí někam vejít. A nejde jen o kapacitu paměti: zásadním limitem je i její propustnost při načítání potřebných vah a práci s cache. Neznamená to, že při každém tokenu načítám všechny experty.

To je také jeden z důvodů, proč na rozdíl od domácího použití dává ve velkém servingu smysl [disagregace prefill a decode](https://docs.nvidia.com/dynamo/v1.0.0/design-docs/disaggregated-serving). Zpracování vstupu bývá více omezené výpočtem, postupné generování zase pamětí a její propustností. Provider může každou fázi poslat na jinak nastavený hardware a škálovat je odděleně. Musí se mu ovšem vyplatit i přenos KV cache mezi nimi.

Ani míru **sparsity**, tedy jak malou část expertů aktivuju, nemůžu zvyšovat libovolně bez dopadu na schopnosti. [Experimenty s MoE a reasoningem](https://arxiv.org/html/2508.18672v3) ukazují, že více parametrů při vysoké sparsity pomáhá ukládání znalostí, ale uvažování potřebuje také dost aktivního výpočtu a trénovacích dat na parametr. Co je efektivní pro znalosti, tedy nemusí být efektivní pro reasoning. Není to univerzální optimální poměr pro každý model, ale dobrý důvod, proč nestačí donekonečna přidávat neaktivní experty.

Od jednotek miliard k jednotkám bilionů jsme přibližně na třech řádech. Velikost ovšem není přesný ceník ani automatická známka kvality. Záleží na architektuře, tréninku, kvantizaci i konkrétní úloze. Menší specializovaný model může být na mém zadání lepší než větší obecný.

Nemůžu tedy vzít stonásobek parametrů a prohlásit ho za stonásobek ceny inference. Ale pořád porovnávám výrazně odlišné hardwarové a schopnostní třídy, ne stejný výrobek s odlepenou cenovkou za licenci.

::: reveal title="A co z toho opravdu poběží v notebooku?"
Čistě na uložení vah potřebuje 30B model ve čtyřbitové reprezentaci přibližně **15 GB**, ve dvoubajtové BF16 asi **60 GB**. Bez KV cache, aktivací, kvantizačních metadat a režie runtime. U 3B je to desetina, u 3T stonásobek.

Jednotky B se proto mohou vejít i do menších zařízení, desítky B už chtějí podstatně víc paměti. Není ale pravda, že jedinou cestou je notebook s velkou dedikovanou grafikou. Pomoci může velká sjednocená paměť nebo offload do RAM; otázkou zůstává rychlost, délka kontextu a baterie.

**„Vejde se mi to tam“ a „chci s tím pracovat“ jsou dvě různá kritéria.** A ani jedno samo neříká, jestli ten model zvládne úlohy, které běžně dávám frontier coding agentovi.
:::

Levný malý model může být skvělá volba. Jen k tomu nepotřebuje otevřené váhy. Existují i levné modely s uzavřenými vahami — přesně ty si do cenového srovnání nesmím zapomenout přidat.
:::

::: card number="04" title="Technologický náskok může část výhody otevřených vah vyrovnat"
V úplné špičce grafu jsou na tomto snímku uzavřené modely Astra a Fable. O kus níž už se pohybují velmi schopné otevřené modely jako GLM-5.3 a Kimi K3.

Moje pracovní hypotéza je, že tým na technologické špičce může část náskoku proměnit také v efektivitu: dosáhnout určité kvality s menším výpočtem, kratším reasoningem nebo lépe optimalizovaným servingem. Pak může uzavřený model potřebovat na srovnatelnou práci méně hardwaru, ale současně mi účtovat víc za přístup k vahám.

O jakých maržích se vůbec bavíme? V [mediálních odhadech pro rok 2025](https://techcrunch.com/2025/11/04/anthropic-expects-b2b-demand-to-boost-revenue-to-70b-in-2028-report/) se u předního poskytovatele modelů objevovalo kolem **50 % hrubé marže**. [Zářijové zprávy z roku 2026](https://money.usnews.com/investing/news/articles/2026-09-13/anthropic-tells-investors-it-will-be-profitable-for-second-straight-quarter-ft-reports) už mluví o více než **80 %**, ovšem před podíly distribučních partnerů a náklady na trénink. Beru je jako řádové odhady, ne auditovanou časovou řadu jednoho API; zářijovou zprávu navíc Reuters nezávisle neověřil.

U cloudu zase pro orientaci vidíme třeba [za rok 2025 tržby AWS 128,7 miliardy USD a provozní zisk 45,6 miliardy](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Fourth-Quarter-Results/default.aspx), tedy provozní marži asi **35 %**. To ale není hrubá marže na pronájmu jedné GPU. Tato různě definovaná procenta nemůžu jednoduše odečíst a rozdíl prohlásit za cenu vah.

Pro řádovou kalkulačku proto vezmu **50 nebo 80 % jako celkovou modelovou marži uzavřené služby**, zahrnující odměnu za serving i modelovou prémii. U otevřené varianty nechám **30 % za serving**. Není to rekonstrukce účetnictví konkrétní firmy: pokud nakupuje compute od cloudu, část infrastrukturní marže už může být zahrnutá v jejích nákladech. Tady obě varianty počítám od stejné nákladové základny a nic nepřičítám dvakrát.

Přímý náklad na inferenci stejné práce bude u uzavřeného modelu **100 jednotek**. Otevřená alternativa bude v našem příkladu o **15 % nákladnější**, tedy 115. Třicetiprocentní marže poskytovatele znamená, že náklad tvoří 70 % prodejní ceny: otevřené API proto stojí **164,29 jednotky**, ne 149,50 jako při pouhé 30% přirážce.

| Celková modelová marže uzavřené služby | Cena uzavřené služby | Cena otevřené služby s 30% serving marží | Kolikrát je uzavřená varianta dražší |
|---|---:|---:|---:|
| 50 % | 200 | 164,29 | 1,22× |
| 80 % | 500 | 164,29 | 3,04× |

Jak v tom modelově oddělím ty dvě složky? Při přímém nákladu 100 by samotný serving s 30% marží stál **142,86**: sto za inferenci, 42,86 jako odměna provozovateli. Do konečných 200 pak zbývá **57,14** jako modelová prémie; do 500 zbývá **357,14**. To není čistý zisk za váhy, financuje se z toho i vývoj, trénink a další náklady.

Patnáctiprocentní rozdíl v efektivitě i třicetiprocentní serving marže zůstávají **předpoklady příkladu**, ne měřením konkrétního endpointu. Kdyby byly obě varianty provozně stejně efektivní, vyjde poměr cen **1,4× až 3,5×**. S naším rozdílem efektivity přibližně **1,2× až 3×**. Pro firmu to může být zajímavá úspora, ale řádově jsme pořád úplně jinde než u **100×**.
:::

::: card number="05" title="Levnější token ještě neznamená levnější odpověď"
Když modely porovnávám přes API, nestačí mi cena za milion tokenů. Potřebuju vědět, kolik jich spotřebují na stejnou práci. Včetně reasoningu, vstupu, opakovaného kontextu a případných dalších pokusů.

Úplně jednoduchý příklad: jeden model má výstupní tokeny za polovinu, ale potřebuje jich třikrát tolik. **Jen jeho výstup mě pak stojí o polovinu víc.** Vstup a cache zatím nechávám stranou.

U Kimi K3 to není jen akademická otázka. V údajích Artificial Analysis dostupných při přípravě článku má [Kimi K3 v nastavení max](https://artificialanalysis.ai/models/kimi-k3) přibližně **160 milionů výstupních tokenů** za běh Intelligence Indexu, zatímco [GPT-5.6 Sol v nastavení max](https://artificialanalysis.ai/models/gpt-5-6-sol) asi **90 milionů**. Kimi má přitom v uvedeném ceníku output za 15 USD za milion, Sol za 20 USD. Levnější token, ale větší spotřeba; vážená cena benchmarkové úlohy vychází u obou přibližně na dva dolary.

Proti [Opusu 5 v nastavení max](https://artificialanalysis.ai/models/claude-opus-5), který má uvedeno asi 140 milionů výstupních tokenů, je ale rozdíl ve spotřebě mnohem menší. Neřekl bych tedy obecně, že Kimi potřebuje násobně víc tokenů než všechny uzavřené modely. **Záleží, proti čemu a v jakém nastavení ho měřím.**

Ani z těchto souhrnných tokenových počtů nelze prostým dělením dopočítat vodorovnou osu grafu. [Cost per Intelligence Index Task](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index) je vážený průměr nákladů jednotlivých evaluací na úlohu. Zohledňuje jejich váhy v indexu a příslušné účtované tokeny — vstup, cache, reasoning a odpověď.

Proto se mi ten graf líbí víc než samotný ceník. Pořád ale ukazuje **cenu benchmarkové úlohy, ne cenu úspěšně vyřešeného firemního případu**. Kvalita je na druhé ose. Když mi levný agent úlohu pokazí, jeho tokeny se sice hezky účtují, ale já práci pořád nemám hotovou.

A při vlastním hostování musím API cenu nahradit svým úplným provozním nákladem. Tenhle obrázek sám o sobě neříká, kolik by mě Kimi stálo na mém clusteru.
:::

:::

::: group id="jak-to-pouzivat" title="Zpátky ke grafu: co z něj plyne pro výběr"

::: card number="06" title="Na Paretově hranici je mix dodavatelů otevřených i proprietárních modelů"
Když se vrátím k obrázku, vidím tři důležité věci.

**Úplný vrchol schopností není automaticky dostupný v otevřené variantě.** Astra a Fable jsou nahoře kolem skóre 53. GLM-5.3 a Kimi K3 kolem 44–45, Sol kolem 47 a Opus 5 kolem 51. To neznamená, že otevřený model nemůže některou konkrétní úlohu zvládnout stejně dobře nebo lépe, ale pro tento benchmark to vychází takhle. Váš use case samozřejmě může být jiný - nicméně nečekám propastně jiné výsledky.

**O kus níž otevřené modely skutečně konkurují, ale nevidím automatickou stonásobnou slevu.** Kimi K3, GLM-5.3 a Sol se tu všechny pohybují přibližně kolem dvou dolarů za úlohu. Opus stojí kolem šesti, ale má také vyšší skóre. Když zvolím Kimi místo Opusu, může to být správné rozhodnutí. Jen je to v tomhle grafu obchod mezi cenou a kvalitou, ne důkaz stejného výsledku třikrát levněji.

**Levný konec trhu není vyhrazený otevřeným modelům.** GPT-5.6 Luna v nastavení medium leží úplně vlevo, přibližně na 0,016 USD za úlohu. To je proti Solu více než stonásobný cenový rozdíl — uvnitř nabídky jednoho výrobce uzavřených modelů. Jenže Luna tu má skóre kolem 25,5, nikoli Solových 47. A otevřený GLM-5.3-Flash je naopak zajímavý bod hranice kolem 0,25 USD a skóre 42. Pozor, Flash není stejná varianta jako GLM-5.3 max z předchozího odstavce.

Zajímavé je, jak si vedou někteří výrobci (ke dni, kdy jsem tento článek napsal). **OpenAI** má velmi vyrovnané portfolio od malých (Luna, Terra) až po velké velmi schopné modely (Sol, Astra). **Anthropic** umí excelovat v high-end spektru, ale jeho cenově dostupnější varianty dnes na Paretovu hranici nemají (Haiku je úplně mimo, Sonnet nic moc, Opus rovněž ztrácí cenově optimální dech). **Google** je dnes ve stavu, kdy je high-end v podobě Gemini Pro mimo hru, ale střední třída s Gemini 3.8 Flash je na Paretově hranici, zatímco nižší třída s 3.5 Flash-Lite je aktuálně mimo hru.

Za mě přesně tohle rozbíjí zkratku „otevřené rovná se levné, uzavřené rovná se drahé“. Na zajímavých místech jsou obě skupiny. Některé jiné modely mají ve sledované dvojici kritérií alternativu, která je levnější i schopnější, bez ohledu na licenci.
:::

::: card number="07" title="Nakonec potřebuju vlastní Paretovu hranici"
Tenhle graf bych používal jako výborný začátek výběru, ne jako jeho konec. Intelligence Index skládá různé typy úloh a jejich váhy. Moje aplikace ale může celý den dělat jednu věc, na kterou je menší model výborný.

Začal bych vlastními příklady a jasnou laťkou: co musí model zvládnout a co už je chyba. Pak bych porovnal několik levných i silnějších modelů, otevřených i uzavřených, včetně rozumných nastavení reasoningu. Vedle výsledků bych měřil **celý účet za hotovou práci**: všechny pokusy, nástroje, případný fallback a opravy člověkem.

Tohle znovu ukazuje, proč jsou do budoucna tak důležité **vlastní evaluations sady a vlastní trénovací prostředí (RLE)**, tak jak jsem o tom už [psal v článku o evals jako nejcennějším aktivu](https://tomaskubica.cz/2026/evals-nejcennejsi-aktivum/).
:::

:::

::: closing
Největší cenový rozdíl není mezi otevřeným a uzavřeným modelem, ale mezi modelem **tak akorát pro moji úlohu** a modelem, který je na ni moc hloupý (a levný) nebo zbytečně chytrý (a drahý).
:::
