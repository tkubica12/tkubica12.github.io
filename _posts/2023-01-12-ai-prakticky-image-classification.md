---
layout: post
published: true
title: "AI v Azure prakticky: trénování vlastní klasifikace obrázků - AutoML vs. Custom Vision vs. holý TensorFlow kód v Azure"
tags:
- AI
---
Potřebujete AI pro klasifikaci obrázků, na kterých jsou nějaké vaše speciality, takže generická služba vám nestačí? Pojďme si dnes ukázat jak na to a srovnat výsledky čtyř přístupů:
- Plně vlastní model s Azure Machine Learning
- Dotrénování hotového modelu v Azure Machine Learning
- AutoML pro automatické nalezení a dotrénování nejlepšího modelu v Azure Machine Learning
- Azure Cognitive Services Custom Vision jako služba pro ty, co chtějí jednoduché vysoce abstrahované řešení

Všechny varianty vyzkoušíme, změříme a nakonec si z toho uděláme nějaké praktické, taktické a finanční závěry. Všechny zdrojáky najdete na mém [GitHubu](https://github.com/tkubica12/ai-demos/tree/main/azureml).

# Hotové modely vs. dotrénování vlastními daty vs. váš vlastní model
Pokud potřebujete klasifikovat obrázky v kategorii kočka vs. pes, je to něco, co už před vámi někdo zkoušel. V takovém případě můžete jednoduše sáhnout po kognitivní službě v Azure - Computer Vision. Ta je trénovaná na obrovitánském vzorku dat a hodně lidského potu a elektrické energie šlo do dosažení optimálního výsledku. Tím máte vyřešeno.

Hodně příkladů použití ale bude takových, že potřebujete něco trochu speciálního. Možná jste kynologická společnost, takže informace, že je to pes, vás neuspokojí. Chcete řešit jaká je to rasa, zjistit nějaké znaky degenerace z přešlechtění, zdravotní stav, neobvyklost vzoru srsti a tak podobně. To vám hotový univerzální model neřekne, ale zase začínat kvůli tomu od pixelů nemusí dávat smysl. Hotové modely se v prvních vrstvách učí identifikovat věci jako hrany a přechody a pak postupně vytahovat nějaké vyšší poznatky (třeba ouška, oči) a k rozhodnutí pes vs. kočka dojde až v pozdějších částech. Dává tedy smysl si většinu věcí z hotového modelu vypůjčit - přenést jeho výsledky na nový problém (transfer learning) a dotrénovat jen ty speciality kynologů - psi se mezi sebou totiž liší určitě stavbou těla, oušek, tlamy, stejně jako ostatní zvířata a tyhle vlastnosti ten obecný model v sobě rozeznává. Tady dnes vyzkoušíme Custom Vision jako jednoduchou službu pro amatéry a taky AutoML v rámci Azure Machine Learning pro trochu pokročilejší.

Pokud by kynologové začali s tvorbou svého modelu od začátku a měli tolik dat, času a energie jako třeba Microsoft, jistě dosáhnou s vlastním modelem nejlepší výsledky - ale ne o moc a taková investice se nevyplatí, proto raději transfer learning. Ale možná děláte na problému, který opravdu od základu vyžaduje jiné naučené postupy. Snímky z rentgenu nebo MRI pro zdravotní diagnostiku nejsou jako kočky a psi. Infra kamery namířené na výrobní linku s cílem detekovat anomálie taky ne. Mikroskopické snímky počítačového procesoru s cílem identifikovat defekty vypadají rovněž dost jinak. A co třeba obraz spektrální analýzy zvuku nebo mapa zbytkového kosmického záření? V takových případech možná sáhnete po vytváření plně vlastního modelu. To taky pro srovnání vyzkouším.

# Příprava dat a infrastruktury
Jako datovou sadu použiji známý set od Intelu čítající 20 000 obrázků o velikostech 150x150 klasifikovaných v jedné ze šesti kategorií (budovy, ulice, hory, ledovce, moře a les). Budeme tedy řešit relativně jednodušší problém multi-class a jeden label na obrázek. Nezabýváme se problémem s tisíci klasifikačních tříd a ještě k tomu současně, neřešíme ani identifikování objektů ani jejich segmentaci, nemáme FullHD rozlišení na vstupu. Zkrátka je to něco, na co nám v rozpočtu určitě zbylo.

Infrastrukturu nahodíme přes Terraform a návod je na mém GitHubu - vytvoří se Azure Machine Learning workspace a jeho zdroje, připraví se nějaké výpočetní clustery (pro práci s obrazem je vhodné výrazně paralelizovat v rámci jednoho nodu, takže budeme používat GPU clustery a doporučuji low-priority, protože to vyjde o dost levněji pokud jste ochotni tolerovat případné odejmutí nebo nepřidělení zdrojů ve špičce). Vedle toho vytvoříme Custom Vision prostředí. V rámci AzureML se dnes budeme pohybovat čistě ve v2 světě.

Pro účely zpracování v Azure ML si data do workspace potřebuji nahrát. Připravil jsem si 3 zip soubory a pracovat budu primárně s train a test (validate) sadou, kdy uvnitř jsou adresáře pro každou ze šesti tříd a v nich potom samotné obrázky. Python skriptem jsem zipy stáhnul a nahrál do workspace jako tři Data Assety typu uri_folder. Proč skriptem? Pro použití AutoML k tomu totiž musím připravit ještě metadata ve formě MLTable. Prozatím skript tedy nechme stranou, dostaneme se k němu u AutoML, ale vězte, že v tuto chvíli mám Data Asset ve workspace k dispozici (defacto je to adresář v Azure Storage, který se přimountuje k mému jobu s kódem).

# Vlastní jednoduchý CNN model v TensorFlow
Začneme tedy vlastním modelem s využitím Convolutional Neural Network (CNN) v TensorFlow a kód nasadíme v Azure Machine Learning. Postupoval jsem tak, že jsem si nejprve s kódem hrál lokálně v notebooku ve Visual Studio Code a pak se posunul do Azure, když základy fungovaly. Tady je výsledný Python kód, který na vstupu dostane adresáře pro trénování a pro validaci ve formátu, kdy jsou v něm vnořené adresáře pro každou třídu a v ní už jednotlivé obrázky. Ty jsem registroval v Azure ML jako Data Asset, ale k tomu později. Pro nás je teď podstatné, že zapneme MLFlow logování, takže v Azure ML uvidíme metriky, parametry, grafy, historii i výsledný model, který pak můžeme snadno nasadit do managed endpointu nebo do Kubernetes clusteru. Definujeme celkem standardní CNN model - pár konvolučních vrstev, ty potom zploštíme do jednoho rozměru a přes standardní Dense DNN provedeme klasifikaci na šest výstupních neuronů se softmax aktivační funkcí (tzn. multi-class single-label výstup). Dále implementujeme early stopping, takže si nemusíme hrát s množstvím epoch ručně a necháme trénování ukončit v okamžiku, kdy se výkon na validační sadě zhoršuje a model začíná být přetrénovaný. Před samotným závěrem jedna dropout vrstva, ať to má trochu menší tendenci k overfit.

```python
import argparse
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import mlflow
import os

parser = argparse.ArgumentParser("prep")
parser.add_argument("--training-data", type=str, help="Training data folder")
parser.add_argument("--test-data", type=str, help="Test data folder")
args = parser.parse_args()

mlflow.autolog()

# Set folders
train_data_dir = os.path.dirname(os.path.dirname(args.training_data))
validation_data_dir = os.path.dirname(os.path.dirname(args.test_data))

# Normalization
train_datagen = ImageDataGenerator(rescale=1/255)
validation_datagen = ImageDataGenerator(rescale=1/255)

# Generators
train_generator = train_datagen.flow_from_directory(
    train_data_dir,  
    target_size=(150,150), 
    batch_size=100,
    class_mode='categorical')

validation_generator = validation_datagen.flow_from_directory(
    validation_data_dir, 
    target_size=(150,150), 
    batch_size=20,
    class_mode='categorical')

# Define model
model = tf.keras.models.Sequential([
    # Convolution layers
    tf.keras.layers.Conv2D(16, (3,3), activation='relu', input_shape=(150, 150, 3)),  
    tf.keras.layers.MaxPooling2D(2, 2),                                            
    tf.keras.layers.Conv2D(32, (3,3), activation='relu'),                        
    tf.keras.layers.MaxPooling2D(2,2),                              
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),                  
    tf.keras.layers.MaxPooling2D(2,2),                                 
    tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
    tf.keras.layers.MaxPooling2D(2,2),

    # Flatten and use DNN to classify
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(6, activation='softmax')
])

model.summary()

# Compile model
model.compile(loss="categorical_crossentropy", optimizer=tf.keras.optimizers.RMSprop(learning_rate=0.001), metrics=["accuracy"])

# Early stopping
callback = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=5)

# Fit model
history = model.fit_generator(
    train_generator,
    steps_per_epoch=140,  
    epochs=200,
    verbose=1,
    validation_data = validation_generator,
    validation_steps=150,
    callbacks=[callback])
```

Tenhle kód jednoduše spustím jako pipeline, vstupem jsou Data Assety a poběžíme na strojích s GPU (to pro úlohy CNN je velmi důležité co do výkonu).

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/pipelineJob.schema.json
type: pipeline

description: intel_image_class_cnn pipeline

display_name: intel_image_class_cnn
experiment_name: intel_image_class_cnn

settings:
  default_datastore: azureml:workspaceblobstore
  default_compute: azureml:gpu-cluster

jobs:
  tensorflow_cnn:
    inputs:
      training_data:
        type: uri_file
        path: azureml:IntelImageClassification-train:4
        mode: ro_mount 
      test_data:
        type: uri_file
        path: azureml:IntelImageClassification-test:8
        mode: ro_mount 
    type: command
    component: file:../components/intel_image_class_cnn/component.yaml
```

Podívejme na sumář topologie modelu (výstup model.summary()) a je tam vidět, že i přestože je model poměrně jednoduchý, má 400 000 parametrů. Na vstupu pracujeme se soubory o velikosti 150x150 (ve třech barvách, takže každý obrázek představuje 150x150x3 = 67500 hodnot, kde každá je číslo mezi 0 a 255) a takových obrázků máme v trénovací sadě asi 14 000. Na GPU stroji žádný problém, ale jak uvidíme později lepší modely mají desítky či nižší stovky vrstev a jednotky i desítky milionů parametrů a jsou trénovány na milionech obrázků (třeba klasický ImageNet jich nabízí 14 milionů).

[![](/images/2023/2023-01-11-16-03-23.png){:class="img-fluid"}](/images/2023/2023-01-11-16-03-23.png)

Nejlepší výsledek na validační sadě byl v 17. epoše s 81.9% accuracy. Na to, že mě to stálo jen 12 minut běhu na VM NC6v3 s kartou V100 ve spot ceně, takže asi 0,26 USD, tak to není zas tak špatné. Pokud bych srovnal s modelem "na náhodu", tak při mých šesti třídách by se trefoval jen s pravděpodobností 16,7%. Takže jsme dramaticky lepší, než házení si kostkou. 

[![](/images/2023/2023-01-11-16-09-31.png){:class="img-fluid"}](/images/2023/2023-01-11-16-09-31.png)

**Vlastní jednoduchý CNN model: accuracy 81.9%, doba učení 12 minut za 0,26 USD**

# Transfer learning s vlastním kódem v Azure Machine Learning
Další pokus bude využívat transfer learning. Na pomoc si zde vezmu jednu z variant resnet modelu. K dispozici je nejen jeho topologie (jak jsou jednotlivé vrstvy zapojeny do sebe a co dělají), ale dostanete i výsledný model včetně všech vah. Jeho klasifikační část nás nezajímá, protože tu si právě chceme dotrénovat sami na svých datech, ale pracně spočítané váhy konvolučních vrstev se nám velmi hodí (v mém příkladu jsem použil výsledky z trénování na ImageNet sadě). Funguje to tedy tak, že si načtu tento model bez svrchní vrstvy pro klasifikaci, ale zmrazím ho - v průběhu svého trénování nebudu umožňovat modifikaci jeho vah. Nad něj přidám plně propojené klasifikační vrstvy podobně jako v předchozím případě a zakončím je šestičlennou vrstvou se softmax aktivační funkcí pro můj problém se šesti třídami.

```python
import argparse
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import mlflow
import os

parser = argparse.ArgumentParser("prep")
parser.add_argument("--training-data", type=str, help="Training data folder")
parser.add_argument("--test-data", type=str, help="Test data folder")
args = parser.parse_args()

mlflow.autolog()

# Set folders
train_data_dir = os.path.dirname(os.path.dirname(args.training_data))
validation_data_dir = os.path.dirname(os.path.dirname(args.test_data))

# Normalization
train_datagen = ImageDataGenerator(rescale=1/255)
validation_datagen = ImageDataGenerator(rescale=1/255)

# Generators
train_generator = train_datagen.flow_from_directory(
    train_data_dir,  
    target_size=(150,150), 
    batch_size=100,
    class_mode='categorical')

validation_generator = validation_datagen.flow_from_directory(
    validation_data_dir, 
    target_size=(150,150), 
    batch_size=20,
    class_mode='categorical')

# Define base model InceptionResNetV2 for transfer learning
base_model = tf.keras.applications.InceptionResNetV2(
                include_top=False,        # Do not include the ImageNet classifier at the top, we will train our own.
                weights='imagenet',       # Load weights pre-trained on ImageNet.    
                input_shape=(150,150,3)
                )

base_model.trainable = False  # Freeze the base model

base_model.summary()

# Define model
model = tf.keras.Sequential([
        base_model,                                       # Starting from frozen base model
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),                     # Dropout layer to prevent overfitting
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(6, activation='softmax')    # Final layer for 6 classes
    ])

