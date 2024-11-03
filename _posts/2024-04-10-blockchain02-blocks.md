---
layout: post
published: true
title: Blockchain od začátečníka 2 - bloky řetězené za sebou
tags:
- Blockchain
---
Dnes se podíváme na to, co dalo blockchainu jeho jméno. Budeme řetězit bloky s využitím hash funkcí.

# Hash funkce
Hash je matematická funkce, která vezme vstupní data libovolné délky a vrátí data pevné délky - pro stejný vstup budou pokaždé stejná. Je to jakýsi otisk. Dobrá hash funkce má několik zásadních vlastností. Tím, že vrací pořád stejnou délku výstupu, tak logicky musí jít o ztrátovou kompresi, tedy existují dva různé vstupy, které vedou na stejnou hash. Nicméně to u dobrého algoritmu je nesmírně obtížně najít když máte úplně volnou ruku (jako u narozeninového paradoxu je to jednodušší varianta), natož pak když chcete najít vstup vedoucí na zadanou hash. Funkce také produkuje velké změny hash při malých změnách vstupu. Z praktického hlediska je hash téměř jednosměrná - snadno se počítá z dat, ale obrácený postup je neprakticky náročný (rozuměj u SHA256 se uvádí, že pokud byste měli všechny dosavadní compute zdroje planety Země, tak to do předpokládaného zániku celého vesmíru nestihnete).

To tedy znamená, že pokud ze svých dat udělám hash a někdo tato data změní, snadno to zjistím - hash bude vycházet jinak. Na tomto místě dlužno zmínit, že pokud hash používám pro bezpečnostní účely jako je třeba ověření hesla, tak abych předešel tomu, že typická slova jsou předpočítána (lookup v tabulce je rychlejší, než výpočet hash), bude dobré heslo nasolit (přidat k němu náhodné znaky a ty společně s ním uložit - tím znemožním předpočítávání dopředu, tzn. rainbow table útok). 

Můžu tedy vzít nějaká data a přes hash si zaznamenat jejich otisk a tím se ujistit, že s nimi nikdo nemanipuloval.

[![](/images/2024/2024-04-08-16-37-55.png){:class="img-fluid"}](/images/2024/2024-04-08-16-37-55.png)

# Blockchain
Co když máme data, která přibývají, například finanční transakce (převody apod.), vlastnictví nějakého tokenu, logy, dokumenty, zálohy a jiné události? Ke každé by dávalo smysl uložit si nějaký čas vzniku a dát jí pořadové číslo.

[![](/images/2024/2024-04-08-16-40-30.png){:class="img-fluid"}](/images/2024/2024-04-08-16-40-30.png)

Všechny tyto informace můžu dát za sebe a udělat hash, takže mám otisk nejen obsahu zprávy, ale i času a pořadového čísla. To je fajn, mám jistotu, že tyto údaje nikdo beztrestně nezmění. Ale co kdyby někdo chtěl nějaké transakce ne změnit, ale prostě smazat? Koupím si auto, pípnu kartou a odjedu - mezitím karetní transakci smažu a to je problém. Obchodník nemá ani peníze ani auto. Co kdybych tedy u první transakce (genesis blok) udělal hash a v následujícím bloku tu hash předchozího přidal do počítání hash současného? A hash druhého bloku zase přidal do výpočtu hash třetího. Tím vzniká řetěz, chain, řetěz bloků, blockchain.

[![](/images/2024/2024-04-08-16-43-42.png){:class="img-fluid"}](/images/2024/2024-04-08-16-43-42.png)

# Ukázka v Pythonu
Zkusil jsem něco takového za vydatného přispění GitHub Copilotu nahodit v Pythonu. Tady je definice objektu blok. Je to jen datová struktura s atributy jako na obrázku a k tomu funkce, které to vyplivne jako dictionary (pro tištěný výstup)

```python
import hashlib
import time
import json

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index  # The position of the block in the blockchain
        self.previous_hash = previous_hash  # The hash of the previous block in the blockchain
        self.timestamp = timestamp  # The time when the block was created
        self.data = data  # The data stored in the block
        self.hash = hash  # The hash of the block's content

    def to_dict(self):
        # Convert the block to a dictionary for visualization
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'data': self.data,
            'hash': self.hash
        }
```

S tímto blokem pak pracuji v třídě Blockchain. Při jejím založení vznikne úvodní blok (genesis) a pak máme pár metod. První počítá hash a je velmi jednoduchá - na vstupu dostane příslušná políčka, tedy číslo bloku, předchozí hash, timestamp a data bloku, jednoduše je sloučí do jediného řetězce a zavolá SHA256. Druhá vytváří nový blok. Ta si vytáhne předchozí blok a načte z něj jeho hash, vytvoří novou instanci bloku a spočítá pro něj hash. Poslední zajímavá funkce je pro validaci blockchainu, která projde všechny bloky a přepočítává hash. Pokud souhlasí, nikdo se nám v tom nehrabal.

