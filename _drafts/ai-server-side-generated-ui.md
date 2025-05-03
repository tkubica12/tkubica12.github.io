---
layout: post
published: true
title: Rozhodne se AI vynechat React či Angular a máme čekat nárůst AI-generovaného server-side UI s HTMX a FastHTML?
tags:
- AI
---
HTML jsem celkem uměl, ale protože mě vždycky výrazně víc bavila logika a backendy, tak mi s masivním nárůstem Javascriptových frameworků na frontendu úplně ujel vlak a v Reactu a podobných platformách se nechytám. Proto mě hodně zaujalo, že se objevuje reinkarnace přístupů řízených více na straně serveru, zejména **HTMX** a pro mě optimálně v kombinaci s **FastHTML** pro Python. Vypadá to ale, že nebudu jediný, koho návrat server-side renderingu může zajímat a spojencem tady může být právě AI. Proč se může stát, že ve světě AI se React, Angular a obecně masivní kód běžící u klienta stane nežádoucí a server-side se bude dařit mnohem lépe?

# AI agent, ad-hoc kódování a o tom, že chat není UI budoucnosti
AI agenti mohou používat nástroje a jedním z nich je prostředí, které jim umožňuje spustit si nějaký kód, který si sami napíšou. Typicky jde o kód pro provedení nějakého matematického či statistického výpočtu, vygenerování grafické vizualizace nebo zpracování dat (typicky přes Pandas). Jinak řečeno **pro jeden konkrétní dotaz uživatele vznikne ad-hoc kód s nějakou logikou**, která umožní dát uživateli odpověď. Místo předem připraveného kódu, který se nekonečně větví, aby dokázal zachytit všechny uživatelské scénáře, vznikne až když je to potřeba. Jednoúčelový kód generovaný AI agentem rize pro přípravu jedné konkrétní odpovědi na dotaz uživatele.

Stejný přístup lze ovšem očekávat i u uživatelského rozhraní, psaní zpráv v chatu přeci není efektivní způsob komunikace. Lidé mají obrovskou část mozku zaměřenou na oblast vidění a nejefektivnější vstřebávání informací je v okamžiku, kdy jsme s nimi schopni interagovat. Pokud tedy vznesete nějakou otázku do AI, nejúčinější odpovědí bude pravděpodobně nějaká **miniaplikace, která vám zobrazí informace interaktivní primárně vizuální formou**. Bude tedy kombinovat něco jako infografiku, tabulku či grafy, kde ale budete moci někde kliknout a dozvědět se další detail nebo si prohlédnout vizualizaci nějakého procesu včetně slovního komentáře. Jinak řečeno **AI agent zvolí optimální způsob interakce s uživatelem ad-hoc** podle toho kdo to je a na co se ptá.

Vzhledem k potřebnému výkonu lze předpokládat, že AI aktuálně i v blízké budoucnosti musí běžet na serverové straně pro zajištění dostatečné inteligence. Moderní aplikace dnes mají velké množství logiky běžící přímo na straně uživatele v telefonu či prohlížeči s frameworky jako React, Angular, Vue.js a dalšími. Při prvním připojení si klient aplikaci stáhne k sobě a ta má na starost prakticky veškerou logiku uživatelského rozhraní a s backendy mluví pouze z důvodů práce s daty. UI je tedy "předpečeno", stáhne se a spustí, a je tedy připraveno řešit nejrůznější scénáře, vizualizace a interakce. Jakmile ovšem bude UI z větší část generované ad-hoc na serverové straně s použitím AI, bude dávat smysl zaměřit se na frameworky, které vrací kontrolu zpět k serveru a omezují množství nutného kódu na klientské straně.

Ať je to tedy z důvodu mé neznalosti klientských frameworků nebo protože velké části UI jsou ad-hoc v režii AI, kouknout se na server-side renderované UI dává za mě velký smysl. A tím zdá se nejlepším kandidátem je HTMX a pro mě ještě lépe v kombinaci s Pythonem na serveru s využitím FastHTML.

