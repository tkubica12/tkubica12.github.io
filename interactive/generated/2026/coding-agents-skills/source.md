---
format_version: 1
title: "Nový standard Agent Skills pro vaše kódovací pracanty v GitHub Copilot"
eyebrow: "Agent Skills v praxi"
subtitle: "Jak dát coding agentovi kontext a jednoduché nástroje bez toho, aby se utopil v AGENTS.md nebo aby kvůli každé drobnosti musel vznikat plnohodnotný MCP server."
slug: "coding-agents-skills"
date: "2026-01-12"
language: "cs-CZ"
status: "experimental"
canonical_url: "/2026/coding-agents-skills/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: "simple-neutral"
  density: "presentation"
---

# Nový standard Agent Skills pro vaše kódovací pracanty v GitHub Copilot

Jak pracovat s kontextem v AI coding nástrojích nebo naučit agenta používat vámi předem připravené skripty? Jde to řešit promptováním v [AGENTS.md](https://agents.md/), ale to není standardizovaný postup a chování bude hodně závislé na použitém modelu. Pro robustnější integrace existuje [Model Context Protocol](https://modelcontextprotocol.io/), jenže ten už znamená napsat kus softwaru a v některých situacích je to zbytečně těžká váha. Proto se dnes zaměříme na variantu někde mezi tím: [Agent Skills](https://agentskills.io/).

::: callout type="verdict" title="Pointa"
**Agent Skills** nejsou šokujícím způsobem nová myšlenka. Jsou ale dobrý standard pro dvě praktické věci: načíst kontext až ve chvíli, kdy ho agent opravdu potřebuje, a zabalit malé lokální skripty tak, aby je agent uměl bezpečně a opakovaně používat.
:::

::: group id="mentalni-model" title="Mentální model"

::: card number="01" title="AGENTS.md, MCP a Skills nejsou totéž" default="open"
Nejdřív si pojďme oddělit tři věci, které se v debatách o coding agentech často pletou dohromady.

::: summary-grid
- **AGENTS.md**: projektové instrukce, styl práce, orientace v repozitáři a pravidla pro agenta.
- **MCP**: protokol pro discovery nástrojů, jejich argumentů, zabezpečení a spouštění nad lokálními i vzdálenými službami.
- **Skills**: lokální adresář s `SKILL.md`, popisem a případnými referencemi nebo skripty, který agent načítá až podle potřeby.
:::

AGENTS.md je výborný na obecné instrukce. MCP je výborný na robustní nástroje a integrace. Skills jsou někde mezi: pořád jsou to obyčejné soubory v repozitáři, ale agent je nemusí celé držet v kontextu od začátku.
:::

::: card number="02" title="Proč je důležité nenačítat všechno hned"
Příliš mnoho kontextu agentovi často nepomůže. Naopak mu zhorší rozhodování, zvýší latenci a u některých nástrojů i cenu. U GitHub Copilot to platíte spíš ve formě Premium Requests, takže to nemusíte počítat po tokenech tak úzkostlivě, ale princip je stejný: co není relevantní pro aktuální úlohu, nemá modelu zbytečně překážet.

Finta Skills je v tom, že se do kontextu dostane jen seznam skillů: název, popis a cesta k detailním instrukcím. Agent tak ví, že skill existuje, ale jeho plný obsah si přečte až ve chvíli, kdy podle popisu usoudí, že ho potřebuje.

::: callout type="note" title="Stav ve VS Code"
V době psaní jsou Agent Skills ve VS Code dostupné od verze 1.108 jako experimentální/preview funkce a je potřeba je zapnout nastavením `chat.useAgentSkills`.
:::
:::

::: card number="03" title="Jak vypadá adresář skillu"
Struktura adresáře je předepsaná. Musí obsahovat `SKILL.md` s YAML hlavičkou, názvem a popisem. V těle pak mohou být instrukce, postupy, odkazy na další soubory a popis skriptů, které má agent umět používat.

Typická místa v repozitáři:

- `.github/skills/jmenoskillu`
- `.claude/skills/jmenoskillu`

Do stejného adresáře můžete přidat třeba `scripts/`, `references/` nebo `README.md`. Důležité je, aby `SKILL.md` agentovi řekl, co v nich najde a kdy to má použít.
:::

:::

::: group id="dynamicky-kontext" title="Dynamické načítání kontextu"

::: card number="04" title="Nejmenší možný skill: projekt BigDog"
Začněme jednoduchým příkladem. Tohle je celý `SKILL.md`:

```markdown label=".github/skills/simplecontext/SKILL.md"
---
name: simplecontext
description: This contains information about company project code-named BigDog
---

Here are information about this project:
- Owner: Michael Coder
- Inventary number: 54321
```

Využijeme toho, že ve VS Code umíme zobrazit, co se skutečně posílá do modelu: Chat Debug view nebo log requestů. Nejdřív se jen zeptám na `Ping`.

![Debug view po jednoduchém dotazu Ping](/images/2026/2026-01-06-14-01-15.png)
:::

::: card number="05" title="Co jde do modelu při obyčejném Ping"
V requestu je toho hodně: metadata nástrojů, system prompt, instrukce agenta a další pracovní kontext. Zkráceně například definice nástroje `apply_patch`:

```json label="Ukázka metadat nástrojů ve zkrácené podobě"
[
  {
    "function": {
      "name": "apply_patch",
      "description": "Edit text files...",
      "parameters": {
        "type": "object",
        "properties": {
          "input": { "type": "string" },
          "explanation": { "type": "string" }
        },
        "required": ["input", "explanation"]
      }
    },
    "type": "function"
  }
]
```

Pak následuje zabudovaný system prompt. Opět jen krátký výsek:

```xml label="Výsek system promptu"
You are an expert AI programming assistant, working with a user in the VS Code editor.
Your name is GitHub Copilot.
<coding_agent_instructions>
You are a coding agent running in VS Code. You are expected to be precise, safe, and helpful.
</coding_agent_instructions>
```

A pak přijde sekce Skills. Tady je jádro celé věci:

```xml label="Seznam skillů v kontextu"
<skills>
Here is a list of skills that contain domain specific knowledge on a variety of topics.
<skill>
<name>simplecontext</name>
<description>This contains information about company project code-named BigDog</description>
<file>c:\git\gh-copilot-demo\.github\skills\simplecontext\SKILL.md</file>
</skill>
</skills>
```

V kontextu je tedy pouze název, popis a cesta. Není tam vlastník projektu ani inventární číslo. Na dotaz `Ping` model skill nepotřeboval, takže odpověděl obyčejně:

```text label="Odpověď bez načtení skillu"
pong — I'm here and ready. What would you like me to do next?
```
:::

::: card number="06" title="Kdy se skill načte"
A teď to přijde. Zeptám se:

```text label="Dotaz, který vyžaduje detail skillu"
What is inventory number for BigDog
```

Tahle informace **není** v kontextu, není v názvu skillu a není ani v jeho popisu. Model ale z popisu pochopí, že by měl načíst soubor `SKILL.md`.

![Agent se rozhodl načíst SKILL.md](/images/2026/2026-01-06-14-09-03.png)

Po načtení už ví odpověď:

![Odpověď po načtení detailu skillu](/images/2026/2026-01-06-14-10-21.png)

Tohle je přesně ten rozdíl proti tomu, když všechno nacpete do `AGENTS.md`. Detailní informace existuje v repozitáři, ale model ji čte až v okamžiku, kdy je relevantní.
:::

:::

::: group id="skripty" title="Skills jako návod k lokálním skriptům"

::: card number="07" title="Druhý příklad: JSON na XML"
Skills nejsou jen na textový kontext. Dobře se hodí i na vysvětlení, jak má agent používat připravený skript. Tady je zkrácený `SKILL.md` pro konverzi JSON na XML:

```markdown label=".github/skills/json-to-xml-converter/SKILL.md"
---
name: json-to-xml-converter
description: Convert JSON data to XML format with customizable root element and attribute handling
---

# JSON to XML Converter Skill

## Purpose

Convert JSON data structures into well-formed XML documents.

## Usage

~~~bash
python .github/skills/json-to-xml-converter/scripts/json2xml.py input.json output.xml
python .github/skills/json-to-xml-converter/scripts/json2xml.py input.json output.xml --root "data"
echo '{"name": "test"}' | python .github/skills/json-to-xml-converter/scripts/json2xml.py - -
~~~

## Parameters

- `input_file`: Path to JSON file or `-` for stdin
- `output_file`: Path to XML output file or `-` for stdout
- `--root`: Root element name, defaultně `root`
```

Pointa není v tom, že JSON na XML je světoborný problém. Pointa je v kontraktu: agent se z popisu skillu dozví, že existuje hotový skript, a z detailu skillu zjistí, jak ho správně spustit.
:::

::: card number="08" title="Skript je obyčejný Python"
V adresáři `scripts` je kromě dokumentace i samotný kód. Zkráceně vypadá takhle:

```python label="scripts/json2xml.py"
#!/usr/bin/env python3

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from typing import Any, Optional

def sanitize_tag_name(name: str) -> str:
    sanitized = name.replace(" ", "_")
    sanitized = "".join(c if c.isalnum() or c in ("_", "-", ".") else "_" for c in sanitized)
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized or "item"

def dict_to_xml(data: Any, parent: Optional[ET.Element] = None, tag_name: str = "item") -> ET.Element:
    element = ET.Element(sanitize_tag_name(tag_name)) if parent is None else ET.SubElement(parent, sanitize_tag_name(tag_name))
    if isinstance(data, dict):
        for key, value in data.items():
            dict_to_xml(value, element, key)
    elif isinstance(data, list):
        for item in data:
            dict_to_xml(item, element, "item")
    elif data is None:
        element.text = ""
    else:
        element.text = str(data)
    return element

def convert_json_to_xml(json_str: str, root_name: str = "root") -> str:
    data = json.loads(json_str)
    root = dict_to_xml(data, tag_name=root_name)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
```

V plné verzi je ještě CLI parsing, hezčí výpis chyb a zápis do souboru nebo na stdout. Pro agenta je ale nejdůležitější to, že nemusí vymýšlet konverzi sám. Má použít připravený nástroj.
:::

::: card number="09" title="Použití v chatu"
Teď vezmu JSON soubor, přihodím ho do chatu jako kontext a řeknu:

```text label="Prompt"
convert this to xml
```

Agent správně vyhodnotí, že má použít skill, načte si instrukce a spustí skript. Výborný výsledek.

![Agent použil skill a spustil skript](/images/2026/2026-01-06-14-37-04.png)

Tady je ještě pohled na debug log:

![Debug log použití skriptu ze skillu](/images/2026/2026-01-06-14-38-34.png)

Pár dalších příkladů najdete na [GitHubu Anthropicu](https://github.com/anthropics/skills/tree/main/skills).
:::

::: card number="10" title="Bezpečnostní poznámka"
Pozor při stahování skills z internetu. Často obsahují skripty a ty se pak spouští lokálně pod právy vašeho uživatele.

::: arrow-list title="Co bych dělal před použitím cizího skillu"
- Projít `SKILL.md`, jestli nepřidává divné instrukce.
- Otevřít skripty a zkontrolovat, co dělají se soubory, sítí a proměnnými prostředí.
- Neschvalovat spouštění naslepo jen proto, že to navrhl agent.
- U firemních skillů preferovat centrální katalog, review a jasné vlastnictví.
:::
:::

:::

::: group id="zaver" title="Závěr"

::: card number="11" title="Kdy bych použil co"
Za mě se z toho skládá docela praktické pravidlo:

::: detail-grid title="Volba mechanismu" hint="Klikněte na kartu pro detail"
::: detail-card title="AGENTS.md" summary="Obecné chování agenta a orientace v repozitáři."
Použijte ho na pravidla práce, coding standardy, testovací příkazy, mapu repozitáře a instrukce, které mají platit často. Není ideální jako skladiště dlouhých manuálů a katalog skriptů.
:::
::: detail-card title="Agent Skills" summary="Kontext a malé nástroje načtené až podle potřeby."
Použijte je na doménový kontext, návody, referenční soubory a jednoduché lokální skripty. Výhoda je standardizace a menší tlak na kontext modelu.
:::
::: detail-card title="MCP" summary="Robustní nástrojová vrstva a integrace."
Použijte ho, když potřebujete skutečný protokol pro nástroje, bezpečnost, discovery operací, vzdálené služby nebo univerzální integraci napříč agenty.
:::
::: detail-card title="CLI nebo skript" summary="Opakovatelný postup, který má být deterministický."
I uvnitř skillu často skončíte u skriptu. To je dobře. Co jde měřitelně a opakovaně udělat kódem, nemá agent pokaždé znovu skládat jen promptováním.
:::
:::
:::

::: card number="12" title="Moje očekávání"
Skills standardizují něco, co šlo ručně udělat už dřív: v `AGENTS.md` byste mohli vést seznam dalších souborů a říkat agentovi, kdy je má číst. Jenže to je práce navíc, snadno vznikne nekonzistence a hůř se to přenáší mezi projekty.

Proto čekám, že se Skills stanou běžnou součástí tuningu jednotlivých modelů. Protože s tím přišel Anthropic, dá se očekávat, že Claude modely na tento vzor budou dobře připravené; u OpenAI Codex a Google bych čekal totéž. Nejde jen o standardizaci souborů, ale i o to, že LLM bude na ten způsob práce specificky trénované a bude ho používat spolehlivěji.

::: summary-grid
- **Kontext až ve chvíli potřeby**: agent ví, že skill existuje, ale detail si načte až při relevantním dotazu.
- **Lehké nástroje bez MCP**: jednoduchý skript nemusí hned znamenat celý server a katalog operací.
- **Přenositelnost**: skill má jasnou strukturu a dá se sdílet mezi projekty i agenty.
- **Menší chaos v instrukcích**: dlouhé manuály nemusí bobtnat v jednom `AGENTS.md`.
:::
:::

:::


::: closing
Pro pomocníky v rámci projektu jsou **Agent Skills** výborná střední cesta: víc pořádku než volné promptování, méně režie než plnohodnotné MCP.
:::
