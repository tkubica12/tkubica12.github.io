---
layout: post
published: true
title: Datové hřiště - generátory fake dat do kontejneru zabalené Terraformem v Azure nahozené
tags:
- Data Analytics
- Automatizace
---
Dnes se v rámci svého miniprojektu na plně automatizované datové hřiště [https://github.com/tkubica12/dataplayground](https://github.com/tkubica12/dataplayground) zaměřím na první část - generování dat. Úvod do toho proč se do něčeho takového pouštím a jak to má fungovat najdete v [předchozím článku](https://www.tomaskubica.cz/post/2022/datove-hriste-jak-si-hrat-s-daty-s-terraform-a-azure/)

# Python Faker
Pro svoje účely potřebuji skutečně plně syntetická data a nemusí dávat nijak zvlášť skutečný smysl, stačí trošku. Na to se ukázal jako ideální balíček Faker ([https://faker.readthedocs.io/en/stable/](https://faker.readthedocs.io/en/stable/)) pro Python. Skvělé je, že dokáže generovat věrohodně vypadající data a to včetně jazykové mutace s podporou češtiny. Tak například takhle generuji záznam uživatele:

```python
entry = {}
entry['id'] = index
entry['name'] = fake.name()
entry['city'] = fake.city()
entry['street_address'] = fake.street_address()
entry['phone_number'] = fake.phone_number()
entry['birth_number'] = fake.birth_number()
entry['user_name'] = fake.user_name()
entry['administrative_unit'] = fake.administrative_unit()
entry['description'] = fake.paragraph(nb_sentences=5, variable_nb_sentences=True)
jobs = []
jobs.append(fake.job())
jobs.append(fake.job())
jobs.append(fake.job())
entry['jobs'] = jobs
```

A tohle je výsledek:

[![](/images/2022/2022-08-19-11-44-13.png){:class="img-fluid"}](/images/2022/2022-08-19-11-44-13.png)

[![](/images/2022/2022-08-19-11-45-03.png){:class="img-fluid"}](/images/2022/2022-08-19-11-45-03.png)

Jasně - data tady nedávají smysl, protože Jméno a username jsou úplně jiné nebo obec Nové Sedlo není součást kraje Praha, ale poměrně hezky reprezentují jak taková data mohou vypadat. Podobným způsobem generuji všechna data a jejich ID jsou vlastně jen indexy:
- Users
- Products
- Orders referencující users
- Items referencující products a orders
- Pageviews a stars referencující users

# Kam data proudí
Jednou z destinací jsou soubory v Azure Data Lake Gen2 storage. U products, kde co záznam to file (takže je to dost pomalé, ale chtěl jsem takový scénář mít, protože se s ním dá běžně potkat) se prostě vytvoří soubor pokaždé. Jak ale na users, kde jde ve výsledku u soubor o několika GB? Mohl bych si soubor celý vytvořit lokálně a pak ho tam poslat, ale to se mi nechtělo. Pokud bude v paměti, kdy mi dojde? Rozhodl jsem se dělat append operaci na blobu a jsem tedy limitován maximálním počtem bloků jediného blobu (to je myslím 50000). Nicméně dělat to po každém řádku je pomalé a brzy bych na limit narazil, takže to řeším tak, že 1000 záznamů si smontuju v paměti a vytvořím blok (jasně - tady by bylo lepší velikost řešit dynamicky - celkový požadovaný počet záznamů vydělit 50000 maximálním počtem bloků a v takových dávkách je montovat). Když mám všechno hotovo dám commit všech bloků (celého blobu).

```python
# Create Azure Data Lake Storage file handler
file = DataLakeFileClient(account_url=storageSas,file_system_name='users', file_path='users.json')
file.create_file()

# Initialize data generator
fake = faker.Faker(['cs_CZ'])

# Generate and write records
offset = 0
data = ""
length = 0
for index in range(count):  # Generate records
    entry = {}
    entry['id'] = index
    entry['name'] = fake.name()
    entry['city'] = fake.city()
    entry['street_address'] = fake.street_address()
    entry['phone_number'] = fake.phone_number()
    entry['birth_number'] = fake.birth_number()
    entry['user_name'] = fake.user_name()
    entry['administrative_unit'] = fake.administrative_unit()
    entry['description'] = fake.paragraph(nb_sentences=5, variable_nb_sentences=True)
    jobs = []
    jobs.append(fake.job())
    jobs.append(fake.job())
    jobs.append(fake.job())
    entry['jobs'] = jobs
    data = data + json.dumps(entry)+"\n"
    length = length + len(json.dumps(entry))+1
    if index % 1000 == 0:   # Every 1000 records, write to block
        file.append_data(data=data, offset=offset, length=length)
        offset = offset + length
        data = ""
        length = 0
        print(f'Record {index+1} of {count}')

# Finish
print(f'Record {index+1} of {count}')
file.append_data(data=data, offset=offset, length=length)   # Write remaining records
file.flush_data(offset+length)    # Commit all blocks
```

Další destinací je SQL. Tam postupuji dost jednoduše a ani nepoužívám Faker - jde v zásadě jen o tabulky obsahující cizí klíče - orders referencují uživatele a celkovou hodnotu objednávky a datum (ten generuji náhodně - vygeneruji číslo pro epoch time v range za posledních 10 let a pak převedu na timestamp). Items pak referencují ProductID a OrderID.

```python
# Generate data
orderCommand = ""
itemCommand = ""
for index in range(count):
    orderId = index + 1
    userId = random.randint(1, user_max_id)
    dateEpoch = random.randint(1281707537, 1660398760)
    date = datetime.datetime.fromtimestamp(dateEpoch).strftime("%Y-%m-%d %H:%M:%S")
    value = random.randint(1, 100000)
    if orderCommand == "":
        orderCommand = f'INSERT INTO orders (orderId, userId, orderDate, orderValue) VALUES '
    else:
        orderCommand = orderCommand + f'({orderId}, {userId}, \'{date}\', {value}),'
    for items in range(random.randint(1, 10)):
        productId = random.randint(1, product_max_id)
        rowId = items + 1
        if itemCommand == "":
            itemCommand = f'INSERT INTO items (orderId, rowId, productId) VALUES '
        else:
            itemCommand = itemCommand + f'({orderId}, {rowId}, {productId}),'
    if index % 100 == 99:   # Every 100 orders send commands, commit and print info
        cursor.execute(orderCommand[:-1])
        orderCommand = ""
        cursor.execute(itemCommand[:-1])
        itemCommand = ""
        conn.commit()
        print(f'Created {index+1} of {count} orders')
```

Zapisovat to po řádcích bylo pomalé, ale SQL command INSERT INTO pojme maximálně 1000 položek.Jedu tedy ve smyčce a přes modulo to čas od času odešlu do SQL. 

Poslední destinace je pro mě EventHub, kde generuji pageviews a stars referencující uživatele. To má představovat dva nezávislé proudy dat - jeden z aplikace samotné (může to být Javascriptové logovátko na frontendu nebo sběr dat z backendu) a druhý z událostí v sociálních sítích redukované jen na to, že nějaký uživatel dal 1-5 hvězdiček hodnocení našemu obchodu. Proč takhle dva? Budeme chtít později proudy korelovat v téměř reálném čase (například s cílem zjistit na jaké produkty uživatel koukal těsně před tím, než dal špatné hodnocení a rychle mu poslat slevový kód právě na ně - ideálně v téměř reálném čase, když má web pořád ještě otevřený).

V kódu jsem nepoužil proprietární SDK, ale klasickou Kafka knihovnu, s kterou Event Hub funguje. Napojím se tedy na dva Event Huby a v nekonečné smyčce generuji data. Vždy počkám náhodně dlouhou dobu v gaussově rozdělení se středem v 10s (a v absolutní hodnotě, protože občas může přistát extrémní hodnota, která by šla pod nulu a to by hodilo chybu). Vygeneruji náhodné ID uživatele, IP adresu a User agent a následně náhodné množství pageviews pokaždé s jinou náhodnou URI a HTTP metodou. Čas od času nechám políčko Client IP prázdné (ať pak máme ve zpracování co čistit). Do latence chci dávat zpoždění gaussově rozdělené se středem v 200ms, ale čas od času chci, aby to ustřelilo někam mezi 500ms a 5s (ať si můžeme pohrát s detekcí extrémních hodnot a nějaké alertování). Když jsou zprávy nagenerované, tak ještě s pravděpodobností 1:50 vygeneruji záznam do stars streamu (to představuje třeba hodnocení z Google nebo Tripadvisor, tedy něco mimo naší aplikaci).

```python
# Initialize data generator
fake = faker.Faker(['cs_CZ'])

# Kafka configuration
conf_pageviews = {'bootstrap.servers': eventhub_endpoint,
         'security.protocol': 'SASL_SSL',
         'sasl.mechanisms': 'PLAIN',
         'sasl.username': "$ConnectionString",
         'sasl.password': eventhub_connection_string_pageviews,
         'client.id': 'client'}
conf_stars = {'bootstrap.servers': eventhub_endpoint,
         'security.protocol': 'SASL_SSL',
         'sasl.mechanisms': 'PLAIN',
         'sasl.username': "$ConnectionString",
         'sasl.password': eventhub_connection_string_stars,
         'client.id': 'client'}

producer_pageviews = Producer(conf_pageviews)
producer_stars = Producer(conf_stars)

# Run forever
while True:
    time.sleep(abs(random.gauss(10,5)))   # Wait for random time centered around 10s
    user_id = fake.pyint(min_value=0, max_value=user_max_id)    # Get new user id
    client_ip = fake.ipv4()   
    user_agent = fake.user_agent()
    for index in range(random.randint(1,30)):   # Generate random ammount of pageviews
        message = {}
        message['user_id'] = user_id
        message['http_method'] = fake.http_method()
        message['uri'] = fake.uri()

        if random.randint(1,100) != 100:
            message['client_ip'] = client_ip
        else:
            message['client_ip'] =  ""   # Make data missing from time to time

        message['user_agent'] = user_agent

        if random.randint(1,100) != 100:
            message['latency'] = abs(random.gauss(200, 50))
        else:
            message['latency'] =  random.randint(500,5000)   # Generate outlier from time to time

        message_json = json.dumps(message)
        print(message_json)
        producer_pageviews.produce('pageviews', message_json)
        producer_pageviews.flush()

    if random.randint(1,50) == 50:   # For some sessions users are giving stars on social media
        message = {}
        message['user_id'] = user_id
        message['stars'] = random.randint(1,5)
        message_json = json.dumps(message)
        print("USER STARS: " + message_json)
        producer_stars.produce('stars', message_json)
        producer_stars.flush()
```

# Vstupní parametry
Všechny skripty poběží v kontejnerech, takže jim chci předávat data přes environmental variables.

```python
# Get input parameters from environment
user_max_id = int(os.getenv('USER_MAX_ID', 999999))
eventhub_connection_string_pageviews = os.getenv('EVENTHUB_CONNECTION_STRING_PAGEVIEWS')
eventhub_connection_string_stars = os.getenv('EVENTHUB_CONNECTION_STRING_STARS')
eventhub_endpoint = f"{os.getenv('EVENTHUB_NAMESPACE')}.servicebus.windows.net:9093"

if not eventhub_connection_string_pageviews or not eventhub_connection_string_stars:
    print('Please provide Event Hub connection string via EVENTHUB_CONNECTION_STRING_PAGEVIEWS and EVENTHUB_CONNECTION_STRING_STARS environmental variable')
    exit(1)
```

Kromě streamu mají skripty konečný počet operací - v parametrech uvádíte kolik produktů, uživatelů apod. generovat. Jakmile skript bude mít hotovo chci, aby se celý kontejner ukončil a už jsem za něj neplatil.

# Docker image
Dalším krokem je zabalení do Dockerfile. Mohl bych jednoduše použít pip, ale přišlo mi, že když se pouštím do dat, měl bych se asi raději naučit s Anacondou. Dost mi tam vyhovuje, že dependence a to včetně verze Pythonu jsou v yaml souboru.

```yaml
name: pageviews
channels:
  - conda-forge
dependencies:
  - python=3.9
  - faker
  - python-confluent-kafka
```

Nicméně zabalení do kontejneru se ukázalo jako ne zrovna triviální. První pokusy skončily enormně velkým image a to nechci. Po chvilce trápení jsem se dočetl jak na to a použil multi-stage Dockerfile, takže si nejdřív bokem připravím Conda prostředí a to pak vyexportované jen nahraju do menšího základního kontejneru.

```
# The build-stage image:
FROM continuumio/miniconda3 AS build

# Install the package as normal:
COPY environment.yml .
RUN conda env create -f environment.yml

# Install conda-pack:
RUN conda install -c conda-forge conda-pack

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n pageviews -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack


# The runtime-stage image; we can use Debian as the
# base image since the Conda env also includes Python
# for us.
FROM debian:buster AS runtime

# Copy /venv from the previous stage:
COPY --from=build /venv /venv

# Copy app
COPY . /venv

# When image is run, run the code with the environment
# activated:
SHELL ["/bin/bash", "-c"]
ENTRYPOINT source /venv/bin/activate && python /venv/stream_pageviews.py
```

# Spuštění kontejneru
Kontejnerový image jsem poslal na svůj GitHub Artifacts. Teď budu chtít v rámci Terraform spustit kontejnery v okamžiku, kdy jsou cílové systémy (storage, SQL, Event Hub) připraveny. K tomu použiji Azure Container Instances. Možná pro někoho trochu exotická věc, ale pro můj scénář naprosto ideální. Většina generátorů mi má běžet jen pár minut nebo hodin, pak už za ně nechci platit. Nepotřebuju trvalý běh (kromě streaming pageviews), nechci, aby na ně někdo přistupoval, aby nějak škálovaly. Vůbec tedy nechci nějaký Kubernetes ani Container Apps, ACI je pro můj problém naprosto ideální a jakmile kontejner doběhne, už za něj neplatím. K tomu musím dobře zvolit restart politiku - Never případně OnFailure, takže když kontejner regulerně doběhne (vstupní proces se korektně ukončí), nic se nemá dělat dál - kontejneru už netřeba. Výjimkou bude stream kontejner, který běží trvale a chci ho restartovat, pokud by se mu něco stalo.

Takhle to vypadá v Terraformu.

```
resource "azurerm_container_group" "generate_orders" {
  name                = "generateorders"
  location            = var.location
  resource_group_name = var.resource_group_name
  ip_address_type     = "None"
  os_type             = "Linux"
  restart_policy      = "Never"

  container {
    name   = "container"
    image  = "ghcr.io/tkubica12/generate_orders:latest"
    cpu    = "1"
    memory = "2"

    environment_variables = {
      "COUNT"          = tostring(var.orders_count)
      "USER_MAX_ID"    = tostring(var.users_count -1)
      "PRODUCT_MAX_ID" = tostring(var.products_count -1)
      "SQL_SERVER"     = azurerm_mssql_server.main.fully_qualified_domain_name
      "SQL_DATABASE"   = azurerm_mssql_database.orders.name
      "SQL_USER"       = azurerm_mssql_server.main.administrator_login
    }

    secure_environment_variables = {
      "SQL_PASSWORD" = azurerm_mssql_server.main.administrator_login_password
    }
  }
}
```

# Závěr a co bude dál
Tak a to je všechno. Není to nijak složité, ale zase ani triviální, těch koleček je potřeba docela dost. Kód, který data generuje a hází do různých destinací. Ten kód musí být parametrizovaný a zabalený do kontejnerového obrazu a kontejner chci automatizovaně spustit ve správný okamžik tak, aby Terraform mohl pro mě ve spolupráci s Azure udělat úplně všechno. Nechci instrukce typu "terraform ti vytvoří SQL, pak si nainstaluj tehle ODBC driver, vytvoř conda prostředí, spusť tenhle Python skript a předej mu heslo" ... kdepak, to neodpovídá mým požadavkům na plnou automatizaci a nulové dependence mého datové hřiště.

Příště mrknem jak jsem se popral s konsolidací dat do Data Lake a vytvoření Delta tabulek - ke slovu přijde Data Factory a Databricks. Také dojde na proudová data a použití Stream Analytics a pak Spark Structured Streaming.