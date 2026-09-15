# Proč open source modely nejsou stokrát levnější? Prozkoumejme Paretovu hranici.

META
- Datum: 2026-09-15. Jazyk: cs-CZ. Publikováno.
- URL: `/2026/proc-open-source-modely-nejsou-stokrat-levnejsi/`.
- Plný zdroj: `source.md`; canonical source `interactive/source/2026/proc-open-source-modely-nejsou-stokrat-levnejsi.article.md`.
- Navazuje: [otevřené modely a vlastní hardware](/2026/vlastni-model-vlastni-server/). Minule výběr modelu vs. způsob provozu; nyní cena vs. kvalita mezi modely.
- Teze: otevřené váhy podle autora zřejmě znamenají nižší cenu, ale ne dramaticky. Stonásobnou úsporu sama otevřenost nedokazuje; porovnávat stejnou práci, kvalitu, celé náklady.
- Přesný pojem: open weights, ne nutně plně open source. Otevřené i uzavřené modely mohou být komerčně poskytované.

## 01 Paretova hranice
- Obrázek: `../../images/2026/2026-09-15-paretova-hranice-modelu.png`; Artificial Analysis, snapshot 15. 9. 2026. Číselný komentář patří ke snímku, ne k budoucím živým datům.
- [Interaktivní graf se stejným výběrem](https://artificialanalysis.ai/?models=gemini-3-5-flash-lite%2Cglm-5-3-flash%2Cgpt-6-astra%2Cclaude-fable-5-1%2Cgpt-5-6-luna%2Cmuse-glimmer%2Cdeepseek-v4-pro%2Cgemini-3-8-flash%2Cqwen3-8-2-4t-a95b%2Cmuse-spark-1-3%2Cqwen3-8-27b%2Cclaude-opus-5%2Cgpt-5-6-terra%2Cgrok-4-6%2Cclaude-fable-5%2Cglm-5-3%2Cgpt-5-6-sol%2Cdeepseek-v4-1-flash%2Cmistral-medium-3-5%2Ckimi-k3%2Cinkling%2Cclaude-fable-5-1-low%2Cclaude-sonnet-5-high%2Cclaude-4-5-haiku-reasoning%2Cgpt-6-astra-medium%2Cgpt-5-6-luna-medium%2Cgemini-3-1-pro-preview%2Cgemini-3-8-flash-medium%2Cqwen3-8-flash-next#intelligence-comparison-tabs). Lze přidat modely a nastavení.
- Osa Y: Intelligence Index, výš lépe. Osa X: USD za benchmarkovou úlohu, doleva levněji; nikoli cena milionu tokenů.
- X logaritmická: 0,1→1 USD stejný násobek/posun jako 1→10 USD.
- Paretova hranice / Pareto frontier: nedominované volby ve sledovaných kritériích. Dominance = alternativa alespoň stejně dobrá v obou a přísně lepší alespoň v jednom; levnější při stejné/vyšší kvalitě nebo lepší při stejné ceně.
- Na hranici zlepšení jednoho kritéria vyžaduje ústupek v druhém. Žádný univerzální vítěz všech rozpočtů.
- Nejde o jedno maximum poměru cena/výkon. Skóre 50 neznamená 2× užitečnost skóre 25; nutná požadovaná laťka kvality.
- Spojnice bodů není dostupný model ani zaručený výsledek směsi modelů. Orientace v naměřených konfiguracích, ne fyzikální zákon.

## 02 Dvě ekonomické vrstvy ceny
- Provoz: GPU, paměť, propojení, energie, datacentrum, serving software, lidé. Odměna provozovateli + riziko nevyužité kapacity. Klasická cloudová ekonomika.
- Váhy: výzkum, data, trénink, post-training a hodnota výsledku. Uzavřený model: platba vlastníkovi/partnerovi za přístup. Open weights: možnost provozu bez průběžné licence, pokud licence dovoluje.
- Otevřený vývoj není zdarma; financování nemusí probíhat stejně. Otevřenost může odstranit platbu za váhy, nikoli práci hardwaru při používání modelu.
- API faktura vrstvy nerozděluje. Cena není povinně „náklad na generování tokenů plus marže za váhy“: konkurence, kapacita, strategie, získávání zákazníků; dočasně i pod náklady.
- Výnosy z rozsahu: více aplikací a časových pásem, společná kapacita, batching, cache, specialisté rozpočítaní na velký objem. Dost práce současně i v čase.
- Předchozí měření s cache: souběh 1→50 přinesl asi 5,5× souhrnnou kapacitu; jednotlivý požadavek pomalejší.
- Blízkost provozu 24×7 pomáhá; přesně nepřetržitý provoz není univerzální podmínkou návratnosti. Rozhoduje užitečná práce při přijatelné latenci.
- Výnosy z rozsahu dostupné poskytovatelům obou typů vah. Odstranění jejich marže neznamená získání jejich nižších provozních nákladů.

## 03 Malý model není velký bez marže
- Srovnání malého otevřeného modelu s drahým frontier modelem mění více než licenci: hardware, schopnosti, nastavení.
- B = miliarda; T = bilion. 2T = dva biliony.
- Ilustrativní celkové parametry proti 3T: 3B = 1 000× méně; 30B = 100× méně; 300B = 10× méně; 3T základ.
- [Kimi K3 model card](https://huggingface.co/moonshotai/Kimi-K3): 2,8T celkem, 104B aktivních/token.
- Jednotky B→jednotky T asi 3 řády.
- Parametry nejsou přesný ceník ani automatická kvalita. Architektura, trénink, kvantizace, workload; specializovaný menší model může na své úloze zvítězit.
- MoE: aktivní parametry ovlivňují compute, všechny váhy se musejí někam vejít. Paměťová propustnost další limit při načítání potřebných vah a práci s cache; ne všechny experty číst při každém tokenu.
- [Disagregace prefill/decode](https://docs.nvidia.com/dynamo/v1.0.0/design-docs/disaggregated-serving): prefill často compute-bound, decode memory/bandwidth-bound; ve velkém servingu jiné nastavení hardwaru a nezávislé škálování, oproti domácímu použití. Nutno zaplatit přenos KV cache.
- [MoE sparsity experimenty](https://arxiv.org/html/2508.18672v3): více parametrů při vysoké sparsity pomáhá znalostem; reasoning potřebuje aktivní výpočet a trénovací data/parametr. Sparsity nelze zvyšovat libovolně bez dopadu; nejde o univerzální optimální poměr všech modelů.
- 100× parametrů NEZARUČUJE 100× inference náklady; stále však rozdílné hardwarové/schopnostní třídy.
- Jen váhy 30B: asi 15 GB při 4 bitech nebo 60 GB BF16. Bez KV cache, aktivací, kvantizačních metadat, runtime. 3B desetina; 3T stonásobek.
- Jednotky B se mohou vejít do menších zařízení; desítky B potřebují více paměti. Dedikovaná GPU není jediná cesta: sjednocená paměť či RAM offload; tradeoff rychlost, kontext, baterie.
- Vejít se ≠ příjemně fungovat ≠ zvládnout frontier coding workload. Levné menší uzavřené modely patří do srovnání také.

## 04 Efektivita versus platba za váhy
- Hypotéza autora: technologický náskok může umožnit stejnou kvalitu s menším výpočtem, kratším reasoningem či lepším servingem. Pak nižší provozní náklad může kompenzovat část poplatku za uzavřené váhy.
- [Mediální odhady pro 2025](https://techcrunch.com/2025/11/04/anthropic-expects-b2b-demand-to-boost-revenue-to-70b-in-2028-report/): u předního poskytovatele kolem 50 % hrubé marže. [Zářijový report 2026](https://money.usnews.com/investing/news/articles/2026-09-13/anthropic-tells-investors-it-will-be-profitable-for-second-straight-quarter-ft-reports): přes 80 %, před podíly distribučních partnerů a tréninkem; Reuters tento report nezávisle neověřil. Řádové odhady, ne auditovaná časová řada jednoho API.
- [AWS FY2025](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Fourth-Quarter-Results/default.aspx): tržby 128,7 mld. USD, operating income 45,6 mld.; provozní marže asi 35 %. Není hrubá marže pronájmu GPU; nelze prostě odečíst od hrubé marže API a určit cenu vah.
- Řádový model: celková marže uzavřené služby 50/80 % zahrnuje serving i modelovou prémii; otevřené API 30 % za serving. Jednotná nákladová základna, ne účetní rekonstrukce konkrétní firmy. Při externím cloudu může být jeho marže již uvnitř nakupovaného compute; nezapočítat dvakrát.
- Přímé inference náklady stejné práce: uzavřený model 100 jednotek, open o 15 % dražší = 115. Open cena při 30% marži = 115/0,7 = 164,29; nikoli 149,50 při 30% přirážce.

| Celková modelová marže uzavřené služby | Uzavřená cena | Otevřená cena s 30% serving marží | Poměr uzavřená/otevřená |
|---|---:|---:|---:|
| 50 % | 200 | 164,29 | 1,22× |
| 80 % | 500 | 164,29 | 3,04× |

- Rozklad uzavřené služby: při nákladu 100 samotný serving s 30% marží stojí 142,86 = 100 inference + 42,86 odměna provozovateli. Zbytek modelová prémie: 57,14 do ceny 200; 357,14 do ceny 500. Ne čistý zisk vah: financuje vývoj, trénink, další náklady.
- 15% rozdíl efektivity i 30% serving marže jsou předpoklady, ne endpointové měření. Při stejné efektivitě obou variant poměr 1,4×–3,5×; při open nákladu vyšším o 15 % asi 1,2×–3×. Ne 100×.

## 05 Token versus hotová práce
- Účet: počet a ceny tokenů vstupu, cache, reasoningu, odpovědi; další pokusy/kontext. Poloviční output sazba při 3× output tokenech = o 50 % dražší výstup, ještě bez vstupu/cache.
- AA údaje při přípravě; nastavení max:
  - [Kimi K3](https://artificialanalysis.ai/models/kimi-k3): asi 160M output tokenů za Intelligence Index; output 15 USD/M.
  - [GPT-5.6 Sol](https://artificialanalysis.ai/models/gpt-5-6-sol): asi 90M; output 20 USD/M.
  - Oba kolem 2 USD za váženou benchmarkovou úlohu. Kimi levnější token, vyšší spotřeba.
  - [Opus 5](https://artificialanalysis.ai/models/claude-opus-5): asi 140M output; rozdíl spotřeby proti Kimi menší. Nezobecňovat násobně vyšší Kimi spotřebu proti všem uzavřeným modelům.
- [Metodika metriky](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index): vážený průměr nákladů evaluací/úlohu podle jejich vah v indexu; input, cache, reasoning, answer ceny. Nelze prostě přepočítat osu z celkových output tokenů.
- Cena benchmarkového pokusu ≠ cena úspěšně vyřešeného firemního případu; kvalita druhá osa. Chybné řešení stojí tokeny bez hotové práce.
- API graf neříká cenu self-hostingu; tam dosadit úplný vlastní provozní náklad.

## 06 Co ukazuje snímek
- Na Paretově hranici mix dodavatelů otevřených/proprietárních modelů. Vrchol Astra/Fable kolem indexu 53; GLM-5.3/Kimi 44–45; Sol 47; Opus 51. Otevřený model může konkrétní úlohu zvládnout stejně či lépe; benchmark vychází takto. Autor nečeká propastně jiné výsledky, vlastní use case se může lišit.
- Kimi, GLM-5.3, Sol kolem 2 USD/úlohu. Opus kolem 6 USD při vyšším skóre; volba Kimi může být rozumný tradeoff, nikoli důkaz totožného výsledku 3× levněji.
- Luna medium asi 0,016 USD/úlohu a index 25,5: proti Solu přes 100× cenový rozdíl uvnitř stejného výrobce uzavřených modelů, ale nižší kvalita.
- GLM-5.3-Flash zajímavý open bod hranice kolem 0,25 USD a indexu 42. Není GLM-5.3 max.
- Autorovo hodnocení ke dni článku: **OpenAI** vyrovnané portfolio od malých Luna/Terra po velké Sol/Astra. **Anthropic** exceluje v high-endu; dostupnější varianty mimo hranici (Haiku úplně mimo, Sonnet nic moc, Opus ztrácí cenovou optimalitu). **Google**: high-end Gemini Pro mimo hru, střední Gemini 3.8 Flash na hranici, nižší 3.5 Flash-Lite mimo.
- Na zajímavých místech oba typy vah; jiné modely dominované bez ohledu na licenci.

## 07 Vlastní hranice
- AA je shortlist, ne poslední rozhodnutí. Vlastní úlohy a kvalitativní laťka; porovnat levné/silné, open/closed, různé rozumné effort varianty.
- Měřit celou hotovou práci: všechny pokusy, nástroje, fallback, lidské opravy.
- Vlastní evaluations sady a trénovací prostředí (RLE) důležité do budoucna; navazuje na [evals jako nejcennější aktivum](https://tomaskubica.cz/2026/evals-nejcennejsi-aktivum/).
- Verdikt: největší cenový rozdíl není otevřený/uzavřený model; hledat model **tak akorát pro moji úlohu**, ne příliš hloupý (levný) ani zbytečně chytrý (drahý).
