---
layout: post
published: true
title: Přidejte si vlastní nástroje do GitHub Copilot s napojením na MCP server
tags:
- AI
- GitHub
---
GitHub Copilot je možné rozšířit o extension, což je věc specifická pro GitHub, ale nově přišla ještě jiná možnost - využití standardu MCP pro připojení nástrojů. To je sice zatím omezeno na Visual Studio Code a pouze Agent režim, takže nefunguje například na github.com nebo v mobilní aplikaci (plnohodnotná extension ano), ale standardizace je nesmírné lákavá a MCP prostě frčí. Pojďme vyzkoušet.

# Model Context Protocol (MCP)
Model Context Protocol (MCP) je standardizovaný protokol pro komunikaci mezi AI modely a externími nástroji. Přímo tvůrci z Anthropicu o něm mluví jako o "USB-C" pro nástroje. Celé je to navržené tak, že AI agent se může napojit na hned několik MCP serverů a každý tento server může servírovat několik nástrojů. Server podporuje discovery nabízených nástrojů, takže model má k dispozici informace co který dělá a jaké vyžaduje parametry. V tomto je to stejné jako třeba registrace tools v OpenAI API nebo v LangChain. Výborné u MCP ale je, že kromě standardizace a možnosti lokální režimu podporuje i transport po síti, konkrétně Server-Sent Events (SSE). MCP tak může běžet kdekoli a může tak vzniknout něco jako tržiště hostovaných MCP, což je hodně zajímavé. Už dnes existuje dost [MCP Serverů](https://github.com/modelcontextprotocol/servers). Typicky nechybí napojení na cloudové služby, databáze nebo třeba GitHub (na tento MCP server se podíváme příště).

# Vytvořme si vlastní MCP server
Vytvoření MCP serveru není složité, protože na to existují knihovny například do Pythonu. Já jsem se rozhodl udělat nástroj pro generování řetězců na základě vstupních podkladů jako je délka, zda použít malá či velká písmena, čísla nebo speciální znaky. A to celé ve dvou variantách - náhodný řetězec a také "unikátní" řetězec, který bude fungovat z nějakého seedu, tedy pro daný vstup vygeneruje pokaždé stejný výstup. Oboje často používám v různých Infrastructure as Code skriptech, kde je na to typicky zabudovaná podpora. Ale co když bych chtěl něco podobného přímo v GitHub Copilot, například když má udělat Bash skript s nějakým unikátním názvem storage accountu a tak podobně, kde to chci přímo natvrdo, ne dělat nějakou funkcí? LLM není zrovna dokonalé v generování náhodných řetězců a má problém počítat znaky (slavný "strawberry" problém), tak by bylo lepší, aby si pomohlo nějakým nástrojem. 

Ten jsem napsal a je to stručné a jednoduché:

```python
from mcp.server.fastmcp import FastMCP
import json
import random
import string
import hashlib

mcp = FastMCP("Random string")

@mcp.tool()
def random_string(length: int, lower: bool, upper: bool, numeric: bool, special: bool) -> str:
    """
    Generate a random string of given length with specified character types.
    :param length: Length of the random string
    :param lower: Include lowercase letters
    :param upper: Include uppercase letters
    :param numeric: Include numeric characters
    :param special: Include special characters
    :return: Random string
    """
    char_pool = ""
    if lower:
        char_pool += string.ascii_lowercase
    if upper:
        char_pool += string.ascii_uppercase
    if numeric:
        char_pool += string.digits
    if special:
        char_pool += string.punctuation

    if not char_pool:
        raise ValueError("At least one character type must be selected.")

    result = ''.join(random.choices(char_pool, k=length))
    return result

@mcp.tool()
def unique_string(seed_text: str, length: int, lower: bool, upper: bool, numeric: bool, special: bool) -> str:
    """
    Generate a unique-like predictable string based on seed_text.
    Using the same seed_text consistently produces the same output.
    """
    # Create a stable seed using sha256.
    seed_value = int(hashlib.sha256(seed_text.encode('utf-8')).hexdigest(), 16) % (2**32)
    rand = random.Random(seed_value)
    char_pool = ""
    if lower:
        char_pool += string.ascii_lowercase
    if upper:
        char_pool += string.ascii_uppercase
    if numeric:
        char_pool += string.digits
    if special:
        char_pool += string.punctuation
    if not char_pool:
        raise ValueError("At least one character type must be selected.")
    return ''.join(rand.choices(char_pool, k=length))

mcp.run(transport="sse")
```

Spustíme a server nám poslouchá.

# MCP server v GitHub Copilot
V rámci GitHub Copilot vlezu do Agent režimu a otevřu nástroje, kde můžu MCP přidat.

[![](/images/2025/2025-04-08-06-30-01.png){:class="img-fluid"}](/images/2025/2025-04-08-06-30-01.png)

Zvolil jsem konfiguraci svázanou s workspace, takže například pro každý repozitář mohu mít jiné nástroje.

```json
{
    "servers": {
        "my-mcp-string-generator": {
            "type": "sse",
            "url": "http://localhost:8000/sse"
        }
    }
}
```

Vidím, že si Copilot načetl dostupné nástroje.

[![](/images/2025/2025-04-08-06-34-47.png){:class="img-fluid"}](/images/2025/2025-04-08-06-34-47.png)

Následně při svém povídání s Copilotem si můžu o něco takového říct. Copilot sám pozná, že tohle je jako stvořené pro použití nástroje.

[![](/images/2025/2025-04-08-06-36-59.png){:class="img-fluid"}](/images/2025/2025-04-08-06-36-59.png)

Vidím, jak nástroj zavolal, jaké mu dal parametry a jaký byl výstup.

[![](/images/2025/2025-04-08-06-37-39.png){:class="img-fluid"}](/images/2025/2025-04-08-06-37-39.png)

To pak zopakoval ještě devětkrát a použil ve výsledku.

[![](/images/2025/2025-04-08-06-38-07.png){:class="img-fluid"}](/images/2025/2025-04-08-06-38-07.png)

Skvělé! Právě jsme si vytvořili vlastní nástroj, který může GitHub Copilot používat a zadrátovali to dohromady. Jednoduché, ne?

# Kam s tím dál, jaké nástroje vás napadají?
Plná GitHub Copilot extension toho dokáže samozřejmě mnohem víc, ale je tam větší bariéra vstupu - MCP je hodně jednoduché a hlavně pro něj, jak už jsem odkazoval, existuje spousta hotových serverů do nejrůznějších systémů. Líbí se mi i možnost mít MCP přímo lokálně na svém počítači ale i ve variantě vzdáleného serveru, třeba v Azure Container Apps. Tady je pár věcí, co mě napadají a mohlo by to mít přínos:
- **Znalostní báze** - GitHub Copilot Enterprise nativně podporuje Knowledge Base, ale Business edice ne a navíc vaše databáze může být i jinde, než v repozitářích - třeba na Confluence a tak podobně. Asi by nebyl problém udělat MCP, kde byste implementovali jednoduchý RAG, takže Copilot by se tam mohl doptávat, když ucítí potřebu mrknout na vaše existující API specifikace, firemní standardy nebo Wiki. Ostatně startovací kód do Atlassianu už [existuje](https://github.com/sooperset/mcp-atlassian).
- **Artefakty** - přístup na interní repozitáře knihoven, SDK, modulů nebo Docker kontejnerů, takže když je chci importovat, tak Copilot bude vědět, jaká je poslední verze a její URL či ID.
- **Konfigurační služby** - co udělat MCP server do nějaké konfigurační služby jako je Azure App Configuration Service, ConfigCat, LaunchDarkly nebo open source řešení jako je Etcd nebo Consul? Váš Copilot by se tak mohl podívat jak co máte aktuálně nastavené nebo, pokud budete odvážní, i měnit nastavení.
- **Databáze** - pokud máte dotazy, ke kterým by se hodil datový model, proč databázi nenapojit přes MCP server tak, že Copilot se může zeptat na schéma tabulky nebo si vytáhnout v CSV prvních 10 řádků pro představu?
- **Kubernetes** - co běží v clusteru a jak je to nastavené?
- **Projektové a produktové řízení** - GitHub Copilot má nativně přistup na Issues a Pull Requesty, ale co když řídíte práci jinde?
- **Figma** - existuje MCP server, díky němuž Copilot může přistupovat k návrhům GUI a číst jejich metadata.
- **Diagramy** - mindmapy, mermaid nebo UML diagramy mohou žít v nějakém SaaS produktu, Copilot by si je mohl načíst a přidat do kontextu podle potřeby.

Co zkusíte vy?