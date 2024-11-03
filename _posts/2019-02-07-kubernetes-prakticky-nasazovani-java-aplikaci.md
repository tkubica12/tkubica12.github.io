---
layout: post
status: publish
title: 'Kubernetes prakticky: nasazování Java aplikací'
tags:
- Kubernetes
---
Ve spolupráci firem Microsoft a Gopas proběhl 31.1.2019 workshop na nasazování Java aplikací v Azure Kubernetes Service. Společně s kolegy [Valdou Zavadsky](https://github.com/valda-z) a [Tomášem Slavíkem](https://github.com/tslavik) jsme připravili podklady pro tento workshop, které najdete na GitHubu [https://github.com/azurecz/java-k8s-workshop](https://github.com/azurecz/java-k8s-workshop). Co tam je?

# Modul první - zabalení Java aplikace do kontejneru a nahrání do Azure Container Registry
V prvním modulu se seznámíte s tím, jak jsme Java aplikaci zabalili do kontejneru. Kolegové připravilli jednoduchou aplikaci postavenou na frontend single-page-app a backend API pro todo využívající PostgreSQL v Azure jako službu pro datovou perzistenci. Můžete se mrknout jak používají Maven pro kompilaci a kompletaci kódu todo. Také jsme následovali best practice a oba kontejnery neběží pod rootem, ale neprivilegovaným účtem. K dispozici máte také Docker Compose file, abyste mohli kód snadno spustit i lokálně na notebooku. Vzykoušíte si i cvičně pustit kontejner bez orchestrátoru v Azure Container Instances s využitím Azure Container Registry.

# Modul druhý - úvod do Azure Kubernetes Service
Druhý modul je základním úvodem do AKS. Vyzkoušíte si nasazení do clusteru, práci s labely, Deployment a Service, rolling upgrade a nainstalujete si Helm a Ingress pro pozdější využití v labu.

# Modul třetí - nasazení Java aplikace do AKS
Ve třetím modulu si vytvoříte Azure PostgreSQL instanci, zadáte přístupové údaje do Secret a nasadíte aplikaci přes Deployment, Service a Ingress.

# Modul čtvrtý - detailnější pohled na AKS pro naší Java aplikaci
Ve čtvrtém modulu si vyzkoušíte další vlastnosti AKS, které se vám můžou hodit. Namapujete si sdílený Volume pro statický obsah implementovaný přes Azure Files, použijete ConfigMap pro custom nastavení NGINX ve kterém servírujeme frontend, init kontejner, downwards API a sdílený kontejner pro inicializaci a předání některých provozních údajů. Dále si pustíte CronJob pro pravidelné exporty dat z PostgreSQL a na závěr si ukážeme použití anotací pro pokročilejší nastavení NGINX Ingress.

# Modul pátý - CI/CD s Java aplikací a AKS
Pátý modul obsahuje zajímavé přístupy k CI/CD s využitím Helm. První varianta jede ve stylu GitOps, takže není postavena na žádném tradičním orchestračním nástroji, ale s využitím projektu Flux, který elegantně propojuje Git s nasazením do Kubernetes. Ve druhé variantě uvidíte tradičnější pohled s CI/CD nástrojem Jenkins a také s využitím cloudové CI/CD služby Azure DevOps.

Java, Azure a Kubernetes? Výborná kombinace. Vyzkoušejte si sami.