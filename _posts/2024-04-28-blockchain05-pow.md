---
layout: post
published: true
title: Blockchain od začátečníka 5 - máš to odmakané? (Proof of Work)
tags:
- Blockchain
---
Minule jsme si ukázali, že pokud jsou mezi nody záškodníci, kteří se aktivně snaží způsobit chaos nebo podvádět, mechanismy distribuovaného konsenzu jako je Raft nestačí. Hlavní problém je v tom, že lhát je snadné a téměř zadarmo. Jedním ze způsobů, jak tohle změnit, je vynutit si pro vítězství v komunitě nějakou práci, kterou je třeba odmakat a která se dá snadno ověřit. Práce znamená jít s kůží na trh, stojí peníze a útočníkům se to pak vůbec nevyplatí. Tohle je koncept Proof of Work (PoW).

# Proof of Work na příkladu
Nejprve tedy co je ta práce. Už víme, že hlavičku bloku, ve které je hash předchozího bloku, nějaké číslo, čas a merkle root hash, proženeme hash algoritmem a tím se zařídí její neměnitelnost (resp. odhalení pokud by někdo něco změnil). To je jednoduché a rychlé. Až moc. Pro nody je pak snadné lhát, navrhovat špatné bloky a zahlcovat síť nesmysly.

Také už jsme si říkali, že hash je z praktického hlediska jednosměrná - nemůžete snadno k dané hash najít nějaká data, která na ni vedou. Změna v datech vyvolá změnu hash. Co kdybychom do hlavičky přidali nějaké "volné políčko", říkejme mu nonce, které nemá žádnou informační hodnotu a může se do něj dát cokoli? To by nám umožnilo změnou nonce nechat vygenerovat jiný hash. Kdybychom tedy určili pravidlo, že první pozice v mé hash musí být nula, tak node nemá jinou možnost, než náhodně dosadit nějakou nonce, udělat hash a uvidí, jestli měl štěstí a začíná nulou. Když ne, zkusí jinou nonce a tak pořád dokola, dokud to náhodou nevyjde. Čím víc pozic chci mít takhle daných, tím roste nepravděpodobnost něčeho takového a tedy průměrný počet pokusů. To je ta práce, work a ostatní nody si velmi snadno mohou ověřit, že to šťastlivci, co našli správný nonce, mají dobře - Proof of Work.

V kódu by to vypadalo nějak takhle. Obtížnost je počet nul na začátku a sekvenčně zvětšuji nonce, dokud to nevyjde.

```python
import hashlib

def mine(data, difficulty):
    # The prefix is a string of zeros, the length of which is the difficulty level
    prefix = '0' * difficulty
    # The nonce starts at 0
    nonce = 0
    # Keep looping until we find a hash that starts with the prefix
    while True:
        # Increment the nonce
        nonce += 1
        # Calculate the SHA-256 hash of the data concatenated with the nonce
        hash = hashlib.sha256(f'{data}{nonce}'.encode()).hexdigest()
        # If the hash starts with the prefix, we've found a solution
        if hash.startswith(prefix):
            # Return the nonce and the hash
            return nonce, hash
```

Samozřejmě, jak se dozvíme později, nody mezi sebou soupeří (za vyřešení totiž získávají odměnu) a logičtější může být zkoušet nuance nějak náhodně - ideálně jinak, než ostatní (takže nejet ani sekvenčně ale možná ani ne nějakým standardním pseudonáhodným generátorem). Obtížnost skutečně roste velmi rychle - pojďme si to změřit.

```python
import time

# The data that we want to mine
data = 'This is my data'

# Loop over difficulty levels from 1 to 6
for difficulty in range(1, 7):
    # Record the start time
    start_time = time.time()
    
    # Mine the data with the current difficulty level
    nonce, hash = mine(data, difficulty)
    
    # Record the end time
    end_time = time.time()
    
    # Print the difficulty level, time taken, nonce and hash
    print(f"Difficulty {difficulty}, Time taken: {end_time - start_time} seconds, Nonce: {nonce}, Hash: {hash}")
```

U obtížnosti 3 a 4 jsem měl dost štěstí.

