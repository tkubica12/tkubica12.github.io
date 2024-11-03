---
layout: post
published: true
title: "Helm vs. Kustomize - co si mám vybrat pro nasazování do Kubernetes?"
tags:
- Kubernetes
---
Dnes se chci podívat na téma, které je dost subjektivní a lidé se na něm často neshodnou - mám do Kubernetes nasazovat přes Helm nebo raději Kustomize? Určitě to dneska nerozlouskneme, ale chtěl bych sepsat pár atributů podle kterých se pro danou situaci rozhoduji. A co použít oboje? Nebo ani jedno?

# Proč potřebuji Helm nebo Kustomize
Když jsem před lety začal nasazovat do Kubernetes, zjistil jsem, že v tom YAMLu potřebuji změnit tag image. Nejdřív jsem měl app-v1.yaml, app-v2.yaml a tak pořád dál - to nebylo pěkné. Tak jsem si místo něj dal třeba !tag! a před jeho nahozením jsem ve skriptu či CI/CD udělal sed v bash. Pak jsem přidal další a pak další. Začal to být docela zmatek. Přišel jsem na to, že si tady vyrábím vlastní šablonovací systém a to není dobrý nápad. Navíc jsem musel řešit jak poznat které YAMLy tam chci poslat - celý adresář? A co teprv když jsem měl nainstalovat něco třetí strany - stáhnou si jejich YAMLy, pozměnit co potřebuji, ale jak si pak vzít jejich novější verzi aniž bych všechny svoje modifikace musel dělat znovu? V té době jsem si všiml, že open source projekty používají Helm - to bylo řešení. Na první pohled trochu komplikované a moc rád jsem to neměl, ale to se časem změnilo.

Při nasazování bude určitě potřeba poslat do clusteru vícero objektů (nějaké deployment, service, PVC, ...) a při tom jednoduše určit nějaké vstupy jako je verze image a tak podobně. Jak získat lepší opakovatelnost, možná schopnost modularizovat, sdílet, využívat projektů třetích stran, verzovat, řídit verze? K tomu samotné YAMLy nestačí - chtělo by to něco lepšího. Helm je velmi úspěšný projekt, nesmírně populární. Kustomize vznikl jako protiváha s dost odlišnou mentalitou. Kromě toho jsou tu i další nástroje, které se na to snaží mít názor.

# Příkladové scénáře a jak se k nim staví Helm vs. Kustomize
Zamýšlím se nad oběma nástroji v určitých scénářích, ve kterých se každý chová jinak. Je samozřejmě mnoho situací, které řeší oba stejně dobře, ale ty teď nechme stranou.

## Vytvoření vrstvy abstrakce - uživatel nemusí znát všechna střeva Kubernetes
Možná potřebujete v produkci nasadit aplikaci výrazně jinak, než v rámci dev prostředí. Není to jen o počtu replik a alokovaných zdrojích, ale o perzistentní storage (kterou v dev nepoužíváte a ani ji nemáte) a dalších komponentách. Nebo nasazujete současně do on-prem clusteru a do Azure Kubernetes Service a s tím souvisí rozdíly v některých objektech - například pro AKS nasadíte SecretProviderClass s Azure Key Vault a anotace pro objekty Service či Ingress odpovídající specifikám tohoto prostředí, zatímco v on-prem variantě máte jinak řešené secrets, jiný storage class na volume, jiné anotace a tak podobně. Ještě jeden scénář - vaše aplikace je určená pro širší publikum a potřebujete lidem umožnit vybrat si, zda chtějí jen základní open source verzi nebo placenou variantu, která má navíc autentizační systém integrovaný třeba s AAD a jestli chtějí základní zabudovaný monitoring (samostatnou jednoduchou instanci Promethea s Grafanou) nebo budou řešení napojovat na vlastní monitoring.

Helm je postavený na šablonách, v kterých lze dělat imperativní operace při generování výsledku. Není tedy problém na základě nastavení některé zdroje nenasazovat, výrazně měnit strukturu podle potřeby (např. vypustit volume a jeho mapování z deploymentu, když není potřeba). Přes jednoduchou abstrakci typu deployMonitoring=true zajistíme nasazení Promethea a Grafany včetně předání potřebných informací do naší aplikace nebo její config mapy. Nebo můžeme udělat něco jako deploymentType basic/enterprise či persistentStorage true/false apod.

