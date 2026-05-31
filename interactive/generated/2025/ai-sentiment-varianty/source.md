---
format_version: 1
title: "Jak na jednoduchou AI analýzu textu? LLM, fine-tuning, BERT nebo embeddingy?"
subtitle: "Na sentimentu krátkých textů porovnávám kvalitu, cenu, latenci a praktičnost čtyř cest."
slug: "ai-sentiment-varianty"
date: "2025-07-08"
language: "cs-CZ"
status: "experimental"
canonical_url: "/2025/ai-sentiment-varianty/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Jak na jednoduchou AI analýzu textu? LLM, fine-tuning, BERT nebo embeddingy?

Před desetiletími byl svět práce s jazykem, tedy NLP, hlavně o specializovaných modelech pro relativně jednoduché úlohy. Byly malé, levné na provoz a člověk musel vědět, co dělá. Dneska máme velké jazykové modely, které umí následovat instrukce a často zvládnou totéž bez trénování vlastního modelu.

Pojďme si to ukázat na sentimentu. Vezmu krátký příspěvek ze sociální sítě a chci ho zařadit do tří tříd: **pozitivní**, **negativní**, **neutrální**. Nejde mi o akademický benchmark, ale o praktickou otázku: co použít, jak dobré to bude, jak rychlé a kolik to stojí?