model.summary()

# Compile model
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

# Early stopping
callback = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=5)

# Fit model
history = model.fit_generator(
    train_generator,
    epochs=5000,
    verbose=1,
    validation_data = validation_generator,
    callbacks=[callback])
```

K tomu příslušný pipeline YAML a hurá poslat do Azure Machine Learning (je to skoro totéž jako v předchozím příkladu, takže zde neuvádím, ale najdete na mém GitHubu).

Podívejme na výsledek.

[![](/images/2023/2023-01-12-08-59-40.png){:class="img-fluid"}](/images/2023/2023-01-12-08-59-40.png)

Dosáhli jsme dramaticky lepší accuracy a přitom nás to nestálo o moc víc peněz za trénovací čas. Evidentně náš problém je natolik klasický, že transfer learning u něj dává naprosto zásadní smysl.

Mohli bychom teď pokračovat a pokusit se výsledek ještě zlepšit. Připravené váhy konvoluční části nám velmi pomohly, ale to neznamená, že je nemůžeme lehce upravit, aby nám model seděl ještě lépe. Teď, když díky jejich zmražení model dosáhl skvělé přesnosti v naší vlastní klasifikaci mohli bychom teď všechny parametry modelu odemknout a opatrně pomalinku (tedy s velmi nízkou learning rate) pokračovat dál v ladění. Tímto postupem bychom se mohli dostat ještě ne vyšší přesnost.

**Vlastní transfer learning s variantou resnetu: accuracy 91,7%, doba učení 15 minut za 0,31 USD**

# AutoML v Azure Machine Learning
Možná nechcete psát kód a snažit se porozumět tomu, jaký model bude nejlepší a jak naladit jeho parametry. Přesto ale potřebujete, aby se model ladit dal, když to bude potřeba, dal se spravovat a nasazovat nějakým uceleným způsobem (MLOps), monitorovat parametry i metriky přes MLFlow, ukládat a verzovat modely do registru, moci je provozovat i trénovat na plně platformním prostředí, ale i v Azure Kubernetes Service nebo přes Arc v compute Kubernetes clusteru v on-premises. Čili hledáme automatiku a uživatelskou jednoduchost, ale se zachováním plné síly a kontroly v machine learningu. Právě na to je funkce AutoML v Azure Machine Learning službě.

AutoML má i svou grafickou podobu, ale ta je aktuálně stále na v1 služby, proto jsem se rozhodl průvodce nepoužít a nasadit AutoML přes pipeline (YAML soubory). V první řadě potřebuji vygenerovat tabulku s metadaty, defacto URL k obrázku a jeho klasifikaci a uložit ve formátu MLTable jako Data Asset. Jak nahrání tak vygenerování JSON a MLTable manifestu jsem obstaral upraveným skriptem z dokumentace:

```python
import argparse
import json
import os
import urllib
from zipfile import ZipFile

