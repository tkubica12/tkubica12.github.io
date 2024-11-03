---
layout: post
title: 'Jak funguje Managed Identity v Azure'
tags:
- Security
---
Na tomto blogu už jsem popisoval, jak je managed identity výborný způsob přihlašování aplikace k službám jako je Blob Storage, Azure SQL, Azure Database for PostgreSQL a jiným službám nebo třeba Azure Key Vault (pro vyzvednutí certifikátů) nebo do Azure samotného (například k automatizaci pro vaše skripty, Azure CLI, Terraform, CI/CD pipeline). Také jsem popisoval, že to funguje ve vícero platformách a to včetně Azure Kubernetes Service s AAD Pod Identity. Dnes chci popsat trochu detailněji jak to celé vlastně funguje.

# Architektura
Přestože to nepotřebujete přesně znát (je to přecijen managed služba), není na škodu alespoň naznačit, jak to vlastně pod kapotou funguje. Rozhodenete se vytvořit managed identitu a pro účely dnešního povídání je jedno, jestli je to system nebo user managed:
- System managed identita má spojený životní cyklus se zdrojem samotným. Vytvořím VM, vnikne jeho identita. Smažu tuto VM, identita zanikne. Nemusím tedy na nic z toho myslet, ale také to znamená, že nemůžu jednu identitu dát dvěma systémům nebo naopak v jednom systému používat víc identit.
- User managed identita se vytvoří a je vidět v portáu jako samostatný zdroj se samostatným životním cyklem. Dá se tak přiřadit většímu množství VM/kontejnerů/WebAppek (třeba worker nody, které dělají všechny to samé a mají tudíš stejnou identitu a vytváří se dynamicky nové) nebo naopak do jednoho VM/kontejneru/WebAppky promítnout víc identit (least privilege - jednu s právem na přísutp do Storage, jinou s právem vyzvedávat certifikát z Key Vaultu a třetí s právem přístupu do SQL).

Jak tedy managed identita funguje? Je zřejmé, že jde o účet v rámci Azure Active Directory, konkrétně zvláštní varianta Service Principal účtu. Zvláštní je v tom, že ji nemůžete spravovat běžným způsobem v AAD. Nemůžeme si pro ni vytvořit heslo, smazat ji v AAD nebo přidělit práva do non-Azure světa (SaaS aplikace, Office365 apod.). Je vytvořena přes Azure, žije v rámci Azure a práva může mít jen v rámci Azure. Je to tedy v porovnání s běžným Service Principal identita značně omezená a to je hodně dobře, přispívá to k větší bezpečnosti.

Jakmile tedy identitu v Azure založíte (nebo pustíte zdroj se systémovou identitou), Azure ji vytvoří v AAD a vygeneruje si pro ní certifikát s platností 90 dní a rotací 45 dní. Ten si bezpečně uloží mimo dosah vašich rukou a pouze tato Azure služba má registraci pro ověření této identity. Azure každých 45 dní provede rotaci certifikátu. To všechno se děje pro vás na pozadí - vy to řešit nijak nemusíte a vše podléhá všem možným auditním a certifikačním standardům (SOC, ISO, FedRAMP, ...).

Jak ale moje aplikace může s identitou pracovat, když je určena jen pro Azure? Aby to mohlo proběhnout, musí aplikace běžet v Azure a obrátit se na metadata endpoint. Funguje to ve VM, ve WebApp, v AKS a dalších compute službách (dokonce i Azure Streaming Analytics podporuje managed identitu na sosání dat z SQL nebo ověření do PowerBI). Tento endpoint je neroutovatelný a nikdy s ním nekomunikujete po síti. Běží přímo na fyzickém hostiteli. Není tedy součástí vašeho VM ani není někde v síti. Podle toho jaké identity máte k VM namapované, drží si hostitel metadata vaší instance (potřebuje toho vědět samozřejmě víc, identity jsou jedním z mnoha atributů), izolovaně pro každé VM na stroji. Ze svého VM se tedy můžete obrátit na svůj metadata endpoint.

Co se děje dál? Tomuto endpointu řeknete, že chcete vystavit token pro komunikaci s nějakou službou. Není to tedy tak, že se k vašemu kódu dostane samotný certifikát identity (ten co se rotuje po 45 dnech) - metadata služba se pro vás přihlásí a vrátí vám jen časově omezený token (výchozí platnost je myslím 8 hodin, na rozdíl od běžné 1 hodiny). Pokud máte identit namapovaných víc, musíte si ještě říct jakou identitu chcete použít. Součástí requestu je i scope, tedy pro jakou službu chcete autorizaci udělat - pro Azure management (když potřebujete třeba přihlásit Terraform nebo Azure CLI), pro Key Vault (když si chcete stáhnout webový certifikát), pro blob storage, pro SQL a tak podobně. Služba běžící na hostiteli také certifikát identity nemá, ale ověří, že je váš požadavek v pořádku (že je na identitu, kterou máte namapovanou) a kontaktuje backendovou Azure službu (vůči ní se ověřuje zase certifikátem, který má každý hostitel vlastní a často rotovaný). Tato backend služba pak komunikuje s AAD, získá pro vás token a opět přes hostitele vám ho doručí do vašeho VM.