```python
class Blockchain:
    def __init__(self):
        # Create the genesis block with index 0 and arbitrary previous hash
        self.genesis_block = Block(0, "0", int(time.time()), "Genesis Block", self.calculate_hash(0, "0", int(time.time()), "Genesis Block"))
        self.blockchain = [self.genesis_block]  # Initialize the blockchain with the genesis block

    def calculate_hash(self, index, previous_hash, timestamp, data):
        # Calculate the SHA-256 hash of a block
        value = str(index) + str(previous_hash) + str(timestamp) + str(data)
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def create_new_block(self, data):
        # Create a new block with the given data
        latest_block = self.blockchain[-1]
        index = latest_block.index + 1
        timestamp = int(time.time())
        hash = self.calculate_hash(index, latest_block.hash, timestamp, data)
        new_block = Block(index, latest_block.hash, timestamp, data, hash)
        self.blockchain.append(new_block)
        return new_block

    def get_latest_block(self):
        # Get the latest block in the blockchain
        return self.blockchain[-1]

    def validate_blockchain(self):
        # Validate the integrity of the blockchain
        for i in range(1, len(self.blockchain)):
            current_block = self.blockchain[i]
            previous_block = self.blockchain[i - 1]

            # Check if the current block's hash is correct
            if current_block.hash != self.calculate_hash(current_block.index, current_block.previous_hash, current_block.timestamp, current_block.data):
                return False
            # Check if the current block's previous hash matches the hash of the previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def to_json(self):
        return json.dumps([block.to_dict() for block in self.blockchain], indent=4)
```

Tady je kód, kterým nahodíme pár bloků a podíváme se na výsledek.

```python
# Create a new Blockchain
my_blockchain = Blockchain()

# Add data to a new block
my_blockchain.create_new_block("Some data for the first block")

# Add data to another new block
my_blockchain.create_new_block("Some data for the second block")

# Print the blockchain
print(my_blockchain.to_json())

# Validate the blockchain
if my_blockchain.validate_blockchain():
    print("\n\nThe blockchain is valid.")
else:
    print("\n\nThe blockchain is not valid.")
```

Výstup bude něco jako:

```json
[
    {
        "index": 0,
        "previous_hash": "0",
        "timestamp": 1712392673,
        "data": "Genesis Block",
        "hash": "5183e88805da345292405f1ef3634ec6a293b07dd036c83f9827ad7c15a5c7f5"
    },
    {
        "index": 1,
        "previous_hash": "5183e88805da345292405f1ef3634ec6a293b07dd036c83f9827ad7c15a5c7f5",
        "timestamp": 1712392673,
        "data": "Some data for the first block",
        "hash": "a0c07fb0c0fff2be8067532394c7d51fdb5b306f3ec81d792a8c2cc9946fe9d8"
    },
    {
        "index": 2,
        "previous_hash": "a0c07fb0c0fff2be8067532394c7d51fdb5b306f3ec81d792a8c2cc9946fe9d8",
        "timestamp": 1712392673,
        "data": "Some data for the second block",
        "hash": "428a22c2b2fadf75309368d490a06fd006a3fc9fc56c4ae3284ab0726ab752d2"
    }
]


The blockchain is valid.
```

Pokusme se nějakou transakci "cinknout".

```python
# Tamper with the blockchain
my_blockchain.blockchain[1].data = "Some data for the tampered block"

# Print the blockchain
print(my_blockchain.to_json())

# Validate the blockchain
if my_blockchain.validate_blockchain():
    print("\n\nThe blockchain is valid.")
else:
    print("\n\nThe blockchain is not valid.")
```

Výstup bude něco jako:

```json
[
    {
        "index": 0,
        "previous_hash": "0",
        "timestamp": 1712392673,
        "data": "Genesis Block",
        "hash": "5183e88805da345292405f1ef3634ec6a293b07dd036c83f9827ad7c15a5c7f5"
    },
    {
        "index": 1,
        "previous_hash": "5183e88805da345292405f1ef3634ec6a293b07dd036c83f9827ad7c15a5c7f5",
        "timestamp": 1712392673,
        "data": "Some data for the tampered block",
        "hash": "a0c07fb0c0fff2be8067532394c7d51fdb5b306f3ec81d792a8c2cc9946fe9d8"
    },
    {
        "index": 2,
        "previous_hash": "a0c07fb0c0fff2be8067532394c7d51fdb5b306f3ec81d792a8c2cc9946fe9d8",
        "timestamp": 1712392673,
        "data": "Some data for the second block",
        "hash": "428a22c2b2fadf75309368d490a06fd006a3fc9fc56c4ae3284ab0726ab752d2"
    }
]


The blockchain is not valid.
```

A to je vlastně všechno!

# Je vhodné do bloku dávat jen jednu transakci nebo ukládat data?
Jak uvidíme později, to složité v blockchain je spíše v distribuovanosti a to s sebou nese nějakou režii. Dává tady smysl, pokud jsou transakce malé, jich dát do bloku víc - obvykle jednotky tisíc (jak se vybírají a jestli je číslo fixní si probereme jindy). Pokud jsem prodejce zmíněného auta, chci si ověřit právě tu svojí transakci a ne nutně si postahovat a kontrolovat všechny ostatní. Abych to nemusel dělat, není blok jen pouhým hash z řetězce všech transakcí, ale používá se merkle tree (a to máme na příště). No a samozřejmě pokud je součástí transakce nějaké NFT typu digitálního umění, tak nedává smysl obrázek ukládat přímo do bloku - určitě bude někde jinde, třeba v blobu v cloudu, a do bloku dáme nějaký důkaz pravosti (jasně, to by zase mohla být hash). Takže příště zkusme merkle tree na transakce.
