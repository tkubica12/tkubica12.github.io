---
layout: post
published: true
title: "Azure OpenAI Service - sumarizace textu v češtině prakticky"
tags:
- AI
---
Pojďme si dnes pohrát s GPT-3.5 v Azure OpenAI Service na příkladu sumarizace textu. Tento jazykový model stojí i za dnes už legendárním ChatGPT, ale my nebudeme konverzovat s robotem, ale využijeme API dostupná přes Azure, která si můžeme ladit a trochu se s tím seznámit. Hned dopředu musím říct jedno - model je obrovitánský, takže češtinu zvládá velmi dobře, ale na druhou stranu je jasné, že pro angličtinu měl mnohem víc dat. Když budeme společně koukat na výsledky, tak mějme na paměti, že nejsme pupek světa a u světových jazyků budou výsledky ještě lepší.

# Zdrojový text
Vzal jsem si něco, co je příliš dlouhé na to, abych měl za normálních okolností chuť to číst, něco, co nemá žádná autorská práva a obsahuje to nějakou informaci. Zvolil jsem tiskovou zprávu Ministerstva pro místní rozvoj a tady je její znění:

> Vyjádření vicepremiéra pro digitalizaci Ivana Bartoše k novele zákona o veřejných zakázkách
> 
> Vicepremiér pro digitalizaci a ministr pro místní rozvoj Ivan Bartoš chystá pozměňovací návrh k novele o zadávání veřejných zakázek. Návrh, který se týká vertikální spolupráce a sdílení kapacit mezi různými orgány státu (nejen) v oblasti IT, vzbudil obavy ve Svazu průmyslu a dopravy, které adresoval poslancům prostřednictvím dopisu. Ve čtvrtek 19. ledna se místopředseda vlády pro digitalizaci se zástupci Svazu sešel a svůj záměr detailně představil. Zástupci Svazu vyjádřili spokojenost se schůzkou a předloženými argumenty a budou spolupracovat na přípravě prováděcí metodiky.
>
> Pozměňovací návrh vzešlý z Kabinetu vicepremiéra pro digitalizaci odstraňuje byrokratické překážky, konkrétně tzv. fikci rozdělení státu na organizační složky. Chápání každého ministerstva, úřadu či podřízené organizace izolovaně od ostatních podle něj může bránit efektivnímu využití zdrojů uvnitř státu. 
> 
> Tyto limity se projevily například během covidové pandemie, kdy bylo třeba okamžitě a velmi agilně rozvíjet systémy, jako byla Chytrá karanténa, rezervační systém na očkování nebo shromažďování dat z testování. Tehdy však musela být využita takzvaná krizová výjimka v nouzovém stavu. 
> 
> Pozměňovací návrh k novele předpokládá, že stát – výhradně pro účely zadávání veřejných zakázek – může být za přesně určených podmínek chápán jako jeden celek. Je možné tak lépe využívat kapacity uvnitř státu. Současně tým kabinetu digitalizace zdůraznil, že využití vertikální spolupráce nemůže být bezmezné. Stále platí podmínky dle Směrnice EU k využití vertikální spolupráce, které jsou jasné a striktní. Metodické usměrnění těchto limitů vydá Ministerstvo pro místní rozvoj ve spolupráci s ÚOHS.
> 
> Svaz průmyslu a dopravy zaslal 6. ledna 2023 poslancům dopis, ve kterém vyjádřil obavy svých členů z možného narušení efektivní hospodářské soutěže, rozporu se Směrnicí Evropského parlamentu a Rady 2014/24/EU ze dne 26. února 2014 o zadávání veřejných zakázek a z otevření široké možnosti zadání bez soutěže.
> 
> Následně se místopředseda vlády pro digitalizaci Ivan Bartoš se svým týmem sešel se zástupci Svazu Milenou Jabůrkovou, viceprezidentkou svazu, Bohuslavem Čížkem, ředitelem hospodářské sekce, a Marcelou Kaňovou, členkou expertního týmu pro digitální ekonomiku a odbornicí na soutěžní právo. Předmětem jednání bylo vysvětlit důvody a dopady pozměňovacího návrhu. 
> 
> Zvláštní důraz byl kladen na rozptýlení obav z předkládaného pozměňovacího návrhu a z toho, jak bude pravidla využívat nově založená Digitální a informačné agenturu (DIA), a zda tato pravidla nenaruší postupy při zadávání veřejných zakázek i v jiných sektorech. Jednání potvrdilo shodu obou stran na potřebě vypracování kvalitní metodiky, která povede jak ke zlepšení procesů zadávání, tak k eliminaci případných rizik. 
> 
> Tým vicepremiéra vysvětlil, že DIA je ústředním správním úřadem, který má zavést jednotné postupy a standardy, zavést metodiku a jednotlivé kroky pro přípravu a zpracování záměrů z oblasti digitalizace a IT projektů, ale není v žádném smyslu dodavatelem konkrétních zakázek. Nebyla zřízena za účelem podnikání a není ani dodavatelem IT služeb pro státní správu (mimo takových, které z povahy věci nelze outsourcovat, tedy např. z bezpečnostních důvodů).
> 
> Významná obava z možného rozporu se Směrnicí Evropského parlamentu a Rady EU o zadávání veřejných zakázek byla zcela rozptýlena vyjádřením Evropské komise ze dne 13. ledna 2023, kterým sděluje, že předkládaný Pozměňovací návrh není v rozporu s Evropskou směrnicí.
> 
> Organizace státní správy nejsou schopné kapacitně pokrýt ani významnou část potřeb státní správy nejen v oblasti ICT, ale i v jiných oblastech. Novela zákona o zadávání veřejných zakázek v tomto naopak dává příležitost trhu. Rychlejší a kvalitnější zadávání veřejných zakázek s sebou nese nejen příležitost pro efektivitu na obou stranách, ale i schopnost realizace větší a kvalitněji vydefinované poptávky ze strany státu. 
> 
> „Pozměňovací návrh je příležitostí, po které už dlouhou dobu volaly všechny resorty i správní úřady. Je to příležitost ke vzájemné pomoci, kooperaci, sdílení zkušeností i expertízy,“ uvedl vicepremiér pro digitalizaci Bartoš. „Schopnost státu vyhlašovat a vyhodnocovat kvalitně nastavené veřejné zakázky by mělo být společným cílem zadavatelů i dodavatelů, kteří se tak mohou soustředit na kvalitní plnění, které se v čase nezdržuje,“ dodal Ivan Bartoš.  
> 
> Zástupci Svazu průmyslu a dopravy závěrem jednání ocenili svolání schůzky a vysvětlení připomínek z předmětného dopisu. Byla nalezena shoda na potřebnosti spolupráce na zkvalitnění procesu a předcházení problémům při zadávání veřejných zakázek. Svaz se bude podílet i na vypracování metodiky a postupů pro realizaci novely v intencích doporučení Evropské komise.