```	
Difficulty 1, Time taken: 0.0 seconds, Nonce: 17, Hash: 0ae5c5b91c882fadf6662a077f6a6b546384b64dbd2ab5095473be210d76682e
Difficulty 2, Time taken: 0.0009980201721191406 seconds, Nonce: 375, Hash: 00b8d9d408c7b5b9bd88396d96c77535bc5196c01a01713c5f5e2a4df592ae03
Difficulty 3, Time taken: 0.003016948699951172 seconds, Nonce: 1209, Hash: 00005807e40c6b6d1223d3415de9405e990e2172b97a723c4b9ba52517f14d19
Difficulty 4, Time taken: 0.003984689712524414 seconds, Nonce: 1209, Hash: 00005807e40c6b6d1223d3415de9405e990e2172b97a723c4b9ba52517f14d19
Difficulty 5, Time taken: 4.424256801605225 seconds, Nonce: 1626749, Hash: 000001f05b855b9dfe5bd97e8ac51f7b3898d71c31fa66a98667cc2569eaf6bd
Difficulty 6, Time taken: 121.322026014328 seconds, Nonce: 41783245, Hash: 000000532c33686f1e02ac2eb8adcf3d0cd3f401cba691dfdab9bf0482121ae4
```

Upravil jsem tedy jednoduchý blockchain z předchozích příkladů o vynucení hash s nějakou přidanou obtížností a nonce.

