---
layout: post
published: true
title: Je už na čase naskočit do ARM64 v cloudu?
tags:
- Compute
---
Určitě jste zaznamenali, že procesory s architekturou ARM64 (nebo jejich open source bratříček RISC-V) se objevují v čím dál tím větším spektru použití a zařízení. Jsou naprostým standardem pro chytrá IoT zařízení a mobilní telefony, ale mají i variantu pro méně chytrá zařízení bez plnohodnotného OS (Cortex-M třeba v legendárních Raspberry Pi Pico RP2040 či STM32 zatímco třeba ESP32 používá RISC-V). U Mac počítačů je dnes ARM synonymem nejnovějších řad s výborným výkonem a nízkou spotřebou a i Windows po mnoha letech experimentování začínají na ARM také sázet. ARM64 má ale i varianty pro datová centra, cloud a dokonce i úplný high-end segment - High Performance Computing. Už se v Azure o ARM64 zajímáte? Pojďme si vyzkoušet.

# Jaký ARM64
Ve světě ARM je velmi časté, že si velký výrobce připraví modifikované vlastní specifikace procesoru, ale ve finále vychází ze stejného designu jader. Přes různé názvy a odlišnosti v počtech jader či výrobním procesu dostáváme tyto varianty:
- **Neoverse N1** (DC řada), například ve formě Azure v5 (Dpds_v5), AWS Graviton 2 (verze 1 byla Cortex A72), GCP T2A (Ampere Altra)
- **Neoverse N2** (DC řada), například Azure v6 (Cobalt 100 aka Dpds_v6)
- **Neoverse V1** (HPC řada), například AWS Graviton 3
- **Neoverse V2** (HPC řada), například AWS Graviton 4 nebo GCP Axion (C4A)

# Výkon
V první řadě je dobré vnímat zásadní odlišnosti v architektuře procesorů, takže se nedá říct, že pro všechny typy workloadů je jeden lepší nebo horší. Rozhodl jsem proto udělat jednoduchý test ve třech scénářích:
- NGINX - test webového serveru, vyžaduje dobrou vyváženost všech součástí
- Redis - hodně o výkonnosti mezi CPU a pamětí
- Stockfish (šachový engine) - hodně o výkonu CPU

Testoval jsem s použitím lokálního disku, aby storage nebyl limitující faktor. Výsledky jsou následující:

[![](/images/2024/2024-11-04-06-33-23.png){:class="img-fluid"}](/images/2024/2024-11-04-06-33-23.png)

Infrastrukturu, skripty na testování a Python kód pro sestavení tabulky najdete na mém [GitHubu](https://github.com/tkubica12/azure-vm-benchmarking)

V testech jsem měřil aktuální generaci obecných mašin D v5 ve variantách ARM (N1), Intel a AMD. V těchto týdnech by měla nastupovat nová generace v6 kdy ARM varianta už je plně dostupná, ale Intel a AMD ještě ne. Jakmile budou dostupné, přitestuji ještě je, protože se dá očekávat zlepšení výkonu v řádu asi 15% a jejich pozice se tak zlepší. Nicméně - podstatné je vidět, že nárůst výkonu mezi N1 a N2 je opravdu zásadní a přitom cena zůstala prakticky stejná, podstatně nižší, než u Intel a AMD variant. Je to jednak obecně příznivější cenou ARM, ale i jeho efektivitou ve spotřebě. Výkon v každém testu jsem pak přeškáloval na score, kde 100 má nejhorší varianta (spolehlivě je to ARM Neoverse N1), takže vidíte procentuální nárůst proti ní. Pak jsem přeškáloval cenu (PAYG a 3y rezervaci ve Sweden Central), abychom dostali poměrné ceny za na výkon. Z toho dobře vylezlo pár závěrů:
- N1 vs. N2 je zásadní rozdíl ve výkonu běžně +50% a někde víc
- N2 je v těchto testech výkonější, než v5 Intel a AMD. To se určitě srovná s v6 generacemi těchto platforem, ale podstatná zpráva je - ARM vůbec neznamená, že nemáte výkon, spíše naopak!
- N2 má velmi příznivou cenu, takže při přeškálování ceny výkonem je aktuálně ze všech variant nejvýhodnější. Můj odhad je, že v6 Intel a ARM dorovná výkon, ale bude držet cenu, takže tipuji, že N2 zůstane králem poměru cena/výkon napříč šestou generací VM v Azure

# Praktické dopady použití ARM procesorů
Tak především Windows Server pokud vím má podporu ARM pouze v preview, takže tam je to ještě nějaká cesta. Linux je v tomto směru plně připraven. Nicméně musíme počítat s tím, že zatímco Intel a AMD jsou kompatibilní, ARM je zásadně jiný a vyžaduje kompilaci přímo pro tento procesor. Pro klasické Linux aplikace "zakoupené v obchodě" nebo migraci z on-premises nebude ARM64 asi častou volbou a současně v platformách vyšší úrovně jako jsou Azure Container Apps se zatím nepoužívá, takže myslím, že ideálním využitím ARM64 je zákazník stavící vlastní aplikace v Azure Kubernetes Service. Určitě to ale znamená přidat ARM64 build do vaší CI/CD třeba v GitHub Actions a doporučuji vyrábět multi-arch image, tedy kompilovat pro AMD64 i ARM64 architektury, ať máte možnost v případě potřeby spustit aplikaci i na běžném serveru (například protože v daném regionu ARM ještě není nebo nemáte dostatečnou kvótu a tak podobně). Ekosystém je na to už velmi dobře připraven:
- Většina různých programovacích jazyků a knihoven podporuje ARM64
- Většina middleware nebo databází podporuje ARM64 (a to včetně Microsoft SQL)
- GitHub Actions mají [hosted ARM64 runnery](https://github.blog/news-insights/product-news/arm64-on-github-actions-powering-faster-more-efficient-build-systems/), což je výborné, protože můžete jet na plné rychlosti bez nějakých simulací typu QEMU
- AKS plně podporuje [ARM64 nodepool](https://learn.microsoft.com/en-us/azure/aks/create-node-pools#add-an-arm64-node-pool)

Samozřejmě přidaná složitost je nevýhodou. Proto doporučuji neodhadovat, ale pořádně si vaše aplikace nad ARM64 vyzkoušet. Stojí vám potenciálně lepší poměr ceny k výkonu za to? U předchozí generace jsem měl dojem, že moc ne, ale tohle už začíná vypadat velmi dobře. Když ještě vezmeme v potaz jisté potíže Intelu v ohni nejen konkurence AMD, ale právě i ARM, RISC-V (kde v mobilním světě už jasně prohrál a v noteboocích se mu to může stát brzo taky) a tlaku akcionářů po ukázkovém dilematu inovátora po té, co je hodnotou převálcovala kdysi malá až trapná NVIDIA, bych skoro čekal, že výhody ARM64 (výkon, cena, spotřeba) se v budoucnu ještě zvýrazní.