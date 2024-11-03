---
layout: post
title: 'Novinky v data protection u Blob Storage: soft delete, verzování, change feed, objektová replikace a point in time restore'
tags:
- Storage
---
Azure Blob Storage zrovna přichází se salvou nových funkcí v ochraně dat. K existujícímu Soft Delete v preview prezentuje možnosti verzování, change feed, objektovou replikaci a point in time restore. Zatím na vyzkoušení ve Francii a Kanadě. Pojďme prozkoumat co to dělá a k čemu to může být dobré.

Protože jde o preview, musíme nejdřív k funkcím získat přístup. Těmito příkazy zažádáme o registraci (některé proběhnout během pár minut automaticky, objektová replikace byla asi ručně schvalována, protože trvala zhruba jeden den).

```bash
az feature register --namespace Microsoft.Storage --name Versioning
az feature register --namespace Microsoft.Storage --name Changefeed
az feature register --namespace Microsoft.Storage --name AllowObjectReplication
az feature register --namespace Microsoft.Storage --name RestoreBlobRanges
```

Podívejte se, jestli funkce ukazují Registered a přeregistrujte Storage provider, ať se vše zaktualizuje a v portálu se objeví nová tlačítka.

```bash
az feature show --namespace Microsoft.Storage --name Versioning --query properties.state
az feature show --namespace Microsoft.Storage --name Changefeed --query properties.state
az feature show --namespace Microsoft.Storage --name AllowObjectReplication --query properties.state
az feature show --namespace Microsoft.Storage --name RestoreBlobRanges --query properties.state

az provider register -n Microsoft.Storage
```

Při vytváření accountu můžeme rovnou potřebné funkce zaškrtnout.

![](/images/2020/2020-06-03-06-54-12.png){:class="img-fluid"}

Máme připraveno, pojďme testovat jednotlivé vlastnosti.

# Soft delete
Začněme s funkcí soft delete, která na rozdíl od těch ostatních už je v plné dostupnosti, ne jen v preview. Je to jednoduše odpadkový koš, kdy vymazání dat je ve skutečnosti neodstraní, ale schová a do propadliště dějin se dostanou až po zadaném čase. Důsledkem je, že za data ve stavu soft delete nadále platíte. Určitě je důležité poznamenat, že tato ochrana je myšlena pro smazání objektu, které si potom rozmyslíte. Samotný soft delete nechrání před přepsáním objektu jiným obsahem (to řeší verzování) a také vás nechrání před smazáním celého kontejneru nebo accountu. Pokud se chcete chránit před smazáním dat omylem, máte dvě jiné možnosti. Můžete použít zámečky, kterými můžete efektivně přepnout do čtecího režimu. Tyto můžete odstranit a vrátit zpět, takže promazání lze udělat, ale nejdříve sejmete zámek, vymažete, zámek vrátíte. To byste už asi neměli udělat "ukliknutím". Druhou variantou je immutable storage, kdy jste schopni nastavit naprostou nesmazatelnost objektů třeba po dobu 1 roku, kterou musíte držet ze zákona. Takové omezení je neodstranitelné aby splňovalo příslušné normy.

Vyzkoušejme si to. V portálu jsem vytvořil kontejner.

![](/images/2020/2020-06-02-20-27-59.png){:class="img-fluid"}

Nahraji tam dva soubory.

![](/images/2020/2020-06-02-20-29-38.png){:class="img-fluid"}

Jeden ze souborů smažu.

![](/images/2020/2020-06-02-20-30-11.png){:class="img-fluid"}

Přepnu si pohled i na smazané objekty.

![](/images/2020/2020-06-02-20-30-54.png){:class="img-fluid"}

Pokud jsem si to rozmyslel, mohu objekt obnovit. Pokud bych neměl aktivované verzování, tak to udělám tlačítkem undelete.

![](/images/2020/2020-06-02-20-31-30.png){:class="img-fluid"}

V případě zapnutého verzování, je smazaný objekt vlastně svou předchozí verzí, takže ho obnovím tak, že předchozí verzi učiním aktuální.

![](/images/2020/2020-06-02-20-35-23.png){:class="img-fluid"}

![](/images/2020/2020-06-02-20-35-44.png){:class="img-fluid"}

# Versioning (preview ve France Central)
Pojďme na druhou funkci - verzování objektů. Pokud stávající objekt přepíšeme novým obsahem, umožní verzování vracet se k předchozím obsahům. Z finančního hlediska je to taky docela zajímavé, protože pokud se jedná o větší soubor, který je složený z několika bloků, tak pokud nová verze má nějaké bloky stejné, není třeba je ve storage vytvářet znovu. Verzování je tedy deduplikované na úrovni bloků (ty mají velikost mezi 64KB a 100MB a dají se v rámci API nebo v portálu při uploadu určit - malé bloky zvyšují poplatky za transakce, ale zvyšují šanci deduplikace, pokud hodně využíváte verzování). Abych předešel nedorozumění - tohle platí jen pro konkrétní objekt. Pokud vytvoříte identický objekt, jen s jiným názvem, uloží se celý tak jak je a platíte ho dvakrát.

