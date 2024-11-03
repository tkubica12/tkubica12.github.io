---
layout: post
title: 'Kubernetes praticky: DAPR napojení na řešení ukládání tajností v Kubernetes, Azure, AWS i Google i Hashicorp'
tags:
- Kubernetes
- Serverless
- DAPR
---
DAPR je výborná platforma pro distribuované aplikace, která vám dá skutečnou přenositelnost mezi prostředími. Nepotřebuje Kubernetes, ale perfektně do něj sedí. Dnes se podíváme jak DAPR umožní sjednotit váš přístup k řešení secrets bez nutnosti uvázat se k proprietárnímu řešení nějakého dodavatele.

# Typické řešení secrets
Nechme stranou všechny ty příklady nevhodného zacházení s tajnostmi (klíče, certifikáty, connection stringy) jako je umístění v kódu, v konfiguračním souboru jako součást kontejneru a tak podobně. Rozumné je secrets vložit do řešení k tomu určenému a bezpečně vyzvedávat. Jak tohle typicky řešit?
- Možná se spokojíte se Secrets v Kubernetes. Cloudové implementace je v rámci Etcd ukládají šifrovaně a jsou i varianty jak Secrets prohnat přes KMS pro větší míru zabezpečení ukládací šifry. Přesto - Secrets jsou perfektní start pro jednoduché projekty, ale mají nevýhody. Nejsou tak dobře bezpečnostně oddělené, neumí hardwarovou implementaci (HSM), ale hlavně - žijí ve vašem clusteru. Co další clustery v jiných regionech? Co clustery pro jiné projekty, kde potřebujete některé tajnosti sdílet? A co klientské části aplikace běžící na mobilu? Svět není jen o Kubernetes, tak co uděláme s aplikacemi ve VM, v nějaké PaaS službě, jak na serverless funkce nebo datové služby typu Spark? To jsou hlavní limity Secrets v Kubernetes.
- Pokud jste v Azure, určitě dává velký smysl přejít na Azure Key Vault. Samozřejmě je to jiné API, než Kubernetes Secrets, tak se musíte poohlédnout například po FlexVolume, který je umí namapovat jako soubor nebo je vyzvedávat aplikací přes API.
- Pokud jste v AWS či Google, určitě zvážíte použít tamní trezory tedy AWS Secret Manager a GCP Secret Manager nebo Cloud KMS.
- Vy opravdu chcete nebo potřebujete on-premises svět? Abyste neměli nevýhody per-cluster Secrets v Kubernetes možná kouknete na Hashicorp Vault, který vám umožní moc pěkný (ale softwarový) trezor rozjet kdekoli.

A jsme znovu u klasického problému, který DAPR tak elegantně řeší. Jak se rozhodnout. Jak napsat aplikaci tak, aby nebyla závislá na těchto detailech? Ať už je to multi-cloudovost, potřeba běžet kousek v on-premises nebo nutnost prodávat software jako takový a přizpůsobit se prostředí zákazníka, DAPR s tím pomůže. Nabídne vám jednotné API, které na backendu může mít libovolnou ze zmíněných variant.

# Vyzkoušíme DAPR secrets
DAPR se jako vždy ocitne přímo u vašeho kódu ve formě sidecar kontejneru a na loopbacku vám bezpečně a jednoduše (nepotřebujete se logovat nebo něco takového, je to sidecar) nabídne sadu aplikačních API včetně toho na Secrets. Stačí si tedy tajnost vyzvednout přes toto API a v mé aplikaci není žádná dependence na konkrétní implementaci secrets store ani dependence na nějakém mechanismu, který zajišťuje Kubernetes (naplnění ENVu apod.).

Nejprve jsem založil v DAPR secrets komponentu.

{% raw %}
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: azurekeyvault
spec:
  type: secretstores.azure.keyvault
  metadata:
    - name: vaultName
      value: {{ .Values.keyVault.name }}
    - name: spnClientId
      value: {{ .Values.keyVault.readerClientId }}
```
{% endraw %}

Všimněte si, že jsem nepoužil Service Principal (heslo pro přihlášení k trezoru), ale AAD Pod Identity s Managed Identity v Azure pro bezpečné přihlašování bez hesla (o tom už jsem minulý týden psal a ještě se k tomu na blogu vrátím - výborný koncept). Každopádně ať přes service principal nebo pod identity se DAPR dostane do trezoru. Pokud mám jinou implementaci (AWS, GCP, Hashicorp), nastavím ji dle návodu pro tuto platformu. A je tu ještě jeden "driver" - Kubernetes Secrets. DAPR se dá tedy napojit na klasické Secrets! Díky tomu můžete ve svém vývojovém prostředí (nebo aktuální verzi produktu) postupně přecházet na DAPR a pak změnit backend implementaci, až budete připraveni nebo mezi testem a produkcí.

To je vlastně celé. Použil jsem to pro získávání tajností pro nasazení mých dalších DAPR komponent jako je heslo do Redisu:

{% raw %}
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  metadata:
  - name: "redisHost"
    value: {{ .Values.redis.host }}
  - name: "redisPassword"
    secretKeyRef:
      name: redis-password
auth:
  secretStore: azurekeyvault
```
{% endraw %}

Teď si ukážeme využití API. V aplikačním Podu s DAPR sidecar se můžu jednoduše obrátit přes http nebo gRPC na loopback a do cesty dát jméno secrets komponenty (v mém případě se jmenuje azurekeyvault a ano - můžete mít napojeno víc trezorů i s různými technologiemi) a jméno klíče v trezoru.

```bash
curl http://localhost:3500/v1.0/secrets/azurekeyvault/psql-jdbc
{"psql-jdbc":"jdbc:postgresql://blabla"}
```

Jednoduché REST volání a mohu ze své aplikace načíst Secret bez nutnosti znát implementaci a to odkudkoli, kde mám DAPR, takže v libovolném Kubernetes prostředí nebo ve své VM jako proces běžící vedle mé aplikace. Mám univerzální aplikaci, výbornou přenositelnost a možnost v průběhu života aplikace s tím šachovat například mezi dev a produkcí, mezi původní verzí a novou verzí atd. Zkuste si DAPR, stojí to za to.