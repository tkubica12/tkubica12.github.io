---
layout: post
published: true
title: Jak na jednoduchou AI analýzu textu? Mám použít LLM, finetuning, vlastní model nebo hrátky nad embeddingy? A za kolik to všechno?
tags:
- AI
---
Před desetilety byl svět AI práce s jazykem (Natural Language Processing, NLP) zaměřený na z dnešního pohledu jednoduché úlohy, pro které se ale vytvářel specializovaný a výpočetně (a tedy i nákladově) nenáročný model. Dnešní svět velkých jazykových modelů (LLM) a jeho schopnost následovat vaše instrukce může dokázat totéž bez trénování vlastních modelů nebo extenzivních znalostí. Pojďme na příkladu analýzy sentimentu textu prozkoumat, jaké možnosti máme, jaké jsou jejich výhody a nevýhody a kolik to všechno stojí.

# Varianty řešení úlohy detekce sentimentu
Potřebujeme model, který vezme krátký příspěvek ze sociální sítě a roztřídí ho na tři kategorie: pozitivní, negativní a neutrální. Jak to můžeme udělat? Vyzkoušejme, změřme a propočítejme čtyři varianty:
- Velký jazykový model (LLM) v různých variantách zero-shot a few-shot (resp. řekněme spíše model střední, ať je to cenově srovnatelné s dalšími variantami)
- Fine-tuning velkého jazykového modelu (LLM) na konkrétní úlohu
- Dotrénovaní klasičtějšího transformer encoder modelu (tedy "ne-generativní" model)
- Použití embeddingů jako formy pre-trainingu a vystavení vlastní primitivní klasifikace nad tím

Podívejme se na pár tabulek s výsledky a pak si vysvětlíme každý scénář a jeho výhody a nevýhody. Přesnost se vám může zdát poměrně malá, ale je to hodně tím, že rozdíl mezi pozitivním a neutrálním sentimentem je často těžké určit. Každopádně, používat budeme datovou sadu s 25k lidmi otagovanými trénovacími příklady a 6k a 5k na test a validaci.

