---
layout: post
title: 'Infrastructure as code v Azure: Bicep (ARM) vs. Terraform vs. Pulumi vs. Crossplane'
tags:
- Automatizace
---
Pravidelní čtenáři jistě vědí, že nejsem zastáncem vyklikávání, ale i skriptování beru primárně jako prostředky pro seznámení se s technologií. Ten okamžik, kdy chcete vědět co a jak se nastavuje a jak jednotlivé služby a kroky na sebe navazují a to je důležité pochopit. Nicméně pak už je vhodné přejít na nějaký desired state model - za mne ideálně deklarativní.

V ten okamžik se pro Azure otevře široké spektrum nástrojů a já se v dnešním srovnání zaměřím jen na nejznámější zástupce svých kategorií. Bude to nativní řešení Bicep (transparentní nadstavba nad ARM), multi-cloud lídr Terraform, kodérský pohled na problematiku v čele s Pulumi a zástupce směru "všechno je Kubernetes API" Crossplane. Na detaily jsem se už zaměřil (nebo to plánuji udělat) v jiných článcích. Dnes je to o pohledu shora - co mají společného, co ne a kdy bych co použil.

# Scénář a kategorie pro srovnání
Všechny nástroje práci skvěle splní, ale všechny mají důležité výhody i nevýhody. Tady jsou aspekty, které mě budou zajímat:
- Míra podpory Azure zdrojů včetně těch nejnovějších, méně používaných nebo funkcí v preview
- Jazyk, jeho čitelnost a konstrukty
- Práce se stavem
- Jednoduchost integrace do CI/CD procesů a GitOps
- Ekosystém, nástroje, komunita a další cloudy

# Bicep
Bicep je nativní Azure nástroj a vznikl jako transparentní nadstavba nad Azure Resource Manager. ARM sice má všechny potřebné vlastnosti, ale jednu zásadní nevýhodu - práce s ním není vždy příjemná. JSON neodpouští, je komplikovaný, ukecaný, funkce jsou kostrbaté a dlouhé, modularice s linkovanými šablonami je tak nepohodlná, že se zdráháte ji použít. Bicep bere všechny výhody ARMu a řeší jeho hlavní nevýhodu - jazyk. Je transparentní, takže můžete přecházet z ARM do Bicep a naopak a nedochází k žádné změně samotného ARMu, který je i nadále srdcem Azure (tzn. Bicep není něco, co Azure musí "implementovat" a něco co by bylo nové a rizikové co do samotného enginu).

## Míra podpory Azure zdrojů
Bicep (ARM) je transparentní nadstavba nad ARM, je nativní a podporuje všechny zdroje Azure a to všetně nových funkcí, veřejných a privátních preview a všech API verzí. V této kategorii na něj žádný nástroj ani zdaleka nemá a to je obrovská výhoda pro mě, protože já potřebuji zkoušet nové věci a produkty. Samozřejmě v produkci nebudete používat věci co jsou v preview, ale ono někdy ostatním trvá funkci dodělat i když je v GA i několik měsíců (a u exotičtějších zdrojů i let) a to už může mrzet. Navíc smyslem preview je si věci vyzkoušet a připravit se na to a po GA tak neztrácet čas. Já ale chci testovací prostředí nasazovat stejně jako produkci, takže chybějící podpora je nepříjemná.

## Jazyk, jeho čitelnost a konstrukty
Já jsem s jazykem velmi spokojen - je jednoduchý, konceptuálně velmi podobný Terraformu, intuitivní. Jediné co mi občas trochu chybí je "adresářový pohled", tedy že jeden soubor rozmontuju na víc souborů pro jednodušší organizaci. Nicméně umí velmi dobře a jednoduše moduly, které to výborně řeší - přesto někdy bych rád i uvnitř modulu použil víc souborů, ať jsou všechny krátké apod. Ale to je věc osobního vkusu. Za mě, pro můj způsob přemýšlení, je Bicep jako jazyk na vrcholku mého žebříčku společně s Terraformem.

## Práce se stavem
Bicep (ARM) svůj vlastní stav nemá a nepotřebuje. Je to dané tím, že je plně nativní a rozumí Azure - stavem je tedy samotný Azure. To je za mne dramatická výhoda, ale jednu drobnou nevýhodu taky najdu.

