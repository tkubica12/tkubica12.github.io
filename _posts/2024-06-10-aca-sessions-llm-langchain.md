---
layout: post
published: true
title: Váš vlastní code interpreter jako služba v Azure Container Apps s LLM a LangChain
tags:
- AI
- AzureContainerApps
---
Jazykové modely, jak je z názvu dost patrné, jsou skvělé v práci s jazykem a ty opravdu velké jako je OpenAI, Anthropic, Gemini nebo velký Mistral zvládají velmi dobře i logické uvažování a další disciplíny. I ty nejlepší jsou ale zatím poměrně špatné v matematice nebo nějaké klasické práci s daty (například dát jim 1000 řádek CSV a chtít z toho něco počítat, to není něco, co dobře zvládnou). Velmi zajímavé ale je, že dokáží skvěle napsat Python program, který přesně tohle udělá. Jinak řečeno LLM je takový inteligentní procesor, který při troše prompt engineeringu nebo finetuningu (a ten už ve velkých modelech je pro vás hotový) dokáže využívat různých klasických nástrojů, aby mu pomáhali v práci. Něco jako když si člověk vezme k ruce kalkulačku. 

Dobře, AI si tedy potřebuje vygenerovat nějaký kód a požádá vás, zda ho pro něj spustíte a výsledky mu vrátíte. V případě Azure OpenAI služby tohle lze dělat přímo na backendu přes Assistants API (této funkci se říká Tools a konkrétně tohle je Code Interpreter), ale někdy můžete chtít tohle běžet vyloženě ve vašich instancích nebo to použít i s nástroji, které tohle v API nemají - například open source modely typu Phi-3, Llama 3 nebo Mistral jako služba v Azure nebo lokálně na vašem počítači. Jak ale kód spustit bezpečně, tedy tak, aby se někomu nepodařilo správně formulovaným dotazem přinutit model vygenerovat kód co někam nahraje data nebo zkusí nějaké útoky a tak podobně? Potřebujeme pro každého uživatele tohle spouštět zcela izolovaně od ostatních a bez možnosti nějakého úniku kódu do okolí.

Tohle přesně pro nás může v Azure zařídit Azure Container Apps dynamic sessions.

# Azure Container Apps dynamic session a první pokus přes portál
Vytvořil jsem tzv. pool v portálu a máme zde možnost si to jednoduše vyzkoušet. Nejprve dosadím nějaké session ID a ACA pro něj vytvoří naprosto izolované prostředí, který je ve formě odlehčeného VM včetně VT-X izolace (tzn. na úrovni hypervisoru). Je to velmi rychlé, jak je to možné? Tak jednak nejsou to nějaká obří VM, ale spíše něco jako Kata kontejnery (orchestrované jako kontejnery, ostatně Azure Container Apps mají pod kapotou Kubernetes, ale runtime neběží jako kontejner ve sdíleném kernelu, ale jako miniVM). Ta tedy dokáže nastartovat hodně rychle. Nicméně to hlavní kouzlo je v tom, že dynamic sessions fungují podobně jako třeba App Service nebo Azure Functions v consumption plánu - drží neustále pool předstartovaných instancí. Celé prostředí tedy běží, jen není nikomu přiřazené, takže jakmile je potřeba, tak je nesmírně rychle k dispozici (já obvykle naměřím něco kolem 50-100ms, což je masakr).

[![](/images/2024/2024-06-10-08-45-06.png){:class="img-fluid"}](/images/2024/2024-06-10-08-45-06.png)

Kromě předpřipraveného kontejneru, ve kterém nechybí Python a některé populární knihovny, si můžete přinést i svůj vlastní image. V takovém případě si v rámci nastavení říkáte, kolik jich chcete mít přednastartovaných (za ty navíc platíte). V tomto režimu si můžete dokonce i vybrat, jestli má kontejner zamezenou komunikaci ven (doporučuji a te to taky výchozí nastavení) nebo ne. 

Billing funguje tak, že platí za čas běhu těchto session ale s tím, že minimální běh je 5 minut (po této době se session smaže). Není to tedy tak flexibilní jako u klasického serverless, ale zase VT-X izolace (kód, kterému nevěříte) a to jak funguje API a integrace do nástrojů typu LangChain za to stojí. Code interpreter stojí 0,03 USD za hodinu session, případně 0,026 a 0,025 USD při zakoupení 1y nebo 3y Savings Plan. To vůbec není špatná cena - kontejner s jedním CPU v ACA by vyšel třeba 3x dráž, což je dobré pokud v něm můžete běžet několik session (= je to váš vlastní kód, kterému věříte), ale pokud byste potřebovali lepší izolaci, je dynamic sessions ve finále levnější.

# API a jeho využití včetně stažení souboru
Tady jsem použil Azure CLI pro založení sessions a získání tokenu a následně využívám curl, abychom se podívali na to, jak je API jednoduché na používání.

