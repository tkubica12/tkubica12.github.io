---
format_version: 1
title: "Jak centrálně spravovat a řídit skills pro agenty"
eyebrow: "Skills jako týmová schopnost"
subtitle: "Stáhnout centrální skill, při potřebě zlepšení udělat lokální PoC, poslat návrh do GitHubu, nechat agenty triážovat i připravit PR po lidském schválení a vylepšený skill distribuovat všem."
slug: agent-skills-centralni-sprava
date: 2026-05-11
language: cs-CZ
status: experimental
canonical_url: "/2026/agent-skills-centralni-sprava/"
agent_friendly:
  source: "source.md"
  caveman: "caveman.md"
design:
  theme: simple-neutral
  density: presentation
---

# Jak centrálně spravovat a řídit skills pro agenty

Chcete něco naučit svého agenta? Ukážu to na demu [skills-demo-catalog](https://github.com/tkubica12/skills-demo-catalog): centrální katalog skillů, simulované Task API, lokální PoC v konzumentském repozitáři, issue proces, agentická triáž, cloud agent a benchmark, který měří, jestli se skill skutečně zlepšil.

::: callout type="verdict" title="Pointa"
Skill je skvělý pro znalost, instrukce a governance. CLI nebo jiný nástroj je skvělý pro opakovanou, vícekrokovou a měřitelnou práci. GitHub je přirozené místo, kde se z lokální zkušenosti stane týmově řízená schopnost.
:::

::: group id="idea" title="Idea"

::: card number="01" title="Task API jako bezpečný demo problém" default="open"
Pro účely dema jsem si vyrobil vlastní API pro správu tasků. Není to GitHub API a nejde o skutečné firemní systémy. Je to simulovaný, kontrolovaný problém: tasky, komentáře, stav `waiting-for-response`, občasné `429` a workflow, které je dost reálné na to, aby agent narazil na stejné potíže jako v praxi. Celý demo katalog je veřejně v repozitáři [tkubica12/skills-demo-catalog](https://github.com/tkubica12/skills-demo-catalog).

V katalogu je skill `task-api-helper`, který obsahuje:

- `SKILL.md` s instrukcemi a popisem schopnosti.
- `scripts/task_cli.py` jako CLI wrapper nad Task API.
- `references/API.md` pro pochopení podkladového API, když CLI nestačí.
- `references/IMPROVEMENT-PROCESS.md` s pravidly, jak skill vylepšovat přes centrální proces.
:::

::: card number="02" title="Evoluce: kontext -> CLI -> vyšší operace" default="open"
Typická evoluce skillu nad API je podle mě tahle:

::: sequence title="Cesta od znalosti ke sdílené schopnosti"
1. **Skill jako kontext** — Markdown vysvětlí API, business kontext a dobrý postup použití.
2. **Přidání CLI** — agent používá stabilní příkazy místo skládání `curl`, JSON escapingu a ručních retry.
3. **Vyšší operace v CLI** — opakované vícekrokové workflow se přesune do kódu, aby ho agent nemusel pokaždé znovu skládat.
:::

Tady se objevila zásadní otázka: pokud takové skilly začnou vznikat lokálně, jak je spravovat centrálně pro tým? Nechci, aby každý kopíroval soubory ručně. Chci governance, návrhy změn, schválení, benchmarky a jasnou distribuci.
:::

:::

::: group id="lokalni-zkusenost" title="Lokální zkušenost"

::: card number="03" title="Nainstalujeme skill z katalogu" default="open"
V novém, úplně obyčejném repozitáři nainstaluji skill z centrálního katalogu pomocí `gh skill`:

```bash label="Instalace z centrálního katalogu"
gh skill install tkubica12/skills-demo-catalog task-api-helper --scope project --agent github-copilot
```

Pak v nainstalovaném skillu nastavím `.env`, aby CLI vědělo, kde běží demo Task API:

```dotenv label=".agents/skills/task-api-helper/.env"
TASK_API_URL=https://task-api-demo.example.azurecontainerapps.io
```

Konzumentský repozitář je pořád čistý. Schopnost přišla z katalogu, ne z lokálního copy-paste promptu.
:::

::: card number="04" title="První použití: funguje, ale bolí" default="open"
Agent umí Task API použít. Umí vypsat tasky čekající na odpověď, otevřít konkrétní task a přidat komentář. Problém začne ve chvíli, kdy chci stejný komentář přidat ke všem taskům ve stavu `waiting-for-response`.

::: reveal title="Transcript z použití Task API"
```text
> List tasks waiting for response and summarize what needs attention.

The Task API is responding, but the first request hit a rate limit. I’m checking the response shape and then retrying with a short pause so I can give you the actual waiting items instead of a guess.

5 tasks are waiting for response. The ones needing the most attention are the two high-priority items stalled on external confirmation or approval.

  ┌──────────────────────────────────────────────────────────────────┬──────────┬───────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Task                                                             │ Priority │ Assignee          │ Needs attention                                                                                                        │
  ├──────────────────────────────────────────────────────────────────┼──────────┼───────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ task-1 — Waiting on customer confirmation — order #8821          │ High     │ alice@example.com │ Customer still has not confirmed after the initial outreach and a 48-hour follow-up.                                   │
  │ task-3 — Awaiting legal sign-off on NDA amendment                │ High     │ carol@example.com │ Legal review is pending after the NDA draft was forwarded.                                                             │
  │ task-2 — Pending vendor reply for Q3 renewal                     │ Medium   │ bob@example.com   │ Vendor has not replied since the renewal quote was sent.                                                               │
  │ task-5 — Infrastructure cost review — ops team response needed   │ Medium   │ eve@example.com   │ Ops response is pending, and there is no comment history, so this likely needs owner context or a first follow-up.     │
  │ task-4 — Customer reported login failure — needs repro steps     │ Low      │ dave@example.com  │ Blocked waiting for the customer to provide reproduction steps.                                                        │
  └──────────────────────────────────────────────────────────────────┴──────────┴───────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

> Open task-1 and add this comment: "Following up - please provide an update."

Added the comment to task-1. The API accepted it as comment c-c0d260d5.

> Add the same comment to every task waiting for response.

The bulk run hit rate limits mid-stream. I’m reading the exact output and then I’ll finish only the tasks that didn’t get updated.
task-5 was the only one not updated. I’m retrying that single task with a slower cadence to get it through cleanly.
Done. The comment was added to all other tasks currently in waiting-for-response, and task-1 was skipped because it already had the same comment.
```
:::
:::

::: card number="05" title="Agent sám navrhne zlepšení"
Přesně v tomhle momentu dává smysl zeptat se agenta, co by šlo udělat lépe. Ne proto, aby rovnou změnil centrální katalog, ale aby nejdřív popsal opakovanou bolest a navrhl ověřitelný lokální experiment.

::: reveal title="Návrh zlepšení"
```text
Best improvement: add a first-class bulk command to the shared CLI, for example:

python task_cli.py bulk-add-comment --status waiting-for-response --text "Following up - please provide an update." --skip-existing

That would help because this workflow currently requires list -> get each task -> detect duplicates -> post comment, which is slow and exposed to 429 rate limits. A bulk command could make it both faster and more reliable by handling:

- built-in retry/backoff for rate limits
- duplicate-comment detection (--skip-existing)
- a single summary of which tasks were updated or skipped

Per the skill’s process, the right next step would be a local proof of concept that captures before/after evidence: fewer API calls, fewer retries, and cleaner operator output.
```
:::
:::

::: card number="06" title="Lokální PoC: issue, benchmark a důkaz" default="open"
Tady je důležitý governance detail: konzumentský agent si může udělat **dočasný lokální PoC**, aby ověřil hypotézu. Nemá ale trvale forkovat centrální skill. Po ověření má lokální změnu zahodit a otevřít issue v katalogu s důkazy.

Výsledek v demu: [skills-demo-catalog issue #15](https://github.com/tkubica12/skills-demo-catalog/issues/15).

::: tabs id="poc-evidence"
::: tab id="baseline-loop" title="Baseline loop"
Původní postup musel dělat list -> get jednotlivých tasků -> kontrolu duplicit -> komentář po jednom. V PoC měření zvládl **4/5 tasků**, trval asi **29.96s** a narazil na **1 rate-limit failure**.
:::
::: tab id="bulk-poc" title="Bulk PoC"
Dočasný příkaz `bulk-add-comment` vyřešil stejný cíl jako jedna vyšší operace. Výsledek: **5/5 tasků**, asi **6.27s**, **0 failures**.
:::
::: tab id="repeat-run" title="Opakovaný běh"
Opakovaný běh ověřil `--skip-existing`: agent neduplikuje komentáře a dostane čistý souhrn, co aktualizoval a co přeskočil.
:::
:::

::: reveal title="Agent zapíše PoC do upstream issue"
```text
> OK, this make sense. Follow improvement guide, test this idea locally as PoC and if it is good, publish this is detailed issue into skills-demo-catalog repository.

I’m setting up a proper local PoC in the installed skill, capturing before/after evidence, and then I’ll revert the local patch before opening the upstream issue if the results hold.
I’ve got a clean baseline: 11 calls over ~30s, one 429, and only 4 of 5 tasks updated.
The first PoC run worked cleanly: all 5 tasks updated in about 6 seconds with no failures.
I’ve got enough evidence now: the PoC fixed the partial-failure case and validated duplicate skipping. I’m writing the findings down, restoring the installed skill to the published baseline, and then I’ll open the upstream issue from that evidence.

https://github.com/tkubica12/skills-demo-catalog/issues/15
```
:::
:::

:::

::: group id="centralni-governance" title="Centrální governance"

::: card number="07" title="Repozitář jako katalog a proces" default="open"
Lokální PoC je dobrý pro učení. Pro tým potřebujeme repozitář, který je katalog, audit trail, distribuční mechanismus i místo, kde se rozhoduje o změnách.

::: steps title="Životní cyklus zlepšení"
1. **Local experiment** — konzumentský tým zkusí dočasný PoC proti workflow, které ho bolí.
2. **Benchmark** — zachytí před/po evidenci: čas, retry, méně ručních kroků, čistší výstup.
3. **Issue with template** — lokální změny se zahodí a otevře se issue v katalogu.
4. **Advisory triage** — agentická workflow přidá doporučení a případně `copilot-recommended`.
5. **Human triage** — maintainer rozhodne, jestli změna patří do sdíleného kontraktu.
6. **Copilot implementation** — po `accepted` implementuje změnu cloud agent.
7. **Pull request** — PR mění CLI, dokumentaci, testy a benchmark spec.
8. **Catalog release** — po merge se katalog taguje a vydává.
9. **Consumer update** — konzumenti aktualizují skill a zahodí lokální workaround.
:::
:::

::: card number="08" title="Agentická triáž v GitHub Actions" default="open"
Pro triáž jsem použil GitHub Agentic Workflows v GitHub Actions. Workflow si přečte issue, ověří, jestli má lokální PoC důkazy, a přidá stručné doporučení pro maintainera. Důležité: agent nepřidává `accepted` a nenahrazuje lidské rozhodnutí.

- Workflow předpis: [`task-api-enhancement-triage.md`](https://github.com/tkubica12/skills-demo-catalog/blob/main/.github/workflows/task-api-enhancement-triage.md)
- Issue: [#15 Bulk add comment command](https://github.com/tkubica12/skills-demo-catalog/issues/15)
- Advisory label: `copilot-recommended`
- Human gate: `accepted`

::: reveal title="Screenshots triáže a labelu"
![Issue s PoC evidence](/images/2026/2026-05-02-12-13-01.png)
![Agentic triage workflow run](/images/2026/2026-05-02-12-13-48.png)
![Accepted label jako signál pro další krok](/images/2026/2026-05-02-12-22-20.png)
:::
:::

:::

::: group id="agenticke-doruceni" title="Agentické doručení"

::: card number="09" title="Accepted label spouští cloud agenta" default="open"
Další krok je záměrně jednoduchý: po přidání labelu `accepted` se issue přiřadí Copilotovi v cloudu. Ten má z issue a katalogu dost kontextu, aby připravil změnu jako pull request. Člověk pořád rozhoduje, ale repetitivní implementační práce jde na agenta.

::: reveal title="Cloud agent workflow a běh"
![Workflow pro spuštění cloud agenta](/images/2026/2026-05-02-12-23-31.png)
![Cloud agent začíná pracovat](/images/2026/2026-05-02-12-23-52.png)
:::
:::

::: card number="10" title="Pull request bez průběžného steerování" default="open"
V tomhle pokusu jsem do agenta nijak dále nezasahoval. Výsledek nebyl dokonalý, ale byl dost dobrý na review: přidal vyšší CLI operaci, aktualizoval skill instrukce, doplnil testy a připravil benchmark spec. Přesně tak má podle mě vypadat první agentické doručení.

::: reveal title="Pull request a změny"
![Pull request od agenta](/images/2026/2026-05-02-14-31-15.png)
![Detail změn v PR](/images/2026/2026-05-02-14-31-55.png)
:::
:::

::: card number="11" title="Benchmark jako důkaz, ne pocit" default="open"
Benchmark je důležitý, protože jinak by šlo jen o dojem. V lokálním PoC už máme důkaz, že vyšší operace pomohla:

| Varianta | Úspěšnost | Čas | Rate-limit failure |
|---|---:|---:|---:|
| Baseline loop | 4/5 | 29.96s | 1 |
| Bulk PoC | 5/5 | 6.27s | 0 |

V PR jde demo ještě dál: workflow `ci-benchmark.yml` spustí agentický benchmark přes GitHub Copilot SDK a porovná stejný cílový úkol se skillem z `main` a se skillem z PR. Měří úspěch, počet aktualizovaných tasků, čas, input/output tokeny, LLM calls, Task API requests a `429`.

::: reveal title="Benchmark workflow a výstup"
![Benchmark workflow](/images/2026/2026-05-02-14-32-31.png)
![Benchmark summary](/images/2026/2026-05-02-14-33-02.png)
:::
:::

:::

::: group id="shrnuti" title="Shrnutí a co si vyzkoušet"

::: card number="12" title="Finální výsledek" default="open"
Pointa není v jednom hezčím promptu. Pointa je v tom, že lokální zjištění nezůstane lokálním hackem, ale projde přes důkaz, issue, lidské rozhodnutí, agentickou implementaci a měřené vydání zpět do sdíleného katalogu.

::: summary-grid
- **Katalog**: `skills-demo-catalog` drží zdroj pravdy pro skill, CLI, API reference a improvement proces.
- **Governance**: lokální PoC vede do issue, triáže, lidského `accepted` a PR.
- **Měření**: benchmarky ukazují čas, tokeny, LLM calls, API requests a `429`.
- **Distribuce**: konzumenti aktualizují centrální skill přes `gh skill`, místo aby udržovali lokální fork.
:::
:::

::: card number="13" title="Praktický checklist" default="open"
Pokud to chcete zkusit podobně, doporučil bych:

::: arrow-list title="Checklist pro vlastní katalog"
- Používejte `gh skill` pro správu skillů a jejich verzování v centrálním repozitáři.
- Přidejte ke skillu jasný improvement process: PoC, evidence, issue template.
- Nechte agenta nejdřív zkusit lokální disposable PoC, ale nenechte ho tajně forkovat centrální skill.
- Použijte GitHub Actions a labely jako explicitní governance signály.
- Vyzkoušejte GitHub Agentic Workflows pro triáž, dokumentaci nebo agentické testování.
- Používejte GitHub Copilot cloud agenta pro přetavení issue na kód a pull request.
- Měřte kvalitu skillu přes Copilot CLI nebo SDK přímo v pipeline.
- Prohlédněte si celé demo: [tkubica12/skills-demo-catalog](https://github.com/tkubica12/skills-demo-catalog).
:::
:::

:::
