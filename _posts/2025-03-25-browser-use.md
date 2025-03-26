---
layout: post
published: true
title: Je krumpáč skladem? A funguje slevový kód? Ať to zjistí AI Agent! A co dál? Co třeba herní kouč?
tags:
- AI
---
Je dnes docela módní říkat všemu **AI Agent**. Osobně pro takové označení chci vidět dvě věci - schopnost přijímat **samostatná rozhodnutí** (tedy ne jen přeposlat otázku do LLM a vrátit odpověď) a schopnost **interagovat s okolním světem**. Například běžný "chat nad Sharepointem" mi do této definice tolik nesedí, ale pokročilý RAG, o kterém jsem psal nedávno, kde agent přeformulovává otázky, vytváří si vlastní query strategii, skládá SQL dotazy, reaguje na jejich výsledky a svou strategii jim přizpůsobuje, to už mi rozhodně sedí (například Deep Research). Pořád je ale "read only" a není vpuštěn do skutečného lidského světa. Dnes zkusíme ale něco co je - **AI agent co se mi hrabe v počítači**.

Pojďme si nejprve ukázat příklad s využitím projektu browser-use a budeme nakupovat krumpáč. Pak si řekněme něco o computer use obecněji a kde už to všude je. Následně se chci podívat do blízké budoucnosti - například na herního kouče a dva směry, kterými se může ubírat přebírání ovládání aplikací AI agenty.