Pojďme na to. Mám tady soubor file.txt, jehož obsahem je řetězec v1. Přímo v editoru v portálu ho přepíšu na v2 (nebo u sebe na notebooku a soubor uploadnu přes ten původní). Zopakuji ještě s řetězcem v3.

![](/images/2020/2020-06-02-20-41-27.png){:class="img-fluid"}

![](/images/2020/2020-06-02-20-41-55.png){:class="img-fluid"}

Podívejme se na předchozí verze.

![](/images/2020/2020-06-02-20-43-31.png){:class="img-fluid"}

![](/images/2020/2020-06-02-20-43-55.png){:class="img-fluid"}

Můžu si jednu vybrat a udělat z ní aktuální verzi (tedy vrátit změny) nebo si starší verzi stáhnout.

# Change feed (preview ve France Central)
Existují tři způsoby, jak se dozvědět o operacích v rámci storage. Nejstarší storage analytics jsou best effort řešení a rozhodně nejde o transakční log, takže se klidně může stát, že nějaká operace chybí. Pro statistickou analýzu a monitoring to určitě stačí, ale ne, pokud nad tím děláte nějakou aplikační integraci s potřebnou garancí kompletnosti. Aplikace lze integrovat přes storage events, které vysílají událost přes Event Grid. Tady platí, že jsou zalogovány konzistentně všechny operace a událost vznikne téměř okamžitě. Nicméně není tady garantováno pořadí operací a to ani na úrovni jednoho blobu (klidně se nejdřív dozvíte, že byl smazán a pak až, že byl vytvořen, pokud se obě události stanou chvilku za sebou). Pokud vám jde o to reagovat na nový soubor s obrázkem a automaticky vytvořit jeho náhledy probuzením Azure Function, budou storage events určitě výborný způsob.

Change feed funguje se zpožděním a jde o transakční log, ve kterém najdete CRUD změny všech objektů včetně jejich metadat (v rámci preview není logována změna tieru). Je to log v pravém smyslu, tedy soubory, které se zpožděním několika minut objeví ve speciálním kontejneru ve storage. To má pár zajímavých výhod:
- Log garantuje pořadí operací na konkrétním objektu skutečně tak, jak se prováděly (ale samozřejmě ne mezi různými objekty, blob storage je masivně paralelizovaný systém, ne transakční databáze)
- Log je perzistentně uložen ve storage a nemusíte se o to starat
- Přes soubory ve storage můžete integrovat nekonečné množství příjemců a aplikací a to nejen ty, co jsou event-driven, ale i ty, které chcete probouzet třeba v noci a projíždět log dávkově

Logy se objeví v read-only kontejneru $blobchangefeed a v adresářové struktuře. Jde o JSON záznamy v Avro formátu. Vypadá to nějak takhle:

```json
[
  {
    "schemaVersion": 4,
    "topic": "/subscriptions/mojesubscriptionid/resourceGroups/storage/providers/Microsoft.Storage/storageAccounts/mujstorageaccount123",
    "subject": "/blobServices/default/containers/kontejner/blobs/ZoomIt.zip",
    "eventType": "BlobCreated",
    "eventTime": "2020-06-02T19:00:00.1917646Z",
    "id": "a4f32166-901e-0006-5d10-3918e2063924",
    "data": {
      "api": "PutBlob",
      "clientRequestId": "mojeclientid",
      "requestId": "a4f32166-901e-0006-5d10-3918e2000000",
      "etag": "0x8D80727266093B7",
      "contentType": "application/x-zip-compressed",
      "contentLength": 458823,
      "blobType": "BlockBlob",
      "blobVersion": "2020-06-02T19:00:00.1907639Z",
      "containerVersion": "01D6390A0CAB13FF",
      "blobTier": null,
      "url": "",
      "sequencer": "0000000000000000000000000000241300000000003bcfa9",
      "previousInfo": null,
      "snapshot": null,
      "blobPropertiesUpdated": null,
      "asyncOperationInfo": null,
      "storageDiagnostics": {
        "bid": "a5208099-4006-002a-0010-39f44d000000",
        "sid": "38ed280c-4f84-b55d-ec4b-917fcb10f9d7",
        "seq": "(9235,901614,3919785,3918768)"
      }
    }
  }
]
```

# Object replication (Preview ve France Central a Canada Central)
Další zajímavou funkci v preview je replikace objektů mezi dvěma accounty. K čemu je to dobré? Tradičně máte samozřejmě už mnoho let k dispozici storage account v režimu globální replikace (GRS) včetně varianty RAGRS, kdy z druhého accountu můžete číst (a v případě havárie výchozího regionu pro vás Microsoft endpointy přepne, takže se zapisovacím stane záložní region). Možná jste nezaznamenali, že padlo předchozí omezení, kdy toto přepnutí zapisovacího regionu nemůžete udělat sami, musí to být Microsoft. Ten se k tomu totiž obvykle moc mít nebude, protože replikace je asynchronní, tedy má nenulové (byť dost nízké) RPO a přepnutí může znamenat ztrátu dat. Microsoft bude raději pár hodin opravovat a rekonstruovat data, než aby vám nějaká ztratil. Nicméně vy se na to můžete dívat úplně jinak a preferujete RTO (přepnout okamžitě) a poslední soubor klidně oželíte. Relativně nedávno přišla možnost si tohle řídit.