```python
import hashlib
import time
import json

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash, nonce):
        self.index = index  # The position of the block in the blockchain
        self.previous_hash = previous_hash  # The hash of the previous block in the blockchain
        self.timestamp = timestamp  # The time when the block was created
        self.data = data  # The data stored in the block
        self.hash = hash  # The hash of the block's content
        self.nonce = nonce  # The nonce used for the proof of work

    def to_dict(self):
        # Convert the block to a dictionary for visualization
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'data': self.data,
            'hash': self.hash,
            'nonce': self.nonce
        }

class Blockchain:
    def __init__(self, difficulty):
        self.difficulty = difficulty  # The difficulty level for the proof of work
        # Create the genesis block with index 0 and arbitrary previous hash
        self.genesis_block = Block(0, "0", int(time.time()), "Genesis Block", self.calculate_hash(0, "0", int(time.time()), "Genesis Block", 0), 0)
        self.blockchain = [self.genesis_block]  # Initialize the blockchain with the genesis block

    def calculate_hash(self, index, previous_hash, timestamp, data, nonce):
        # Calculate the SHA-256 hash of a block
        value = str(index) + str(previous_hash) + str(timestamp) + str(data) + str(nonce)
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def proof_of_work(self, index, previous_hash, timestamp, data):
        # Implement the proof of work
        nonce = 0
        while True:
            hash = self.calculate_hash(index, previous_hash, timestamp, data, nonce)
            if hash[:self.difficulty] == '0' * self.difficulty:
                return nonce, hash
            nonce += 1

    def create_new_block(self, data):
        # Create a new block with the given data
        latest_block = self.blockchain[-1]
        index = latest_block.index + 1
        timestamp = int(time.time())
        nonce, hash = self.proof_of_work(index, latest_block.hash, timestamp, data)
        new_block = Block(index, latest_block.hash, timestamp, data, hash, nonce)
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
            if current_block.hash != self.calculate_hash(current_block.index, current_block.previous_hash, current_block.timestamp, current_block.data, current_block.nonce):
                return False
            # Check if the current block's previous hash matches the hash of the previous block
            if current_block.previous_hash != previous_block.hash:
                return False
            # Check if the current block's hash starts with the correct number of zeros
            if not current_block.hash.startswith('0' * self.difficulty):
                return False
        return True

    def to_json(self):
        return json.dumps([block.to_dict() for block in self.blockchain], indent=4)

# Create a new Blockchain
my_blockchain = Blockchain(difficulty=5)

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

```json
[
    {
        "index": 0,
        "previous_hash": "0",
        "timestamp": 1712425591,
        "data": "Genesis Block",
        "hash": "dfc5e0e773bcdf008d4d8e4987302ce6c8d8f43263aad6adf311fb125412274e",
        "nonce": 0
    },
    {
        "index": 1,
        "previous_hash": "dfc5e0e773bcdf008d4d8e4987302ce6c8d8f43263aad6adf311fb125412274e",
        "timestamp": 1712425591,
        "data": "Some data for the first block",
        "hash": "000004a8ae8123413b11c214f633a1e7ceffcb33464471da5782b8e4aab15dba",
        "nonce": 95220
    },
    {
        "index": 2,
        "previous_hash": "000004a8ae8123413b11c214f633a1e7ceffcb33464471da5782b8e4aab15dba",
        "timestamp": 1712425591,
        "data": "Some data for the second block",
        "hash": "000006b032b35b4164b9d2fdc738a59bf1b68ba8ebe75ea0e027aa161212a38d",
        "nonce": 1917116
    }
]
```

# Bitcoin a další blockchain řešení s PoW
Bitcoin, Litecoin nebo Dogecoin stojí na PoW. Původní Etherum to tak mělo taky, ale pak přešlo na Proof of Stake (o tom příště).

Nody, miners (těžaři) se snaží mít štěstí a být první, protože za to dostanou odměnu (u Bitcoinu v měsíci dubnu nejdřív stále ještě 6.25 BTC, ale v druhé půlce už jen polovina - halving, snížení odměny, událost stávající se jednou za 4 roky). Navíc ještě vydělají na zapsání transakcí, ale transakcích a incentivách jindy. Bitcoin je udělaný tak, že se obtížnost automaticky ladí tak, aby statisticky trvalo uzavřít blok 10 minut. Správně spočítaný blok se propaguje sítí a každý node ověří jeho správnost (přepočte hashe a koukne se, jestli i transakce dávají smysl a nejsou v nich podvody).

Často se říká, že díky PoW je Bitcoin neekologický, ale tento mechanismus je řešením pro bezpečnost celého systému. Pokud před svojí aplikaci dáte Web Application Firewall, který provádí inspekci veškerého provozu a hledá v ní vzorce útoků, také lze argumentovat, že nijak nepřispívá k funkčnosti systému, protože nedělá žádnou byznys logiku. Problém tedy nevidím v tomhle, ale spíše v míře - v tomto případě je alokace zdrojů do bezpečnosti poměrně nevyvážená. Ceny a ekonomické incentivy ještě rozebereme jindy - energetická náročnost jedné transakce je asi 1,2 kWh.

Co se stane, když hash najde víc nodů současně? Pak vzniknou dvě větve, síť se rozštěpí, protože obě varianty jsou naprosto správně (a mohou obsahovat jiné transakce - o nich se pobavíme ještě později). Některé nody budou vykonávat práci (přidávat blok) k jedné verzi světa, jiné k té druhé. Je velmi pravděpodobné, že jedna větev to najde dřív a v rámci konsenzu je pravidlo delšího bloku (resp. pravidlo největší naakumulované provedené práce). Tím původní větev zmizí a pokud obsahovala transakce, které zatím v síti zapsané nejsou (nejsou taky v té druhé větvi), tak ty se vrátí zpátky na seznam pro další bloky. Někdy se může stát, že rozštěpená realita přežije ještě o další kolo (zase se výsledek najde současně), ale to už je hodně nepravděpodobné. Dřív nebo později se to vyřeší. To tedy znamená, že pokud vaše transakce je úspěšně součástí nějakého bloku, nemáte ještě jistotu, že v řetězci nutně zůstane (proto je dobré u kritických transakcí počkat třeba 30 minut než vydáte zboží). Tady vidíte, že aby útočník dokázal urvat všechno na svou stranu, musel by mít 51% veškeré výpočetní kapacity Bitcoinu. To je nesmírně drahé a nepraktické pro skutečné zneužití. 

To by tedy byl Proof of Work, ale metod je víc. Jak ještě jinak můžeme zabránit tomu, aby to lháři měli jednoduché a mohli beztrestně síť kazit? Pokud to s něčím myslíte vážně, vložíte tam svoji práci a energii nebo vaše peníze. Právě to druhé je mechanismus s využitím zástavy, Proof of Stake, a o něm příště.