# Parametry OpenAI API
Službu jsem si vytočil v Azure a nasadil nejnovější model - text-davinci-003 (tedy GPT 3.5). V grafickém studiu si mohu zkoušet naživo.

[![](/images/2023/2023-01-24-08-57-45.png){:class="img-fluid"}](/images/2023/2023-01-24-08-57-45.png)

Budu si hrát s následujícími parametry:
- **max_tokens** - Token je v tomto API celkem proměnlivá jednotka a pro angličtinu se pohybuje kolem 4 znaků na token. V případě češtiny pravděpodobně kvůli speciálním znakům mi to obvykle vychází průměrně na 2 znaky na token. Původní text jsem hodil do [OpenAI token kalkulačky](https://beta.openai.com/tokenizer) a má 2711 tokenů. Sumarizaci chci provádět tak, aby výsledkem byl text 5x kratší (20% originálu), takže max_tokens nastavím na 550 pro všechny běhy.
- **temperature** je parametr, který určuje míru nahodilosti ve výsledku. Pokud se blíží nule, tak jsou výsledky deterministické (na stejný vstup dostanete stejný výstup), směrem k číslu jedna se model chová stochasticky (můžete dostat odlišné výsledky). To může být užitečné, když budete chtít vygenerovat víc variant, z kterých si vyberete.
- **top_p** je podobné parametru temperature, ale jde na to jinak (a OpenAI doporučuje ladit jeden nebo druhý, ale ne oba zároveň). Pokud se blíží 1, vybírá model tokeny ze 100% celé sady, tedy je ochoten zvážit cokoli. Jak se blížíme číslu nula, tak necháváme model vybírat jen z nějaké omezené sady těch "nejlepších" variant dalšího tokenu pro daný vstup. Jinak řečeno hrajeme víc na jistou a u čísla nula se tak dostáváme opět k determinismu.
- **frequency_penalty** je koeficient od -2 do 2 a v případě kladných hodnot penalizuje model za produkování výsledku, ve kterém se věci opakují. Někdy je vhodné, když text řekne jednu věc víckrát pokaždé jinak - vede to k lepšímu pochopení. Jindy to zas může působit otravně a ztrácí se informační koncentrovanost. Právě proto je tento parametr laditelný. Záporné hodnoty upřednostňují opakování (a grafické studio je ani nenabízí) - asi nevím, proč bych to měl někdy využít u sumarizace.
- **presence_penalty** je znovu koeficient -2 až 2, který umí penalizovat model za výstup, který obsahuje doslovně něco z toho, co bylo na vstupu. Někdy můžeme skutečně mít potřebu vynutit, že to bude řečeno jinak (například když nechceme, aby v tom někdo původní text snadno poznal), někdy ale naopak požadujeme, aby výsledek byl složen z úryvků, citací původního textu.

# Python kód pro generování odpovědí
Azure OpenAI Service má jednoduché API a přímo grafické studio vám vygeneruje kód pro Python nebo curl. Z toho jsem vyšel a připravil jednoduchý kód, který vezme text a vyzkouší různá nastavení parametrů a výsledek pak uloží do CSV souboru. Kromě zde na blogu to najdete na mém [GitHubu](https://github.com/tkubica12/ai-demos/tree/main/openai).

```python
import os
import openai
import csv
openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_API_URL")
openai.api_version = "2022-12-01"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Exit if the environment variables are not set
if "OPENAI_API_URL" not in os.environ or "OPENAI_API_KEY" not in os.environ:
    raise Exception("Please set OPENAI_API_KEY and OPENAI_API_URL environment variable")

# Read input text file
with open("./text.txt", 'r') as f:
    prompt = f.read()

# Add the TL;DR to the prompt
prompt = prompt + "\n\nTL;DR"

# Define combinations of parameters to score
dataset = [
    {"temperature": 1, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0},
    {"temperature": 1, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0},
    {"temperature": 0, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0},
    {"temperature": 0, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0},
    {"temperature": 1, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0},
    {"temperature": 1, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 0},
    {"temperature": 1, "top_p": 0, "frequency_penalty": 0, "presence_penalty": 0},
    {"temperature": 1, "top_p": 0, "frequency_penalty": 0, "presence_penalty": 0},
    {"temperature": 0, "top_p": 1, "frequency_penalty": 1, "presence_penalty": 0},
    {"temperature": 0, "top_p": 1, "frequency_penalty": 2, "presence_penalty": 0},
    {"temperature": 0, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 1},
    {"temperature": 0, "top_p": 1, "frequency_penalty": 0, "presence_penalty": 2},
    {"temperature": 0.5, "top_p": 1, "frequency_penalty": 0.5, "presence_penalty": 0.2},
]

# Generate the responses
for data in dataset:
    print(f"Generating: temperature={data['temperature']}, top_p={data['top_p']}, frequency_penalty={data['frequency_penalty']}, presence_penalty={data['presence_penalty']}")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=data["temperature"],
        max_tokens=550,
        top_p=data["top_p"],
        frequency_penalty=data["frequency_penalty"],
        presence_penalty=data["presence_penalty"],
        stop=None)
    data["response"] = response.choices[0].text
    print(f"Response: {data['response']}\n\n")

# Write the output to CSV file
print("Writing output to CSV file")
headers = ["temperature", "top_p", "frequency_penalty", "presence_penalty", "response"]
with open("output.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(dataset)
```

Skript jsem spustil, všechno proběhlo, pojďme analyzovat výsledky.

# Výsledky - jak se daří sumarizovat text a jaký je efekt nastavení parametrů
Nejprve se podívejme na výsledky čtyř běhů s maximální mírou ochoty experimentovat, tedy s temperature 1 a top_p 1. Tady jsou čtyři výsledné texty - každý trochu jiný a za mě tedy všechny dávají smysl o jsou příjemné na čtení. Musím přiznat, že slovo "exprimovali" jsem tedy raději vyhledal ve slovníku, ale ve finále pasuje - holt model se toho prostě nebál. V jednom případě se objevila chyba - státní organismy určitě mají být státní orgány. Oboje považuji za znaky maximální ochoty modelu jít do rizika a tím současně generovat diverifikovanější výstupy. Pokud budeme preferovat metodu, kdy si pak sami vybereme, je tohle nastavení myslím ideální.

- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o veřejných zakázkách, který usnadňuje sdílení kapacit státu v oblasti IT. Kvůli obavám ze strany Svazu průmyslu a dopravy pozměňovací návrh podrobně vysvětlil a rozptýlení obav bylo potvrzeno vyjádřením Evropské komise ze dne 13. ledna 2023. Toto vyjádření také potvrdilo, že pozměňovací návrh není v rozporu s evropskou směrnicí. Svaz průmyslu a dopravy se bude podílet na vypracování metodiky a postupů pro realizaci novely, aby bylo zajištěno vysoce kvalitní zadávání veřejných zakázek.
- Vicepremiér pro digitalizaci a ministr pro místní rozvoj Ivan Bartoš a Svaz průmyslu a dopravy se sešli, aby debatovali o novele zákona o veřejných zakázkách, která odstraňuje byrokratické překážky při zadávání veřejných zakázek. Poslancům byl odeslán dopis se strachem, že pozměňovací návrh může poškodit hospodářskou soutěž. Na jednání vyvstaly i obavy z možného rozporu se Směrnicí EU o veřejných zakázkách. Naštěstí byly tyto obavy rychle vyvráceny a obě strany se shodly na přípravě metodiky. Obecně chce Bartoš zlepšit efektivitu zadávání veřejných zakázek prostřednictvím sektorové spolupráce, jasných a striktních limitů a kooperace mezi státními organismy.
- Vicepremiér pro digitalizaci Ivan Bartoš chystá pozměňovací návrh k novele o zadávání veřejných zakázek. Tento návrh má odstranit byrokratické překážky týkající se vertikální spolupráce a sdílení kapacit mezi jednotlivými orgány státu. Zástupci Svazu průmyslu a dopravy exprimovali obavy, ve kterých se dotkli možností narušení efektivní hospodářské soutěže. Místopředseda vlády se zástupci Svazu sešel a obě strany přijaly dohodu o spolupráci a vypracování metodiky, která povede nejen ke zlepšení procesů zadávání, ale i eliminace rizik.
- Vicepremiér pro digitalizaci Ivan Bartoš chce urychlit proces zadávání veřejných zakázek tím, že odstraní byrokracii a umožní, aby si orgány veřejné správy sdílely kapacity. Návrh se setkal s obavami Svazu průmyslu a dopravy, které byly rozptýleny po schůzce s vyjádřením Evropské komise. Tým vicepremiéra přesvědčivě vysvětlil, že nový návrh nenaruší hospodářskou soutěž a má naopak vést ke zkvalitnění procesů zadávání. Obě strany se dohodly na přípravě metodiky pro realizaci novely.

Co se stane když shodíme buď temperature nebo top_p na nulu? Měl by nastat determinismus - jak to dopadlo? Dle očekávání je všechno stejné a z mého pohledu správně co do informační přesnosti i stylu.

- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o zadávání veřejných zakázek, který má za cíl odstranit byrokratické překážky a umožnit efektivní využití kapacit uvnitř státu. Svaz průmyslu a dopravy vyjádřil obavy z možného narušení efektivní hospodářské soutěže, ale po schůzce s vicepremiérem a vyjádření Evropské komise byly tyto obavy rozptýleny. Tým vicepremiéra vysvětlil, že DIA není dodavatelem IT služeb pro státní správu a že novela má za cíl zkvalitnit proces zadávání veřejných zakázek. Svaz se bude podílet na vypracování metodiky pro realizaci novely.
- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o zadávání veřejných zakázek, který má za cíl odstranit byrokratické překážky a umožnit efektivní využití kapacit uvnitř státu. Svaz průmyslu a dopravy vyjádřil obavy z možného narušení efektivní hospodářské soutěže, ale po schůzce s vicepremiérem a vyjádření Evropské komise byly tyto obavy rozptýleny. Tým vicepremiéra vysvětlil, že DIA není dodavatelem IT služeb pro státní správu a že novela má za cíl zkvalitnit proces zadávání veřejných zakázek. Svaz se bude podílet na vypracování metodiky pro realizaci novely.
- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o zadávání veřejných zakázek, který má za cíl odstranit byrokratické překážky a umožnit efektivní využití kapacit uvnitř státu. Svaz průmyslu a dopravy vyjádřil obavy z možného narušení efektivní hospodářské soutěže, ale po schůzce s vicepremiérem a vyjádření Evropské komise byly tyto obavy rozptýleny. Tým vicepremiéra vysvětlil, že DIA není dodavatelem IT služeb pro státní správu a že novela má za cíl zkvalitnit proces zadávání veřejných zakázek. Svaz se bude podílet na vypracování metodiky pro realizaci novely.
- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o zadávání veřejných zakázek, který má za cíl odstranit byrokratické překážky a umožnit efektivní využití kapacit uvnitř státu. Svaz průmyslu a dopravy vyjádřil obavy z možného narušení efektivní hospodářské soutěže, ale po schůzce s vicepremiérem a vyjádření Evropské komise byly tyto obavy rozptýleny. Tým vicepremiéra vysvětlil, že DIA není dodavatelem IT služeb pro státní správu a že novela má za cíl zkvalitnit proces zadávání veřejných zakázek. Svaz se bude podílet na vypracování metodiky pro realizaci novely.

Tak budete preferovat odvážný model, kterému se podaří čas od času exprimovat nějaké zajímavé (ale správné) slovní spojení, ale občas také udělat drobnou chybu nebo chcete stritkně to, co model deterministicky považuje za nejlepší odpověď? Povětšinou se asi shodneme, že obvykle bude ideální být někde mezi tím a k tomu se na konci článku vrátíme.

Pojďme teď při zachování ostatních parametrů nastavit frequency_penalty na 0, 1 a 2. Použiji temperature na 0, ať tu máme determinismus a do výsledku nám nepromlouvá náhoda. Všimněte si, jak tímto parametrem ubíráme schopnost modelu vracet perfektní výsledky. Tak například při koeficientu 1 můžeme vidět některá rozumná zestručnění - například "ale po schůzce s vicepremiérem" skutečně lze zkrátit na "ale po schůzce", protože o vicepremiéru už se hovořilo a lze to pochopit z kontextu. Nicméně došlo tady k nepřesnosti - není to tak, že Evropskému parlamentu bylo sděleno, ale naopak ten sdělil. To je poměrně velký faktický prohřešek, který se bez bičování tímto parametrem nikde neopakoval. No a při koeficientu 2 už se to rozpadlo úplně včetně nedokončené věty. Dává tedy smysl tento parametr držet spíše někde mezi 0 a 0.5.

- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o zadávání veřejných zakázek, který má za cíl odstranit byrokratické překážky a umožnit efektivní využití kapacit uvnitř státu. Svaz průmyslu a dopravy vyjádřil obavy z možného narušení efektivní hospodářské soutěže, ale po schůzce s vicepremiérem a vyjádření Evropské komise byly tyto obavy rozptýleny. Tým vicepremiéra vysvětlil, že DIA není dodavatelem IT služeb pro státní správu a že novela má za cíl zkvalitnit proces zadávání veřejných zakázek. Svaz se bude podílet na vypracování metodiky pro realizaci novely.
- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o zadávání veřejných zakázek, který má odstranit byrokratické překážky a umožnit efektivnější využití kapacit státu. Svaz průmyslu a dopravy vyjádřil obavy, ale po schůzce se shodl na potřebě spolupráce na metodice pro realizaci novely. Evropskému parlamentu a Radě EU bylo sděleno, že není v rozporu s evropskou směrnicí.
- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o zadávání veřejných zakázek, který měl odstranit byrokratické překážky a umožnit efektivní vyučení stanovených limitovaných prostor. Svaz pr

Jaká je situace s nastavením parametru presence_penalty na 0, 1 a 2 opět při plném determinismu? Všimněte si, jak termín *narušení hospodářské soutěže*, který se v textu objevuje, donutil nejpřísnější variantu penalizace najít alternativní vyjádření *zneužití této možnosti*. Jiný příklad je, že vyjádření Evropské komise nevedlo k *rozptýlení obav* (což je slovo použité v původním textu), ale *potvrzení, že návrh není v rozporu*.

- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o zadávání veřejných zakázek, který má za cíl odstranit byrokratické překážky a umožnit efektivní využití kapacit uvnitř státu. Svaz průmyslu a dopravy vyjádřil obavy z možného narušení efektivní hospodářské soutěže, ale po schůzce s vicepremiérem a vyjádření Evropské komise byly tyto obavy rozptýleny. Tým vicepremiéra vysvětlil, že DIA není dodavatelem IT služeb pro státní správu a že novela má za cíl zkvalitnit proces zadávání veřejných zakázek. Svaz se bude podílet na vypracování metodiky pro realizaci novely.
- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o zadávání veřejných zakázek, který má odstranit byrokratické překážky a umožnit efektivní využití kapacit státu. Svaz průmyslu a dopravy vyjádřil obavy z možného narušení hospodářské soutěže a rozporu se Směrnicí EU. Na schůzce s vicepremiérem byly tyto obavy rozptýleny a obě strany se shodly na potřebě spolupráce na vypracování metodiky pro realizaci novely.
- Vicepremiér pro digitalizaci Ivan Bartoš představil pozměňovací návrh k novele o zadávání veřejných zakázek, který má odstranit byrokratické překážky a umožnit efektivní využití kapacit státu. Svaz průmyslu a dopravy vyjádřil obavy ze zneužití této možnosti, ale po schůzce se zástupci vicepremiéra se shodli na potřebě spolupráce na metodice, která bude respektovat Směrnici EU. Evropská komise potvrdila, že navrhovaný pozměňovací návrh není v rozporu s evropskou směrnicí.

Co tedy zkusit nějakou střední cestu? Pojďme dát temperature na 0.5, protože nějaká míra "odvahy" modelu je dobrá. Opakovat se nepůsobí dobře, ale nepřehánět, protože pak stylistické požadavky zastíní informační kvalitu (nastavme na 0.5) a doslovné opakování vstupního textu mi nějak zásadně nevadí, ale i tak papouškování by nepůsobilo ideálně, takže dáme na 0.2. Tady je výsledek:

**Vicepremiér pro digitalizaci Ivan Bartoš představil svůj pozměňovací návrh k novele zákona o veřejných zakázkách, který umožní vertikální spolupráci mezi orgány státu v oblasti IT. Jeho návrh vzbudil obavy ve Svazu průmyslu a dopravy, které adresoval poslancům prostřednictvím dopisu. Bartoš se sešel se zástupci Svazu a svou myšlenku detailně představil. Zvláštní důraz byl kladen na rozptýlení obav z použití nově založené Digitální a informační agentury (DIA) a možného rozporu se Směrnicí EU o zadávání veřejných zakázek. Tato obava byla rozptýlena vyjádřením Evropské komise ze dne 13. ledna 2023. Z jednání s vicepremiérem vyplynulo, že DIA má zavést jednotné postupy a standardy pro přípravu a realizaci projektů, ale není dodavatelem IT služeb pro státní správu.**

To vůbec není špatné! Tenhle model není nijak specificky vyladěn na češtinu a nikdy neslyšel třeba o Digitální a informační agentuře (trénovací data modelů rodiny GPT-3 nejsou mladší, než z roku 2019 a to nic takového neexistovalo). Azure OpenAI Service by mělo už brzy umožnit dotrénovávání modelů a jejich vyšší přizpůsobení. Navíc jak víte z ChatGPT, tenhle model umí dělat i klasifikaci, vyhledávat strukturu a dělat další zajímavé věci, které si zkusíme někdy příště. No a hlavně - za dveřmi je GPT-4, který přijde ke konci tohoto roku. Aktuální verze GPT má 175 miliard (175 a devět nul) trénovacích parametrů, GPT-4 pracuje se 100 biliony (jednička a čtrnáct nul). Kromě toho ale je tu model codex na práci s kódem (toho využívá úžasný GitHub Copilot) nebo Dall-e 2 pro generování obrázků. Ke všemu se dostaneme. Mezitím se ke službě Azure OpenAI Service přihlaste a zkuste si to taky.