from azure.identity import InteractiveBrowserCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes


def create_ml_table_file(filename):
    """Create ML Table definition"""

    return (
        "paths:\n"
        "  - file: ./{0}\n"
        "transformations:\n"
        "  - read_json_lines:\n"
        "        encoding: utf8\n"
        "        invalid_lines: error\n"
        "        include_path_column: false\n"
        "  - convert_column_types:\n"
        "      - columns: image_url\n"
        "        column_type: stream_info"
    ).format(filename)


def save_ml_table_file(output_path, mltable_file_contents):
    with open(os.path.join(output_path, "MLTable"), "w") as f:
        f.write(mltable_file_contents)


def create_jsonl_and_mltable_files(uri_folder_data_path, dataset_dir):
    print("Creating jsonl files")

    # Create metadata folder and annotations file path
    metadata_folder = os.path.join(dataset_dir, "metadata")
    os.makedirs(metadata_folder, exist_ok=True)
    annotations_file = os.path.join(metadata_folder, "annotations.jsonl")

    # Baseline of json line dictionary
    json_line_sample = {"image_url": uri_folder_data_path, "label": ""}
    print(f"json_line_sample: {json_line_sample}")

    # Scan each sub directory and generate a jsonl line per image, distributed on train and valid JSONL files
    with open(annotations_file, "w") as train_f:
        for class_name in os.listdir(dataset_dir):
            sub_dir = os.path.join(dataset_dir, class_name)
            if not os.path.isdir(sub_dir):
                continue

            # Scan each sub directary
            print(f"Parsing {sub_dir}")
            for image in os.listdir(sub_dir):
                json_line = dict(json_line_sample)
                json_line["image_url"] += f"{class_name}/{image}"
                json_line["label"] = class_name

                train_f.write(json.dumps(json_line) + "\n")
    print("done")

    # Create and save mltable
    mltable_file_contents = create_ml_table_file(os.path.basename(annotations_file))
    save_ml_table_file(metadata_folder, mltable_file_contents)

