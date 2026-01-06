---
layout: post
publish: Coding agenti - paralelní práce agentů na vašich úkolech
tags:
- AI
- GitHub
---
S tím jak rostou schopnosti AI modelů kódovat a pracovat víc samostatně se snažím do svého workflow začlenit více paralelismu. 

Jsou situace, kdy chci s agentem fungovat interaktivně - sledovat co dělá, abych se jednak učil já od něj, ale současně abych zasáhl pokud se vydá špatným směrem nebo mi začne hrabat do architektury a dělat různé workaroundy místo toho, aby přišel jak správně na to. Ale jindy tohle nepotřebuji - jsou to úlohy, kde mám jasnou specifikaci nebo dostatečné zadání a stačí mi se podívat až na výsledek - třeba nějaká investigace (návrhy co zlepšit, například se často ptám jestli nemám udělat refaktoring, lépe modularizovat, abstrahovat apod.), aktualizace dokumentace, deployment skripty a předpisy (třeba manifesty do Helm chartu - u toho nemusím být, stačí mi překontrolovat výsledek), drobné úpravy, dodělání Dockerfile a ozkoušení že fungují (vyrobit image, lokálně spustit jestli se rozjedou - přes MCP nástroje nebo CLI například). 

V okamžiku, kdy v hlavním okně dělám něco interaktivně jsem to řešil tak, že otevřu ještě další okno GitHub Copilotu a v něm zadám něco dalšího. Jenže všichni agenti pak běží a sahají na stejné soubory, což nemusí dopadnou dobře. Proto jsem zatím tohle omezoval na investigační věci (povídání, analýza) nebo situace, kdy se jedná o úplně jiné části projektu (například adresář /src s kódem vs. třeba /specs). Čas od času použiji cloud agenta v GitHub, který jede zcela v cloudu a vytvoří Pull Request, ale pro rychlé obrátky kdy jsem na to jen já sám mi to přijde zbytečně robustní a trochu mě to zdržuje. Raději bych běžel víc agentů lokálně a na origin pushnul až výsledek svých úloh pro různé agenty. Jak na to?