Kustomize nepoužívá šablony a nevytváří vrstvu abstrakce. Co modifikujete (patchujete) jsou vlastnosti Kubernetes datového modelu, nepřidáváte si svůj typu "deploymentType". Modifikovat nasazení přes Kustomize znamená rozumět všem použitým Kubernetes objektům. 

Pokud tedy chcete nabídnout jednodušší parametry při nasazování aplikace, které nevyžadují hluboké znalosti, je Helm ideální. V případě Kustomize je něco takového podstatně složitější (například kondicionály mu vlastní rozhodně nejsou) a budete to řešit spíš tak, že nabídnete už hotové patch (overlay) pro určitě scénáře. Tak dokážete konzumentům zjednodušit rozhodování a nepotřebují všemu hned rozumět. 

Na druhou stranu pokud jde o abstrakce pro vnitřní týmy může se vám stát, že si nakonec sami vyrobíte něco jako Open Application Model (na jeho implementaci pro Kubernetes - KubeVela - se podíváme někdy příště). Pak bych doporučoval spíše jít s proudem a nastoupit do KubeVela a tyto abstrakce pak nasazovat přes Helm nebo Kustomize (tedy použít Helm/Kustomize pro úpravu parametrů OAM).

## Možnost změnit cokoli bez úpravy základních objektů/šablony
Při použití Helm se objevuje jeden nešvar. Vytáhneme si klíčové parametry, možná s trochou abstrakce a pak uživatel řekne, že potřebuje změnit nějaký jiný parametr - třeba místo serviceType LoadBalancer potřebuje použít NodePort, protože neběží v nějakém cloudu ale třeba na jednom IoT zařízení typu Raspberry a tam nemá implementaci pro typ LoadBalancer. Fajn, tak to přidáte. Pak někdo bude potřebovat anotace, aby dokonfiguroval proprietární nadstavby Ingresu nebo Service. Přidáte. Pokud máte velké množství příjemců, tak nakonec přidáte skoro všechno. Je tu také možnost, že vydavatel Helmu to neudělá a pak je na vás zvážit, jestli si chcete šablonu upravit sami. To samozřejmě jde, ale při každé další změně šablon od poskytovatele to budete muset vždy znovu upravit.

Kustomize je v tomhle ohledu skvělý, protože dokáže přenastavit jakýkoli parametr aniž by se musel měnit základ (base YAMLy). Zkrátka pokud víte co přesně hledáte, je Kustomize velmi příjemný.

Mimochodem - ne každého napadne, že by mohl věci kombinovat a získat tak výhody obojího. Vaše CI/CD může vzít nejprve Helm (příkaz helm template), vygenerovat objekty (YAMLy) a nad nimi pak přes Kustomize provést patch (případně to udělat přes deployment hook v Helmu nebo naopak v Kustomize je na to generátor). Nemusíte tak měnit originální šablony a přesto dosáhnout svého cíle.

## Změny vyskytující se u mnoha objektů
V případě Helm můžete do šablony dát cokoli kamkoli. Tak například pokud chcete umožnit uživateli dodat si vlastní label, který z důvodů inventarizace nebo řízení nákladů bude u všech součástek stejný, ale konfigurovatelný, tak ho přidáte do všech potřebných šablon a ven vytáhnete jako jediný parametr. Tohle je v případě Kustomize docela problém, protože byste měli vytvořit patch (overlay) úplně pro všechny objekty - pro každý zvlášť. Je to tak nepříjemné, že se to komunita rozhodla vyřešit speciálními funkcemi - jedna pro přidávání labelů, druhá pro anotace, třetí pro vytvoření prefixu před každým jménem a tak podobně. Bohužel pro mě se tak čistota a krása Kustomize trochu pokřivila - z jednoduchého patch modelu postaveného čistě na Kubernetes objektech jsou tu najednou nové konstrukty a dokonce i nové koncepty jako jsou Kustomize Compontens.

## Release vlastnosti
Helm má i ambice na poli správy nasazování. Tuhle hru Kustomize nehraje a jednoduše spoléhá na soubory či Git. Helm se snaží nabídnout vám životní cyklus a možnost ho ovlivňovat - například pokud se nasazení nepovede udělat rollback nebo přidávat hooky na různé události (například před nasazením zavolat skript pro backup databáze ... pro všechny případy).