def extract_upload_data(ml_client, dataset_parent_dir, download_url):

    # Create directory, if it does not exist
    os.makedirs(dataset_parent_dir, exist_ok=True)

    # download data
    print(f"Downloading data from {download_url}")

    # Extract current dataset name from dataset url
    dataset_name = os.path.basename(download_url).split(".")[0]

    # Get dataset path for later use
    dataset_dir = os.path.join(dataset_parent_dir, dataset_name)

    # Get the name of zip file
    data_file = os.path.join(dataset_parent_dir, f"{dataset_name}.zip")

    # Download data from public url
    urllib.request.urlretrieve(download_url, filename=data_file)

    # extract files
    with ZipFile(data_file, "r") as zip:
        print("extracting files...")
        zip.extractall(path=dataset_parent_dir)
        print("done")
    # delete zip file
    os.remove(data_file)

    # Upload data and create a data asset URI folder
    print("Uploading data to blob storage")
    my_data = Data(
        path=dataset_dir,
        type=AssetTypes.URI_FOLDER,
        description=dataset_name,
        name=dataset_name,
    )

    uri_folder_data_asset = ml_client.data.create_or_update(my_data)

    print(uri_folder_data_asset)
    print("")
    print("Path to folder in Blob Storage:")
    print(uri_folder_data_asset.path)
    return uri_folder_data_asset.path, dataset_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare data for image classification"
    )

    parser.add_argument("--subscription", type=str, help="Subscription ID")
    parser.add_argument("--group", type=str, help="Resource group name")
    parser.add_argument("--workspace", type=str, help="Workspace name")
    parser.add_argument("--data_path", type=str, default="./localdata", help="Dataset location")

    args, unknown = parser.parse_known_args()
    args_dict = vars(args)

    credential = InteractiveBrowserCredential()
    ml_client = None
    try:
        ml_client = MLClient.from_config(credential)
    except Exception as ex:
        # Enter details of your AML workspace
        subscription_id = args.subscription
        resource_group = args.group
        workspace = args.workspace
        ml_client = MLClient(credential, subscription_id, resource_group, workspace)

    # Upload train data
    print("\n\n\nUploading train data\n-----------------------------\n")
    uri, dir = extract_upload_data(
        ml_client=ml_client, dataset_parent_dir=args.data_path, download_url="https://tkubicastore.blob.core.windows.net/datasets/IntelImageClassification-train.zip?sp=r&st=2023-01-10T08:07:34Z&se=2050-01-10T16:07:34Z&spr=https&sv=2021-06-08&sr=b&sig=NLeEHjOJWP8axxa%2F5tRgFbheFPjug7ZjV4NW9COlJWQ%3D"
    )
    create_jsonl_and_mltable_files(
        uri_folder_data_path=uri, dataset_dir=dir
    )

    # Upload test data
    print("\n\n\nUploading test data\n-----------------------------\n")
    uri, dir = extract_upload_data(
        ml_client=ml_client, dataset_parent_dir=args.data_path, download_url="https://tkubicastore.blob.core.windows.net/datasets/IntelImageClassification-test.zip?sp=r&st=2023-01-10T07:35:28Z&se=2050-01-10T15:35:28Z&spr=https&sv=2021-06-08&sr=b&sig=ll4OfueLALA4O0kMMNeOr5A10aQMWXOruUO%2F5cryocE%3D"
    )
    create_jsonl_and_mltable_files(
        uri_folder_data_path=uri, dataset_dir=dir
    )

    # Upload pred data
    print("\n\n\nUploading pred data\n-----------------------------\n")
    uri, dir = extract_upload_data(
        ml_client=ml_client, dataset_parent_dir=args.data_path, download_url="https://tkubicastore.blob.core.windows.net/datasets/IntelImageClassification-pred.zip?sp=r&st=2023-01-10T08:07:01Z&se=2050-01-10T16:07:01Z&spr=https&sv=2021-06-08&sr=b&sig=NjCHkPluekLnbgVGi%2FTVfN%2FdVR2oCS2zmmUEPm6TYjU%3D"
    )