```bash
# Install CLI extension
az extension add --name containerapp --upgrade --allow-preview true -y

# Create a resource group
az group create --name d-aca-sessions --location eastus

# Create session pool
az containerapp sessionpool create \
    --name mypool \
    --resource-group d-aca-sessions \
    --location eastus \
    --container-type PythonLTS \
    --max-sessions 100 \
    --cooldown-period 300 \
    --network-status EgressDisabled

# Get session management API endpoint
export sapi=$(az containerapp sessionpool show \
    --name mypool \
    --resource-group d-aca-sessions \
    --query 'properties.poolManagementEndpoint' -o tsv)

# Get Entra token
export token=$(az account get-access-token --resource https://dynamicsessions.io --query accessToken -o tsv)

# Execute code in new session
export sessionId="mysession1234"

curl -X POST "$sapi/code/execute?api-version=2024-02-02-preview&identifier=$sessionId" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d '{
    "properties": {
        "codeInputType": "inline",
        "executionType": "synchronous",
        "code": "import socket\nprint(f\"Hello from {socket.gethostname()}!\")"
    }
}'
```
```json
{"$id":"1","properties":{"$id":"2","status":"Success","stdout":"Hello from aa23222b-4a8f-44ec-a7e3-6c735abc374a!\n","stderr":"","result":"","executionTimeInMilliseconds":10}}
```

Jednoduché a účinné, odpověď zpět velmi rychle. Zavolal jsem v rámci stejné session podruhé, zapsal kódem soubor a ten si stáhl.

```bash
# Execute code in existing session writing some file
curl -X POST "$sapi/code/execute?api-version=2024-02-02-preview&identifier=$sessionId" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d '{
    "properties": {
        "codeInputType": "inline",
        "executionType": "synchronous",
        "code": "with open(\"/mnt/data/hello.txt\", \"w\") as f:\n    f.write(\"Hello from session!\")"
    }
}'
```
```json
{"$id":"1","properties":{"$id":"2","status":"Success","stdout":"","stderr":"","result":"","executionTimeInMilliseconds":8}}
```

```bash
# Check session files
curl "$sapi/files?api-version=2024-02-02-preview&identifier=$sessionId" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json"
```
```json
{"$id":"1","value":[{"$id":"2","properties":{"$id":"3","filename":"hello.txt","size":19,"lastModifiedTime":"2024-06-08T18:57:50.2464287Z"}}]}
```
```bash
# Download file from session
curl "$sapi/files/content/hello.txt?api-version=2024-02-02-preview&identifier=$sessionId" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json"
```
```
Hello from session!
```

# První kroky v SDK pro LangChain
API je pěkné, ale většinou bude chtít přímo integraci do některého z frameworků na práci s jazykovými modely a možnost pracovat s nimi v kombinaci s různými nástroji jako je právě interpretace Pythonu. Azure Container Apps dynamic sessions podporuje tři velmi populární - LangChain (etalon hlavně pro Python, ale umí i Javascript a Javu), SemanticKernel (skvělý pro .NET, ale i Java a TypeScript) nebo LlamaIndex (Python a TypeScript), aktuálně pouze pro jejich Python varianty.

V případě LangChain se přihlašuje do Azure přes knihovnu DefaultAzureCredential, takže si sama rovnou najde přihlášení z Azure CLI (pokud jedete ze svého notebooku) a snadno přidáte věci jako je Managed Identity, Identity Federation (třeba do AKS či ACA) nebo Service Principal. 

Začnu jednoduchým příkladem - mám kód a chci ho spustit v dynamic session podobně, jak jsme to dělali přímo s API.

```python
from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
import json

tool = SessionsPythonREPLTool(
	pool_management_endpoint="https://eastus.dynamicsessions.io/subscriptions/d3b7888f-c26e-4961-a976-ff9d5b31dfd3/resourceGroups/d-aca-sessions/sessionPools/mypool",
)

code = """
# Comments are ignored

a = 5
b = 8
x = a*b

# Whatever gets printed to stdout is captured
print(f"Answer is {x}")

# Last expression is returned as the output
x
"""

output = tool.execute(code)
print(json.dumps(output, indent=2))
```

```json
{
  "$id": "2",
  "status": "Success",
  "stdout": "Answer is 40\n",
  "stderr": "",
  "result": 40,
  "executionTimeInMilliseconds": 10
}
```

Dále si vyzkoušíme nahrání souboru do prostředí. Připravil jsem si CSV soubor se jmény, zeměmi a věkem a použijeme Python kód pro jeho zpracování, konkrétně vypočítání průměrného věku.

```python
from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
import json

tool = SessionsPythonREPLTool(
    pool_management_endpoint="https://eastus.dynamicsessions.io/subscriptions/d3b7888f-c26e-4961-a976-ff9d5b31dfd3/resourceGroups/d-aca-sessions/sessionPools/mypool",
)

upload_metadata = tool.upload_file(
    local_file_path="./people.csv", remote_file_path="important_data.json"
)

code = f"""
import csv
import statistics

# Read the data from the CSV file
with open('{upload_metadata.full_path}', 'r') as f:
    reader = csv.DictReader(f)
    ages = [int(row['Age']) for row in reader]

# Calculate the average age
statistics.mean(ages)
"""

output = tool.execute(code)
print(json.dumps(output, indent=2))
```