Proč je to dobré? Nemusíte se trápit s tím, kde bezpečně a spolehlivě state file uložit (to bezpečně podtrhuji - řešení v něm typicky mají hodně věcí včetně hesel) a celé se to zjednodušuje (přišli jste někdy o state file? Pak víte jak je to nepříjemné). Tak například se rozhodnete přidat nový zdroj, ale ze začátku nevíte, tak použijete GUI. Následně si ho vyexportujete z portálu a po nějaké úpravě přidáte do svého Bicep souboru. To je celé - bude to fungovat. State je Azure, takže Bicep vezme vaše zadání, podívá se na realitu v Azure a protože to je stejné, je to pro něj vyřešené. U ostatních nástrojů vám v této situaci hodí chybu a musíte hledat způsob, jak zdroj nejen dát do šablony, ale také ho nějak importovat do stavového souboru. 

Bicep je srostlý s konceptem Resource Group, kde si máte umisťovat zdroje se stejným životním cyklem. Mazání zdrojů pak probíhá jedním ze dvou způsobů:
- Smažete Resource Group
- Použijete Bicep (ARM) v režimu Complete, který srovná předpis vs. obsah Resource Group a nejen že upraví a přidá chybějící zdroje, ale také odmaže zdroje, které jsou tam navíc (odstranili jste je ze šablony, protože už nejsou potřeba). To je plnotučný desired state model a líbí se mi, byť je ve špatných rukou trochu nebezpečný. Tohle ostatní nástroje typicky neumožňují - nepoznají, když vám do resource group někdo něco přidá ručně a pokud něco odeberete ze šablony, musíte explicitně zajistit, že než to uděláte, zničíte to (nebo vymažete ručně z Azure i ze state souboru)

Naproti tomu řešení se stavem jako je Terraform mažou zdroj za zdrojem tak jak si prochází state file. Je to lepší? Nikoli nezbytně, ale pokud nepřemýšlíte jak dávat zdroje do Resource Group a házíte všechno na jednu hromadu, pak vám Terraform bude vyhovovat víc. 

## Jednoduchost integrace do CI/CD procesů a GitOps
Bicep jde převádět do ARM a zpět, takže může snadno využít nástrojů pro ARM. Každopádně Bicep má samostatný modul do GitHub Actions a Azure DevOps Pipelines. Další důležitá vlastnost je test deploymentu před nasazením a ta u ARM je (What-if režim). Dále je občas užitečné mít nástroj pro vynucení některých praktických věcí jako je jmenná konvence, kontrola, že nejsou hesla v souborech, grafické zformátování na jednotný standard a tak podobně. Tady pro Bicep specificky zatím myslím nic není, ale pro ARM lze použít ARM testing toolkit, který řadu těchto věcí nabízí. End-to-end testy (skutečné nasazení v sandboxu a jeho protestování a smazání) jsou samozřejmě také možné, ale specifický nástroj na to není - výborně se dají udělat třeba v GitHub Actions. Celkově vzato z pohledu testování je na tom Terraform a Pulumi asi lépe.

Co se týče GitOps tak veškeré použité parametry lze ukládat do parameters file. V rámci GitOps tak můžete použít obvyklé řešení:
- Jednotlivé součástky jsou řešeny jako moduly, kterých lze využít ke sdílení mezi týmy a rozdělení práce.
- Výsledná šablona je ucelený artefakt a veškeré proměnlivé věci, tedy specifika jednotlivých prostředí, jsou parametrizována a nevyžadují jakýkoli zásah do šablony.
- Definice "instance šablony", tedy prostředí, může být uložena v souboru.

Kolem toho lze modelovat GitOps procesy a vždy mít veškeré parametry takto uloženy v jednom místě pravdy - v Gitu. Nicméně automatizace spuštění nasazení v okamžiku změny v Gitu je klasickým push způsobem (např. s GitHub Actions), nějaký Kubernetes operátor navázaný na pull z Flux nativně k dispozici není.

Bicep ale nemá rekoncilační smyčku přímo v sobě. Je navržen na to, že se spustí, nasadí nebo opraví co je potřeba a doběhne. Triggerem bude nejčastěji změna v Gitu - úprava souboru s parametry nebo samotné šablony. Pokud si přejete, aby Bicep proaktivně detekoval/opravoval změnu v Azure (když vám někdo do prostředí hrábne ručně), musíte si sami vyřešit jeho spouštění (dát si např. opakovaný časový trigger).