::: callout type="note" title="Data a kód"
Používám datovou sadu s přibližně 25 tisíci ručně označenými trénovacími příklady, 6 tisíci validačními a 5 tisíci testovacími. Všechny detaily včetně kódu na testování a trénování najdete na mém [GitHubu](https://github.com/tkubica12/d-ai-sentiment/tree/main).
:::

::: group id="uvod" title="Úvod do srovnání"

::: card number="01" title="Čtyři varianty vedle sebe" default="open"
Pro stejnou klasifikační úlohu mám čtyři praktické cesty. V dalších kartách projdu každou samostatně, ale tady je rychlý přehled toho, co budu porovnávat.

::: tabs id="approaches"
::: tab id="llm" title="LLM bez trénování"
Modelu řeknu instrukcí, že má vrátit jednu třídu. Zkouším skoro zero-shot a few-shot s 100 nebo 1000 příklady. Nejjednodušší varianta, ale cena a latence rostou s délkou kontextu.
:::
::: tab id="ft" title="Fine-tuned LLM"
Vezmu GPT-4.1 nano nebo mini a dotrénuji ho na 25 tisících příkladech. Pořád je to generativní model, ale už je výrazně specializovaný na naši úlohu.
:::
::: tab id="bert" title="BERT encoder"
Klasický encoder-only transformer je na klasifikaci textu vlastně velmi přirozený. Není generativní, dívá se obousměrně na celý vstup a vrací třídu.
:::
::: tab id="emb" title="Embeddingy + LR"
Text převedu embedding modelem do vektoru a nad ním natrénuji obyčejnou logistickou regresi. Cloud udělá univerzální reprezentaci, lokální malý model rozhodne třídu.
:::
:::

::: summary-grid
- **Nejvyšší přesnost**: fine-tuned GPT-4.1-mini, 80,0 %.
- **Nejnižší cena**: embeddingy + logistická regrese, asi 0,0005 USD na 1000 vzorků.
- **Nejnižší latence**: BERT, asi 0,09 sekundy na vzorek.
- **Nejjednodušší změny**: obyčejný LLM, protože měním prompt a ne model.
:::
:::

::: card number="02" title="Výsledky: přesnost, cena a rychlost" default="closed"
Přesnost nevypadá na první pohled ohromně. Je to ale i tím, že hranice mezi pozitivním a neutrálním sentimentem bývá neostrá. Některé příspěvky prostě člověk označí jinak než jiný člověk.

**Kvalita klasifikace**

| Skupina | Experiment | Model / přístup | Strategie | Accuracy | Cena běhu | Čas | Vzorků/s |
|---|---:|---|---|---:|---:|---:|---:|
| LLM | LLM_NANO_ZEROSHOT | GPT-4.1-nano | Zero-shot | 67,7 % | $0.13 | 3306,7 s | 1,56 |
| LLM | LLM_NANO_FEWSHOT_100 | GPT-4.1-nano | Few-shot 100 | 68,6 % | $1.45 (~$0.87 cached) | 4215,4 s | 1,23 |
| LLM | LLM_NANO_FEWSHOT_1000 | GPT-4.1-nano | Few-shot 1000 | 68,4 % | $13.39 (~$8.03 cached) | 9160,4 s | 0,56 |
| LLM | LLM_MINI_ZEROSHOT | GPT-4.1-mini | Zero-shot | 69,3 % | $0.55 | 3919,9 s | 1,38 |
| LLM | LLM_MINI_FEWSHOT_100 | GPT-4.1-mini | Few-shot 100 | 69,4 % | $5.88 (~$3.53 cached) | 5565,6 s | 0,94 |
| LLM | LLM_MINI_FEWSHOT_1000 | GPT-4.1-mini | Few-shot 1000 | 68,4 % | $55.53 (~$33.32 cached) | 16084,1 s | 0,33 |
| Fine-tuned LLM | LLM_FT_NANO_ZEROSHOT | GPT-4.1-nano FT | Zero-shot | 79,0 % | $0.26 | 1907,0 s | 2,71 |
| Fine-tuned LLM | LLM_FT_NANO_FEWSHOT_100 | GPT-4.1-nano FT | Few-shot 100 | 78,4 % | $2.90 (~$1.74 cached) | 1940,0 s | 2,66 |
| Fine-tuned LLM | LLM_FT_MINI_ZEROSHOT | GPT-4.1-mini FT | Zero-shot | 80,0 % | $1.04 | 1564,2 s | 3,30 |
| Fine-tuned LLM | LLM_FT_MINI_FEWSHOT_100 | GPT-4.1-mini FT | Few-shot 100 | 79,3 % | $11.58 (~$6.95 cached) | 1918,4 s | 2,69 |
| Embeddingy + ML | LR_100 | OpenAI Embeddings + LR | 100 vzorků | 60,9 % | $0.0025 | 963,2 s | 5,40 |
| Embeddingy + ML | LR_1000 | OpenAI Embeddings + LR | 1000 vzorků | 67,1 % | $0.0025 | 951,7 s | 5,47 |
| Embeddingy + ML | LR_ALL | OpenAI Embeddings + LR | celá sada | 73,2 % | $0.0025 | 932,1 s | 5,58 |
| Transformer encoder | BERT_SENTIMENT | BERT-base FT | celá sada | 74,5 % | $0.028 | 465,4 s | 11,19 |

::: reveal title="Plná měření tokenů a dokončených predikcí"
| Experiment | Dokončeno | Selhalo | Total tokens | Input tokens | Output tokens |
|---|---:|---:|---:|---:|---:|
| LLM_NANO_ZEROSHOT | 5166 (99,3 %) | 39 (0,7 %) | 1 289 946 | 1 284 780 | 5166 |
| LLM_NANO_FEWSHOT_100 | 5165 (99,2 %) | 40 (0,8 %) | 14 470 776 | 14 465 611 | 5165 |
| LLM_NANO_FEWSHOT_1000 | 5166 (99,3 %) | 39 (0,7 %) | 133 890 834 | 133 885 668 | 5166 |
| LLM_MINI_ZEROSHOT | 5076 (97,5 %) | 129 (2,5 %) | 1 351 565 | 1 346 144 | 5421 |
| LLM_MINI_FEWSHOT_100 | 5140 (98,8 %) | 65 (1,2 %) | 14 688 863 | 14 683 620 | 5243 |
| LLM_MINI_FEWSHOT_1000 | 5088 (97,8 %) | 117 (2,2 %) | 138 814 519 | 138 809 163 | 5356 |
| LLM_FT_NANO_ZEROSHOT | 5166 (99,3 %) | 39 (0,7 %) | 1 289 946 | 1 284 780 | 5166 |
| LLM_FT_NANO_FEWSHOT_100 | 5166 (99,3 %) | 39 (0,7 %) | 14 473 578 | 14 468 412 | 5166 |
| LLM_FT_MINI_ZEROSHOT | 5166 (99,3 %) | 39 (0,7 %) | 1 289 946 | 1 284 780 | 5166 |
| LLM_FT_MINI_FEWSHOT_100 | 5165 (99,2 %) | 40 (0,8 %) | 14 470 685 | 14 465 520 | 5165 |
| LR_100 | 5205 (100 %) | 0 | 124 123 | 124 123 | 0 |
| LR_1000 | 5205 (100 %) | 0 | 124 123 | 124 123 | 0 |
| LR_ALL | 5205 (100 %) | 0 | 124 123 | 124 123 | 0 |
| BERT_SENTIMENT | 5205 (100 %) | 0 | N/A | N/A | N/A |
:::

::: reveal title="Náklady na 1000 vzorků a latence"
**Náklady na 1000 vzorků**

| Kategorie | Experiment | Cena na 1000 vzorků | Pořadí |
|---|---|---:|---:|
| Nejlevnější | LR_100 | $0.0005 | 1 |
| Nejlevnější | LR_1000 | $0.0005 | 1 |
| Nejlevnější | LR_ALL | $0.0005 | 1 |
| Nízké | LLM_NANO_ZEROSHOT | $0.025 | 4 |
| Nízké | BERT_SENTIMENT | $0.028 | 5 |
| Nízké | LLM_FT_NANO_ZEROSHOT | $0.050 | 6 |
| Nízké | LLM_MINI_ZEROSHOT | $0.106 | 7 |
| Nízké | LLM_FT_MINI_ZEROSHOT | $0.202 | 8 |
| Střední | LLM_NANO_FEWSHOT_100 | $0.280 ($0.168 cached) | 9 |
| Střední | LLM_FT_NANO_FEWSHOT_100 | $0.562 ($0.337 cached) | 10 |
| Střední | LLM_MINI_FEWSHOT_100 | $1.130 ($0.678 cached) | 11 |
| Střední | LLM_FT_MINI_FEWSHOT_100 | $2.242 ($1.345 cached) | 12 |
| Drahé | LLM_NANO_FEWSHOT_1000 | $2.590 ($1.554 cached) | 13 |
| Drahé | LLM_MINI_FEWSHOT_1000 | $10.670 ($6.402 cached) | 14 |

**Latence**

| Kategorie | Experiment | Čas na vzorek |
|---|---|---:|
| Nejrychlejší | BERT_SENTIMENT | 0,09 s |
| Rychlé | LR_ALL | 0,18 s |
| Rychlé | LR_1000 | 0,18 s |
| Rychlé | LR_100 | 0,19 s |
| Střední | LLM_FT_MINI_ZEROSHOT | 0,30 s |
| Střední | LLM_FT_MINI_FEWSHOT_100 | 0,37 s |
| Střední | LLM_FT_NANO_ZEROSHOT | 0,37 s |
| Střední | LLM_FT_NANO_FEWSHOT_100 | 0,38 s |
| Pomalejší | LLM_NANO_ZEROSHOT | 0,64 s |
| Pomalejší | LLM_MINI_ZEROSHOT | 0,72 s |
| Pomalejší | LLM_NANO_FEWSHOT_100 | 0,81 s |
| Pomalejší | LLM_MINI_FEWSHOT_100 | 1,06 s |
| Mimo | LLM_NANO_FEWSHOT_1000 | 1,77 s |
| Mimo | LLM_MINI_FEWSHOT_1000 | 3,00 s |
:::
:::

:::

::: group id="varianty" title="Čtyři varianty do hloubky"

::: card number="03" title="Velký jazykový model bez trénování" default="closed"
LLM dokáže následovat instrukce, takže mu můžeme jednoduše říct: klasifikuj text a vrať jen jeden výstupní token. V mém případě číslo `0`, `1` nebo `2`. Kdybych model nechal dlouze uvažovat a vysvětlovat se, možná by byl přesnější, ale zároveň násobně dražší. Tady mě zajímá praktický provoz.

::: detail-grid title="Co se u LLM ukázalo" hint="Klikněte na kartu pro detail"
::: detail-card title="Kvalita" summary="Mini je o něco lepší než nano, ale žádný zázrak se nekoná."
Few-shot se 100 příklady trochu pomůže. Few-shot s 1000 příklady už malé modely spíš mate a prodlužuje kontext tak moc, že výsledek nedává smysl.
:::
::: detail-card title="Cena" summary="Rozhodují hlavně vstupní tokeny."
Proto je few-shot 1000 prakticky nesmysl: dramaticky dražší a přitom horší. U few-shot scénářů může pomoct cache input tokenů, ale pravidla hry to nemění.
:::
::: detail-card title="Latence" summary="Krátký kontext je rychlejší, nano je rychlejší."
Sekvenční zpracování vychází zhruba od 0,64 do 1,06 sekundy na vzorek. Varianta s 1000 příklady je úplně mimo, u mini modelu tři sekundy na vzorek.
:::
::: detail-card title="Flexibilita" summary="Tady LLM vyhrává."
Bez trénování, bez pipeline, bez specializovaného modelu. Změním prompt a mám jiné chování. Jeden endpoint, jedny knihovny, jeden provozní model.
:::
:::
:::

::: card number="04" title="Fine-tuning velkého jazykového modelu" default="closed"
Tady vezmu opět mini a nano model a ukážu mu 25 000 trénovacích příkladů. Pak ho zkusím použít zero-shot i s few-shot 100 příklady.

::: detail-grid title="Fine-tuned LLM v praxi" hint="Klikněte na kartu pro detail"
::: detail-card title="Kvalita" summary="Nejlepší výsledek celého testu."
Fine-tuning dramaticky pomohl. GPT-4.1-mini se dostal na 80,0 %. Zajímavé je, že few-shot už nepomáhá, spíš zhoršuje. Tipuji, že náhodně vybraných 100 příkladů není reprezentativních proti 25 000 příkladům z učení.
:::
::: detail-card title="Cena" summary="Inferencing není celý příběh."
Fine-tuning samotný stál 40 USD. U Azure OpenAI Service má model stejnou cenu tokenů jako běžná verze, ale platí se hosting hodinovou sazbou 1,7 USD/h. U OpenAI se hosting neúčtuje, ale tokeny jsou dražší. Někdy vyjde lépe jedno, někdy druhé.
:::
::: detail-card title="Latence" summary="V mém měření výrazně lepší."
Testoval jsem v Azure, kde platíte hosting. Nemá to být oficiální garance, ale naměřil jsem 2× až 3× nižší latenci než u běžné varianty.
:::
::: detail-card title="Flexibilita" summary="Pořád jde trochu ohýbat promptem."
Je to specializovaný model, ale pořád generativní. Drobné korekce instrukcí nebo příklady v kontextu fungují. Větší změny znamenají nové trénování.
:::
:::
:::

::: card number="05" title="Dotrénovaný transformer encoder (BERT)" default="closed"
BERT je starší, ale pro klasifikaci textu se hodí skvěle. Generativní modely jsou decoder-only a učí se predikovat další token. Encoder-only model negeneruje text, ale umí dobře zpracovat celý vstup a dát mu třídu.

::: detail-grid title="BERT: starší věc, pořád silná" hint="Klikněte na kartu pro detail"
::: detail-card title="Kvalita" summary="Velmi dobrá, ale fine-tuned LLM je výš."
Jednoduchá a krátce trénovaná varianta dopadla výrazně nad neupravenými LLM a podobně jako logistická regrese nad embeddingy. Věřím, že s BERTem by se dalo ještě zapracovat.
:::
::: detail-card title="Cena" summary="Model je zadarmiko, provoz ne."
Potřebujeme GPU stroj. Počítal jsem dva starší NVIDIA T4 nody z Azure VM za 0,56 USD/h. Trénování běželo 500 sekund, takže skoro nic. Inferencing ale stojí compute, a tím se BERT dostává někam do vod GPT-4.1-nano.
:::
::: detail-card title="Latence" summary="Nejlepší v testu."
BERT běžel lokálně na Azure VM, takže neměl stejný cloudový round trip jako ostatní varianty. I kdyby místo 0,09 s vycházel 0,12 s, pořád je to výborné.
:::
::: detail-card title="Flexibilita" summary="Největší slabina."
Musíte do kódu nebo AutoML, model je jednoúčelový a promptem ho nedoladíte. Navíc vycházím z BERTu, který neumí česky, takže české a vícejazyčné scénáře budou náročnější.
:::
:::
:::

::: card number="06" title="Embeddingy a logistická regrese" default="closed"
Tohle je kombinace moderního pre-trainingu a prehistoricky jednoduché klasifikace. Embedding model převede text do latentního prostoru, zhruba 1500 dimenzí, a logistická regrese z toho udělá tři třídy.

::: reveal title="Proč mi tahle kombinace přijde zajímavá"
Embeddingy samy o sobě nejsou klasifikátor. Neřeknou „pozitivní" nebo „negativní". Jsou ale univerzální reprezentací významu textu. Nad ní můžu postavit malý model, který se trénuje rychle, běží na CPU a skoro nic nestojí. Inferencing je pak cloudové získání embeddingu plus lokální výpočet klasifikace.
:::

::: detail-grid title="Embeddingy + LR" hint="Klikněte na kartu pro detail"
::: detail-card title="Kvalita" summary="S celou sadou překvapivě dobrá."
Při trénování na celé sadě je výsledek výrazně nad neupraveným LLM a blíží se BERTu.
:::
::: detail-card title="Cena" summary="Řádově nejnižší."
Náklady na logistickou regresi jsou zanedbatelné. Rozhoduje cena embedding tokenů a ta je velmi nízká.
:::
::: detail-card title="Latence" summary="Velmi dobrá."
Embeddingy se z cloudu vrací rychle a lokální LR model je hotový v mžiku.
:::
::: detail-card title="Flexibilita" summary="Jednoúčelové, ale jazykově praktické."
Stejně jako BERT je výsledný klasifikátor fixní. Na rozdíl od BERTu ale moderní embeddingy typicky umí česky i další jazyky, což je velká praktická výhoda.
:::
:::
:::

:::

::: group id="zaver" title="Co bych tedy vybral"

::: card number="07" title="Moje praktické doporučení" default="open"
Žádná z variant není absolutní vítěz. Záleží na úloze, objemu, jazyce a tom, kolik flexibility chcete do budoucna.

| Scénář | Volba | Proč |
|---|---|---|
| Jsem nerd a šetřílek | LR + embeddingy | Nejnižší náklady, skvělá rychlost, složitější a jednoúčelové. |
| Chci něco univerzálního a laditelného v čase | LLM | Základní kvalita, vyšší cena a latence, ale extrémní jednoduchost. |
| Chci nejlepší kvalitu a relativně snadný provoz | Fine-tuned LLM | Nejlepší kvalita, hostované řešení, ale specializace a vyšší náklady. |
| Jsem nerd, nechci cloud, mluvím anglicky a mám GPU nazmar | BERT fine-tuning | Velmi dobrá kvalita, nízké náklady při dobrém vytížení, nejlepší latence, nejméně flexibility. |

::: arrow-list title="Moje praktická zkratka"
- Pokud úloha ještě není stabilní, začal bych obyčejným LLM a promptem.
- Pokud jde o velký objem a jasně definovanou třídu, vyzkoušel bych embeddingy + jednoduchý klasifikátor.
- Pokud honím kvalitu a chci hostovaný provoz, sáhl bych po fine-tuningu LLM.
- Pokud mám silný ML tým a vlastní compute, dává smysl encoder model.
:::
:::

:::


::: closing
Samozřejmě, tohle je můj příklad; ve vašem to může dopadnout jinak. Důležité je nepřemýšlet jen o přesnosti, ale zároveň o ceně, latenci, provozu a budoucích změnách zadání.
:::
