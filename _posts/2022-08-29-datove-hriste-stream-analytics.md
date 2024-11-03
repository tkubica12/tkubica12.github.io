---
layout: post
published: true
title: Datové hřiště - zpracování proudu událostí s Azure Stream Analytics nakopnuté Terraformem
tags:
- Data Analytics
- Automatizace
- Stream Analytics
---
Minule jsem k projektíku datového hřiště [https://github.com/tkubica12/dataplayground](https://github.com/tkubica12/dataplayground) popsal generování dat a dnes se mrkneme na zpracování té proudové části s využitím Azure Stream Analytics. To samé se pak někdy příště pokusím udělat v Databricks s využitím Structured Streaming. Čeká nás pak určitě i ETL s Data Factory, zpracování s Databricks, možná trocha Synapse, PowerBI, AzureML a uvidím čeho ještě. Proč to vlastně všechno dělám a jaké předpoklady to má splňovat? To se dočtete v [předchozím článku](https://www.tomaskubica.cz/post/2022/datove-hriste-jak-si-hrat-s-daty-s-terraform-a-azure/).

Základní princip - jeden terraform apply musí nahodit kompletně všechno od Azure zdrojů přes generátory, šoupače dat i zpracování až po vizualizaci.

# Od generátorů po zpracovaný výsledek
Jak jsem popsal minule generátory napsané v Pythonu využívající Kafka API posílají data do dvou Event Hubů - jeden reprezentuje pageviews (řekněme proud analytických dat z naší webové aplikace) a druhý stars (představuje proud hvězdiček a lajků ze sociálních sítí). Zdrojový kód, zabalený kontejner i Terraform předpis pro nastartování a vytvoření kompletně celého prostředí najdete jako vždy na GitHubu. 

Co budu chtít s daty dělat:
- zachytávat oba toky a ukládat do Data Lake pro pozdější dávkové zpracování (dlouhodobé analýzy apod.)
- využít korelaci s tabulkou VIP uživatelů a vytvořit proud pageviews jen pro VIP uživatele
- v reálném čase korelovat pageviews a stars, tedy chci dostat ta data, kde uživatel v okně 15 minut byl současně na mém webu a hodnotil nás na sociálních sítích
- agregovat počty přístupů za jednotlivé HTTP metody seskupené po pěti minutách
- zachytit situaci, kdy je latence větší, než 2000 ms
- totéž jako předchozí bod, ale zaslané informace obohatit korelací s daty o uživatelích, takže tam bude například i plné jméno, bydliště nebo telefon
- detekovat první přístup na stránku za každého uživatele v rozmězí 60 minut (tedy chci se dozvědět, že uživatel přišel - například proto, že na pozadí nastartuji nějaký ML model, co má podle aktuální situace a historie zákazníka poslat nejvhodnější slevový kupón)

Protože tady tvoříme jen datové hřiště, ne celé řešení, postačí mi jako výstup zapisovat do Data Lake (řekněme do silver tieru) - v praxi by tady samozřejmě mohla být další fronta a z ní si události bude vyzobávat už můj kód (třeba Azure Function nebo vlastní serverless kontejner běžící v Azure Container Apps) a dělat co je potřeba.

# Azure Stream Analytics
V dnešní části se zaměřím na to, čím jsem začal pro real time zpracování - Azure Stream Analytics. Hlavním důvodem je to, že jde o velmi etablovanou a plně platformní službu, takže umí krásně sama škálovat a dělat podobná další kouzla. Navíc využívá jednoduše SQL jazyk a to už od svého počátku. Je to tedy plně deklarativní přístup což mi přijde fajn z hlediska opakovatelnosti a jednoduchého porozumění. V dalších dílech mrknu i na Spark pohled - Structured Streaming, který dnes taky umí SQL přístup. Do čeho se asi nezvládnu pustit je plně proudové a imperativní řešení se Storm - ale uvidíme, třeba dojde i na to. Samozřejmě si můžeme i napsat všechno sami se serverless ala Azure Functions - určitě v pohodě a sympatické pro bezestavové věci (vezmi zprávu, zkonvertuj/dopočítej/obohať a ulož), ale pro cokoli stavovějšího kdy nemůžu brát každou zprávu jako samostatnou věc (už jen pouhé agregace v plovoucím okně) mi přijde nesmysl vymýšlet znovu kolo.

Koukněme nejprve jak jsem automatizoval jednotlivé vstupy a výstupy a pak na samotné srdce řešení - jejich zpracování.

# Vstupy, výstupy a Terraform
Vstupem jsou dva Event Huby a pro autentizaci jsem použil Managed Identity - to je za mne ideální, žádné klíče. V adresáři modulů najdete stream_analytics a v souboru sa_rbac.tf dávám Systems Managed Identitě Stream Analytics Jobu (o něm později) právo na přístup k Event Hubům.

```
// Managed identity RBAC to Event Hubs
resource "random_uuid" "event_hub_pageviews" {
}

resource "azurerm_role_assignment" "event_hub_pageviews" {
  name                 = random_uuid.event_hub_pageviews.result
  scope                = var.eventhub_id_pageviews
  role_definition_name = "Azure Event Hubs Data Owner"
  principal_id         = azurerm_stream_analytics_job.main.identity[0].principal_id
}

resource "random_uuid" "event_hub_stars" {
}

resource "azurerm_role_assignment" "event_hub_stars" {
  name                 = random_uuid.event_hub_stars.result
  scope                = var.eventhub_id_stars
  role_definition_name = "Azure Event Hubs Data Owner"
  principal_id         = azurerm_stream_analytics_job.main.identity[0].principal_id
}
```

Následně v souboru sa_inputs.tf najdete Event Hub jako vstup. Tady jsem ovšem nepoužil běžně azurerm provider pro Terraform, protože ten sice v době psaní článku uměl vstup na Event Hub definovat, ale ne s použitím managed identity (resp. shared token bylo mandatory políčko - a to já v takovém případě nemám). Použil jsem tedy AzApi, které dokáže volat přímo Azure API a podporuje tak naprosto cokoli. Jak jsem zjistil potřebný JSON? Vytvořil jsem vstup v GUI a pak přes export do ARM šablony jsem získal hotový JSON rovnou k použití s AzApi. Druhý už pak byl jen úprava prvního.

```
resource "azapi_resource" "pageviews" {
  type                      = "Microsoft.StreamAnalytics/streamingjobs/inputs@2021-10-01-preview"
  name                      = "pageviews"
  parent_id                 = azurerm_stream_analytics_job.main.id
  schema_validation_enabled = false
  body = jsonencode({
    properties = {
      type : "Stream"
      datasource : {
        type : "Microsoft.EventHub/EventHub",
        properties : {
          eventHubName : var.eventhub_name_pageviews
          serviceBusNamespace : var.eventhub_namespace_name
          authenticationMode : "Msi"
        }
      }
      compression : {
        type : "None"
      }
      serialization : {
        type : "Json"
        properties : {
          encoding : "UTF8"
        }
      }
    }
  })
}

resource "azapi_resource" "stars" {
  type                      = "Microsoft.StreamAnalytics/streamingjobs/inputs@2021-10-01-preview"
  name                      = "stars"
  parent_id                 = azurerm_stream_analytics_job.main.id
  schema_validation_enabled = false
  body = jsonencode({
    properties = {
      type : "Stream"
      datasource : {
        type : "Microsoft.EventHub/EventHub",
        properties : {
          eventHubName : var.eventhub_name_stars
          serviceBusNamespace : var.eventhub_namespace_name
          authenticationMode : "Msi"
        }
      }
      compression : {
        type : "None"
      }
      serialization : {
        type : "Json"
        properties : {
          encoding : "UTF8"
        }
      }
    }
  })
}
```

To ale není ze vstupů všechno - budu si ještě načítat referenční tabulky uživatelů a VIP uživatelů a ty nám generátor sází do Data Lake (Azure Data Lake Storage Gen2) ve formě JSON souboru. Referenční data do Stream Analytics jsou zase vstupy. Opět použiji Managed Identitu, takže nastavím RBAC pro přístup do storage (to se pak použije i pro moje výstupy, které dávám pro jednoduchost do stejného accountu).

```
resource "random_uuid" "stream_analytics" {
}

resource "azurerm_role_assignment" "stream_analytics" {
  name                 = random_uuid.stream_analytics.result
  scope                = var.datalake_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_stream_analytics_job.main.identity[0].principal_id
}

resource "azapi_resource" "input_users" {
  type                      = "Microsoft.StreamAnalytics/streamingjobs/inputs@2021-10-01-preview"
  name                      = "users"
  parent_id                 = azurerm_stream_analytics_job.main.id
  schema_validation_enabled = false
  body = jsonencode({
    properties = {
      type : "Reference"
      datasource : {
        type : "Microsoft.Storage/Blob",
        properties : {
          storageAccounts : [
            {
              accountName : var.datalake_name
            }
          ]
          container : "bronze"
          pathPattern : "users/users.json"
          authenticationMode : "Msi"
        }
      }
      compression : {
        type : "None"
      }
      serialization : {
        type : "Json"
        properties : {
          encoding : "UTF8"
        }
      }
    }
  })
}

resource "azapi_resource" "input_vip" {
  type                      = "Microsoft.StreamAnalytics/streamingjobs/inputs@2021-10-01-preview"
  name                      = "vip"
  parent_id                 = azurerm_stream_analytics_job.main.id
  schema_validation_enabled = false
  body = jsonencode({
    properties = {
      type : "Reference"
      datasource : {
        type : "Microsoft.Storage/Blob",
        properties : {
          storageAccounts : [
            {
              accountName : var.datalake_name
            }
          ]
          container : "bronze"
          pathPattern : "users/vip.json"
          authenticationMode : "Msi"
        }
      }
      compression : {
        type : "None"
      }
      serialization : {
        type : "Json"
        properties : {
          encoding : "UTF8"
        }
      }
    }
  })
}
```

To bychom měli vstupy. Výstupy budou pro zjednodušení vždy jen soubory ve storage (jak už jsem říkal v reálu tady často bude další fronta a nějaké její serverless aplikační zpracování apod.). Všechno najdete v souboru sa_outputs.tf, pro příklad tady je jeden z nich.

```
resource "azurerm_stream_analytics_output_blob" "raw_pageviews" {
  name                      = "raw-pageviews"
  stream_analytics_job_name = azurerm_stream_analytics_job.main.name
  resource_group_name       = var.resource_group_name
  storage_account_name      = var.datalake_name
  storage_container_name    = "bronze"
  path_pattern              = "streamanalytics/pageviews/year={datetime:yyyy}/month={datetime:MM}/day={datetime:dd}"
  date_format               = "yyyy-MM-dd"
  time_format               = "HH"
  batch_min_rows            = 20
  batch_max_wait_time       = "00:00:01"
  authentication_mode       = "Msi"

  serialization {
    type = "Parquet"
  }
}
```

Výsledek vypadá v portálu takhle:

[![](/images/2022/2022-08-28-17-13-53.png){:class="img-fluid"}](/images/2022/2022-08-28-17-13-53.png)

[![](/images/2022/2022-08-28-17-14-23.png){:class="img-fluid"}](/images/2022/2022-08-28-17-14-23.png)

# Query a jejich výsledky

## Zachycení RAW dat
Prvním požadavkem bylo jednoduché odlévání proudu dat do storage. Na to se dá použít i Event Hub Capture, ale ta ukládá výsledek jako Avro (to by mi vůbec nevadilo), navíc ale celou zprávu ukládá jako jediný sloupec zakódovaný do base64. Chápu proč to tak je (obsahem zprávy může být doslova cokoli), ale to mi pro následné zpracování trochu komplikuje situaci. Takže když už Stream Analytics stejně chci použít, nechávám si od něj i zpracovat RAW data včetně porozumění tomu, že tělo zprávy je JSON a výsledek uložím do Parquet (velmi efektivní formát a ideální pro další zpracování).

Takhle vypadá query.

```
/* Store RAW data to bronze tier */
SELECT *
INTO [raw-pageviews]
FROM [pageviews]

SELECT *
INTO [raw-stars]
FROM [stars]
```

A tohle je výsledek na příkladu pageviews.

[![](/images/2022/2022-08-28-17-33-18.png){:class="img-fluid"}](/images/2022/2022-08-28-17-33-18.png)

## Proud RAW dat pageviews jen pro VIP uživatele
V tomto zadání potřebuji u každého pageview udělat lookup do tabulky VIP uživatelů a poslat dál pouze, pokud je uživatel v této kategorii. Z pohledu SQL je to vlastně jen jednoduchý JOIN na referenční tabulku. Moc se mi líbí takový deklarativní přístup - přestože data mi běží pod rukama, jejich zpracování definuji stejně jakoby šlo o běžné tabulky.

```
/* Store VIP only RAW data to bronze tier */
SELECT L.user_id, L.http_method, L.client_ip, L.user_agent, L.latency, L.EventEnqueuedUtcTime, L.uri
INTO [raw-vip-only]
FROM [pageviews] L
JOIN vip R
ON L.user_id = R.id
```

[![](/images/2022/2022-08-28-17-34-32.png){:class="img-fluid"}](/images/2022/2022-08-28-17-34-32.png)

## Korelace dvou proudů - přístupy uživatelů, kteří ve stejném období současně dali hvězdičky na sociální síti
Dalším požadavkem bylo propojit dva datové proudy a zjistit, zda uživatelské přístupy korelují s jejich udělováním hvězdiček v druhém proudu v okně 15 minut. K čemu je to dobré? Rozhodně je pro nás důležité propojit co uživatel na webové aplikaci dělal s tím jaké pak dal hodnocení na sociální síti. To by jistě šlo analyzovat po dávkách v noci, ale nám tady může jít o čas - nechceme to jen vědět, ale reagovat nějakou incentivou. V co nejkratším čase uživatele oslovit - poslat nějaké promo, přidat body za věrnost, vyzvat k dialogu (např. Jak se vám dnes líbila naše aplikace? Posíláme vám 10 kreditů na další nákup a 20 dalších, pokud nám poskytnete zpětnou vazbu - to by mohlo nespokojeného zákazníka vrátit zpátky do pohody a zabránit další bouři na sociálních sítích).

Query je díky deklarativnímu modelu zase hrozně jednoduché - JOIN nad dvěma proudy.

```
/* Pageviews and stars correlation */
SELECT L.user_id, L.http_method, L.client_ip, L.user_agent, L.latency, L.EventEnqueuedUtcTime, L.uri, R.stars
INTO [pageviews-stars-correlation]
FROM [pageviews] L
JOIN [stars] R
ON L.user_id = R.user_id AND DATEDIFF(minute,L,R) BETWEEN 0 AND 15  
```

## Agregace - pětiminutové statistiky přístupů podle HTTP metod
Do zadání jsem si dal, že potřebujeme koukat na agregovaná data. Problém proudu typu všechny přístupy na stránky je v tom, že těch dat může být opravdu hodně. Dělat nad nimi agregační dotazy může být pak hodně drahé (ptát se do SQL s miliardami údajů může vyžadovat poměrně robustní a tedy drahý stroj) pokud chceme rychlý přístup k údajům nebo hodně opožděné (nějaké noční dávkové zpracování, které sice bude určitě levnější, ale pomalé). Dalo by se použít specializované řešení, které často zvládne oboje současně - Azure Data Explorer, ale to pro moje účely teď neřeším. Budeme tedy chtít proudově udělat agregace každých 5 minut díky čemuž můžeme mít jednak velmi dlouhou a přitom malou a dobře zpracovatelnou/vizualizovatelnou historii a současně nám tam přilétají neustále aktuální hodnoty, které jednoduše hned můžeme zobrazit.

```
/* Aggregations */
SELECT COUNT(*) as count, http_method, System.Timestamp() AS WindowEnd
INTO [agg-http-method]
FROM [pageviews]
GROUP BY TumblingWindow(minute, 5), http_method
```

```json
{"count":34,"http_method":"PATCH","WindowEnd":"2022-08-28T12:35:00.0000000Z"}
{"count":32,"http_method":"DELETE","WindowEnd":"2022-08-28T12:35:00.0000000Z"}
{"count":31,"http_method":"POST","WindowEnd":"2022-08-28T12:35:00.0000000Z"}
{"count":42,"http_method":"GET","WindowEnd":"2022-08-28T12:35:00.0000000Z"}
{"count":39,"http_method":"OPTIONS","WindowEnd":"2022-08-28T12:35:00.0000000Z"}
{"count":43,"http_method":"PUT","WindowEnd":"2022-08-28T12:35:00.0000000Z"}
{"count":67,"http_method":"HEAD","WindowEnd":"2022-08-28T12:40:00.0000000Z"}
{"count":53,"http_method":"CONNECT","WindowEnd":"2022-08-28T12:40:00.0000000Z"}
{"count":70,"http_method":"TRACE","WindowEnd":"2022-08-28T12:40:00.0000000Z"}
{"count":39,"http_method":"PATCH","WindowEnd":"2022-08-28T12:40:00.0000000Z"}
{"count":47,"http_method":"DELETE","WindowEnd":"2022-08-28T12:40:00.0000000Z"}
```

## Alert při vysoké latenci
Dejme tomu, že potřebujeme vytvořit separátní proud dat tam, kde přístup na stránku byl pomalý. Například z toho chceme předvídat nějaké budoucí problémy, připravit jiný kanál komunikace (třeba poslat uživateli push notifikaci na mobil, že může nákup dokončit v mobilní appce) a nebo informovat operations.

Základní query bude vlastně jen jednoduchý filtr.

```
/* High latency alert */
SELECT *
INTO [alert-high-latency]
FROM [pageviews]
WHERE latency > 2000
```

Co kdybychom ale potřebovali data obohacená? Podle user_id jsme schopni uživatele dohledat a získat tak další užitečné informace - odkud je, jaké má telefonní číslo a tak podobně. Opět tedy použijeme referenční tabulku, ale tentokrát ne na filtraci dat, ale jejich obohacení. Tady nutno říct, že to má nějaké limity - pro malé počty streaming jednotek nemůže mít víc jak 150 MB, pro 6 a více by referenční data měla být do 5 GB. Pokud by váš scénář zahrnoval nějaké obrovitánské referenční tabulky budete možná muset sáhnout po jiném řešení (například něco kde použijete mašiny s extrémní velikostí paměti - takové M stroje s několika TB RAM by vám měly stačit na takřka cokoli).

```
/* High latency alert enriched with user lookup */
SELECT L.user_id, L.http_method, L.client_ip, L.user_agent, L.latency, L.EventEnqueuedUtcTime, L.uri, R.name, R.city, R.street_address, R.phone_number, R.birth_number, R.user_name, R.administrative_unit, R.description
INTO [alert-high-latency-enriched]
FROM [pageviews] L
JOIN users R
ON L.user_id = R.id
WHERE L.latency > 2000
```

Výsledný JSON lines vypadá takhle.

```json
{"user_id":13379,"http_method":"TRACE","client_ip":"91.178.33.182","user_agent":"Opera/9.28.(Windows NT 5.0; hne-IN) Presto/2.9.175 Version/11.00","latency":2506,"EventEnqueuedUtcTime":"2022-08-28T12:31:57.1970000Z","uri":"http://novotna.cz/search/categories/privacy.php","name":"Božena Křížová","city":"Sezemice","street_address":"U Podjezdu 17","phone_number":"777 820 142","birth_number":"810903/2954","user_name":"robertzeman","administrative_unit":"Středočeský kraj","description":"Francouzský aplikace tajný tábor zpět vyrazit domov. O směr jednání. Rozměr vydat potvrdit můj jakýkoli špatně. List zase včera vždyť."}
{"user_id":13713,"http_method":"DELETE","client_ip":"166.84.62.85","user_agent":"Opera/8.61.(X11; Linux x86_64; sd-PK) Presto/2.9.162 Version/11.00","latency":3270,"EventEnqueuedUtcTime":"2022-08-28T12:33:46.4750000Z","uri":"http://www.blaha.cz/register.htm","name":"Ludmila Bartošová","city":"Kralovice","street_address":"Družná 1","phone_number":"790 058 230","birth_number":"740111/6965","user_name":"robert58","administrative_unit":"Ústecký kraj","description":"Křičet červen praktický odchod výkon. Kultura dohoda brána počítač znát jestliže. Žít zbýt trend někde."}
{"user_id":66173,"http_method":"PATCH","client_ip":"154.108.14.196","user_agent":"Opera/8.34.(X11; Linux i686; bo-IN) Presto/2.9.175 Version/10.00","latency":4954,"EventEnqueuedUtcTime":"2022-08-28T12:35:30.3460000Z","uri":"http://jelinkova.com/main/category/list/faq.php","name":"Vendula Veselá","city":"Havířov","street_address":"Hněvkovského 321","phone_number":"606 709 047","birth_number":"065124/4352","user_name":"smarkova","administrative_unit":"Ústecký kraj","description":"Vojenský bydlet přiblížit. Rozumět váš teplý soutěž první. Spustit označovat jen podmínka vůči doprava následně. Spatřit dneska promluvit hrát bavit typický možnost."}
```

## Stavový pohled na časovou řadu - ukaž první událost, kterou uživatel v posledních 60 minutách udělal
Proudová data budou často časové řady a Stream Analytics v sobě mají dost funkcí třeba na detekci anomálií a pokud nějaké chybí, můžete si je dodat přes Azure ML (o tom jindy). Já vyzkoušel něco jednoduchého, co ale taky musí pracovat se stavem. Představme si, že z proudu dat nedokážeme vyčíst okamžik, kdy začal s webem komunikovat (typicky bychom měli k dispozici údaj o přihlášení, ale třeba něco takového nemáme - například se ověřuje jen jedno denně nebo tak něco nebo uživatele odlišujeme jen podle cookie apod.). Potřebovali bychom v rámci poslední hodiny vědět o té první události - prvním přístupu. Proč? Můžeme chtít probudit nějaké naše roboty pro doporučování, chatování nebo něco podobného a předat jim uživatelovu aktuální IP adresu a použitý browser. Také bychom mohli třeba zjišťovat situace, kdy uživatel změnil IP adresu (ukaž mi první přístup v dané hodině pro který platí, že tenhle uživatel už tam byl s jinou IP) - třeba pro bezpečnostní analýzu. Nebo třeba pokaždé, když se mu změní user_agent, takže možná přešel z PC na mobil.

```
/* Detect first event by user over last 60 minutes */
SELECT user_id, client_ip, uri
INTO [first-event-in-user-sequence]
FROM [pageviews]
WHERE ISFIRST(mi, 60) OVER (PARTITION BY user_id) = 1
```

```json
{"user_id":2395,"client_ip":"31.180.198.73","uri":"http://www.ticha.cz/index/"}
{"user_id":36432,"client_ip":"38.65.106.183","uri":"https://holub.cz/faq/"}
{"user_id":33913,"client_ip":"140.165.167.192","uri":"https://www.prochazka.cz/category/tags/tags/homepage/"}
{"user_id":34858,"client_ip":"70.70.231.37","uri":"https://maskova.cz/terms.html"}
{"user_id":74443,"client_ip":"15.105.200.102","uri":"http://soukup.cz/terms/"}
{"user_id":77156,"client_ip":"171.221.60.48","uri":"http://www.urbanova.cz/faq.html"}
{"user_id":53606,"client_ip":"166.239.186.46","uri":"https://www.soukupova.cz/tag/home.asp"}
{"user_id":83086,"client_ip":"76.59.179.60","uri":"http://zeman.cz/category.htm"}
{"user_id":13713,"client_ip":"166.84.62.85","uri":"http://www.blaha.cz/register.htm"}
{"user_id":55312,"client_ip":"4.27.211.241","uri":"https://www.kadlec.cz/app/main/post.php"}
{"user_id":2994,"client_ip":"43.240.186.213","uri":"https://www.jelinek.com/explore/terms.htm"}
```

# Vytvoření a spuštění Jobu Terraformem
Všechny query jsem naházel do jediného Jobu. Moc jsem se netrápil s výkonnostní optimalizací, tak bych měl poznamenat, že Event Hub podporuje partitioning a Stream Analytics taky a dávalo by smysl toho v query využít tak, aby toho co nejvíc běželo paralelně. Pokud by se tedy u mě veškeré zpracování točilo kolem agregace uživatelů, dávalo by smysl, aby user_id bylo partition ID v Event Hub i Stream Analytics, aby toho co nejvíc dokázalo běžet souběžně. Ale to je pro moje účely zatím moc velký detail, který teď řešit nechci - ale může to být podstatné pro celkovou cenu (efektivnější řešení = menší spotřeba). 

Takhle vypadá Terraform.

```
// Stream Analytics job
resource "azurerm_stream_analytics_job" "main" {
  name                                     = "stream_analytics"
  location                                 = var.location
  resource_group_name                      = var.resource_group_name
  compatibility_level                      = "1.2"
  data_locale                              = "en-GB"
  events_late_arrival_max_delay_in_seconds = 60
  events_out_of_order_max_delay_in_seconds = 50
  events_out_of_order_policy               = "Adjust"
  output_error_policy                      = "Drop"
  streaming_units                          = 6

  identity {
    type = "SystemAssigned"
  }

  transformation_query = <<QUERY
/* Store RAW data to bronze tier */
SELECT *
INTO [raw-pageviews]
FROM [pageviews]

SELECT *
INTO [raw-stars]
FROM [stars]

/* Store VIP only RAW data to bronze tier */
SELECT L.user_id, L.http_method, L.client_ip, L.user_agent, L.latency, L.EventEnqueuedUtcTime, L.uri
INTO [raw-vip-only]
FROM [pageviews] L
JOIN vip R
ON L.user_id = R.id

/* Pageviews and stars correlation */
SELECT L.user_id, L.http_method, L.client_ip, L.user_agent, L.latency, L.EventEnqueuedUtcTime, L.uri, R.stars
INTO [pageviews-stars-correlation]
FROM [pageviews] L
JOIN [stars] R
ON L.user_id = R.user_id AND DATEDIFF(minute,L,R) BETWEEN 0 AND 15  

/* Aggregations */
SELECT COUNT(*) as count, http_method, System.Timestamp() AS WindowEnd
INTO [agg-http-method]
FROM [pageviews]
GROUP BY TumblingWindow(minute, 5), http_method

/* High latency alert */
SELECT *
INTO [alert-high-latency]
FROM [pageviews]
WHERE latency > 2000

/* High latency alert enriched with user lookup */
SELECT L.user_id, L.http_method, L.client_ip, L.user_agent, L.latency, L.EventEnqueuedUtcTime, L.uri, R.name, R.city, R.street_address, R.phone_number, R.birth_number, R.user_name, R.administrative_unit, R.description
INTO [alert-high-latency-enriched]
FROM [pageviews] L
JOIN users R
ON L.user_id = R.id
WHERE L.latency > 2000

/* Detect first event by user over last 60 minutes */
SELECT user_id, client_ip, uri
INTO [first-event-in-user-sequence]
FROM [pageviews]
WHERE ISFIRST(mi, 60) OVER (PARTITION BY user_id) = 1
QUERY
}
```

A výsledek v GUI.

[![](/images/2022/2022-08-28-17-59-39.png){:class="img-fluid"}](/images/2022/2022-08-28-17-59-39.png)

Z pohledu Stream Analytics mám s automatizací jeden problém. Job je potřeba nastartovat a pokud běží nelze ho ani modifikovat ani mazat. To je trochu nemilé. Nastartování by se tak dalo vyřešit jinou službou (třeba zavolat z Data Factory, Azure Function s time triggerem, z Logic App, z GitHub Actions, ...), ale v AzApi providerovi pro Terraform byla přidána podpora nejen API pro zdroje, ale i API pro akce! Díky tomu bude možné Job nahodit přímo v Terraformu - nejdřív vytvoří, pak zapne... ale nemám ještě vyzkoušeno, v době psaní nebyla verze 0.5 v registru.

```
resource "azapi_resource_action" "startcapturepageviews" {
  type                   = "Microsoft.StreamAnalytics@2020-03-01"
  resource_id            = azurerm_stream_analytics_job.main.id
  action                 = "start"
  response_export_values = ["*"]
  body = jsonencode({
    outputStartMode = "JobStartTime"
  })
}
```

Nicméně to není úplné řešení - pokud uděláte změnu v předpisu Jobu nebo pokud dáte Terraform destroy a Job je zapnutý, popadá to :/  Aktuálně tedy nezbývá než přidat trochu imperativní omáčky - pokud bych třeba spouštěl terraform apply z GitHub Actions, tak bych před tím Joby zastavil a pak je zase spustil. Nicméně mým fundamentálním předpokladem datového hřiště je, že se celé dokáže postavit bez jakýchkoli dependencí (to platí) a že i pokud do něj nešťouchnete, tak se všechno zapne a bude fungovat (to je taky splněno). Pokud děláte změny, budete si muset holt Job nejdřív zastavit - ach jo, ale zvládneme. Já vždycky říkám, že je pro mě zásadní preferovat deklarativní cestu kde to jen jde, ale je nutné být neustále připraven nasadit lepidlo ve formě imperativních úkonů pro integraci mezi světy nebo pro vyřešení drobných nedostatků (vždycky je něco, co ještě není podporované nebo dočasně není k dispozici a tak) - třeba z GitHub Actions.



Tolik tedy ke zpracování proudu dat se Stream Analytics. Příště už si nahodíme i Databricks a uděláme nějaké ETL operace s Data Factory a pak se vhrneme na Structured Streaming v Databricks jako alternativu ke Stream Analytics. Pak nás čeká dávkové zpracování v Databricks, možná nějaká Synapse, PowerBI a uvidíme, co všechno se ještě bude dít. Sledujte [https://github.com/tkubica12/dataplayground](https://github.com/tkubica12/dataplayground) - je to živé. 