## Ekosystém, nástroje, komunita a další cloudy
Bicep a ARM nepotřebují cloudovou službu, protože nemají state file, tím je samotný Azure, takže z tohoto pohledu je to pokryté. K dispozici je velmi povedené rozšíření do Visual Studio Code (a hlavně úžasný Intellisense) a schopnost exportovat šablony přímo z portálu Azure (přes ARM, který lze konvertovat na Bicep). Z mého pohledu je tohle dostatečné.

Komunita kolem Bicep je relativně v začátcích, ale tím, že je to transparentní nadstavba nad ARM, tak vše co existuje pro ARM je tak využitelné i pro Bicep. Dokumentace je za mne v pohodě, návodů i příkladů je dost. Vyhledávání na diskusních skupinách vám často odpověď sežene, ale kolem Terraformu je příspěvků určitě víc.

Podpora dalších cloudů je nulová - jde o nativní nástroj pro Azure, ne pro cokoli jiného.

# Terraform
Terraform je multi-cloud nástroj od Hashicorp a je v současné době asi nejrozšířenějším nástrojem v oblasti správy cloudové infrastruktury obecně. Přemýšlet o Infrastructure as Code v cloudu a Terraform nezahrnout do rozhodování by byla chyba. Ale nemá jen pozitiva - jako všechno najdeme i některé nepříjemnosti, takže o tom co použít vůbec není rozhodnuto.

## Míra podpory Azure zdrojů
Podpora Azure je za mne velmi dobrá, ale ne úplná. Tak například v době psaní článku chybí možnost zapnout Kubernetes addon na Application Gateway ingress kontroler, přepnout storage drivery na CSI nebo nasadit managed SecretProviderClass pro Key Vault. To jsou novější věci, které se objeví s nějakým zpožděním, ale logicky v Bicep/ARM už jsou. Terraform perfektně podporuje infrastrukturní a aplikační zdroje, ale například v oblasti budgetů stále pár věcí chybí. Zkrátka Terraform musí být vždy ručně upraven vývojáři na to, aby podporoval novější funkce a pokud chcete mít schopnost nasazovat méně používané objekty, nové funkce stávajících nebo zkoumat věci v preview, budete muset jít přes nějaký workaround - například doklepávat to v CLI nebo z Terraformu zavolat ARM.

## Jazyk, jeho čitelnost a konstrukty
Co se jazyka a uspořádání Terraformu týče je myslím nesmírně přívětivý a stal se standardem celého trhu. Stejně jako Bicep jde o DSL jazyk a podporuje základní konstrukty jako jsou parametry, proměnné a další operace včetně třeba smyček nebo kondicionálů. Práce se soubory a moduly umožňuje vytvářet velmi přehledné, opakovatelné a udržitelné konstrukty.

V poslední době na Terraform zatlačil jeho novější konkurent - Pulumi. Terraform proto uvedl alpha verzi Cloud Development Kit, tedy varianty, kdy místo DSL můžete použít plnohodnotný programovací jazyk a infrastrukturu definovat v něm. Je jasné, že je to obranná reakce a bude zajímavé sledovat jak to bude hrát všechno dohromady. O výhodách a nevýhodách tohoto přístupu se rozepíšu u Pulumi o trochu později.

## Práce se stavem
Terraform potřebuje state file a ten ukládá v nezašifrované podobě. Nechává na vás, jak to provedete s bezpečností což má dvě roviny. Jednak byste měli zajistit, aby se do state file nedostávalo moc citlivých údajů, což znamená nasazovat infrastrukturu co nejvíce s využitím AAD loginů a ne pevných hesel. To je dobrý nápad vždy, ale u Terraform ještě víc, protože pevná hesla jsou ve state file (např. u Bicep to tak není - heslo se zadá při deploymentu, což zajistí třeba secret management ve vašem CI/CD nástroji nebo se pošle reference na Azure Key Vault a tím, že není state file, se pak nikde neobjevuje). Druhá věc je řídit přístup k tomuto souboru - s tím vám může pomoci Terraform Cloud (ale z pohledu compliance si uvědomte, že pak tato entita reálně ukládá hesla a to ne certifikovaným způsobem typu HSM, pokud je v infrastruktuře používáte).

Výhody této práce se stavem jsou v možnostech jako je generování názvů náhodně (pro zdroje, kde je název v globální URL - v Bicep řešíte přes hash typu funkce uniqueString nebo guid, ale to odvozujete např. od id resource group nebo subskripce právě proto, aby to při každém deploymentu v dané RG vycházelo stejně). Jste schopni nasazovat i mazat zdroje selektivně (-target přepínač), příkaz destroy zlikviduje zdroje tak jak jsou ve state file.