![](/images/2020/2020-06-03-06-58-00.png){:class="img-fluid"}

Nicméně stále platí, že GRS je pro párové regiony (nemůžete vybrat odkud kam), takže to není řešení pro distribuci dat mezi kontinenty nebo nějakou chytřejší logiku (jeden kontejner z Evropy do Ameriky, druhý z Evropy do Asie). Také platí, že se replikuje celý storage account, ale ve vašem řešení vás mohou zajímat jen určité kontejnery. Tady je pár příkladů, kdy replikace dává smysl:
- Máte lokální accounty (per světadíl nebo region), kde data vznikají a aplikace je využívají. Nad celou planetou pak potřebujete provést datovou analýzu a tak si vybraná data replikujete do centrálního accountu v jednom regionu, ve kterém je váš analytický compute.
- Data vám vnikají v jednom místě, ale pro narychlení aplikací v regionech je chcete replikovat do accountů po světě.
- Jedna organizace je odpovědná za archivaci dat a někdo jiný data zpracovává. Z organizačních důvodů můžete chtít data ukládat na jednom accountu, odkud se zreplikují a hned jak se tak stane, tak se přesunou do archivního tieru. Tým zpracovávající data má jejich kopii a je na jeho uvážení (a jeho peněžence) jak dlouho si je nechá a co s nimi bude dělat, aniž by zatěžoval rozpočet týmu odpovědného za archivaci.
- Potřebujete replikaci z důvodu regionální redundance, ale chcete komplikovanější pravidlo na základě jménné konvence souborů (např. replikuj jen soubory začínající na PROD_)

Na obou accountech musí být zapnuté verzování a na zdrojovém ještě change feed. Ke svému prvnímu accountu v Paříži tedy vytvořím ještě druhý v Canada Central.

Pokud vaše registrace preview funkcí proběhla, najdete v portálu novou sekci a můžeme vytvořit replikační nastavení.

![](/images/2020/2020-06-03-20-23-36.png){:class="img-fluid"}

Budu replikovat z kontejneru prvního accountu do kontejneru druhého v Kanadě.

![](/images/2020/2020-06-03-20-25-25.png){:class="img-fluid"}

Přidám filter a budu chtít kopírovat jen objekty, které mají v názvu "file".

![](/images/2020/2020-06-03-20-26-06.png){:class="img-fluid"}

Co s existujícími objekty před vznikem replikační politiky? Poslat tam všechno? Nebo jen nové objekty? Nebo objekty vytvořené tento týden?

![](/images/2020/2020-06-03-20-27-04.png){:class="img-fluid"}

Uložil jsem politiku a hnedle v druhém storage accountu nacházím repliku objektů.

![](/images/2020/2020-06-03-20-27-52.png){:class="img-fluid"}


# Point in time restore
Další novinkou v preview je možnost vrátit blob storage do stavu k nějakému času. Zatím je tu jedno zásadní omezení a to, že pokud smažete celý kontejner, vrátit to zatím nejde (ale do obecné dostupnosti to prý už půjde). Jak to funguje? Jde vlastně o nadstavbu nad funkcemi soft delete a change feed. Vrátit v čase se můžete pouze v rámci periody soft delete (resp. o jeden den méně), takže pokud dám soft delete na 31 dní, můžu udělat restore maximálně do 30 denní historie. Co tahle funkce udělá je, že vezme čas, který jí zadáte a přehraje transakční log do tohoto okamžiku.

Nejdříve zaktivuji point in time restore (v GUI to zatím není).

```bash
az storage account blob-service-properties update --account-name mujstorageaccount123 \
    -g storage \
    --enable-restore-policy \
    --restore-days 5
```

Z předchozích pokusů tady mám soubor file.txt s obsahem "v3".

![](/images/2020/2020-06-03-07-22-24.png){:class="img-fluid"}

Změním na něco jiného a uložím.

![](/images/2020/2020-06-03-07-23-04.png){:class="img-fluid"}

Vrátím se teď o 10 minut zpátky (samozřejmě nemůžu jít dál, než za okamžik, co jsem funkci aktivoval, takže bude potřeba chvilku čekat). Můžu specifikovat konkrétní kontejner nebo range blobů, já chci vrátit prostě všechno, takže range uvádět nebudu.

```bash
time=`date -u -d "-10 minutes" '+%Y-%m-%dT%H:%MZ'`
az storage blob restore --account-name mujstorageaccount123  -g storage -t $time
```

Funguje! Změněné soubory mají zpět původní obsah, smazané objekty jsou obnovené.

Blob storage je nejlevnější způsob uložení dat v Azure, ale jeho možnosti se neustále rozšiřují. Není to souborový systém (na rozdíl od Azure Files), takže se s ním musíte naučit pracovat trochu jinak, ale nedostatkem funkcí netrpí. Zkuste si to a ušetřete.