# HTMX a FastHTML
HTMX je technologie nezávislá na typu použitého backendu, která umožňuje vytvářet interaktivní webové aplikace bez nutnosti psát stohy JavaScriptu. Dovoluje vám používat HTML jako jazyk pro popis interakce s uživatelským rozhraním. Místo toho, abyste psali JavaScript pro manipulaci s DOM (ten můžeme považovat za HTML výsledek dynamického vytváření UI), můžete použít HTML atributy k definování akcí, které se mají provést při událostech, jako jsou kliknutí na nějaký element. HTMX pak zajišťuje komunikaci se serverem a aktualizaci DOM na základě odpovědí serveru. To má výhody a nevýhody:
- Žádný Javascript na klientské straně (nebo minimální množství)
- Většina logiky a session state běží na serveru, což přispívá i k lepší bezpečnosti
- Rychlé iniciální načtení stránky, možnost využít univerzálního silného compute pro generování UI elementů
- Jednoduché použití, rychlé prototypování a vývoj
- Request na server při každém kliknutí může mít vliv na odezvu aplikace, pokud je server daleko
- Větší zátěž na serveru (a menší využití výpočetní výkonu klienta)

Posílání HTML "po drátu" dělá i Blazor Server v .NETu (přes SignalR), ale ten je zaměřený specificky na C# backendy (a přes Blazor WebAssembly může běžet .NET i na klientovi) nebo Laravel s PHP backendy. **HTMX** je univerzálnější. Na GitHubu má 44k hvězdiček a jeho popularita roste. 

**FastHTML** je pak moderní Python framework, který je postaven na výkoných knihovnách jako je FastAPI a Starlette. Na Python je tak dostatečně rychlý. Špička v této oblasti je dál, zejména ASP.NET Core, Go Fiber nebo Java Vert.x až 20x, Node.js Fastify asi 10x, nicméně je na úrovni nebo předčí starší frameworky jako je Node.Js Express, Python Django či Flask nebo Go Martini. Tedy žádná výkonnostní extratřída, ale pro moje účely dostatečné zejména s přihlédnutím ke jednoduchosti a snadnosti nasazení.

Podívejme na příklad. Na rozdíl od typického řešení v Pythonu (rendering z Jinja2 šablon jako u Flask či FastAPI nebo přes Django šablony) je FastHTML "pydantické".

```python
from fasthtml.common import *
css = Style('''
:root {--pico-font-size:90%,--pico-font-family: Pacifico, cursive;}
main button { margin-right: 5px; }
main button:last-child { margin-right: 0; }
''')
app = FastHTML(hdrs=(picolink, css))

count = 0

@app.get("/")
def home():
    return Title("Count Demo"), Main(
        Div(
            H1("Count Demo"),
            P(f"Count is set to {count}", id="count"),
            Button("Increment", hx_post="/increment", hx_target="#count", hx_swap="innerHTML"),
            Button("Decrement", hx_post="/decrement", hx_target="#count", hx_swap="innerHTML"),
            Button("Reset", hx_post="/reset", hx_target="#count", hx_swap="innerHTML"),
        ),
        style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 20vh;"
    )

@app.post("/increment")
def increment():
    print("incrementing")
    global count
    count += 1
    return f"Count is set to {count}"

@app.post("/decrement")
def decrement():
    print("decrementing")
    global count
    count -= 1
    return f"Count is set to {count}"

@app.post("/reset")
def reset():
    print("resetting")
    global count
    count = 0
    return f"Count is set to {count}"

serve()
```

Home stránka obsahuje HTML elementy, které jsou reprezentované Pydantic způsobem jako objekty a je tak možné vytvářet například sdílené UI elementy ve formě funkcí, využívat nové třídy nebo dědičnost. Elementy v tomto příkladu používají specifické HTMX atributy s předponou "hx". Tlačítka tak přes hx_post říkají, že jejich stisknutí má vygenerovat POST request na server, to co server vrátí zpět za HTML fragment patří do elementu s id="count" a má se vyměnit jeho vnitřní HTML (hx_swap="innerHTML"). Podporuje to samozřejmě i další HTTP slovesa a další swap mechanismy jako je přidání a tak podobně.

# Závěr
FastHTML je myslím hodně zajímavé pro ty, co znají HTML a chtějí přidat přidat interakci bez nutnosti tuny Javascriptu a zůstat nativně v Pythonu a to dokonce i bez šablonování. Možná na to AI agenti budou mít stejný názor, ale třeba ne. Co mi ale přijde pravděpodobné je, že díky nástupu ad-hoc generovaného UI pro každý jednotlivý request uživatele dojde k návratu server-side renderingu a speciálně technika **HTML over wire** na to bude skvěle sedět. Co se mě týče, jdu se do HTMX a FastHTML ponořit víc, protože by mohl splnit věci, které jsou pro mě osobně atraktivní - ideální pro AI, Python způsobem a s minimem Javascriptu.