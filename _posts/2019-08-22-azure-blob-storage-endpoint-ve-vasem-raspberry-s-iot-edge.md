---
layout: post
published: true
title: Azure Blob Storage endpoint ve vašem Raspberry s IoT Edge
tags:
- IoT
- Storage
---
Zvykli jste si ve vašich aplikacích využívat Azure Blob Storage API, ale teď potřebujete data prvotně ukládat někde blíž, předzpracovávat lokálně nebo máte časté výpadky konektivity protože používáte IoT síť kde se vysílá v dávkách? Azure Stack nebo Azure Data Box Edge je moc velký pro vaše účely? Prozkoumejme BLob Storage endpoint pro Azure IoT Edge a využít můžeme třeba vaše Raspberry.

# Metody, jak dostat Blob Storage endpoint blíž k sobě
První ultimátní variantou je určitě Azure Stack. S ním k sobě přitáhnete nejen storage API (a to včetně podpory HTTPS, storage queues i storage table), ale celou IaaS konzistentní s Azure API, některé PaaS služby jako jsou WebApps, Azure Functions, připravovaný IoT Hub a další služby. Nicméně Azure Stack je velká sada beden vyžadující skutečnou serverovnu a má velkou kapacitu, kterou možná pro váš scénář nepotřebujete.

Další možností je tedy Azure Data Box Edge. Místo šelmostroje s Azure komponentami dostanete 1U systém specificky zaměřený na ingesting a zpracování dat. Rozvítí se na něm storage API, můžete v něm data zpracovávat s využitím hardwarově akcelerovaných IoT Edge modulů (AI, streaming analytics apod.) a nastavit synchronizaci do storage accountu v Azure. Pokud vám konektivita vypadne, nic se neděje - data se uloží lokálně a sesynchronizují při nejbližší příležitosti. Nepotřebujete skutečnou serverovnu ani velké kapitálové investice, protože box se pronajímá. Nicméně i to může být pro vaše účely moc velké řešení.

Třetí možností je nový IoT Edge modul pro storage API, který dostanete do IoT Edge zařízení s Windows či Linux x86 nebo Linux s ARM jako je Raspberry. Právě na to se dnes podíváme.

# Vyzkoušejme si IoT Edge s blob storage
Pro účely článku jsem zvolil IoT Edge zařízení v podobě Linux stroje s x86, ale funguje to i pro ARM jako je Raspberry.

Vytvořil jsem IoT Hub v Azure, nainstaloval v Linuxu IoT Edge platformu a všechno propojil dle [návodu](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-linux).

![](/images/2019/2019-08-09-07-44-52.png){:class="img-fluid"}

Zařízení je připraveno a IoT Hub vidí. Nasadíme IoT Edge modul obsahující blob storage endpoint.

![](/images/2019/2019-08-09-07-45-46.png){:class="img-fluid"}

![](/images/2019/2019-08-09-07-46-15.png){:class="img-fluid"}

Odkážu na obraz modulu dle dokumentace.

![](/images/2019/2019-08-09-07-47-49.png){:class="img-fluid"}