Výsledek?
- Nepotřebujete vaší aplikaci předávát žádné, opakuji žádné tajnosti typu hesla nebo klíče.
- Pokud cílová služba podporuje AAD ověřování, můžete se do ní rovnou připojit - Azure samotný, Key Vault, SQL, PostgreSQL, storage, ...
- Pokud služba něco takového neumí (je mimo Azure nebo nepodporuje AAD, např. dnes Cosmos DB) nebo potřebujete tajnost pro něco jiného (certifikát na web), můžete si to předat přes Key Vault. Do něj uložíte tajnosti a klíčky od trezoru nepotřebujete, vůči trezoru se ověřujete přes managed identitu - takže stále platí, že aplikace při startu nepotřebuje znát jakoukoli tajnost.

# Vyzkoušejme si na příkladu storage
Založíme resource group a spravovanou identitu.

```bash
az group create -n managed-identity-rg -l westeurope
az identity create -g managed-identity-rg -n identity1
```

![](/images/2020/2020-05-09-20-18-29.png){:class="img-fluid"}

Vytvoříme storage account, kontejner, soubor a ten uploadujeme jako blob.

```bash
az storage account create -n mujsuperstorageaccount -g managed-identity-rg
export AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string -n mujsuperstorageaccount -g managed-identity-rg -o tsv)
echo Tohle jsou moje data > object.txt
az storage container create -n cont
az storage blob upload -c cont -f object.txt -n object.txt
rm object.txt
```

Výborně. Naše identita nicméně v tuto chvíli nemá autorizaci vůbec na nic. Pro přístup do Blob storage přes AAD existují speciální role "Storage Blob Data", tedy přístup na "data plane". Tímto právem nedáváme identitě možnost pracovat na úrovni Azure (měnit nastavení accountu apod.), jen přistupovat k datům na konkrétním scope (celý account nebo kontejner).

```bash
az role assignment create --role "Storage Blob Data Reader" \
    --assignee-object-id $(az identity show -g managed-identity-rg -n identity1 --query principalId -o tsv) \
    --scope $(az storage account show -n mujsuperstorageaccount -g managed-identity-rg --query id -o tsv)
```

Teď vytvoříme VM a namapujeme tuto identitu.

```bash
az vm create -n mivm \
    -g managed-identity-rg \
    --image UbuntuLTS \
    --admin-username tomas \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --assign-identity $(az identity show -g managed-identity-rg -n identity1 --query id -o tsv)
```

![](/images/2020/2020-05-09-20-22-04.png){:class="img-fluid"}

Vyzkoušíme. Nejdřív si zjistíme clientId této identity, protože si řekneme specificky o ni (pokud bychom měli namapovanou jenom jednu identitu, znát ho nepotřebujeme - nejjednodušší je tedy mít jen jednu identitu na VM, WebApp nebo kontejner v AKS)

```bash
az identity show -g managed-identity-rg -n identity1 --query clientId -o tsv
b7b71530-ab56-440c-bf64-91644215b2a3
```

Připojím se do VM a zevnitř nejdřív nainstaluji jq (ať můžeme parsovat JSON) a obrátím se na metadata službu (169.254.169.254) s žádostí o token. Resource bude URI mého storage accountu (může být včetně kontejneru, pokud mám právo jen na určitý kontejner) a jako parametr uvedu client_id (pro případ, že bych měl ve VM namapovaných identit víc - jinak to nepotřebuju).

```bash
ssh tomas@$(az network public-ip show -n mivmPublicIP -g managed-identity-rg --query ipAddress -o tsv)
sudo apt update && sudo apt install jq -y
export clientid=b7b71530-ab56-440c-bf64-91644215b2a3
export token=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/identity/oauth2/token?resource=https://mujsuperstorageaccount.blob.core.windows.net&api-version=2018-02-01&client_id=$clientid" | jq -r '.access_token')
```

V tuhle chvíli máme časově omezený token vydaný pro naši identitu a pro scope mého blob storage. Je na čase použít storage API a vyzvednout si objekt. Povinně musím zadat autorizační hlavičku (s naším AAD tokenem), specifikovat v hlavičce verzi API a musím zadat aktulní čas ve správném formátu a to celé poslat jako GET na URL mého objektu.

```bash
curl -H "Authorization: Bearer ${token}" \
    -H "x-ms-version: 2019-07-07" \
    -H "x-ms-date: $(date -u +%a,\ %d\ %b\ %Y\ %H:%M:%S\ GMT)" \
    https://mujsuperstorageaccount.blob.core.windows.net/cont/object.txt
Tohle jsou moje data
```

Perfektní, funguje! Šlo mi dnes o to, podívat se celému procesu pod kapotu. Ve finále jak funguje backend nepotřebujete znát a jak funguje samotné získání tokenu a jeho použití v přístupu ke službě ve také ne, protože tohle je typicky součástí nějakého SDK pro váš programovací jazyk nebo je to zahrnuto přímo v hotovém software, který to využije (Azure CLI, Terraform, Ansible).

Používejte managed identity. Je to bezpečné, nepotřebujete se babrat s hesly a nepotřebujete čekat na centrální IT, než vám vystaví Service Principal.