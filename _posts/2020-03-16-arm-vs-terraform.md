---
layout: post
title: ARM vs. Terraform - co mám v Azure použít pro automatizaci infrastruktury?
tags:
- Automatizace
---
Infrastructure as Code považuji za zásadní krok na vaší cestě k modernímu provozování infrastruktury a platforem. Za nejvyšší vývojový stupeň mám a zásadně doporučuji desired state deklarativní model - pokud jste v době klikací a přemýšlíte o přechodu do éry skriptovací, zvažte udělat větší skok. Skriptovat jistě budete potřebovat, ale další v cestě jsou typicky desired state imperativní modely (Chef, Ansible) a pak ty deklarativní. No a tam jsou pro ovládání Azure dvě fantastické volby - Azure Resource Manager a Terraform. Chybu neuděláte ani jedním z nich a mám strašně rád oba. ARM je nativní součást Azure a to sebou přináší některé zásadní výhody. Terraform ale můžete použít i na jiné věci, než jen Azure a má některé další příjemné vlastnosti, jenže to přináší i nevýhody.

Jak si vybrat? Tady je můj pohled na výhody a nevýhody použití obou pro Azure.

# Co mají společného
Nechci dnes popisovat celý koncept desired state a deklarativního modelu, to už jsem na tomto bloku několikrát udělal (koukněte třeba na ARM tag). Oba systémy jsou deklarativní, podporují vstupní parametry a modularizaci, výstupní parametry a provázanost modulů a tak podobně.

# Výhody Azure Resource Manager
ARM je základní součástí Azure, je to vrstva, která je primárním interface mezi uživatelem a komponentami poskytujími služby (Resource Providers) a vystavuje buď deklarativní JSON popis nebo API (které má ovšem stejnou JSON strukturu, ale má slovesa navíc). Veškeré další metody ovládání jako je GUI (portál), CLI či PowerShell moduly využívají tuto vrstvu a to typicky jako API volání, ale GUI často používá i deklarativní ARM (všimněte si, že většina průvodců v Azure vám nakonci dává možnost stáhnout si šablonu - průvodce typicky znamená, že projdete otázky, které slouží jako vstupní parametr do šablony, kterou průvodce použije).

Jaké jsou zásadní výhody:
- ARM je součást Azure a state (přehled co v cloudu vlastně běží) je tak přímo ten Azure. Nepotřebujete si někde uchovávat informaci o tom, co bylo nebo nebylo nasazeno, ARM to čte přímo z Azure. To všechno dost zjednodušuje.
- Tím, že ARM je přímo součást Azure, můžete v šabloně jednoduše vytáhnout informace ze zdrojů v Azure ať už byly nasazeny jakýmkoli způsobem. Použijete reference funkci (případně listKeys a další) a tou lze vytáhnout jakýkoli atribut jakéhokoli zdroje v Azure (včetně zdroje v jiné subskripci). Terraform remote state je méně známý a pořád potřebuje mít state file.
- Velkou výhodou je, že formát ARM šablony je totéž, co najdete přímo v běžícím Azure například přes Resource Explorer nebo Export Template tlačítko na zdroji nebo resource group. Dá se tak například naklikat něco v portálu a pak si z toho nechat udělat šablonu. Nějaké drobné úpravy sice mohou být potřeba (například mohou být zdroje, kde to nejde jednoduše exportovat a budete potřebovat třeba jinak parametrizovat), ale jiné systémy jako Terraform něco takového neumožňují, takže je to zásadní výhoda.
- ARM = Azure, takže v něm najdete podporu pro naprosto všechno. Velmi často nejnovější produkty i ve fázi private preview ARM podporují (v private preview často právě pouze ARM a CLI nebo GUI v té době neexistuje), takže máte veškeré novinky okamžitě k dispozici a nedochází zde k prodlevám (není tu potřeba čekat na implementaci funkce do Go SDK a následně implementace do Terraform). 
- ARM má dobře vyřešenou bezpečnost aniž by to bylo složité nastavit a to včetně integrace Azure Key Vault. Zejména je dobré, že neexistuje nějaký soubor, ve kterém jsou v plain textu uloženy citlivé informace. Terraform na tom není genericky hůř, ale vyžaduje víc nastavení, aby to bylo správně.
- ARM deployment probíhá jako služba, nepotřebujete tedy server. Tedy nemusíte se trápit tím, že to někdo spustí z notebooku (to defacto nejde - z notebooku pouze pošlete zadání, ale váš počítač nijak konkrétní API nevolá) nebo řešit kde vzít deployment server a jak se o něj starat. To všechno je zdarma. Terraform vám dá stejnou míru pohodlnosti s produktem Terraform Cloud (velmi doporučuji, pokud tímto nástrojem jdete) - není to zadarmo, ale zas je univerzálnější.
- ARM budete potřebovat, pokud budete chtít publikovat své řešení v Azure Marketplace nebo vytvářet interní šablony pro použití ve vaší organizaci včetně custom GUI (Azure Managed Applications). Stejně tak Azure Blueprints, velmi důležitý governance nástroj, používá ARM. Vyplatí se ho tedy umět.