```

Pojďme k tomu zajímavějšímu. AutoML pro mě bude samo hledat různé modely a hrát si s jejich hyperparametry, takže takhle dokážu určitě najít ten nejlepší. Začal jsem režimem, kdy to nechám všechno na AutoML a jediné co omezím je počet zkoušených modelů.

```yaml
$schema: https://azuremlsdk2.blob.core.windows.net/preview/0.0.1/autoMLJob.schema.json

type: automl

experiment_name: intel_image_class_automl_small
description: intel_image_class_automl_small

compute: azureml:gpu-cluster

task: image_classification
log_verbosity: debug
primary_metric: accuracy

target_column_name: label
training_data:
  path: ./data/intel_image_classification/localdata/IntelImageClassification-train/metadata
  type: mltable
validation_data:
  path: ./data/intel_image_classification/localdata/IntelImageClassification-test/metadata
  type: mltable

limits:
  max_trials: 5
  max_concurrent_trials: 1
```

Pro další variantu jsem zvolil situaci, kdy chci trochu promluvit do toho jaké modely se použijí, ale jejich parametry nechám v default nastavení.

```yaml
$schema: https://azuremlsdk2.blob.core.windows.net/preview/0.0.1/autoMLJob.schema.json

type: automl

experiment_name: intel_image_class_automl_large
description: intel_image_class_automl_large

