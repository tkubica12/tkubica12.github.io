---
title: "Jak centrálně spravovat a řídit skills pro agenty"
slug: agent-skills-centralni-sprava
date: 2026-05-11
language: cs-CZ
status: experimental
canonical_url: /new/2026/agent-skills-centralni-sprava/
---

# Centrální správa skills

Cíl: lokální skill -> týmová schopnost. Demo: https://github.com/tkubica12/skills-demo-catalog. Není to GitHub API; používá simulované Task API: tasky, komentáře, stav `waiting-for-response`, občas `429`. Skill `task-api-helper` obsahuje instrukce, `scripts/task_cli.py`, API referenci a improvement process.

## Pointa

Skill = znalost + instrukce + governance. CLI/nástroj = opakovaná vícekroková práce. GitHub = katalog, audit trail, issue proces, PR, release.

## Tok

1. Skill dá agentovi kontext Task API.
2. CLI zabalí mechaniku: příkazy, retry, JSON, error handling.
3. Vyšší CLI operace zabalí opakované workflow.
4. Konzument udělá disposable lokální PoC.
5. PoC se změří.
6. Lokální patch se zahodí.
7. Do katalogu jde issue s důkazy.
8. Agentická triáž přidá doporučení, třeba `copilot-recommended`.
9. Člověk přidá `accepted`.
10. Cloud Copilot implementuje PR.
11. Vylepšený skill se vydá zpět všem.
12. Po merge konzumenti aktualizují skill přes `gh skill`.

## Instalace

```bash
gh skill install tkubica12/skills-demo-catalog task-api-helper --scope project --agent github-copilot
```

`.env` ve skillu:

```dotenv
TASK_API_URL=https://task-api-demo.example.azurecontainerapps.io
```

## Lokální bolest

Úkol: vypsat tasky `waiting-for-response`, otevřít task, přidat komentář, potom stejný komentář přidat všem čekajícím taskům. Agent to zvládl, ale workflow bylo list -> get každý task -> kontrola duplicit -> post comment po jednom. To je pomalé a náchylné na `429`.

Agent navrhl příkaz:

```bash
python task_cli.py bulk-add-comment --status waiting-for-response --text "Following up - please provide an update." --skip-existing
```

Smysl: retry/backoff, skip duplicit, jeden souhrn aktualizováno/přeskočeno.

## PoC důkaz

Upstream issue: https://github.com/tkubica12/skills-demo-catalog/issues/15

| Varianta | Úspěch | Čas | 429/fail |
|---|---:|---:|---:|
| Baseline loop | 4/5 | 29.96s | 1 |
| Bulk PoC | 5/5 | 6.27s | 0 |

Opakovaný běh ověřil `--skip-existing`: neduplikuje komentáře.

## Governance

Repozitář katalogu je zdroj pravdy pro skill, CLI, API reference a improvement process. Agentická GitHub Actions triáž čte issue a kontroluje, jestli má návrh PoC a měření. Přidá doporučení/advisory label, ale ne finální schválení. Lidský gate je `accepted`.

Workflow předpis: `.github/workflows/task-api-enhancement-triage.md` v `skills-demo-catalog`. Důležité labely: `copilot-recommended` = agent doporučuje; `accepted` = člověk schválil implementaci.

## Doručení

Po `accepted` se issue přiřadí Copilot cloud agentovi. Agent udělá PR: vyšší CLI operace, změny skill instrukcí, testy, benchmark spec. Člověk review/merge.

Benchmark v PR může přes GitHub Copilot SDK porovnat skill z `main` vs skill z PR na stejném úkolu. Metriky: success, aktualizované tasky, čas, input/output tokeny, LLM calls, Task API requests, `429`.

## Výsledek

- Lokální zjištění nezůstane lokální hack.
- Katalog: `skills-demo-catalog` drží zdroj pravdy.
- Governance: PoC -> issue -> triáž -> human `accepted` -> PR -> vydání.
- Měření: benchmarky místo pocitu.
- Distribuce: `gh skill`, žádné lokální forky.

## Checklist

- Spravuj skilly přes centrální repo a `gh skill`.
- Ke skillu přidej improvement process.
- Lokální PoC dovol, ale jako disposable patch.
- Návrh musí mít evidenci před/po.
- Agentická triáž je advisory, člověk rozhoduje.
- Cloud agent implementuje PR, ne finální merge.
- Kvalitu skillu měř pipeline benchmarkem.
