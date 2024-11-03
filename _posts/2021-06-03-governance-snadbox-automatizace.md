---
layout: post
published: true
title: "Automatizujte koloběh sandbox prostředí v Azure s Bicep, Terraform nebo Pulumi"
tags:
- Governance
- Automatizace
---
Jak podnítit inovaci s využitím Azure, mít věci pod kontrolou co do bezpečnosti a nákladů a přitom se neuklikat k smrti? Podívejme se jak automatizovat vznik sandboxů včetně řízení přístupů, vytvoření budgetů i automatizované reakce na jejich překročení a to včetně odmazání prostředků. To vše řízené jednou šablonou pro všechny sandboxy a udělal jsem ji rovnou ve třech provedeních - Bicep, Terraform a Pulumi, stačí si vybrat.

# Sandbox požadavky a jejich řešení
Tady jsou základní výchozí předpoklady pro jednoduché řešení sandboxů ve firmě:
- Sandbox je prostor pro hraní - je sice oddělený od ostatních a hlavně od firemní sítě, ale uvnitř si může uživatel dělat cokoli (to je jeho smyslem).
- Sandbox má jednoznačného vlastníka, ale ten ať má možnost do něj přizvat další členy týmu podle potřeby, aniž by se musel někoho ptát.
- Sandbox odpovídá potřebě něco vyzkoušet, má jasné určení. Pokud se potřebuji učit Kubernetes pro svoje aplikace a nezávisle na tom si chci pohrát s AI, požádám o dva sandboxy. Tedy nepreferoval bych "jó Franta do toho Azure nějaký přístup má, mu řekni, tam se to udělá" a pak se neví co k čemu vlastně vzniklo (a kdy se to dá smazat).
- Sandbox si nese budget a ten je monitorován.
- Pokud se blíží vyčerpání měsíčního budgetu, vlastník dostane notifikaci (btw. v mém případě používám zprávu při 80% budgetu, ale nově můžete také použít Forecast typ, což je skvělé - řekne vám to, když se ocitnete na špatné trajektorii, třeba jste na 50% po pár dnech).
- Pokud uživatel dosáhne 100% ať se všechna jeho VM stopnou.
- Pokud uživatel dosáhne 120% ať se prostředky vymažou.
- Nepoužil jsem tagy, ale je to samozřejmě jednoduché přidat - cost location, department, cokoli takového.

Technické řešení takového zadání je následující:
- Každý sandbox odpovídá jedné Resource Group ve sdílené subskripci.
- Vlastník je Owner Resource Group (může zvát kolegy), ale nevidí jiné sandboxy (pokud ho nepozvou) a nemá práva na úrovni subskripce.
- Je vytvořen příslušný budget s notifikacemi a spouštěním automatizovaných akcí. Místo budgetu se scope resource group jsem použil budget na úrovni subskripce, ale s filtrem na konkrétní resource group. Smyslem je, aby tento budget nešel modifikovat Ownerem resource group (mohl by pak vypnout mazání zdrojů při přešvihnutém rozpočtu) a současně to vlastníkovi umožní vytvářet si vlastní budgety (přidat si vlastní notifikace dle potřeby).
- Akce jsou implementované jako Azure Function, kde jsem použil Powershell. Jsou to dvě funkce - jedna vypne všechna VM v resource group a druhá smaže resource group. Kromě toho před tím odstraní případné zámky (aby uživatel neuměl zabránit akci). Na funkce jsou navázány Action Groups, které jsou spouštěny notifikačními pravidly budgetů.
- Pro nasazení funkce je potřeba jí dodat zdrojové kódy - proto řešení nahraje zip soubor do storage account, z kterého se funkce nainstalují. Tyto komponenty jsou v resource group budgets, která obsahuje podpůrné zdroje (třeba právě i ty Azure Functions).

# Automatizace s Bicep, Terraform a Pulumi
Vytvořil jsem řešení pro tři způsoby automatizace - nativní Bicep, multi-cloudový Terraform používající DSL a na standardním programovacím jazyce postavené Pulumi. 

Kompletní řešení najdete v tomto repozitáři vždy v adresáři sandbox (subscriptions je něco jiného a k tomu jindy): [https://github.com/tkubica12/governance-automation/](https://github.com/tkubica12/governance-automation/)

Klíčem k ovládání celého řešení je sepsání jednotlivých sandbox prostředí. Stačí tedy přidat sandbox s potřebnými parametry do seznamu, který jsem ve všech řešení pojal stejně:

```
var sandboxes = [
  {
    name: 'research1'
    ownerId: '7424fb4c-5e9f-45cd-9f7d-453d45655e75' // tokubica
    ownerEmail: 'tomas.kubica@microsoft.com'
    monthlyBudget: 100
  }
  {
    name: 'research2'
    ownerId: '7424fb4c-5e9f-45cd-9f7d-453d45655e75' // tokubica
    ownerEmail: 'tomas.kubica@microsoft.com'
    monthlyBudget: 80
  }
  {
    name: 'research3'
    ownerId: '7424fb4c-5e9f-45cd-9f7d-453d45655e75' // tokubica
    ownerEmail: 'tomas.kubica@microsoft.com'
    monthlyBudget: 5
  }
]
```

Pro přidání nového projektu ho tedy stačí přidat do seznamu a pro odebrání ho jednoduše ze seznamu odstranit.

V tomto konkrétním případě narazíme u Bicep na některá omezení. Nedá se jednoduše udělat nahrání souboru do storage jako součást deploymentu - musel bych použít deploymentScripts a to je úplně zbytečně kostrbaté. Jde jen o zdrojový kód pro Azure Function a ten může sedět už dopředu třeba na GitHubu, ale pro srovnání jsem připravil Azure CLI skript pro nahrání do Azure Blob Storage. Terraform i Pulumi mohou tohle udělat přímo při deployment a také jsem to tam takhle použil. 

Druhý a asi důležitější rozdíl je, že Bicep/ARM neumožňuje použít mode Complete na subscription scope, jinak řečeno nedokáže odmazat zdroje, které ze šablony odstraníte automaticky (na rozdíl od zdrojů v resource group, kde to podporuje) - a to se nás týká, protože budget a resource group vzniká na subscription scope. Pro Bicep variantu tedy budete muset odmazávat sandboxy třeba skriptem. U Terraform a Pulumi tohle není problém, protože si drží state bokem a stačí vyhodit sandbox ze seznamu a postarají se o jeho likvidaci.

Ještě zbývá dořešit jednu nepříjemnost. Při zakládání budgetu musí být určen start čas a ten musí být na začátku aktuálního měsíce. Zatím to je v kódu dané natvrdo a plánuji to vyřešit. Finta bude v tom tohle vygenerovat automaticky, ale pokud už budget existuje, tak tohle políčko ignorovat (tedy nepřenasazovat budget kvůli změně start času, což nechceme). V Pulumi to bude jednoduché, mám plný programovací jazyk. U Terraform to tak přímočaré asi nebude a u Bicep asi nezbude než to dát jako vstupní parametr a vyřešit při spouštění.

Pro práci se sandboxy bych volil Terraform nebo Pulumi. Být to před měsícem, Terraform by ještě budgety neuměl a Pulumi by vítězilo - ostatně to je jeho velká výhoda proti Terraformu. Jak řešíte sandbox vy a jakou máte strategii? Pinkněte mi na [LinkedIn](https://www.linkedin.com/in/tkubica/).