# Výhody Terraform
Terraform je od třetí strany, firmy Hashicorp, nicméně Azure pokud vím spolufinancuje vývoj modulů pro svou platformu. Podporuje větší množství providerů jako je Azure, Azure Stack, AWS, GCP, ale in on-premises záležitosti typu VMWare nebo OpenStack. Kromě toho umí například ovládat GitHub (založit organizaci apod.) nebo nasazovat objekty do Kubernetes. To ale začínají být oblasti, kde nejsem přítelem všechno dělat jedním nástrojem a preferuji specializovaná řešení. Například nasazovat do Kubernetes Terraformem (v původní podobě, tedy jednotlivé objekty) mi nepřijde vhodné a podpora pro Helm v Terraform je nová a nic moc. Může to vést ke smíchání vrstev a to mi přijde špatný nápad. Určitě tedy mentálně zvládnu použití Terraform k nasazení infrastrukturních komponent Kubernetes clusteru (Ingress kontroler, Flagger, Sdervice Mesh, ...), ale ani to není ideální a určitě nepreferuji pro nasazování aplikace. Terraform bych nechal dělat to co umí dokonale (nasazovat infrastrukturu) a nepouštěl bych ho k řešení aplikací (Helm, RUDR, WebDeploy apod.) ani k orchestraci (Azure DevOps Pipelines, GitHub Actions, Ansible).

Tady jsou důvody, proč mám Terraform rád:
- Syntaxe je čitelnější pro provozního smrtelníka - daleko příjemnější než JSON (kde se člověk utápí v zapomenutých čárkách při kopírování) nebo YAML (kde "nic" znamená moc aneb mezery/odsazení hrají zásadní roli a při kopírování se často rozbijou). To hodně oceňuji.
- Líbí se mi jak Terraform počítá graf závislostí. Navádí k používání provázanému přiřazování například názvů, tedy místo definice názvu  resource ve variable a její následné používání v dalších objektech doporučuje v těchto objektech odkazovat na definici resource.name. Jde to jednoduše, elegantně a krásně se tak automaticky vyřeší návaznost zdrojů (není potřeba tak často explicitně uvádět dependOn).
- Terraform už od začátku velmi dobře pracuje s troubleshootingem a plánováním, terraform plan je výborný příkaz, který do světa ARM (pod názvem WhatIf) přišel teprve nedávno.
- Považuji za velmi pohodlné používání modulů. ARM v tomto nabízí nested šablony (ale ty mají nějaká omezení a nehodí se pro modularizaci) nebo linkované šablony, které ale klientem nepošlete, musíte je nejdřív uložit ve storage a odkázat se na ně. Chápu proč to tak je, nicméně Terraform je v tomhle podstatně příjemnější.
- Terraform je velmi přívětivý k vytváření zdrojů v různých resource group, resp. koncept resource group není zásadní součástí jeho fungování (na rozdíl od ARM, ale výhodou tam zase je, že je to logicky navázáno na portál apod.). Jinak řečeno můžete bez omezení nahazovat i mazat zdroje v různých resource group a tyto i vytvářet. V ARM tohle uděláte taky, ale je to jednak složitější (musíte mít subscription-scoped šablony na vytvoření resource group a pak v ní pouštět nested šablony) a druhak to má omezení (max. 5 resource group najednou).
- Přijde mi že se Terraform lépe ladí. Většinu chyb chytne už terraform plan, hlášky jsou vypovídající a jednoduše si necháte nasadit pouze určitý zdroj (který zrovna ladíte) nebo naopak vynecháte ten, který máte rozbitý (bez nutnosti komentovat nebo jinak modifikovat šablonu). 
- V neposlední řadě je tu univerzálnost Terraform. Nepřeceňujte ji - to, že máte hotovu šablonu pro Azure neznamená, že pouhým nakopírováním uděláte šablonu pro AWS. Vůbec ne, budete ji psát znova. Nicméně jazyk, moduly, state file a všechny ty procesní věci zůstanou stejné. 

# Co bych si vybral
Pokud používáte (z opravdového cloudu) jen Azure, doporučuji jít do ARM. Zejména pokud jste pokročilý enterprise uživatel dává to největší smysl, protože tím můžete ovládat všechno včetně preview funkcí, ARM použijete v Azure Blueprints a Managed Applications, můžete exportovat komplexní ručně vytvořené projekty apod. Jak už jsem zmínil používat tyto nástroje k nasazování aplikací není moje oblíbená strategie, takže mi v ARM nic nechybí a kombinuji ho s Azure DevOps či GitHub Actions pro orchestraci (často je lepší šabony/moduly orchestrovat/pouštět v CI/CD nástroji či Ansible, než používat linkované šablony), s Ansible pro VM configuration management, s Helmem (a v budoucnu RUDRem) pro nasazování do Kubernetes případně pošilhávám po GitOps scénářích s Flux či Argo nebo v případě serverless (FaaS).

Terraform je ovšem výborná volba, pokud chcete (nebo potřebujete vykázat) podporu pro další cloudy nebo VMware. Moje doporučení je nepatlat se s open source verzí, protože tam často vídám zásadní chyby co do bezpečnosti (nulový RBAC, nesprávně zabezpečený state file) a provozu (např. pouštění věcí z notebooku bez sjednoceného kódu) a pořídit Terraform Enterprise integrovaný do Azure Active Directory pro SSO (Terraform Cloud je mi příjemnější volba, ale nejsem si jist, že podporuje SSO, což by pro mě byl zásadní důvodu jít raději do Enterprise i za cenu, že to musím mít ve VM). Ještě pro multi-cloud doporučuji případně promyslet integraci s Hashicorp Key Vault.

Ať se rozhodnete pro jeden nebo druhý, jdete správnou cestou ... klikače vidíte jen ve zpětném zrcátku a skripťáci mají zrovna schůzi, protože ten skript, co loni napsal Franta, než odešel jinam, v půlce padá a nikdo neví co se tam vlastně děje.