Na druhou stranu state musíte spravovat, takže například přesuny živých zdrojů z jednoho modulu do druhého nebo odstranění komponenty ze šablony vyžadují ruční poladění stavu. Stejný boj je s vytvořením zdroje v GUI a jeho následným zanesením do Terraformu. 

## Jednoduchost integrace do CI/CD procesů a GitOps
Integrace do CI/CD je určitě v Terraformu excelentní a všechny nástroje ho dobře podporují. Co se týče GitOps, tak kombinace modulů a vars souborů umožňuje udržovat sdílené moduly jako funkční bloky, šablony jako hotové projekty (kombinace modulů třeba pro určitou aplikaci) a soubory s vars jako uložené parametry konkrétní instance, třeba prostředí (dev, test, uat, pre-prod, prod). Protože změny lze prohánět přes konstrukty typu Pull Request, dokážete skutečně plnohodnotně GitOps implementovat.

Terraform, ale hlavně komunita kolem, má velmi propracované možnosti testování v rámci CI/CD pipeline. K dispozici je řada projektů zaměřující se na unit testing Terraform šablon, například Terrascan, tfsec, Deepsource, Checkov stejně tak jako komplexní řešení na compliance jako je terraform-compliance nebo end-to-end testování s Terratest. Za mne - v tomhle Terraform a svět okolo exceluje. Bicep takový ekosystém kolem sebe aktuálně nemá. A ostatní hráči, jak ještě uvidíte, na to jdou tak, že používají konstrukty, na které netřeba vytvářet specifické frameworky - stojí na přístupech, které už existují a nepotřebují nutně vytvářet další nástroje. 

Stejně jako u Bicep je Terraform primárně koncipován jako spusť, zjisti jaký je stav, naplánuj změnu a implementuj ji. Pokud chcete, aby vám Terraform pravidelně kontroloval, jestli ve vašem prostředí někdo něco nezměnil ručně a chcete to vrátit do původního stavu, musíte si udělat vlastní trigger o tohle si vyřešit. V klasickém řešení se bude Terraform spouštět v okamžiku, kdy provedete merge změny do Gitu - pokud chcete proaktivně spouštět i bez těchto změn čistě pro detekci driftu, je to na vás. 

Novinkou je Terraform Cloud operátor pro Kubernetes, ale ten pokud správně chápu potřebuje Terraform Cloud nebo Terraform Enterprise a je to spíš "spouštěč" věcí v Terraform cloudu, než přesun Terraformu do Kubernetes API. Je to vlastně CI/CD v Kubernetes navázané na Git, totéž uděláte třeba s GitHub Actions. Každopádně ale dobré sledovat - v Hashicorpu evidentně věci kolem GitOps a konkurenci snažící se jít hlouběji do Kubernetes API vnímají a něco s tím dělají. V kombinaci třeba s Flux v2 pro pull mechanismus z Gitu může být Terraform operátor pro Kubernetes zajímavá volba.

## Ekosystém, nástroje, komunita a další cloudy
Dokumentace je perfektní a to nejen v na samotných Terraform stránkách, tak ale i v dokumentaci jednotlivých cloudů, které pro své uživatele uvádí jak s Terraform začít. Azure například podporuje Terraform napřímo i ve svém Cloud Shell a blueprinty a architektury jako je Azure Well-architected Framework jsou nabízeny i ve formě Terraform šablon přímo od Microsoftu. Ekosystém je nesmírně silný, podpora všech tří významných cloudů dobrá. Na Terraform existují samostatné komerční knihy, tuny příkladů a diskusí.

# Pulumi
Základním prvkem Pulumi je myšlenka, že není důvod dělat nové DSL, když jsou tu plnohodnotné programovací jazyky. Pro programátory nebo týmy s velkými imperativními choutkami je to dost zásadní argument viz dále, ale jiní to budou vnímat spíše odpudivě. V čem si ale Pulumi za mě zaslouží největší potlesk je způsob podpory Azure zdrojů - žádný z dalších nástrojů třetích stran se mu nepřibližuje a měly by se jím inspirovat. 