compute: azureml:gpu-spot-cluster

task: image_classification
log_verbosity: debug
primary_metric: accuracy

target_column_name: label
training_data:
  path: ./data/intel_image_classification/localdata/IntelImageClassification-train/metadata
  type: mltable
validation_data:
  path: ./data/intel_image_classification/localdata/IntelImageClassification-test/metadata
  type: mltable

limits:
  timeout_minutes: 240
  max_trials: 10
  max_concurrent_trials: 10

training_parameters:
  early_stopping: True
  evaluation_frequency: 1

sweep:
  sampling_algorithm: random
  early_termination:
    type: bandit
    evaluation_interval: 2
    slack_factor: 0.2
    delay_evaluation: 6

search_space:
  - model_name:
      type: choice
      values: [vitb16r224, vitl16r224, seresnext, resnet50, resnet152, mobilenetv2]
```

Takhle můžete pokračovat ještě dál a volit hledání hyperparametrů pro různé typy modelů s využitím různých technik jako je výčet, náhoda, standardní rozdělení a tak podobně. Mně šlo ale hlavně o to porovnat si jednotlivé použité transfer learning modely. Výsledek je tady:

[![](/images/2023/2023-01-11-19-35-18.png){:class="img-fluid"}](/images/2023/2023-01-11-19-35-18.png)

Nejlepší pro tento problém, toto množství dat a kategorií, byl Vision Transformer v provedení Large, tedy ze seznamu jeden z nejnovějších a není to tradiční CNN, ale upravený transformer. Výsledkem je accuracy 95,8%.

Ostatní jsou ale také zajímavé - například resnet50 dává 94,1% accuracy, ale zvládne se dotrénovat za 14 minut - více jak 10x rychleji (= levněji) a MobileNetV2 ještě o polovinu rychleji (s accuracy 93,6%) a je to model, který je velmi efektivní i na spotřebu zdrojů při inferencingu (například pro běh v mobilu). Uvažme, že resnet50 za stejné náklady dává dramaticky lepší výsledky, než můj vlastní jednoduchý CNN model. Na mém problému je tedy jednoznačně vidět, že transfer learning, tedy převzít váhy z masivně protrénovaného modelu, se mi hodně vyplatilo. Navíc všechny vyzkoušené modely jsou lepší, než když jsem si tranfer learning udělal sám (výsledek tam byl 91,7%) - takže pokud stejně jako já tomu nerozumíte dostatečně, AutoML vám dá do začátku nejlepší výsledky.

**Nejlepší výsledek v AutoML: accuracy 95,8%, doba učení 168 minut za 3,7 USD ... ale pokud bych dal jen 0,3 USD i tak se dostanu k 94%**

# Custom Vision
Vrhněme se teď na službu, která se dá komplet vyklikat a zvládne ji opravdu každý. Nejprve jsem si udělal skript pro nahrání a otagování obrázků (protože zas až tak moc klikat nechci). Není to nic složitého. Stáhnu zip s trénovací sadou, kde co adresář, to třída. Použiji Python SDK pro Custom Vision a založím projekt (problém bude multi-class a výchozí model General A2, což představuje to domain id ve skriptu). Pak už jen procházím adresáře jeden po druhém, založím tag a nahraji jeho obsah. Není to úplně efektivní a měl bych používat batch API (max. 64 obrázků najednou), ale pro těch 14 000 kousků nemá cenu se s tím trápit.

```python
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
# from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import os, time, uuid
import argparse
import urllib
from zipfile import ZipFile

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--training-endpoint", help="Training endpoint for Custom Vision", required=True)
parser.add_argument("--training-key", help="Training key for Custom Vision", required=True)
parser.add_argument("--data_path", type=str, default="./localdata", help="Dataset location")
args = parser.parse_args()

