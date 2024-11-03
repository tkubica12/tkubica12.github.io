---
layout: post
title: SLA a ceny pro Azure Kubernetes Service vs. EKS a GKE
tags:
- Kubernetes
---
Dnes je uvolněno do plné platnosti (GA) volitelné SLA pro Azure Kubernetes Service. Jak funguje, je opravdu potřeba a jak vypadá v porovnání s AWS a Google?

# AKS zůstává i nadále zdarma pro produkční použití
AKS má skvělou cenu - je zadarmo. Platíte za worker nody (to, kde reálně běží vaše aplikace) a to běžnou cenu VM bez nějakých příplatků a Kubernetes control plane (API Server, Etcd apod.) dostáváte zdarma. Jak je to v takovém případě s SLA?

Virtuální stroje se řídí SLA pro VM, tedy 99,95% SLA pro clustery bez použití zón dostupnosti a 99,99% SLA na clustery přes víc zón dostupnosti. 

Control plane tím, že je zdarma, nemůže mít formálně vzato SLA (není z čeho vracet peníze), ale nabízí Service Level Objective. Je to indikace jak je služba designovaná a přestože to není garantováno smluvně, není to řečeno jen tak do větru, takže podle toho můžete plánovat a počítat celkovou dostupnost nebo riziko. Toto SLO je 99,5% a je potřeba říct, že nedostupnost API serveru neznamená nutně odstávku aplikačního provozu! V jednoduchém scénáři si toho vůbec nevšimnete, všechno jede dál. Samozřejmě dlouhodobá odstávka už bude mít vliv, pokud dojde k nějakým dalším událostem v clusteru, které si vyžadují zásah mozku. Samozřejmě to je instalace nové verze aplikace, ale třeba i autoškálování nějaké aplikace při zátěži či vypadnutý node a nutnost jeho Pody rozjet na jiném. Pokud se tedy sejde nedostupnost řídícího uzlu s nedostupností worker node (2 havárie současně), je to problém. Každopádně to není tak, že výpadek řízení znamená hned výpadek aplikace.

AKS tedy můžete provozovat zdarma, v libovolném množství a včetně zónově redundantní varianty s SLA na nody 99,99% a SLO 99,5% na řízení, které nemá okamžitý dopad na nedostupnost aplikace. Nejde tedy o žádné "freemium", trial ukázku nebo něco nevhodného pro produkci.

# Příplatkové SLA
V některých společnostech jsou věci zdarma a bez SLA prostě zakázané nebo zkrátka chcete mít větší jistotu a dostupnost řídích uzlů AKS. Nově si ji můžete připlatit a u clusterů se zónovou dostupností má control plane AKS SLA 99,95%: [https://azure.microsoft.com/cs-cz/support/legal/sla/kubernetes-service/v1_1/](https://azure.microsoft.com/cs-cz/support/legal/sla/kubernetes-service/v1_1/). Získáváte tak 99,95% na AKS řízení a stále máte 99,99% na worker nody.

Kolik vás něco takového stojí? Je to 0,1 USD za hodinu.

# AWS EKS
Jaké je srovnání ceny a SLA s EKS? Tam je SLA 99,9% a řídí uzly stojí také 0,1 USD za hodinu. Navíc zde není verze zdarma, takže platba je v tomto případě povinná.

# Google GKE
Google svou strategii v cenotvorbě a SLA v poslední době změnil (ne k lepšímu). Od 6. června to pokud správně čtu mají tak, že můžete dostat SLA na řídící nody na úrovni 99,95% a rovněž za 0,1 USD za hodinu. Z tohoto pohledu tedy stejné, jako AKS. V čem je ale rozdíl je to, že verze zdarma už je spíše upoutávkou pro vývojáře, než produkční řešení, protože můžete mít takový cluster jen jeden a nepodporuje VM v zónové dostupnosti. 


Shrnuto. AKS je dnes už jediný ze tří hráčů, který nabízí plně produkční Kubernetes zadarmo - EKS to nikdy nedělalo a GKE změnilo strategii a nabízí už jen jeden nezónový cluster na hraní. Z pohledu příplatků za SLA, jsou ve všech případech finančně naprosto stejné, ale u zónově redundantních clusterů v tom AKS a GKE zahrnuje 99,95% SLA, EKS jen 99,9%.