# GitHub Copilot CLI - agent bez IDE běžící prakticky kdekoli
V poslední době se dost mluví o AI coding agentech, kteří neběží v rámci IDE, ale jsou ve formě nějakého CLI. Je zajímavé, jak se principy interface z počítačů před šedesáti lety stále v jisté pozměněné formě drží. Já budu používat [GitHub Copilot CLI](https://github.com/features/copilot/cli/), ale podobně bude fungovat třeba open source projekt [OpenCode](https://opencode.ai/), který na backendu může mít různé lokální i cloudové modely, takže si ho můžete napojit na vaše Microsoft Foundry v Azure a využít třeba modely GPT-5.1-codex-max nebo Claude Sonnet 4.5, nebo [OpenAI CODEX CLI](https://developers.openai.com/codex/cli) či proprietární [Claude Code](https://claude.com/product/claude-code).

GitHub Copilot CLI má i hezké ASCII UI.

```
┌──                                                                         ──┐
│                                                           ▄██████▄          │
    Welcome to GitHub                                   ▄█▀▀▀▀▀██▀▀▀▀▀█▄
    █████┐ █████┐ █████┐ ██┐██┐     █████┐ ██████┐     ▐█      ▐▌      █▌
   ██┌───┘██┌──██┐██┌─██┐██│██│    ██┌──██┐└─██┌─┘     ▐█▄    ▄██▄    ▄█▌
   ██│    ██│  ██│█████┌┘██│██│    ██│  ██│  ██│      ▄▄███████▀▀███████▄▄
   ██│    ██│  ██│██┌──┘ ██│██│    ██│  ██│  ██│     ████     ▄  ▄     ████
   └█████┐└█████┌┘██│    ██│██████┐└█████┌┘  ██│     ████     █  █     ████
    └────┘ └────┘ └─┘    └─┘└─────┘ └────┘   └─┘     ▀███▄            ▄███▀
│                              CLI Version 0.0.363      ▀▀████████████▀▀      │
└──                                                                         ──┘
 Version 0.0.363 · Commit 66416ad

 Copilot can write, test and debug code right from your terminal. Describe a task to get started or enter ? for help.
 Copilot uses AI, check for mistakes.

 ● Logged in with gh as user: tkubica12

 ● Connected to GitHub MCP Server

 C:\git\gh-copilot-demo\src\services\toy[⎇ main]                                                claude-sonnet-4.5 (1x)
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 >  Enter @ to mention files or / for commands
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Ctrl+c Exit · Ctrl+r Expand recent
```

Použití interaktivního režimu mi přijde zajímavé zejména v situaci, kdy jsem na nějakém vzdáleném systému a potřebuji tam pomoci řešit nějaké úlohy. Tak například na mém domácím Orange Pi (čínský "klon" Raspberry), což je malá pasivně chlazená krabička s ARM procesorem, na které běžím Docker s pár kontejnery, můžu GitHub Copilot CLI používat.

```
 Welcome to GitHub Copilot CLI
 Version 0.0.374 · Commit 9fecd24

 Copilot can write, test and debug code right from your terminal. Describe a task to get started or enter ? for help.
 Copilot uses AI, check for mistakes.

 ● Logged in as user: tkubica12

 ● Connected to GitHub MCP Server

 ~                                                                                              claude-sonnet-4.5 (1x)
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 > Na tomhle počítači běží několik Docker kontejnerů. Zjisti jaké to jsou, analyzuj jejich logy jestli tam nejsou
   nějaké chyby a stručně mi je popiš a posuď míru závažnosti. Také prozkoumej jak zatěžují tento systém a zda jsou
   to aktuální verze nebo ne a pokud ne, uveď 3 nejdůležitější změny u každého kontejnerového image.
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Ctrl+c Exit · Ctrl+r Expand recent



 ● Dobře, provedú komplexní analýzu Docker kontejnerů běžících na tomto systému.
   Začnu zjištěním, jaké kontejnery běží, a pak provedu detailní analýzu.

 ○ Zobrazit běžící Docker kontejnery
   $ docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
   ↪ 1 line...

 ╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
 │ Zobrazit běžící Docker kontejnery:                                                                                 │
 │                                                                                                                    │
 │ ╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮ │
 │ │ docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"                            │ │
 │ ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯ │
 │                                                                                                                    │
 │ Do you want to run this command?                                                                                   │
 │                                                                                                                    │
 │ ❯ 1. Yes                                                                                                           │
 │   2. Yes, and approve `docker` for the rest of the running session                                                 │
 │   3. No, and tell Copilot what to do differently (Esc)                                                             │
 │                                                                                                                    │
 │ Confirm with number keys or ↑↓ keys and Enter, Cancel with Esc                                                     │
 ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

Nicméně tím největším lákadlem CLI verzí není zas tolik interaktivní režim nebo editace souborů (na to raději použiji VS Code a pokud vzdálený systém nemá UI tak nevadí, použiji lokální VS Code s remote SSH připojením), ale samostatné použití - spuštění s konkrétním zadáním a parametry přímo z příkazové řádky a Copilot odvede práci a ukončí se. Skvělé do skriptů, CI/CD pipeline (například vygenerování nějakého popisu změn pro zobrazení při schvalování v rámci GitHub Actions) nebo právě pro použití samostatného agenta.

# Manuální použití vícero agentů s Git worktree
Rád bych lokálně zadal úkoly několika agentům nad jedním repozitářem, ale tak, že si všechny agenty a všechny změny řídím sám a nepotřebuji tak dělat komplexní Pull Requesty a CI/CD pipeline pro všechny tyto změny zvlášť. Na druhou stranu jejich běh nad stejnými soubory, když mají všichni zapisovat a spouštět a testovat, tak nedopadne dobře - potřebujeme izolaci, ale stačí mi to všechno jen lokální. Git podporuje možnost vytvořit branch (samozřejmě), ale tam se přepínáte do konkrétního branch a my chceme provozovat agenty paralelně. Proto můžeme použít koncept worktree, kdy dokážeme pro každý branch vytvořit samostatný adresář a tím mít soubory lokálně izolované a pracovat na více větvích současně.

Pojďme vytvořit dvě nové worktree a s nimi asociovaný nový branch - pro každého agenta jeden.

```bash
git worktree add ../gh-copilot-demo-agent1 -b agent1-task
git worktree add ../gh-copilot-demo-agent2 -b agent2-task

git worktree list
C:/git/gh-copilot-demo         fc02290 [main]
C:/git/gh-copilot-demo-agent1  fc02290 [agent1-task]
C:/git/gh-copilot-demo-agent2  fc02290 [agent2-task]
```

V jednom terminálu zadám práci jednomu agentovi (specifikuji model, ale může toho být víc).

```bash
cd ../gh-copilot-demo-agent1
copilot --allow-all-tools --model claude-sonnet-4.5 --prompt "I have k6 perftest, but no README for it. Create README.md file explaining how to run the perftest, what scenarios it covers, and how to interpret results."
git add -A
git commit -m "Agent 1 commit"
```

A v druhém paralelně pojede ten druhý.

```bash
cd ../gh-copilot-demo-agent2
copilot --allow-all-tools --model claude-sonnet-4.5 --prompt "Some of Python services are using pip and requirements.txt. I want to migrate everything to uv as package manager. Make sure to migrate to toml files, remove requirements.txt and change Dockerfile and READMEs accordingly. Test your able to sync uv and that Dockerfile builds without errors."
git add -A
git commit -m "Agent 2 commit"
```

Teď můžeme obě změny projít, otestovat a tak podobně - každou samu za sebe. Pokud jsem spokojen, mohu změny lokální zamergovat do své hlavní větve a celé worktree a branche vymazat - teprve pak to celé poslat na origin do GitHubu (nebo tam vytvořit Pull Request na to celé - kompletní sadu změn).

```bash
git merge agent1-task
git merge agent2-task
git worktree remove ../gh-copilot-demo-agent1
git worktree remove ../gh-copilot-demo-agent2
git branch -D agent1-task agent2-task
```

```
git log --graph --oneline --all
*   71e7342 (HEAD -> main) Merge branch 'agent2-task'
|\
| * 4d53ba3 Agent 2 commit
* | fdf038c Agent 1 commit
|/
```

# Agent HQ ve Visual Studio Code s GitHub Copilot Background agentem
Přímo ve Visual Studio Code můžu kromě interaktivní práce s agentem zvolit nového background agenta.

[![](/images/2026/2026-01-06-07-39-38.png){:class="img-fluid"}](/images/2026/2026-01-06-07-39-38.png)

GitHub Copilot mi přímo nabízí izolaci přes worktree - tedy to co jsme dělali ručně pro mě zautomatizuje.

[![](/images/2026/2026-01-06-07-41-05.png){:class="img-fluid"}](/images/2026/2026-01-06-07-41-05.png)

```bash
git worktree list
C:/git/gh-copilot-demo                                         fc02290 [main]
C:/git/gh-copilot-demo.worktrees/worktree-2026-01-06T06-41-14  fc02290 [worktree-2026-01-06T06-41-14]
```

Práci jednotlivých běžících agentů pak můžu sledovat a různě mezi nimi přepínat.

[![](/images/2026/2026-01-06-07-42-19.png){:class="img-fluid"}](/images/2026/2026-01-06-07-42-19.png)

Skvělé je, že můžeme provádět handoff, tedy předávat práci mezi agenty. Tak například můžu mít interaktivní diskusi jak něco implementovat nebo vylepšit a v okamžiku, kdy už z mé strany necítím potřebu u toho dál být, předám to do bacground agenta. 

[![](/images/2026/2026-01-06-07-47-54.png){:class="img-fluid"}](/images/2026/2026-01-06-07-47-54.png)

Zavolat background agenta lze taky přímo z promptu přes zavináč.

```
@cli I have k6 perftest, but no README for it. Create README.md file explaining how to run the perftest, what scenarios it covers, and how to interpret results.
```

Stav každého agenta si můžu snadno zobrazit a vidět co dělá, co píše a jaké změny navrhuje. Jednoduše můžu rozhodnout jaké změny přijmu - tedy mám UI pro automatizace mergování do větve, ve které je můj VS Code workspace. Mám tedy klasické tlačítko Keep/Undu (v rámci session mi jen ukazuje co se v interakci změnilo v souborech a já můžu snadno udělat undu aniž bych musel řešit nějaké commity a jejich reverty) a také tlačítko "Aplikovat do hlavního workspace".

[![](/images/2026/2026-01-06-07-55-57.png){:class="img-fluid"}](/images/2026/2026-01-06-07-55-57.png)

Jakmile dám aplikovat, uvidím tuto změnu přímo ve svém hlavním workspace, tedy ve větvi, ve kterém mám VS Code otevřený. 

[![](/images/2026/2026-01-06-07-58-18.png){:class="img-fluid"}](/images/2026/2026-01-06-07-58-18.png)

V seznamu agentů vidím u koho mám nepřečtené zprávy, kolik je tam změn a můžu se rozhodnout co s tím dál.

[![](/images/2026/2026-01-06-07-59-49.png){:class="img-fluid"}](/images/2026/2026-01-06-07-59-49.png)

# Kdy použít background nebo cloud agenty vs. interaktivního lokálního agenta
Kdy co používám?

**Interaktivní lokální agent**
- Potřebuji interakci, chci předkládat názory, možnost, já si vybírám a směřuji konverzaci
- Chci sledovat jak Copilot moje zadání zpracovává, protože mě zajímá jak se to dělá nebo ho potřebuji kontrolovat, aby nesešel z cesty a nezačal dělat něco, co jsem nechtěl
- Úkol je krátký a počkat na něj mě nezdrží dlouho - přepínání myšlenek do backgroundu a zpět je na půl minuty nevýhodné
- Potřebuji sice paralelní běh, ale všechno je jen v režimu čtení - například vedu paralelní diskusi nad dalším krokem nebo architekturou a na to mi stačí nové okno

**Background agent ve VS Code**
- Už vím co chci, mám specifikaci nebo dobrý prompt a věřím, že tenhle úkol model dobře zvládne (už jsme to dělali, vím, že tohle dopadá dobře).
- Potřebuji vyzkoušet různé varianty řešení nebo vyzkoušet různé modely, nepostupuji lineárně - například mě napadají 3 způsoby jak to řešit a nevím jestli bude lepší to udělat v GPT 5.2 nebo Sonnetu 4.5, není problém to pozadávat background agentům a až to budou mít hotové vybrat co vedlo na nejlepší výsledek.
- Zásadní pro tento scénář je, že úlohy jsou všechny moje a sám si je vyhodnotím a pro "projekt", tedy ostatní členy týmu, je předložím až najednou. Beru to tedy jako jakésy rychlo-obrátkové řešení pro mě a teprve jeho kompilací vznikne ten Pull Request, který si projede plným schvalovacím a testovacím kolečkem.

**Cloud agent v GitHub.com**
- Pro mě hlavně pro situace, kdy potřebuji nemít spuštěný počítač - chci to odstartovat třeba z mobilu a podívám se na výsledky později, zejména, pokud už je k tomu založeno Issue. 
- To hlavní ale je robustní auditovatelné řešení v rámci spolupráce mnoha lidí a agentů, kdy navrhované změny prochází různí členové týmu nebo AI agenti (třeba bezpečnostní), ke každému kroku je potřeba robustního testování apod. Pak použití cloud agenta, který vyrobí plnohodnotné PR je správný a udržitelný postup. 

Do toho všeho ale ještě samozřejmě promlouvají nástroje a dnes už ne jen MCP, ale i Skills (které ale lze použít i na efektivnější správu kontextu) - na to mrkneme hned příště. No a také ve VS Code existuje koncept Custom Agent, i na ten se podíváme - jak lze agenty customizovat a připravit si nějaké specializovanější.