print(f"Using training endpoint {args.training_endpoint}, training key {args.training_key}, data path {args.data_path}")

# Download data
dir = args.data_path
url = "https://tkubicastore.blob.core.windows.net/datasets/IntelImageClassification-train.zip?sp=r&st=2023-01-10T08:07:34Z&se=2050-01-10T16:07:34Z&spr=https&sv=2021-06-08&sr=b&sig=NLeEHjOJWP8axxa%2F5tRgFbheFPjug7ZjV4NW9COlJWQ%3D"
os.makedirs(dir, exist_ok=True)
print(f"Downloading data from {url}")
dataset_name = "custom_vision_intel_image_classification"
dataset_dir = os.path.join(dir, dataset_name)

urllib.request.urlretrieve(url, filename="data.zip")

with ZipFile("data.zip", "r") as zip:
    print("Extracting files")
    zip.extractall(path=dataset_dir)
    print("Extraction complete")
os.remove("data.zip")

# Custom Vision training client
print("Getting client")
credentials = ApiKeyCredentials(in_headers={"Training-key": args.training_key})
trainer = CustomVisionTrainingClient(args.training_endpoint, credentials)

# Create a new project
print ("Creating project")
project = trainer.create_project("intel_image_classification", classification_type="Multiclass", domain_id="2e37d7fb-3a54-486a-b4d6-cfc369af0018")	

# Upload images - each class in a separate folder
dataset_base_dir = os.path.join(dataset_dir, os.listdir(dataset_dir)[0])
for class_name in os.listdir(dataset_base_dir):
    sub_dir = os.path.join(dataset_base_dir, class_name)
    if not os.path.isdir(sub_dir):
        continue

    print(f"\n\nProcessing {sub_dir}")
    print(f"Creating tag {class_name}")
    tag = trainer.create_tag(project.id, class_name)
    print(f"Uploading images for tag {class_name}")
    for image in os.listdir(sub_dir):
        trainer.create_images_from_data(project.id, open(os.path.join(sub_dir, image), "rb").read(), [tag.id])
```

Tohle je výsledek - obrázky a jejich tagy jsou vidět v Custom Vision portálu.

[![](/images/2023/2023-01-11-08-17-55.png){:class="img-fluid"}](/images/2023/2023-01-11-08-17-55.png)

Dám je tedy vytrénovat. Hodina práce stojí 10 USD, jsem ochoten investovat 60 USD.

[![](/images/2023/2023-01-11-08-32-58.png){:class="img-fluid"}](/images/2023/2023-01-11-08-32-58.png)

Po asi čtyřech hodinách je model hotový a mohu ho publikovat.

[![](/images/2023/2023-01-11-16-34-11.png){:class="img-fluid"}](/images/2023/2023-01-11-16-34-11.png)

Tím získám endpoint (project id je uvnitř) a klíč ke službě.

[![](/images/2023/2023-01-11-16-35-14.png){:class="img-fluid"}](/images/2023/2023-01-11-16-35-14.png)

Custom Vision mi neumožňuje v GUI nahrát testovací sadu a změřit accuracy (ukazuje jen precision a recall, ale na trénovacích datech), tak si na to znova uděláme skript. Ten je vlastně velmi podobný tomu původnímu, jen tentokrát stáhnu testovací sadu a místo uploadu provedu scoring a vytisknu accuracy.

```python
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import os
import argparse
import urllib
from zipfile import ZipFile

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--prediction-endpoint", help="Prediction endpoint for Custom Vision", required=True)
parser.add_argument("--prediction-key", help="Prediction key for Custom Vision", required=True)
parser.add_argument("--project-id", help="Custom Vision project id", required=True)
parser.add_argument("--publish-name", help="Published iteration name", required=True)
parser.add_argument("--data_path", type=str, default="./localdata", help="Dataset location")
args = parser.parse_args()

print(f"Using prediction endpoint {args.prediction_endpoint}, prediction key {args.prediction_key}, data path {args.data_path}")

