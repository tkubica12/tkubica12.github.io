---
layout: post
published: true
title: Jak nechat jazykový model přemýšlet a při tom používat nástroje podle potřeby s o4-mini. Začnou modely uvažovat v ne-lidštině?
tags:
- AI
---
Chci se dnes věnovat něčemu, co zdá se mi občas lidem ne plně dochází - reasoning modely o3 a o4-mini mohou přistupovat k nástrojům opakovaně v průběhu svého přemýšlení. To hodně zajímavý rozdíl oproti předešlé generaci, tedy o3-mini a o1. Podívejme se proč.

# Chování o3-mini vs. o4-mini
Nástroje jsou čím dál zásadnější pro výsledky vašich AI aplikací a jsou jádrem toho, čemu dnes obvykle lidé říkají AI Agent. Nástroje zahrnují například vyhledávání na Internetu, vyhledávání v databázi dokumentů (RAG), pokročilé datové dotazy do klasických databází, spouštění AI generovaného počítačového kódu, ovládání počítače nebo provolávání nějakých API a tak podobně. 

**o3-mini** funguje tak, že na dotaz uživatele posoudí, zda bude vhodné volat nějaké nástroje, kterých může vybrat hned několik, a jaké parametry bude potřeba nástrojům předat. Následně váš kód (nebo serverová strana u zabudovaných nástrojů třeba v Responses API) nástroje provolá, výstupy připraví a předá je modelu, který začne přemýšlet (reasoning) a když si vše rozmyslí, vygeneruje odpověď. Ta "agency", tedy schopnost se rozhodovat, je na tom začátku, kdy se rozhodne které nástroje a jak použít.

Určitě jste ale narazili na pokročilejší agenty jako je **deep research**. Tam se děje víc věcí, ale jedna je zásadní - agent nefunguje jen na principu otázka a následná odpověď, ale je to cyklický proces, kdy agent se rozhoduje, co udělat dál. Tak například vybere nástroje, přečte si odpovědi, uvažuje a sestaví seznam oblastí, které pro odpověď hrají zásadní roli. Náš kód by pak následně vzal tyto oblasti a pro každou z nich znovu zavolal o3-mini. To by pro každou tuto větev určilo vhodné nástroje (například vyhledání informací o této oblasti na Internetu), sběr výsledků, uvažování, odpověď. Následně v kódu vezmeme všechny odpovědi a znovu zavoláme o3-mini, ať si všechny oblasti pročte a provede syntézu závěrečné odpovědi. Náš kód funguje jako **orchestrátor** a celý tento proces vede na hlubší, přesnější a komplexnější odpovědi možná až na úrovni deep research v různých produktech.

**o4-mini** dělá ale jednu věc jinak. Dokáže si říkat o nástroje **v průběhu uvažování**, ne jen jednou na začátku. Může uvažovat a točit několik cyklů dokud není spokojen a teprve pak generovat odpověď. Samotný reasoning modelu je tedy sám o sobě **"agentic"**, průběžně vyhodnocuje situaci a žádá o provolávání nástrojů dle aktuálního stavu jeho uvažování. Jinak řečeno **reasoning je orchestrátorem**. 

Technicky budeme používat Responses API, ale já chci jít do vlastního nástroje, takže se jeho používání nebude odehrávat na serverové straně. To je vyřešeno přes **streaming** - model mi servíruje události, například přemýšlení, nástroje, generování parametrů nástrojů či finálních odpovědí token po tokenu. 

# Extrémní příklad, kde se to dobře ukáže
Jak si jednoduše ukázat situaci, kdy iterativní používání nástrojů model bude opravdu potřebovat a simulovat tak scénář složitého zkoumání? Vytvořil jsem si nástroj, který vrací "následující vhodné město" k návštěvě na dovolené či chcete-li cestě kolem světa. Nástroj očekává na vstupu buď <START> když jede od začátku, nebo nějaké město po cestě a vrací město následující případně <END> pokud už není kam jet. Model bude mít úkol zjistit celou trasu a je jasné, že v ten okamžik mu nestačí rozhodnout o nástroji jen jednou na začátku. Musí iterativně zjišťovat co je dalšího a získané znalosti uplatňovat pro další hledání. A abych mu to trochu znesnadnil, tak v promptu ještě budu chtít aby až dojde na konec, tak ověřil správnost trasy tím, že půjde zase pozpátku až do začátku.