```json
{
  "$id": "2",
  "status": "Success",
  "stdout": "",
  "stderr": "",
  "result": 36.017857142857146,
  "executionTimeInMilliseconds": 27
}
```

Co kdybychom nechali Python nakreslit nějaký graf? Výstup z matplotlib dostaneme přes API zpět jako obrázek zakódovaný do base64.

```python
from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
import json

tool = SessionsPythonREPLTool(
	pool_management_endpoint="https://eastus.dynamicsessions.io/subscriptions/d3b7888f-c26e-4961-a976-ff9d5b31dfd3/resourceGroups/d-aca-sessions/sessionPools/mypool",
)

code = """
import numpy as np
import matplotlib.pyplot as plt

# Generate values for x from -1 to 1
x = np.linspace(-1, 1, 400)

# Calculate the sine of each x value
y = np.sin(x)

# Create the plot
plt.plot(x, y)

# Add title and labels
plt.title('Plot of sin(x) from -1 to 1')
plt.xlabel('x')
plt.ylabel('sin(x)')

# Show the plot
plt.grid(True)
plt.show()
"""

result = tool.execute(code)
print(f"Output is of type {result['result']['type']} in format {result['result']['format']}")

import base64

# Get the base64 encoded data
encoded_data = result['result']['base64_data']

# Decode the data
decoded_data = base64.b64decode(encoded_data)

# Write the data to a file
with open('output.png', 'wb') as f:
    f.write(decoded_data)
```

[![](/images/2024/2024-06-09-11-28-28.png){:class="img-fluid"}](/images/2024/2024-06-09-11-28-28.png)

# LangChain a Azure OpenAI s vlastním Code Interpreter nástrojem v Azure Container Apps
Na závěr se pusťme do toho klíčového scénáře - umožníme LLM využít nástroje, konkrétně možnost napsat si kód a nechat si ho spustit (code interpreter). Díky integraci Azure Container Apps dynamic session do LangChain to je velmi snadné.

Zaregistrujeme si nástroj jako v předchozích případech a také použiji llm komponentu, konkrétně AzureChatOpenAI (nezapomeňte naplnit .env soubor přístupovými parametry). Všimněte si, že na jeho místě může být i jakýkoli jiný, takže řešení je hodně univerzální a může využívat klidně i plně lokálních komponent. Dál jen použiji předpřipravený systémový prompt a koncept agenta, kterému dáme náš nástroj k dispozici. O vše ostatní se postará LangChain. Naše otázka je okopírovaná z dokumentace a je to něco, s čím by si jazykový model sám poradil hodně špatně, ale s nástrojem mu to půjde skvěle.

```python
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
from langchain_openai import AzureChatOpenAI
import dotenv

dotenv.load_dotenv()

llm = AzureChatOpenAI(model="gpt-4o", temperature=0, verbose=True)
prompt = hub.pull("hwchase17/openai-functions-agent")

tool = SessionsPythonREPLTool(
    pool_management_endpoint="https://eastus.dynamicsessions.io/subscriptions/d3b7888f-c26e-4961-a976-ff9d5b31dfd3/resourceGroups/d-aca-sessions/sessionPools/mypool",
)

agent = create_tool_calling_agent(llm, [tool], prompt)
agent_executor = AgentExecutor(
    agent=agent, tools=[tool], verbose=True, handle_parsing_errors=True
)

response = agent_executor.invoke(
    {
        "input": "what's sin of pi . if it's negative generate a random number between 0 and 5. if it's positive between 5 and 10."
    }
)
```

Podívejme se na výpis co se dělo. LLM si nejprve vygenerovalo Python kód pro získání sinusu z pi. Ten LangChain poslal do Azure Container Apps dynamic session pro spuštění a výsledky vrátil do LLM. Protože byl výsledek kladný, požádalo OpenAI znovu o spuštění jiného Python kódu, tentokrát pro vygenerování náhodného čísla mezi 5 a 10 a na závěr z výsledku připravil textovou odpověď. Klasická ukázka Code Interpreter.

```
> Entering new AgentExecutor chain...

Invoking: `Python_REPL` with `import math
result = math.sin(math.pi)
result`


{
  "result": 1.2246467991473532e-16,
  "stdout": "",
  "stderr": ""
}
Invoking: `Python_REPL` with `import random
random_number = random.uniform(5, 10)
random_number`
responded: The sine of \(\pi\) is approximately \(1.2246467991473532 \times 10^{-16}\), which is a very small positive number.

Since it is positive, I will generate a random number between 5 and 10.

{
  "result": 6.443740307405746,
  "stdout": "",
  "stderr": ""
}

The random number generated between 5 and 10 is approximately \(6.44\).

> Finished chain.
```

Pokud používáte Azure OpenAI službu a její Assistants API, tak ta má přímo v sobě funkce nástrojů včetně Code Interpreter jako služba. Možná ale musíte z regulatorních důvodů tuto integraci mít víc pod kontrolou nebo potřebujete použít jiný model, jehož API tyto možnosti nenabízí, je Azure Container Apps dynamic session skvělá volba a hlavně nabízí integraci do klíčových frameworků LangChain, SemanticKernel i LlamaIndex. Vyzkoušejte!