# Download test data
dir = args.data_path
url = "https://tkubicastore.blob.core.windows.net/datasets/IntelImageClassification-test.zip?sp=r&st=2023-01-10T07:35:28Z&se=2050-01-10T15:35:28Z&spr=https&sv=2021-06-08&sr=b&sig=ll4OfueLALA4O0kMMNeOr5A10aQMWXOruUO%2F5cryocE%3D"
os.makedirs(dir, exist_ok=True)
print(f"Downloading data from {url}")
dataset_name = "custom_vision_intel_image_classification_test"
dataset_dir = os.path.join(dir, dataset_name)

urllib.request.urlretrieve(url, filename="data.zip")

with ZipFile("data.zip", "r") as zip:
    print("Extracting files")
    zip.extractall(path=dataset_dir)
    print("Extraction complete")
os.remove("data.zip")


# Custom Vision prediction client
print("Getting client")
credentials = ApiKeyCredentials(in_headers={"Prediction-key": args.prediction_key})
predictor = CustomVisionPredictionClient(args.prediction_endpoint, credentials)


# Score images - each class in a separate folder
correct = 0
total = 0

dataset_base_dir = os.path.join(dataset_dir, os.listdir(dataset_dir)[0])
for class_name in os.listdir(dataset_base_dir):
    sub_dir = os.path.join(dataset_base_dir, class_name)
    if not os.path.isdir(sub_dir):
        continue

    print(f"\n\nProcessing {sub_dir}")
    for image in os.listdir(sub_dir):
        results = predictor.classify_image(args.project_id, args.publish_name, open(os.path.join(sub_dir, image), "rb").read())
        if results.predictions[0].tag_name == class_name:
            correct += 1
            total += 1
        else:
            total += 1
        print(f"Correct {correct} out of {total} ({correct/total*100:.2f}%)")
```

Takhle po jednom volání to tak patnáct minut trvá (na nějaké masivní batch inferencing věci tahle služba asi není ideální), ale mně stačilo. Výsledek byl moc pěkných 94,93%.

**Custom Vision: accuracy 94,93%, doba učení 4 hodiny za 40 USD**

# Co tedy zvolit pro trénování AI na vaše vlastní obrázky?
**Custom Vision** - nemusíte nic moc znát, dá se to celé i úplně vyklikat, funguje i pro malé datové sady a dosahuje velmi dobrých výsledků. Pro velikánské úlohy už ale může vycházet dráž, hůře se dělá "ve velkém" (MLOps - spousty modelů co chcete různě verzovat a nasazovat).

**AutoML v Azure ML** - výborný poměr uživatelské náročnosti (ML nemusíte moc znát, škoda, že ještě není GUI pro v2, ale to se asi dodělá), ceny a výsledku. Získáte velmi profesionální řešení včetně celého MLOps, hybridního učení i nasazování, škálování a tak podobně. Jakmile si věci odladíte a naučíte se to, můžete snadno jít o krok dál a víc a víc ovlivňovat, co AutoML dělá. Je to za mě to řešení, které je vhodné jak pro téměř záčátečníka, tak pro někoho, kdo už ML zná a umí ho efektivně ladit. Nebo pro tým, který má jak začátečníky tak pokročilé a chce jednotný nástroj.

**Vlastní kód pro transfer learning v Azure ML** - když víte co hledáte a umíte to napsat, můžete mít něco naprosto univerzálního a celý kód je plně váš. To může být třeba případ, kdy sice převezmete první CNN vrstvy, ale následnou klasifikaci v plně propojené vrstvě si potřebujete udělat výrazně jinak, protože vaše situace je hodně jedinečná. Například sice transfer learning vaší úloze pomáhá, ale je to jiný obor (třeba snímky z MRI) a pravá strana modelu musí být jiná, než běžná klasifikace.

**Vlastní kód a model v Azure ML** - s jednoduchým modelem jsem se ani zdaleka nepřiblížil ostatním variantám a ještě to vyžaduje daleko víc znalostí a zkušeností. Nicméně pokud řešíte speciální úlohu typu analýza obrazů histogramů nebo potřebujete kombinovat počítačové vidění s dalšími technikami (nějaká tranformace, generování - odstranění defektů obrazu, jeho úpravy, vylepšení), tak vám Azure ML nabídne řízení procesu od kódu po nasazení a všechno mezi tím.

Nebo ještě jinak - vývojáři a klikači osamocení ve firmě, která nemá nikoho na ML, použijte Custom Vision. Začátečníci i pokročilí, ti co to chtějí pochopit, tam kde je nějaký ML tým, kde je různá úroveň znalostí v týmu, ale dává smysl sjednotit nástroje, ale i tam, kde je vyfutrováno datovými vědci - použijte Azure Machine Learning. AutoML pro ty, co chtějí rychle a jednoduše výborný výsledek, vlastní kód pro ty, co tomu plně rozumí - ale pořád jeden nástroj.