Celá ukázka je [na mém GitHubu](https://github.com/tkubica12/azure-workshops/tree/main/d-ai-reasoning-with-tools)

Tady je kód:

```python
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
import os
import json
import itertools

# Load environment variables from .env file
load_dotenv()

# Get Azure OpenAI endpoint and model name from environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
MODEL_NAME = os.getenv("MODEL_NAME")

# Set up Azure AD token provider for authentication
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

# Initialize Azure OpenAI client
client = AzureOpenAI(
  azure_endpoint = AZURE_OPENAI_ENDPOINT, 
  azure_ad_token_provider=token_provider,
  api_version="2025-04-01-preview"
)

# Tool that model can use, it is static for demo purposes
def get_next_item(current_item):
    """
    Returns the next item in the static chain of cities to visit.
    Special items:
      - '<START>': returns the first item in the chain.
      - '<END>': returned if there is no next item.
    """
    chain = ["Prague", "Vienna", "Tokyo", "Bangkok", "Paris"]
    if current_item == "<START>":
        return chain[0]
    try:
        idx = chain.index(current_item)
        if idx + 1 < len(chain):
            return chain[idx + 1]
        else:
            return "<END>"
    except ValueError:
        return "<END>"

# Define available tools for the model
tools = [{
    "type": "function",
    "name": "get_next_item",
    "description": "Returns the next city in the chain of cities to visit",
    "parameters": {
        "type": "object",
        "properties": {
            "current_item": {
                "type": "string",
                "description": "The current city. Use '<START>' to get the first city."
            }
        },
        "required": ["current_item"],
        "additionalProperties": False
    }
}]

# Initialize response tracking variables
response_id = None
input_messages = [{"role": "user", "content": "Gather full chain of cities to visit. When using the tool you must make sure that it works by going back in opposite direction once you reach the end of the chain and this way verify results. Make sure to provide details about your reasoning on each step."}]

# Loop until the model stops calling tools
while True: 
    # Create a streaming response from the model
    response = client.responses.create(
        model=MODEL_NAME,
        input=input_messages,
        tools=tools,
        stream=True,
        store=True,
        reasoning={
            "effort":  "high",          # optional: low | medium | high
            "summary": "detailed",      # auto | concise | detailed
        },
    )

    # Collect tool outputs to send back after this streaming pass
    pending_outputs = []

    # Process streaming events from the model
    for event in response:
        if hasattr(event, "response_id"):
            response_id = event.response_id
        if event.type == 'response.output_text.delta':
            print(event.delta, end='', flush=True)
        elif event.type == 'response.function_call_arguments.delta':
            print(event.delta, end='', flush=True)
        elif event.type == 'response.output_item.added':
            if event.item.type == 'function_call':
                print(f"\n🔧 Calling {event.item.name}, arguments: ", end='', flush=True)
            elif event.item.type == 'reasoning':
                print(f"\n🧠 Reasoning")
            elif event.item.type == 'message':
                print("\n💬 Responding")
            else:
                print(f"[DEBUG] Added item: {event.item}")
        elif event.type == 'response.output_item.done':
            if event.item.type == 'function_call' and event.item.name == 'get_next_item':
                # 1. Execute tool
                current_item = json.loads(event.item.arguments)['current_item']
                next_item = get_next_item(current_item)
                print(f"\n🔧 Function call result: {next_item}")

                # 2. Remember messages to send back in next request
                input_messages.append(event.item)                  # the call itself
                pending_outputs.append({                           # its result
                    "type": "function_call_output",
                    "call_id": event.item.call_id,
                    "output": next_item
                })
            elif event.item.type == 'reasoning':
                for seg in event.item.summary:
                    print("🧠", seg.text)
                print("🧠 Finished reasoning")
                input_messages.append(event.item)    # keep reasoning in history
            elif event.item.type == 'message':
                print("\n\n💬 Finished responding.")
            else:
                print(f"\n[DEBUG] Done item: {event.item}")        
    # After stream ends, append all outputs (if any) and decide whether to loop again
    if not pending_outputs:
        break                                   # no more tool calls → finished
    input_messages.extend(pending_outputs)      # add results, then loop

# Cleanup: delete the response if it exists
if response_id is not None:
    client.responses.delete(response_id)
```

Doporučuju si pustit u sebe, ať vidíte jak se to streamuje. K vysvětlení kódu:
- **get_next_item** - nástroj, který vrací další město v řetězci.
- **tools** - definice nástrojů, které model může použít. V našem případě je to jen jeden nástroj, ale může jich být víc a model si je může volit podle potřeby. 
- **User message** - dává za úkol za použití nástrojů odhalit celou trasu a ještě si ji ověřit zpětně tak, že projde znovu odzadu.
- **Responses API** - všimněte si jednak, že registrujeme nástroje, používáme streaming a u reasoning jsem specificky zapnul jednak vysoké úsilí (jsem ochoten platit za víc přemýšlecích tokenů) a jednak poskytování detailního shrnutí přemýšlecích kroků. Na rozdíl od open source modelů, kde si můžete přečíst skutečné thinking tokeny, tady jde jen o bezpečné shrnutí, ne tokeny samotné. Předpokládám, že důvodů je několik, ale hlavní dva budou duševní vlastnictví (právě ten přemýšlecí proces je to nejcennější - proto třeba Deepseek R1 není zajímavý jen z pohledu toho 671B modelu, který je obrovský a zcela mimo hranice domácího hardware a to minimálně 20x, ale i proto, že jeho přemýšlecí proces lze použít k dotrénování menších modelů) a druhý důvod je počítám "bezpečnostní" (přemýšlení není cenzurované a může zahrnovat věci, které jsou pro komerční model nepřípustné ať by šlo o násilí, politiku, rasismus a tak podobně).
- **Eventy** - streamované události, které model generuje. Všimněte si, že máme několik typů událostí. Například `response.output_text.delta` je text, který model generuje a `response.function_call_arguments.delta` je generování argumentů pro nástroj. Pak máme události, které označují začátek a konec nástroje, přemýšlení a odpovědi. Jedeme ve smyčce a sháníme modelu odpovědi na nástroje, o které si řekne, dokud se model nerozhodne, že to stačí a vygeneruje závěrečnou odpověď. 

Podívejme na výstup celého procesu a uvažování modelu. Dojde tam asi ke dvanácti postupným voláním nástroje a sice ne vždy, ale občas o4-mini prozradí jak o tom přemýšlí. Fascinující, když si model pomyslí třeba tohle:

*Můj další krok je zavolat další město po „Tokiu“. Jsem zvědavý, co to bude! Připadá mi to jako malé dobrodružství sbírat názvy těchto měst a jsem nadšený, že mohu pokračovat. Uvidíme, co přinese další. Těším se, že budu sbírat další!*

```markdown

🧠 Reasoning
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"<START>"}
🔧 Function call result: Prague

🧠 Reasoning
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"Prague"}
🔧 Function call result: Vienna

🧠 Reasoning
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"Vienna"}
🔧 Function call result: Tokyo

🧠 Reasoning
🧠 **Proceeding with city collection**

I've got "Tokyo" added to my list of cities, which now includes Prague, Vienna, and Tokyo. My next step is to call for the next city after "Tokyo." I'm curious to see what it will be! It feels like a little adventure gathering these city names, and I'm eager to keep going. Let's see what the next one will bring. I'm excited to collect more!
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"Tokyo"}
🔧 Function call result: Bangkok

🧠 Reasoning
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"Bangkok"}
🔧 Function call result: Paris

🧠 Reasoning
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"Paris"}
🔧 Function call result: <END>

🧠 Reasoning
🧠 **Verifying city sequence**

The function returned "<END>", indicating I've completed forward traversal with cities: Prague, Vienna, Tokyo, Bangkok, and Paris. Now, I need to verify this sequence in reverse. I’ll check that each preceding city returns the correct next one, excluding the end. Beginning with Bangkok, I’ll see that it points to Paris, and continue with Tokyo to Bangkok, Vienna to Tokyo, and Prague to Vienna. Finally, confirming that Paris is last seems essential.      
🧠 **Verifying links in reverse**

I need to go back through the cities I collected to verify the results by calling get_next_item. It seems like I should start from the end, with Paris, and work backwards to check each connection. For each city, I'll expect the correct next city based on the order: Bangkok should point to Paris, Tokyo to Bangkok, Vienna to Tokyo, Prague to Vienna, and finally, <START> should lead to Prague. I could also verify that Paris points to <END> for an extra confirmation.
🧠 **Setting up backward verification**

I’ll do backward verification by checking the links again. We’ll call get_next_item for each city, starting with the last one, Paris. For Paris, I'll expect <END>. Then I'll proceed through Bangkok expecting Paris, Tokyo expecting Bangkok, Vienna expecting Tokyo, Prague expecting Vienna, and finally checking <START> expecting Prague. So, my first step is to verify Paris returns <END>. Then, I'll continue with the rest of the cities to validate the links. Let's start!
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"Paris"}
🔧 Function call result: <END>

🧠 Reasoning
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"Bangkok"}
🔧 Function call result: Paris

🧠 Reasoning
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"Tokyo"}
🔧 Function call result: Bangkok

🧠 Reasoning
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"Vienna"}
🔧 Function call result: Tokyo

🧠 Reasoning
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"Prague"}
🔧 Function call result: Vienna

🧠 Reasoning
🧠 Finished reasoning

🔧 Calling get_next_item, arguments: {"current_item":"<START>"}
🔧 Function call result: Prague

🧠 Reasoning
🧠 Finished reasoning

💬 Responding
Here is the full chain of cities and a detailed account of each step, including forward retrieval and backward verification.

Forward Retrieval  
1. Step 1: call get_next_item("<START>") to get the first city  
   • Result: “Prague”  
2. Step 2: call get_next_item("Prague")  
   • Result: “Vienna”  
3. Step 3: call get_next_item("Vienna")  
   • Result: “Tokyo”  
4. Step 4: call get_next_item("Tokyo")  
   • Result: “Bangkok”  
5. Step 5: call get_next_item("Bangkok")  
   • Result: “Paris”  
6. Step 6: call get_next_item("Paris")  
   • Result: “<END>” — indicates we’ve reached the end of the chain

Collected chain (in order):  
1. Prague  
2. Vienna  
3. Tokyo  
4. Bangkok  
5. Paris  

Backward Verification  
Starting from the end, we call get_next_item on each preceding city to confirm it yields the correct successor:

1. Verify last city: call get_next_item("Paris") → “<END>” (expected)  
2. call get_next_item("Bangkok") → “Paris” (matches)  
3. call get_next_item("Tokyo") → “Bangkok” (matches)  
4. call get_next_item("Vienna") → “Tokyo” (matches)  
5. call get_next_item("Prague") → “Vienna” (matches)  
6. call get_next_item("<START>") → “Prague” (matches)

All expected outputs were confirmed. The chain is valid.

Final confirmed itinerary of cities to visit:  
Prague → Vienna → Tokyo → Bangkok → Paris

💬 Finished responding.
```

# Závěr
Před rokem jste museli běžný model promptem instruovat, ať to bere "krok za krokem" a ohýbat ho, aby se pokoušel si věci rozmýšlet, což sice reasoning zlepšovalo, ale ne tak výrazně. Lepších výsledků bylo možné dosáhnout v multi-agent scénáři, kdy jste nechali model mluvit v různých rolích sama se sebou a s různými nástroji nebo použili pokročilou orchestraci jako u deep research. Dnešní schopnost nejet uvažovat, ale v průběhu přemýšlení volit nástroje a průběžně zpracovávat jejich výsledky, je zásadní krok dopředu. V jedné "otáčce" tak zvládnete mnohem víc i bez orchestrace. Myslím, že to může vést na o dost lepší výsledky, protože umožňujete modelu zůstat ve svém "vnitřním světě", v "jazyce v hlavě" a teprve po ukončení uvažování to přetavit do odpovědi. Na Deepseek R1 jsme viděli, že pokud je modelu ponechána volnost, uvažuje podivným mixem angličtiny a čínštiny. Očekávám, že v budoucnu vzniknou modely, jejichž proces uvažování nebude používat lidský jazyk, ale něco efektivnějšího s čím přijdou sami a do jazyka se to přeloží až na výstupu. 