Všechny detaily včetně kódu na testování a trénování najdete na mém [GitHubu](https://github.com/tkubica12/d-ai-sentiment/tree/main).

## Úspěšnost klasifikace
| Experiment | Model/Approach | Strategy | Accuracy | Completed Predictions | Failed Predictions | Total Tokens | Input Tokens | Output Tokens | Estimated Cost | Execution Time | Samples/sec |
|------------|---------------|----------|----------|---------------------|-------------------|--------------|--------------|---------------|----------------|----------------|-------------|
| **LLM Approaches** |
| LLM_NANO_ZEROSHOT | GPT-4.1-nano | Zero-shot | 67.7% | 5,166 (99.3%) | 39 (0.7%) | 1,289,946 | 1,284,780 | 5,166 | $0.13 | 3,306.7s | 1.56 |
| LLM_NANO_FEWSHOT_100 | GPT-4.1-nano | Few-shot (100) | 68.6% | 5,165 (99.2%) | 40 (0.8%) | 14,470,776 | 14,465,611 | 5,165 | $1.45 (~$0.87 cached) | 4,215.4s | 1.23 |
| LLM_NANO_FEWSHOT_1000 | GPT-4.1-nano | Few-shot (1000) | 68.4% | 5,166 (99.3%) | 39 (0.7%) | 133,890,834 | 133,885,668 | 5,166 | $13.39 (~$8.03 cached) | 9,160.4s | 0.56 |
| LLM_MINI_ZEROSHOT | GPT-4.1-mini | Zero-shot | 69.3% | 5,076 (97.5%) | 129 (2.5%) | 1,351,565 | 1,346,144 | 5,421 | $0.55 | 3,919.9s | 1.38 |
| LLM_MINI_FEWSHOT_100 | GPT-4.1-mini | Few-shot (100) | 69.4% | 5,140 (98.8%) | 65 (1.2%) | 14,688,863 | 14,683,620 | 5,243 | $5.88 (~$3.53 cached) | 5,565.6s | 0.94 |
| LLM_MINI_FEWSHOT_1000 | GPT-4.1-mini | Few-shot (1000) | 68.4% | 5,088 (97.8%) | 117 (2.2%) | 138,814,519 | 138,809,163 | 5,356 | $55.53 (~$33.32 cached) | 16,084.1s | 0.33 |
| **Fine-tuned LLM Approaches** |
| LLM_FT_NANO_ZEROSHOT | GPT-4.1-nano (Fine-tuned) | Zero-shot | 79.0% | 5,166 (99.3%) | 39 (0.7%) | 1,289,946 | 1,284,780 | 5,166 | $0.26 | 1,907.0s | 2.71 |
| LLM_FT_NANO_FEWSHOT_100 | GPT-4.1-nano (Fine-tuned) | Few-shot (100) | 78.4% | 5,166 (99.3%) | 39 (0.7%) | 14,473,578 | 14,468,412 | 5,166 | $2.90 (~$1.74 cached) | 1,940.0s | 2.66 |
| LLM_FT_MINI_ZEROSHOT | GPT-4.1-mini (Fine-tuned) | Zero-shot | 80.0% | 5,166 (99.3%) | 39 (0.7%) | 1,289,946 | 1,284,780 | 5,166 | $1.04 | 1,564.2s | 3.30 |
| LLM_FT_MINI_FEWSHOT_100 | GPT-4.1-mini (Fine-tuned) | Few-shot (100) | 79.3% | 5,165 (99.2%) | 40 (0.8%) | 14,470,685 | 14,465,520 | 5,165 | $11.58 (~$6.95 cached) | 1,918.4s | 2.69 |
| **Embedding + ML Approaches** |
| LR_100 | OpenAI Embeddings + LR | Trained on 100 samples | 60.9% | 5,205 (100%) | 0 (0%) | 124,123 | 124,123 | 0 | $0.0025 | 963.2s | 5.40 |
| LR_1000 | OpenAI Embeddings + LR | Trained on 1000 samples | 67.1% | 5,205 (100%) | 0 (0%) | 124,123 | 124,123 | 0 | $0.0025 | 951.7s | 5.47 |
| LR_ALL | OpenAI Embeddings + LR | Trained on full dataset | 73.2% | 5,205 (100%) | 0 (0%) | 124,123 | 124,123 | 0 | $0.0025 | 932.1s | 5.58 |
| **Fine-tuned Transformer Approaches** |
| BERT_SENTIMENT | BERT-base Fine-tuned | Trained on full dataset | 74.5% | 5,205 (100%) | 0 (0%) | N/A | N/A | N/A | $0.028 | 465.4s | 11.19 |

## Náklady na klasifikaci
| Experiment | Cost per 1K Samples | Cost Efficiency Rank |
|------------|-------------------|---------------------|
| **Most Cost-Effective** |
| LR_100 | $0.0005 | 1st (Best) |
| LR_1000 | $0.0005 | 1st (Best) |
| LR_ALL | $0.0005 | 1st (Best) |
| LLM_NANO_ZEROSHOT | $0.025 | 4th |
| BERT_SENTIMENT | $0.028 | 5th |
| LLM_FT_NANO_ZEROSHOT | $0.050 | 6th |
| LLM_MINI_ZEROSHOT | $0.106 | 7th |
| LLM_FT_MINI_ZEROSHOT | $0.202 | 8th |
| **Moderate Cost** |
| LLM_NANO_FEWSHOT_100 | $0.280 ($0.168 cached) | 9th |
| LLM_FT_NANO_FEWSHOT_100 | $0.562 ($0.337 cached) | 10th |
| LLM_MINI_FEWSHOT_100 | $1.130 ($0.678 cached) | 11th |
| LLM_FT_MINI_FEWSHOT_100 | $2.242 ($1.345 cached) | 12th |
| **High Cost** |
| LLM_NANO_FEWSHOT_1000 | $2.590 ($1.554 cached) | 13th |
| LLM_MINI_FEWSHOT_1000 | $10.670 ($6.402 cached) | 14th (Most Expensive) |

## Latence
| Experiment | Processing Speed Rank | Time per Sample (seconds) |
|------------|---------------------|---------------------------|
| **Fastest Processing** |
| BERT_SENTIMENT | 1st (Fastest) | 0.09 |
| LR_ALL | 2nd | 0.18 |
| LR_1000 | 3rd | 0.18 |
| LR_100 | 4th | 0.19 |
| **Moderate Speed** |
| LLM_FT_MINI_ZEROSHOT | 5th | 0.30 |
| LLM_FT_MINI_FEWSHOT_100 | 6th | 0.37 |
| LLM_FT_NANO_ZEROSHOT | 7th | 0.37 |
| LLM_FT_NANO_FEWSHOT_100 | 8th | 0.38 |
| LLM_NANO_ZEROSHOT | 9th | 0.64 |
| LLM_MINI_ZEROSHOT | 10th | 0.72 |
| LLM_NANO_FEWSHOT_100 | 11th | 0.81 |
| LLM_MINI_FEWSHOT_100 | 12th | 1.06 |
| **Slower Processing** |
| LLM_NANO_FEWSHOT_1000 | 13th | 1.77 |
| LLM_MINI_FEWSHOT_1000 | 14th (Slowest) | 3.00 |

# 1. Velký jazykový model (LLM)
LLM dokáže následovat naše instrukce, takže bez nějakého trénování mu můžeme jednoduše říct, co má dělat - v tomto případě provést klasifikaci. Použití modelu gpt-4.1 na něco takového by nebylo cenově srovnatelné s ostatními variantami, zaměřím se tedy na varianty mini a nano tohoto modelu. Prompt donutí model vrátit jeden jediný výstupní token - číslo 0, 1 nebo 2 představující vybranou třídu. Veškeré zpracování se tedy vtiskne do jediného výstupního tokenu (samozřejmě, pokud bychom model nechali dělat Chain of Thoughts a spotřebovat třeba 500 tokenů tím, že vysvětlí jak k tomu došel, výsledky budou jistě přesnější, ale násobně dražší). Z cenového hlediska tedy tohle bude hlavně o vstupních tokenech a proto budou tři varianty:
- (skoro) zero-shot, kdy model dostane prompt a jeden pidipříklad za každou třídu
- few-shot se 100 příklady
- few-shot s 1000 příklady

## Kvalita
Kvalita je u všech variant ve výsledku velmi podobná. Je vidět, že mini model je lepší, než nano, ale rozdíl není dramatický. Také je vidět, že few-shot je lepší, ale protože jde o malé verze modelů, tak příliš mnoho ukázek je spíše mate, než že by pomohlo, takže 100 příkladů výsledek zlepšuje, 1000 ho zhoršuje. Nedokončené úlohy jsou ty, kde model zastavila content politika (někteří uživatelé nepíšou nic hezkého) nebo model nevrátil validní odpověď (tedy něco jiného než 0, 1 nebo 2).

## Cena
Cena je hodně odvozená z počtu příkladů na vstupu, tedy délky kontextu. Používat few-shot 1000 je tak nesmysl - velmi drahé a přitom horší výsledky. Nicméně například few-shot se 100 příklady je 10x dražší, než zero-shot. To je znát. Samozřejmě u few-shot variant je velká šance, že využijeme nižší ceny input tokenů z cache (50% sleva za cached token, ne všechny a ne vždy ale cachované budou), ale ani to nemění pravidla hry. Jinak samozřejmě nano varianty jsou levnější.

## Latence
U sekvenčního zpracování (měříme latenci, ne propustnost) se pohybuji mezi 0,64 až 1,06 sekundami na vzorek. Platí, že nano je rychlejší a kratší kontext je rychlejší. Few-shot s 1000 příklady je úplně mimo (3 vteřiny u mini).

## Jednoduchost a flexibilita
Tato varianta je jednoznačný vítěz v jednoduchosti použití a univerzálnosti, schopnosti se přizpůsobit podmínkám. Žádné trénování a ladění, stačí jednoduše změnit prompt a máte jiné výsledky podle toho, jak se požadavky úlohy budou měnit. Navíc model dokáže hromadu dalších úloh, takže můžu mít jeden systém na všechno - jeden endpoint, jedny knihovny, jedny zkušenosti apod.

# 2. Fine-tuning velkého jazykového modelu (LLM)
Vezmeme opět mini a nano model a provedeme fine-tuning naší trénovací sadou, tedy ukážeme našich 25 000 příkladů a následně zkusíme zero-shot a few-shot 100. 

## Kvalita
Kvalita je dramaticky lepší, než cokoli jiného v testu, tady se ukázala síla fine-tuningu. mini sice bylo lepší, ale opět ne nějak výrazně. Zajímavé je, že jak je model laděný, tak few-shot už mu nepomáhá, naopak ho zhoršuje.Tipuji, že vzorek 100 příkladů, byť je vybraný náhodně, není reprezentativní (vs. 25 000 příkladů z učení) a tím může být pro model matoucí.

## Cena
S cenou je to složitější. Jednak musíme započítat cenu za fine-tuning samotný a ta byla 40 USD - "jednorázová" platba (v uvozovkách proto, že při potřebě změnit příklady a doučit se platíme znova). U Azure OpenAI Service je cena tokenů stejná jako u běžné verze modelu, ale platíte za jeho hosting v hodinové sazbě (1,7 USD za hodinu). V tabulce najdete cenotvorbu z OpenAI, která hosting neúčtuje, ale zdražuje tokeny. Někdy se v praxi vyplatí to, jindy ono.

## Latence
Latence je testovaná v Azure, kde platíte hosting poplatek a přestože vám to nedává nějaké oficiální garance, v mém měření byla latence 2x - 3x nižší, což je super.

## Jednoduchost a flexibilita
Pořád je to generativní model, takže máte možnost ho "ohnout" v inference time změnou instrukcí nebo příkladů v kontextu. Už není univerzální, ale drobné opravy v rámci životního cyklu jde kontextem dosáhnout. Nicméně pro větší změny musíte přetrénovat model.

# 3. Dotrénovaní klasičtějšího transformer encoder modelu
Tady použijeme BERT model, který je dnes už starší, ale perfektní pro tento typ problému. Generativní modely používají decoder-only architekturu, protože jsou trénované pro predikci následujícího tokenu v textu, koukají tedy jednosměrně, jen dopředu v čase. Encoder-only model nejsou generativní, neumí vytvořit text, ale dokáží se vstupním textem pracovat a mít pozornost obousměrně a mohou třeba doplňovat chybějící slova nebo, což je náš případ, provést klasifikaci textu. Na náš problém se tedy hodí skvěle a vlastně lépe. Nicméně je to starší věc, jak obstojí s LLM, které byly trénované na o několik řádech větších datových sadách a o několik řádů větším compute?

## Kvalita
Jednoduchá a chvilku trénovaná varianta dopadla velmi dobře - výrazně nad neupravenými LLM a srovnatelně s LR nad embeddingy. Nicméně, fine-tunovaná LLM byla lepší (ale věřím, že by se dalo s BERTem zapracovat).

## Cena
Model je "zadarmiko", ale musí někde běžet a není to tak malé, že by tomu stačilo v pohodě CPU - potřebujeme tedy GPU stroj. Ten musím započítat do ceny a aby to bylo srovnatelné, tak na jeden bez vysoké dostupnosti, ale dva. Výpočet a test běžel na starší NVIDIA T4 zapůjčené z Azure VM, které stojí 0,56 USD na hodinu. Trénování běželo 500 vteřin, takže cena zanedbatelná (0,078 USD). Inferencing cenu počítám z naměřené latence a ceny za compute vynásobenou dvěma. Tím se cena modelu "zadarmo" dostává do vod gpt-4.1-nano, ale jasně - pokud necháme běžet jen na jednom nodu, tak je to levnější a nepochybně půjdou udělat optimalizace v propustnosti a paralelismu. Nicméně na embedding + LR (viz dále) to ani tak řádově nemá.

## Latence
Latence byla skvělá. Nutno vzít v úvahu, že všechny ostatní varianty mají nějakou cloudovou komponentu, která z mého počítače přidává třeba 30 ms round trip time, BERT běžel lokálně na VM v Azure a testoval se z něj. Nicméně jestli místo 0,09 vteřiny na vzorek to bude 0,12 sekund, tak pořád výborné a nejlepší v testu.

## Jednoduchost a flexibilita
Rozhodně zásadní nevýhoda. Není to ani klikačka jako fine-tuning LLM, musíte buď do kódu nebo do nějaké AutoML platformy a ani tam to není triviální. Model je naprosto jednoúčelový, nedá se dolaďovat promptem, velmi fixní záležitost. A navíc vycházíme z BERTu, který neumí česky, takže pro české scénáře to bude mnohem náročnější na trénování nemluvě a situacích, kdy potřebujete podporu pro mnoho jazyků. 

# 4. Použití embeddingů a klasifikace
Tohle je taková kombinovaná varianta využívající výhody masivně natrénovaného moderního modelu ve spojení s vlastní malinkatou rychlou klasifikací. Embedding model OpenAI je levný a převádí zadaný text do latentního prostoru, chcete-li redukuje množství dimenzí nebo to také můžete brát jako určitou variantu ztrátové komprese, kde model "uloží" to nejdůležitější. Výsledný vektor ale není interpretovatelný, jednotlivé dimenze mají skrytý význam. Co kdybychom ale vzali tyto výsledky a provedli nad nimi klasifikaci na pozitivní, neutrální a negativní nějakou relativně snadnou Machine Learning metodou? Jdeme z cirka 1500 dimenzí na 3 třídy, to by nám mohla stačit obyčejná až prehistorická logistická (nebo taky softmax) regrese (v tabulkách uvádím jako LR). To je něco, co je při 25 000 vzorcích vytrénované velmi rychle a může to v pohodě běžet na CPU se zanedbatelnými náklady. Inferencing je tedy o získání embeddingu z cloudu a následném lokálním výpočtu klasifikace.

## Kvalita
Při tréningu na celé sadě je kvalita výsledku výrazně nad neupraveným LLM a blíží se kvalitě BERTu.

## Cena
Cena je extrémně nízká, protože náklady na LR jsou zcela zanedbatelné, takže rozhodující jsou náklady za tokeny pro embedding a to je v cloudu služba velmi levná. Náklady jsou tak o řády nejnižší než cokoli jiného testovaného.

## Latence
Embeddingy vrací cloud velice rychle a LR model je v mžiku - perfektní latence.

## Jednoduchost a flexibilita
Podobně jako u BERTu je výsledné LR jednoúčelový model. Embeddingy jsou sice univerzální, ale samy o sobě nemají interpretaci - lze je používat pro hledání podobností (semantic search, relativní srovnání), ale ne klasifikaci. Tohle je tedy podstatná nevýhoda. Na druhou stranu - BERT neumí česky, embeddingy typicky ano, takže pro jazykové mutace je "pre-training" model v cloudu velkou výhodou oproti BERTu.

# Shrnutí
Co si tedy vybrat?

| Scénář | Volba | Vlastnosti |
|------------|---------------------|---------------------------|
| Jsem nerd a šetřílek | LR + embeddingy | nejnižší náklady, skvělá rychlost, ale složitější a jednoúčelové |
| Chci něco zcela univerzálního a laditelného v čase | LLM | základní kvalita, vyšší cena a latence, ale flexibilní a jednoduché |
| Chci nejlepší kvalitu a relativně snadno |  LLM fine-tuning | nejlepší kvalita, hostované řešení, ale jednoúčelové a drahé |
| Jsem nerd, ne-cloud, mluvím anglicky a mám GPU nazmar | BERT fine-tuning | velmi dobrá kvalita, nízké náklady, nejlepší latence, ale nejméně flexibilní |

Samozřejmě, tohle je můj příklad - v tom vašem to může být všechno jinak. Smyslem ale bylo představit si jak přemýšlet o variantách řešení úloh, které jsou v dnešním světě chytrých agentů takové "jednoduché", ale přitom mají obrovské množství využití. 