Nasazení předáme konfigurační hodnoty. Jednak půjde o název storage accountu na zařízení, jeho klíč a také port, na kterém chceme endpoint běžet. Klíč musí být 64-bytový base64 string, který si pro zjednodušení vygeneruji [tady](https://generate.plus/en/base64?gp_base64_base%5Blength%5D=64). Jako mount point můžu použít Volume nebo jen interní cestu.

```json
{
  "Env":[
    "LOCAL_STORAGE_ACCOUNT_NAME=mujedgeblob",
    "LOCAL_STORAGE_ACCOUNT_KEY=kxjbY0vnFB8Kn//SZq0byIXHSx8zsWCwxHzXAT013W+pUjZDLYZQy/5ygvu/DL5gjXrf7Eu+AccXgf9e1tG+sg=="
  ],
  "HostConfig":{
    "Binds":[
        "/tmp:/blobroot"
    ],
    "PortBindings":{
      "11002/tcp":[{"HostPort":"11002"}]
    }
  }
}
```

Doklikám až na konec a provedu nasazení.

![](/images/2019/2019-08-09-08-01-55.png){:class="img-fluid"}

Pokud potřebuji jen endpoint a data budu zpracovávat lokálně, tak nám to takhle stačí. Já ale ještě využiji vlastnost modulu, kdy bude sám data tak jak jsou nahrávat do storage v Azure. Tyto konfigurační možnosti se mu předávají jako Device Twin konfigurace (dejte si tam správnou connection na storage account v Azure). Buď tam budu soubory nechávat, nebo je po nahrání smažu či je nechám smazat po hodině a tak podobně.

```json
{
  "properties.desired": {
    "deviceAutoDeleteProperties": {
      "deleteOn": true,
      "deleteAfterMinutes": 60,
      "retainWhileUploading": true
    },
    "deviceToCloudUploadProperties": {
      "uploadOn": true,
      "uploadOrder": "OldestFirst",
      "cloudStorageConnectionString": "DefaultEndpointsProtocol=https;AccountName=<your Azure Storage Account Name>;AccountKey=<your Azure Storage Account Key>; EndpointSuffix=<your end point suffix>",
      "storageContainersForUpload": {
        "<source container name1>": {
          "target": "<target container name1>"
        }
      },
      "deleteAfterUpload": false
    }
  }
}
```

Parametry zakomponuji do Module Twin konfigurace.

![](/images/2019/2019-08-09-09-25-48.png){:class="img-fluid"}

![](/images/2019/2019-08-09-09-26-37.png){:class="img-fluid"}

![](/images/2019/2019-08-09-09-27-44.png){:class="img-fluid"}

Moje IoT Edge zařízení má public IP, tak se ze svého PC připojím na storage endpoint přes Storage Explorer. Tady jedna důležitá poznámka - storage endpoint v tuto chvíli nepodporuje HTTPS. Je zaměřen spíše na použití lokálně v rámci aplikací v IoT Edge nebo u zařízení připojených přes nějakou privátní síť. 

Otevřu storage explorer a připojím se. Protože běžíme na nestandardním portu musíme využít connection string, který v mém případě vypadá takhle:

```
DefaultEndpointsProtocol=http;AccountName=mujedgeblob;AccountKey=kxjbY0vnFB8Kn//SZq0byIXHSx8zsWCwxHzXAT013W+pUjZDLYZQy/5ygvu/DL5gjXrf7Eu+AccXgf9e1tG+sg==;BlobEndpoint=http://40.68.216.139:11002/mujedgeblob;
```

![](/images/2019/2019-08-09-09-05-00.png){:class="img-fluid"}

![](/images/2019/2019-08-09-09-05-26.png){:class="img-fluid"}

![](/images/2019/2019-08-09-09-05-52.png){:class="img-fluid"}

Vytvořím kontejner sourcecontainer a nahraji tam nějaký soubor.

![](/images/2019/2019-08-09-09-07-09.png){:class="img-fluid"}

Podívám se do druhého accountu v cloudu a skutečně tam IoT Edge provedlo upload.

![](/images/2019/2019-08-09-09-29-05.png){:class="img-fluid"}

Pojďme si vyzkoušet ještě jednu situaci. Jak by to vypadalo, pokud by IoT Edge zařízení na nějaký okamžik ztratilo přísup do Internetu? Nasimuluji to tak, že vytvořím NSG, které outbound zablokuje. Následně nahraji další soubor do IoT Edge endpointu.

![](/images/2019/2019-08-09-09-43-55.png){:class="img-fluid"}

Ať čekám jak čekám, soubor se samozřejmě v Azure neobjevuje - IoT Edge ztratil konektivitu.

![](/images/2019/2019-08-09-09-44-44.png){:class="img-fluid"}

NSG dám pryč a obnovím konektivitu.

![](/images/2019/2019-08-09-09-47-02.png){:class="img-fluid"}



Potřebujete dostat Azure Blob Storage endpoint blíž? V první řadě využijte plné nabídky všech Azure regionů po celé planetě a na všech světadílech kromě Antarktidy. Jen v Evropě najdete Dublin, Amsterdam, Paříz, Mareseille, Londýn, Cardiff a chystá se dalších šest regionů v Německu, Švédsku a Švýcarsku. Potřebujete ještě blíž? Můžete si vzít část Azure technologií a konzistentně je využívat v Azure Stack. Ještě blíž, i tam, kde není místo na celý rack? Zkuste Azure Data Box Gateway. Potřebujete, aby to pracovalo na baterky nebo se vešlo do kabelky? Pak je pro vás cesta přes IoT Edge modul třeba v Raspberry.