Myslím ale, že důležitost něčeho takového dramaticky poklesla. Od prvních dob Helmu před šesti lety se ve světě CI/CD nástrojů podpora pro Kubernetes stala naprosto běžnou, bohatou a výborně vyladěnou záležitostí. Proč si to dnes budu patlat v rámci Helm, když mám v GitHub Actions všechno hezky připravené. Role Helm tak v dnešní době je spíše ve schopnosti kompletovat a nasazovat, ne řídit celý životní cyklus včetně komponent okolo - pokud potřebuji pro jistotu odzálohovat data před nasazení aplikace, myslím, že to dnes určitě udělám v CI/CD, ne podivně v Helmu.

## Generovatelnost vstupů
Všechny Helm vstupy lze uložit do Values souboru, což je obyčejný YAML. Díky tomu se dají velmi pěkně generovat. Takovým testem může být myšlenkový experiment - představme si, že potřebujeme vytvořit GUI, v kterém by uživatel vyklikal jak svou aplikaci chce a ono se to samo. V případě Helm to bude dost jednoduché - stačí udělat okno s příslušným obsahem a jednoduše vygenerovat YAML. Tohle u Kustomize takhle snadné nebude - tam už vaše GUI musí rozumět Kubernetu. Jsme zase u toho - Helm může být vrstva abstrakce.

## Univerzálnost modifikace složitých struktur
Představme si, že součástí nasazení je ConfigMap s vnořeným souborem - aplikace totiž vyžaduje konfigurák ve formátu třeba ini nebo JSON. Pokud jde o Kustomize, ve svém overlay musím nahradit celou value - a tou je v tomto případě celý ini soubor. U Helm můžu v šabloně dát cokoli kamkoli, tedy udělat si z jednoho místa v ini vstupní parametr. A teď ještě považte, že Helm už nemusí obsahovat pouze už tak poměrně mocné Go šablony, ale můžete to celé napsat v Lua. Dá se tedy udělat prakticky cokoli včetně pokročilejší logiky.

Kustomize není šablonovací jazyk, takže takhle to neudělá, ale má alespoň k dispozici generátor ConfigMap - to se může hodit. Nicméně síla Helmu je v tomto případě v jiné dimenzi.

## Schopnost sdílet, šířit, prodávat, řetězit
Helm má dobře promyšlený systém sdílení. Standardní repozitáře v OCI formátu, možnost vyhledávat Charty nebo dobře zpracovaný systém dependency chartů usnadňují sdílení projektů. TO je hodně poznat zejména u těch veřejně dostupných dostupných. Také se mi líbí zabudované verzování přímo v metadatech Chartu, což oceníte zejména při jejich vnořování nebo využívání komponent z veřejných zdrojů. Kustomize v tomhle jednoduše spoléhá na soubory resp. Git. Ale pro použití uvnitř organizace to nemusí být vůbec nevýhoda.


Mám tedy použít Helm nebo Kustomize nebo oboje? Nebo něco úplně jiného, třeba tlačit YAMLy Terraformem nebo je generovat v CI/CD nebo Skaffoldem? To za vás určitě nerozhodnu, ale já to mám takhle:
- S Helm jsem začínal dříve, než Kustomize existoval, zvyk hraje určitě roli.
- Odlišovat jednotlivá prostředí přes Values file v Gitu se mi zdá přehlednější, než v adresářích a vícero souborech v overlay - tady mi Helm vyhovuje víc.
- Pokročilé vlastnosti typu Lua, složité šablony, release management Helmu nepotřebuji.
- Pro demo účely mi vyhovuje, že base Kustomize YAML je normálně nasaditelný i bez patchování - nemusím hned ukazovat nějaké ošklivosti v šabloně, vše je srozumitelné.
- Vyhovuje mi, že můžu přepsat libovolný parametr aniž bych musel řešit změnu šablony a vzpomínat si, proč jsem tentokrát pojmenoval proměnou "tag" a ne "imageTag" jako posledně - ta vrstva abstrakce mi vlastně občas působí potíže.

Co z toho plyne pro mě? Pro účely zkoušení a demování začínám preferovat Kustomize. Od komponent třetích stran ale očekávám spíše Helm (až moc často teď chodí s vlastním CLI, přes které to instalují). Pokud bych měl řešit komplexní projekt, asi bych dal přednost Helmu.