## Míra podpory Azure zdrojů
Pulumi na tom byl nejprve stejně jako Terraform (ostatně i Terraform moduly používal). Podpora velmi dobrá a široká, ale ručně dodělávaná. Takže nové funkce, nové flagy, nové verze, preview služby - smůla. To se ale změnilo s modulem azure-native. Od teď Pulumi Azure zdroje automaticky generuje z API specifikace a má tak extrémně blízko k samotnému Azure (některé private preview věci mohou podporovat jen ARM šablony, ale API je vždy k dispozici minimálně ve fázi public preview). To je myslím naprosto ideální přístup a v tomto mi Pulumi naprosto vyhovuje. Můžu použít nástroje třetí strany i v situaci, kdy jsem experimentátor potřebující vždy dostupnost nejnovějších vlastností cloudu i těch v preview.

## Jazyk, jeho čitelnost a konstrukty
Pulumi je sice deklarativní, ale používá běžných programovacích jazyků. Každý Azure zdroj je tedy řekněme třída a parametry zdroje (velikost VM, do kterého subnetu patří apod.) jsou atributy, které jí založíte například konstruktorem. 

Pro mne je to dost neúsporné a obtížně čitelné. Ale pro programátora, který žije v C#, Javascript, Python nebo Go (všechny tyto jazyky jsou podporované), je to určitě jinak. Ve většině situací si ale myslím, že IaC nástroje budou využívat SRE a obecněji lidé se zkušenostmi spíše z provozu, než chladnokrevní vývojáři a pro ně je obvykle DSL příjemnější. Ale je to otázka osobního vkusu.

Výhodou plnohodnotného jazyka může být to, že ho lze použít. V DSL samozřejmě není problém kombinovat nějaké řetězce apod., ale na komplikované imperativní úkony to určitě není. Nemusím opustit programovací jazyk použitý v Pulumi na to, abych například:
- Vytáhnul dynamicky parametery infrastruktury z externího zdroje, například kontaktoval IP Address Management nástroj a nechal si přidělit rozsah IP adres pro VNET nebo zjistil metadata z CMDB a zapsal je je jako tagy
- Založil tabulky v databázi a nahrál syntetická data
- Provolával triggery na jiné systémy, například odstartoval CI/CD pipeline pro nasazení aplikace po dokončení provisioningu infrastruktury
- Zajistil service discovery nových objektů například doplněním do Consul, CMDB, přidáním záznamu do DNS serveru apod.

To už ale jdu z deklarativního přístupu k imperativnímu - daleko víc flexibility, ale může to být úkor předvídatelnosti, spolehlivosti a udržitelnosti, pokud to neudržím v rozumných mezích.

## Práce se stavem
Stejně jako Terraform potřebuje Pulumi state a ten se snaží "prodat" ve své cloudové službě (default Terraform je state v lokálním souboru, default Pulumi je v jejich cloudu), ale tu má samozřejmě Terraform taky. Z compliance důvodů ale možná budete chtít držet state svými prostředky, třeba v Azure Blob Storage, a to samozřejmě také lze. Pro stav platí vlastně stejné výhody a nevýhody jako pro Terraform - Bicep state nemá a problém jak ho řešit odpadá. Pokud jste přeskočili, vraťte se k této části u Terraformu, bude to vlastně stejné povídání.

## Jednoduchost integrace do CI/CD procesů a GitOps
Pulumi má velmi širokou podporu CI/CD nástrojů, takže v tomto směru mi určitě nic nechybí. Modularizace je možná vytvářením balíčků tak, jak je v programovacím jazyce běžné.

Podpora pro testování je na velmi dobré úrovni. Stejně jako Bicep/ARM what-if a terraform up přináší pulumi preview stejné funkce, tedy běh nanečisto. Zajímavý je přístup k unit testování konfigurací, protože tam dokáže využít vlastností konkrétního použitého jazyka. V závislosti na tom co použijete tak můžete psát unit testy v libovolném toolingu kolem daného jazyka. To umožňuje využít bohatý ekosystém a nástroje.

Unit testy ale neposlouží pro odchycení nějakých konkrétních parametrů a politik. Na to má Pulumi CrossGuard, který se dá použít pro implementaci politik.

Integrační nebo chcete-li end-to-end testy jsou podobně jako u Bicep ve vaší režii, ale jsou samozřejmě velmi dobře možné - třeba s využitím GitHub Actions.

