---
layout: post
title: 'Azure SQL Edge - krutopřísná databáze na malině'
tags:
- SQL
---
Azure IoT Edge je řešení, kdy si z chytrého zařízení typu Raspberry vytvoříte cloudem spravovanou IoT bránou s lokální logikou včetně Azure ML modelů a kognitivních služeb, API managementu, lokálního azure blob storage, zpracování proudových dat s Azure Stream Analytics a tak podobně. Vaše koncové IoT systémy jako je Azure Sphere tak můžete napojit jak napřímo do Azure IoT Hub, tak do lokální Azure IoT Edge brány pro místní předzpracování a logiku. 

Novinkou v této oblasti je Azure SQL Edge - Microsoft SQL pro potřeby zařízení v térénu, na zdi, pod stolem, za motorem traktoru, ve výrobní hale, zkrátka "na kraji", tam, kde vaše zařízení žijou. Přináší tam věci jako je robustní plně podporovaná enterprise databáze a to včetně Always Encrypted (maximální bezpečnost s šifrováním na klientovi) nebo redundanci s Always On. SQL obsahuje funkce pro práci s time-series daty, ML operace typu anomaly detection a má zahrnutu funkci Stream Analytics (syntakticky identická forma, jak ji znáte z Azure Stream Analytics). Jinak řečeno je to prostě pořádný SQL pro krajní prvky.

Zaujalo mě to hlavně proto, že tento Linux kontejner se SQL (což už je ohraná písnička, varianta běžného SQL v kontejneru už s námi nějakou dobu je) nově ve verzi Azure SQL Edge podporuje (v preview) i ARM64, tedy moje Raspberry! To jsem musel vyzkoušet.

Primární model nasazení je s Azure IoT Edge, které se vám postará o deployment a případně i upgrady a nasazení dalších modulů s logikou, ML modely a další záležitosti a to celé je spravováno z Azure IoT Hub. Já pro začátek zvolil jednoduché spuštění kontejneru se SQL Edge přímo a jsem zvědav, jestli se rozsvítí nebo ne. Řešení nepotřebuje Azure pro svůj běh, zařízení tedy může být offline (je možné, že bude potřeba nějaké občasné připojení pro billing, ale to zatím není jasné).

Pokud vás napadá jak se to bude licencovat a kolik ta věcička stojí, tak aktuálně je to v preview a cena nebyla zatím stanovena (takže si můžete hrát zadarmiko). 

Vzal jsem postarší Raspberry 3 B+, což už není žádný rychlík jak do CPU tak do velikosti paměti, která je jen 1GB (Raspberry 4 by tomuto řešení slušela určitě podstatně víc). SQL Edge vyžaduje 64-bitovou verzi, což Raspberry OS (Raspbian) není, takže jsem šel do jiného OS. Ubuntu 18.04 tam bylo jen ve verzi Core, ale já bych raději větší OS, takže jsem tam dal nové Ubuntu 20.04 v 64-bitové verzi pro malinu. Následně jsem nainstaloval Docker a jdu nahodit Azure SQL Edge kontejner.

```bash
docker pull mcr.microsoft.com/azure-sql-edge-developer
mkdir /home/tomas/sqldata

docker run -p 1433:1433 \
    --name azure-sql-edge \
    -d \
    --cap-add SYS_PTRACE \
    -v /home/tomas/sqldata:/var/opt/mssql \
    -e ACCEPT_EULA=Y \
    -e SA_PASSWORD=Azure12345678@ \
    -e MSSQL_LCID=1033 \
    -e MSSQL_COLLATION=SQL_Latin1_General_CP1_CI_AS \
    -e MSSQL_AGENT_ENABLED=TRUE \
    -e MSSQL_PID=Developer \
    -e ClientTransportType=AMQP_TCP_Only \
    --restart always \
    mcr.microsoft.com/azure-sql-edge-developer
```

Cca 4 minuty chroupání a podle logů to vypadá, že SQL je nahoře. Žhavím Azure Data Studio na počítači a jdu se přihlásit.

![](/images/2020/2020-06-01-07-35-45.png){:class="img-fluid"}

Není to žádný rychlík, ale běží mi tady nejnovější SQL na starším Raspberry předchozí generace jako Docker kontejner v plnohodnotném Linuxu. 

Tak teď už jen musím najít sponzora, protože taková trojice Raspberry 4 v Kubernetes clusteru, uvnitř SQL v Always On redundanci, Azure API Management gateway, aplikační logika a sada ML modelů, to je teprv krutopřísná kombinace.