# Krumpáč v Baumaxu s browser-use
Následující test jsem provedl s využitím open source projektu [browser-use](https://github.com/browser-use/browser-use). Instalace je jednoduchá a pro klikání na webu využívá agent [Playwright](https://playwright.dev/) - velmi oblíbený open source projekt od Microsoftu na testování webových aplikací.

Scénář je následující. Pokud chci třeba zjistit jaká je otevírací doba obchodu, stačí mi na to určitě web search, což je jeden z nástrojů, který mohou AI agenti využívat. Důvodem je, že tahle informace je dohledatelná vyhledáním a přečtením stránky. Něco jiného ale je zjištění stavu zásob, to už je typicky věc dynamická stejně jako vložení slevového kódu při placení nákupního košíku. Tady nám jednoduché hledání nepomůže a je to tak dobrý příklad úlohy pro browser-use.

Kód je skandálně jednoduchý:

```python
from langchain_openai import AzureChatOpenAI
from browser_use import Agent
from pydantic import SecretStr
from dotenv import load_dotenv
import os

load_dotenv()

import asyncio

llm = AzureChatOpenAI(
    model="gpt-4o",
    api_version='2024-10-21',
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT', ''),
    api_key=SecretStr(os.getenv('AZURE_OPENAI_KEY', '')),
)

async def main():
    agent = Agent(
        task="Je v Baumaxu na prodejně v Letňanech dostupný krumpáč skladem? Pokud ano, lze při platbě uplatnit slevový kód JARO10?",
        llm=llm,
        use_vision=True, 
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
```

Tady se podívejte na celé video, kde je vidět jak si agent najde zajímavá místa na stránce a pak do nich kliká.

<div class="video-container">
  <iframe width="100%" height="415" src="https://www.youtube.com/embed/D0b3dZm1Z4Y" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

Agent se nejprve rozhodne vyhledávat na Googlu.

```markdown
INFO     [agent] 🚀 Starting task: Je v Baumaxu na prodejně v Letňanech dostupný krumpáč skladem? Pokud ano, lze při platbě uplatnit slevový kód JARO10?
INFO     [agent] 📍 Step 1
INFO     [agent] 🤷 Eval: Unknown - Starting point is an empty page.
INFO     [agent] 🧠 Memory: Task: Find out if Baumax in Letňany has a pickaxe in stock and check if the discount code JARO10 can be applied. Current step 1/100.
INFO     [agent] 🎯 Next goal: Search for Baumax Letňany to locate the store and check stock availability for the pickaxe.
INFO     [agent] 🛠️  Action 1/1: {"search_google":{"query":"Baumax Letňany"}}
INFO     [controller] 🔍  Searched for "Baumax Letňany" in Google
```

Výsledky se vrátili a rozhodl se přijmout cookie, aby na stránku viděl.

```markdown
INFO     [agent] 📍 Step 2
INFO     [agent] 👍 Eval: Success - Google search results for Baumax Letňany are accessible.
INFO     [agent] 🧠 Memory: Task: Verify Baumax Letňany stock for a pickaxe and applicability of JARO10 discount code. Currently interacting with Google results (Step 2/100).
INFO     [agent] 🎯 Next goal: Accept all cookies to proceed with exploring Google search results.
INFO     [agent] 🛠️  Action 1/1: {"click_element":{"index":5}}
INFO     [controller] 🖱️  Clicked button with index 5: Přijmout vše
INFO     [agent] 📍 Step 3
INFO     [agent] 👍 Eval: Success - Cookies were accepted, and search results are now fully visible.
INFO     [agent] 🧠 Memory: Task is to confirm Baumax Letňany stock for a pickaxe and discount code JARO10 applicability. Progress is at Step 3/100.
INFO     [agent] 🎯 Next goal: Click on the entry for Baumax Letňany store page to identify stock availability.
INFO     [agent] 🛠️  Action 1/1: {"click_element":{"index":37}}
WARNING  [controller] Element not clickable with index 37 - most likely the page changed
INFO     [agent] 📍 Step 4
INFO     [agent] ⚠ Eval: Failed - Attempt to interact with a navigation element resulted in a page change which interrupted the action.
INFO     [agent] 🧠 Memory: Now present on the Baumax Praha 9 Letňany webpage. Cookies prompt visible again which needs to be resolved before further exploration. Identifying stock for pickaxe and coupon application still underway. Current step: 5/100.
INFO     [agent] 🎯 Next goal: Accept cookies with 'Povolit všechny' to allow website functionality.
INFO     [agent] 🛠️  Action 1/1: {"click_element":{"index":38}}
INFO     [controller] 🖱️  Clicked button with index 38: Povolit všechny
```

Po otevření odkazu dal agent vyhledat krumpáč.

```markdown
INFO     [agent] 📍 Step 5
INFO     [agent] 👍 Eval: Success - Cookies were accepted, and now fully navigating Baumax Letňany store page.
INFO     [agent] 🧠 Memory: Current URL indicates the store page of Baumax Letňany. Task focus remains on checking stock for pickaxes and discount code JARO10 applicability. Current step: 6/100.
INFO     [agent] 🎯 Next goal: Search for pickaxe in Baumax store using input box to locate stock availability.
INFO     [agent] 🛠️  Action 1/2: {"input_text":{"index":13,"text":"krumpáč"}}
INFO     [agent] 🛠️  Action 2/2: {"click_element":{"index":14}}
INFO     [controller] ⌨️  Input krumpáč into index 13
INFO     [agent] Something new appeared after action 1 / 2
```

Jeden vybral.

```markdown
INFO     [agent] 📍 Step 6
INFO     [agent] 👍 Eval: Success - Input and search for 'krumpáč' displayed relevant products in Baumax Letňany.
INFO     [agent] 🧠 Memory: Products including Krumpáč 2,5kg and Krumpáč 2,5 kg 95 cm appear visible, prices confirmed. Checking their status and further details on JARO10 discount remains. Step done 6/100.
INFO     [agent] 🎯 Next goal: Click on the first Krumpáč 2,5kg link to verify product stock and explore payment options for discount codes
INFO     [agent] 🛠️  Action 1/1: {"click_element":{"index":18}}
INFO     [controller] 🖱️  Clicked button with index 18: Krumpáč 2,5kg
```

Přidal ho do košíku a zkontroloval skladovou dostupnost.

```markdown
INFO     [agent] 📍 Step 7
INFO     [agent] 👍 Eval: Success - Navigated and confirmed Krumpáč details and available stock.
INFO     [agent] 🧠 Memory: Stock status for Krumpáč 2,5kg is 'zboží je dostupné'. Next focus is confirming discount code JARO10 applicability (Step 8/100).
INFO     [agent] 🎯 Next goal: Verify whether a discount code can be applied during checkout or at payment stage.
INFO     [agent] 🛠️  Action 1/1: {"click_element":{"index":44}}
INFO     [controller] 🖱️  Clicked button with index 44: Přidat do košíku
```

Přešel k pokladně.

```markdown
INFO     [agent] 📍 Step 8
INFO     [agent] 👍 Eval: Success - Product added to cart, now verifying payment details and discount code JARO10.
INFO     [agent] 🧠 Memory: Krumpáč 2,5 kg is in Baumax Letňany stock and added to cart. Next focus is verifying if discount code JARO10 is applicable. Step continues 9th Out Of 100.
INFO     [agent] 🎯 Next goal: Click on 'K pokladně' for progress towards payment options verification and discount code stage.
INFO     [agent] 🛠️  Action 1/1: {"click_element":{"index":38}}
INFO     [controller] 🖱️  Clicked button with index 38: K pokladně
```

Zadal slevový kód.

```markdown
INFO     [agent] 📍 Step 9
INFO     [agent] 👍 Eval: Success - Navigated to the cart with Krumpáč 2,5kg added successfully to checkout options.
INFO     [agent] 🧠 Memory: The pickaxe is in the cart, its availability is confirmed. Current focus remains on applying the JARO10 discount code. Step continues with current exploration - verification.
INFO     [agent] 🎯 Next goal: Input JARO10 in the discount code field to check applicability and recalculate order total.
INFO     [agent] 🛠️  Action 1/2: {"input_text":{"index":49,"text":"JARO10"}}
INFO     [agent] 🛠️  Action 2/2: {"click_element":{"index":50}}
INFO     [controller] ⌨️  Input JARO10 into index 49
INFO     [controller] 🖱️  Clicked button with index 50:
```

Zjistil, že je neplatný a tím má splněno.

```markdown
INFO     [agent] 📍 Step 10
INFO     [agent] ⚠ Eval: Failed - The discount code JARO10 is invalid as indicated by 'Neplatný kód slevy JARO10'.
INFO     [agent] 🧠 Memory: Stock is available for Krumpáč 2,5kg at Baumax Letňany. However, JARO10 discount code cannot be applied. Task is completed after verifying both stock and discount (Step 10/100).
INFO     [agent] 🎯 Next goal: Finalize the task and provide results.
INFO     [agent] 🛠️  Action 1/1: {"done":{"text":"Krumpáč 2,5kg is in stock at Baumax Letňany for 399 Kč. However, the discount code JARO10 is invalid and cannot be applied.","success":true}}
INFO     [agent] 📄 Result: Krumpáč 2,5kg is in stock at Baumax Letňany for 399 Kč. However, the discount code JARO10 is invalid and cannot be applied.
INFO     [agent] ✅ Task completed
INFO     [agent] ✅ Successfully
```

# Computer Use
Computer use je obecněji zaměřen na interakci s aplikacemi a systémy počítače na základě sledování obrazovky a klikání či psaní na klávesnici. Dva komerční produkty s plnou podporou jsou **Anthropic Computer Use v Claude 3.5** a **OpenAI Operator**. Google o tom hovořil, ale reálný výstup pokud vím ještě nemá a Microsoft je na tom podobně s tím, že demonstroval, jak Windows Copilot pomáhá uživateli s nastavením počítače. Kromě toho jsou tu i open source projekty, například právě použitý browser-use nebo [OmniParser](https://www.microsoft.com/en-us/research/articles/omniparser-v2-turning-any-llm-into-a-computer-use-agent/) od Microsoftu.

Zásadní výhodou webu je, že AI ho může rozebrat přes accessibility snapshot v Playwrightu, což je výpočetně méně náročné, než screenshot. Nicméně snímek obrazovky používá browser-use taky (kombinuje to) a pro computer use obecně to je důležité, protože ne-webové aplikace jinak neuděláte.

Nicméně je tady jeden "slon v místnosti" - přenášení obrazu do cloudu znamená velké pásmo. Jak se bude zvyšovat efektivita modelů bude během roku či dvou běžné provozovat alespoň tu obrazovou část modelu na lokálním počítači. To je důvod, proč Microsoft zavedl kategorii **Copilot+ PC** obsahující **NPU** čipy zaměřené na AI výpočty (kolem 40 TOPS). **Apple** na akceleraci AI pracuje rovněž v čipech používá **Neural Engine jádra** (M4 má až 16 jader a 38 TOPS a nedávno uvedená M3 Ultra má 32, ale starších pomalejších jader - dá se tedy očekávat, že někdy později bude M4 Ultra znovu se zdvojenými jádry).

Všimněte si - AI železo v počítači je nezávislé na GPU a AI tak může obstojně fungovat i na ne-herním počítači. NPU dnes vytáhne 40 TOPS z 10W spotřeby a přidávají méně jak 50 USD do ceny procesoru. Letos přijde AMD Strix Point a Intel Lunar Lake a vypadá to na 100 TOPS při 20W spotřebě.

# Herní kouč jako pokročilý příklad do budoucna
Před pár dny oznámil Microsoft **Copilot for Gaming** a myslím, že je to dobrý příklad computer use. Nechám stranou co v první verzi bude nebo nebude umět, spíše se zamyslím nad konceptem. Tak jak se dramaticky snižuje cena tokenů při stejné inteligenci (např. destilované mini modely), tak lze předpokládat, že nebude problém, aby během roku běžel multi-modální AI model přímo na herním počítači a doslova vám koukal přes rameno. Vidí co vidíte vy, kouká jak vám to jde, jakou máte strategii a nabídne pomoc. Řekne, když se vám něco podaří, doporučí jak to ještě zlepšit a tak podobně. To má za mě zásadní dopad na oba konce hráčského spektra - začátečníky i herní šílence:

- Začátečník bude mít daleko menší učící křivku a bude mít možnost se rychleji dostat na úroveň, kdy si hru užije. Tím se hra stane přístupnější těm co začínají nebo těm jako já, kteří obvykle dělají něco jiného, ale párkrát do roka si několikadenní herní sprint rádi udělají.
- Herní šílenci budou muset jít za rámec běžné strategie, protože tu Copilot vykecá postupně všem. Musí přicházet s unikátní strategií a navíc ji měnit, protože ji možná bude AI okoukávat a provalovat. Tím vzroste obtížnost pro ty nejlepší hráče, což je výzva která je láká, a přesto nejde o nefér souboj s AI. Stále zůstává efekt zábavy člověk proti člověku, jen díky dobrým AI trenérům bude víc lidských soupeřů hodno se s vámi utkat.

# Budoucnost aplikací ve světě s AI agenty
Baumax troufnu si odhadnout nepočítal s tím, že jeho stránky budou využívat AI Agenti a možná ještě neví, že v budoucnu to nebudou lidé, co budou na jejich stránkách nakupovat, ale jejich AI agenti. Na to lze ze strany firem myslím reagovat na následující škále:
- **Odmítnutí a zákazy**: V mých testech browser-use se ukázalo, že agenta lze dnes snadno oslepit - často se nedostane přes různé cookie pop-upy. Určitě tedy půjde mu to udělat co nejtěžší a efektivně agentům práci s aplikací znemožnit. Navíc očekávám, že vznikne standard, který budou slušní agenti dodržovat, kdy majitel aplikace může vyjádřit nesouhlas s takovým zacházením. Dnes existuje **robots.txt** zaměřený na signalizaci nesouhlasu pro vyhledávače a postupně se rozšiřuje i o AI crawlery apod. Nicméně - s takovýmto přístupem jste **neviditelní** pro AI agenty a stojíte mimo tento potenciální kanál interakce se zákazníky, což vás za nějakou dobu může mrzet.
- **Přizpůsobení a spolupráce**: Existují nástroje jak zjistit, zda je vaše stránka dobře přístupná osobám s nějakými nedostatky - například zda lidé se zrakovými vadami mohou číst dostatečně kontrastní text, barevné kombinace nečiní prvky neviditelnými pro barvoslepé nebo zda ovládací prvky mají potřebné atributy pro čtečky obrazovky pro slepce. Myslím, že podobným způsobem je možné zajistit, že aplikace je dobře přístupná pro AI agenty. Tato cesta má tu výhodu, že to je stále jedna stejná stránka, která vyhovuje jak běžné populaci, tak populaci s nějakými těžkostmi tak i AI agentům. Další varianta je, že vytvoříte automaticky jednoduchou markdown verzi své stránky viz [llms.txt](https://llmstxt.org/).
- **Převzetí iniciativy - vlastní AI agent**: Přestože pro to zatím není žádný standard, očekávám, že nejlepším řešením bude AI přístupům vyčlenit něco speciálního - kromě UI pro lidi vytvořit i vlastního AI agenta, který bude dostupný pro ostatní agenty. Tohle umožní jít o mnoho kroků dál. AI agent zákazníka, který si jen kliká na webu, si přečte vaši nabídku, ale když dorazí na "pro enterprise licence nás kontaktujte", tak vám sice může napsat, ale je to pro vás nevýhoda. Agent-to-agent ale mohou začít vyjednávat rovnou - váš agent zná vaše portfolio, obchodní strategii, marže, existující klienty, takže se zájemcem může všechno rovnou dohodnout. Až budu mít svého AI asistenta, tak přesně tohle od něj budu chtít - nechci ztrácet čas tím, že budu s nějakým obchodníkem hrát přetahovanou o slevách.