Specificky z pohledu GitOps není problém tento koncept vystavět třeba nad GitHub Actions. Existuje také Pulumi operátor pro Kubernetes, který se rovněž může postarat o sledování Git a nasazování změn. Nicméně nejedná se o plnou integraci do Kubernetes - na to je expertem určitě Crossplane. 

## Ekosystém, nástroje, komunita a další cloudy
Podpora pro další cloudová prostředí je velmi dobrá a přímo Pulumi má nástroje na konverzi ARM nebo Terraform šablon, což je příjemné. Dokumentace mi vyhovuje, ale z pohledu prohledávání webů, blogů a diskusních skupin nebo knížek se to s Terraform nedá moc srovnat. 

# Crossplane
Posledním zástupcem v dnešním srovnání je Crossplane. Řešení vystavěné kolem Kubernetes API, které ho využívá spolu s celým ekosystémem pro implementaci infrastructure as code. Všechno je Kubernetes resource. Definice jednotlivých zdrojů v infrastruktuře, jejich state, šablony s vyšší mírou abstrakce, zkrátka všechno.

## Míra podpory Azure zdrojů
Jednoznačně velkou slabinou je šíře podpory Azure zdrojů a jejich čerstvost. Nejen v Azure, ale i v jiných cloudech, bych zatím použití Crossplane pro všechno považoval za zásadní problém, protože toho prostě chybí příliš mnoho. Snad jen specifické projekty, které si vystačí s tím co v Crossplane dnes je, jsou dobrým kandidátem, ale univerzální řešení, které nahradí váš Bicep, Terraform nebo Pulumi to myslím dnes zkrátka není. Ale pokud vám výhody pro konkrétní projekt za to stojí (a jsou nemalé, takže si to umím dobře představit), jděte do toho.

## Jazyk, jeho čitelnost a konstrukty
Jazykem pro Crossplane je YAML a definice objektů tak, jak je v Kubernetes běžné. To může být pro někoho výborná zpráva - YAML je přece hezky čitelný a už ho dobře znáte. Pro jiného to může být pravé peklo, protože jedna mezera navíc dokáže všechno rozhodit a jazyk samotný vám nenabídne nic moc pro podporu věcí jako je generování názvů, skládání řetězců, vytahování dynamických hodnot, referencování zdrojů mezi sebou a tak podobně. Tohle všechno musíte implementovat Kubernetes způsobem - dynamické hodnoty jako klíče jsou v Secrets, odkazy jeden na druhý objekt jsou podle jejich názvu, na proměnné a složitější operace sáhnete po Helm nebo Kustomize a tak podobně. To může vyhovovat týmu zvyklém na Kubernetes, ale ostatním dost možná ne.

Abstrakce nad základními zdroji jsou možné a fungují tak, že si vytvoří vlastní definici kompozitního resource, který se skládá z menších komponent. Je to vlastně podobné jako u ostatních, jen místo modulu (a jeho vstupních parametrů jako u Bicep a Terraform), package (jako u Pulumi) jde tady definici nového zdroje, nového API a jeho struktura (vstupní parametry) a distribuce je přes Crossplane packages v OCI image formátu (řekněme taková alternativa k Terraform Registry).

## Práce se stavem
Problému stavu, jeho bezpečnému a spolehlivému uložení se Crossplane elegantně vyhnul - state je v Kubernetes, v kterém Crossplane provozujete. Pokud je to něco jako minikube nebo kind na notebooku, máte asi problém, ale stejně tak můžete použít Azure Kubernetes Service s SLA a bude to hned jiná píseň. Pokud tedy jde o vaše vlastní clustery můžete redundantně postavit Etcd a zálohovat si ji nebo použijete Kubernetes službu v cloudu. A to je zajímavá výhoda - "managed state" nemusíte mít od výrobce řešení, ale od svého cloudu (na rozdíl od Terraform Cloud nebo Pulumi Cloud).

## Jednoduchost integrace do CI/CD procesů a GitOps
Opět platí, že Crossplane vlastně veškerou odpovědnost za nástroje pro nasazování, šablonování nebo testování hodil na komunitu kolem Kubernetes. Crossplane používá stejné postupy, jsou to CRD v Kubernetu, takže stávající nástroje pro politiky v YAML souborech apod. se dají použít. Ale je tu například docela palčivá absence některých imperativních věcí - ARM what-if, terraform plan a pulumi preview. Tady prostě hodíte YAML do clusteru a uvidíte. Pro klasické ověření funkčnosti před nasazením a tvorbu CI/CD pipeline se zpětnou vazbou autorovi změny to je tady docela problém.

Na druhou stranu v čem Crossplane vyniká je podpora GitOps. Všechno je Kubernetes, takže můžete použít nejen všechny push metody (Kubernetes je integrovaný do všech pipeline systémů na světě), ale pull systémy, které číhají na změny v Gitu a sami je aplikují bez nutnosti jim to říkat (Flux, Flux v2, Argo CD). Navíc Crossplane, protože vychází z myšlenkových základů Kubernetes, používá rekoncilační smyčku. Na rozdíl od všech dříve uvedených není zaměřen na spusť, zjisti co a jak, nasaď. Neustále sleduje jestli realita odpovídá požadovanému zadání - automaticky bez dalších nástrojů. Pokud tedy chcete nejen nasazovat změny, ale také opravovat všechno, co by někdo neoprávněně změnil třeba přes GUI do Azure, tak pro tento přístup je Crossplane přímo zrozen.

## Ekosystém, nástroje, komunita a další cloudy
Z pohledu podpory dalších cloudů je to podobné jako pro Azure - jsou tam jen základní věci a tempo přidávání mi zatím nepřipadá takové, že by se to během krátkého horizontu mělo změnit. To je velká škoda, ala naznačený směr dává hodně velký smysl. Nicméně konsolidace je teprve na začátku. Podobný koncept Open Service Broker se jednoduše nechytl, takže tohle už jednou selhalo. Alternativně všechny cloudy nabízí své proprietární Kubernetes operátory, které sice typicky neumožňují abstrakce do kompozitních zdrojů tak elegantně jako Crossplane, ale jsou ve finále na stejném písečku, takže vzniká zmatek co použít. Do toho vezměte úvahu, že jak Terraform tak Pulumi na tento směr reagují a nabízí svoje operátory pro Kubernetes. Ty sice nedosahují takové míry integrace (řešení principiálně nejsou Kubernetes native), ale řadu výhod přístupu Crossplane tak dostanete i s tradičnějším řešením.

Ekosystém nástrojů je na jednu stranu obrovský, protože jsou to všechny systémy pro Kubernetes - policy engine, validační nástroje, šablonovací nástroje typu Helm, nasazovací patch nástroje typu Kustomize, GitOps nástroje Flux a Argo a samozřejmě celá řada dalších. To je nesmírně silné a je to obrovská výhoda. Na druhou stranu ale nic z toho není specifické pro Crossplane, takže sice máte nástroj, ale nějaké best practice kolem jeho používání, příklady, články nebo knihy jsou zdroje značně omezené. Zkrátka u Crossplane se připravte na to, že se budete cítit průkopníky. To je pro experiment s konkrétním projektem určitě skvělé, ale ne pro produkční migraci firmy do cloudu - tam vás bude Crossplane spíš omezovat a brzdit.

# Shrnutí a doporučení
Popíšu pár situací, moje doporučení a jeho vysvětlení.

| Situace      | Doporučení | Důvod |
| ----------- | ----------- | ----------- |
| Řešíte centrální pohled na Azure a to ne primárně nutně nasazování zdrojů typu VM,  ale spíše governance - správa subskripcí, RBAC, politik, budgetů apod.    | Bicep/ARM       | Podpora těchto konstruktů je u 3rd party nástrojů často neúplná a stejnak jsou tyhle věci dost specifické pro každý cloud a to i po procesní stránce. Použijte nativní nástroj. | 
| Vsadili jste hlavně na Azure a hledáte plnou konzistenci od experimentálních prostředí až po produkci. Potřebujete kompletní podporu všech zdrojů i nejnovějších funkcí.    | Bicep/ARM       | 100% pokrytí včetně preview vlastností nabídne typicky jen nativní nástroj. | 
| Máte mutli-cloud strategii a řešíte automatizaci primárně produkčních a UAT prostředí. Jde vám o ucelený pohled, možná centrální IT řešení, celofiremní doporučení, operations.   | Terraform      | Terraform je multi-cloud nástroj, který je nejstandardnější (není konfliktní, líbí se skoro všem), nejoblíbenější a velmi dobře funkční pro tyto situace. | 
| Pro váš aplikační projekt, který je tažen především vývojáři, potřebujete vyřešit nasazování multi-cloud infrastruktury. Chcete širokou podporu Azure zdrojů a váš tým vývojářů si všechno pořeší.    | Pulumi       | Pulumi nejspíš nebude vyhovovat infra a operations lidem, ale pro tým vývojářů může být tou nejpříjemnější cestou. Navíc podporuje multi-cloud velmi dobře a můžete ho využít i pro nasazování preview věcí, tedy od dev až do produkce bez nějakých nedostatků. | 
| Pro svůj projekt využívající Kubernetes potřebujete, aby váš tým mohl pohodlně řídit i nasazování PaaS komponent jako jsou databáze a fronty jako služba. Nepotřebujete nějaké centrální řešení pro celou firmu, jde čistě o záměry tohoto projektu, kde chcete jet hlavně GitOps na všechno.   | Crossplane      | Na rozdíl od ostatních variant se stane Crossplane součástí vašeho Kubernetes ekosystému, pokud vystačíte s tím, co dnes v Azure umí vytvořit. Rozhodně pro takový scénář to bude velmi elegantní řešení. | 
| Začínáte a vůbec nevíte co použít, ale nechcete vyklikávat a skriptovat, nějaký lepší mechanismus by se vám hodil.  | Bicep/ARM nebo Terraform      | Pokud opravdu nevíte, nezkoušejte exotické varianty a jděte po mainstream přístupu. Tam určitě počítám Terraform. Možná ale současně jděte po tom, co je jednoduché a dobře kombinovatelné s vyklikáváním, které se na začátku prostě dít bude - to je rozhodně doménou Bicep/ARM. | 

A teď další pohled - vyhlásil bych (čistě subjektivní) vítěze v mých kategoriích:
- Míra podpory Azure zdrojů včetně těch nejnovějších, méně používaných nebo funkcí v preview
  - Bicep, tedy je to jasné a další v pořadí Pulumi
- Jazyk, jeho čitelnost a konstrukty
  - Terraform, ale Bicep velmi těsně v závěsu
- Práce se stavem
  - Bicep, nejlepší stav je ten reálný, ne jeho obraz v souboru
- Jednoduchost integrace do CI/CD procesů a GitOps
  - Terraform, ale Crossplane je určitě šampion na GitOps
- Ekosystém, nástroje, komunita a další cloudy
  - Terraform

Ať už se vydáte jakoukoli cestou, z pohledu infrastructure as code doporučuji:
- Nezabijte globální standardizací vývoj - jedna věc je dostat pod kontrolu governance, bezpečnost a produkční workloady, jiná jsou vývojová prostředí. Mít na infrastrukturu jednotné moduly od dev po prod je určitě skvělé a čím víc týmů k tomu dojde, tím lépe, ale začít v Azure by nemělo znamenat nemožnost experimentovat s GUI, CLI i zdroji v preview.
- Pro široké nasazení nepodlehněte tomu, co je cool. Jděte po nudných standardních věcech (jen si je nespleťte s "legacy" - standardních pro svět cloudu, ne pro "devadesátky"), novátorské postupy aplikujte spíš na jednotlivé projekty, než plošně. 
- Mějte jednotné místo pravdy v Gitu, kde budou nejen šablony, ale i "dosazené parametry" či chcete-li popisy instancí. Klidně to pouštějte zatím z notebooku ručně - tohle je na začátku důležitější, než jak skvěle automatizujete spuštění pipeline. Nejdřív se naučte kvalitně psát, dokumentovat, sdílet, modularizovat a udržovat data o předpisech i nastaveních na jednom místě.
- Doporučuji věci kolem schvalování, revizí a diskusí přesunout na version control systém a použít GitOps - třeba s GitHubem nebo Azure DevOps.
- Až budete připraveni přesuňte nasazování na CI/CD nástroj, nepouštějte věci z notebooku pod svým účtem a současně vymyslete, jak pracovat s technickými účtu, pod kterými CI/CD nasazuje. 
- Dbejte na čistotu citlivých informací - žádná hesla a klíče v šablonách, v souborech, state filech. Najděte lepší mechanismy - Managed Identity, Azure Key Vault apod.
- Vysněnou metou ať je automatizované testování, ale nechte to až si budete jistí zbytkem. Kontrolujte syntaxi, nasaditelnost před samotným nasazením, sledujte politiky a na konec přidejte i "integrační testy" typu nasazení nanečisto do izolovaného prostředí nebo odrolování změn přes pre-prod.

Držím palce! A napište mi na LinkedIn nebo Twitter svoje tipy a triky nebo další možnosti, které se vám osvědčily.