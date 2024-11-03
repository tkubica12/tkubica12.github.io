---
layout: post
published: true
title: Blockchain od začátečníka 3 - transakce ověřené rostoucím binárním stromem (merkle tree)
tags:
- Blockchain
---
Minule jsme začali pěkně řetězit bloky a při té příležitosti jsem zmínil, že dělat blok pro každý kousek informace, každou transakci, by mohlo být hodně neefektivní (tak například - v systémech Proof of Work se na nový blok čeká klidně 10 minut a stojí to nemálo výpočetního výkonu). Bude dávat smysl dát tam záznamů víc najednou, víc transakcí. Tyto budou potenciálně přicházet z různých směrů (minule jsem kupoval auto, ale někdo jiný ve stejný čas objednává zbytkové piliny s horou lepidla a nálepkou na povrchu v IKEA). Nechme teď stranou, podle čeho budou nody transakce do bloku vybírat (necháme si na jindy, ale je to zajímavé a důležité), spíše se soustřeďme, jak toho technicky dosáhnout.

# Transakce a merkle tree

V první řadě každou transakci je dobré při vytvoření podepsat, aby s ní nešlo manipulovat. To už umíme - vezmeme atributy transakce (já použil jen čas a data, ale ty se ve skutečnosti budou typicky skládat z adres, input a output) a uděláme z toho hash a té se typicky říká txid. 

[![](/images/2024/2024-04-09-11-43-40.png){:class="img-fluid"}](/images/2024/2024-04-09-11-43-40.png)

Transakcí můžeme chtít do bloku dát poměrně dost, typicky tisíce, ale nechceme mít nějaký limit škálovatelnosti. Ne vždy je pro všechny účastníky nutné vidět všechno - ať už z hlediska soukromí nebo čistě z důvodů efektivity (výpočetní prostředky, čas, pásmo na stažení dat). Nezapomínejme například, že kromě velkých nodů (například těžařů a těch, co za úplatek ve formě gas fee pomáhají procesovat a ověřovat transakce i bloky) jsou v síti i peněženky spotřebitelů. Chci si jen pípnout a sednout do svého nového auta, ne stahovat romány z Internetu a zuřivě počítat.

Dává tedy smysl oddělit to podstatné, tedy identifikátor a důkazy do hlavičky bloku a samotná data, tedy naše transakce, dát do nějakého body, které ne každý musí nutně chtít stahovat.

[![](/images/2024/2024-04-09-12-18-35.png){:class="img-fluid"}](/images/2024/2024-04-09-12-18-35.png)

Určitě bychom tedy mohli transakce naskládat do body a z jejich hash (txid) udělat spojením všech dohromady další hash a tu uložit ve hlavičce. Tím bychom měli jistotu, že jednak každá transakce není cinknutá (txid odpovídá) a ještě navíc nikdo do bloku žádnou nepřidal, neubral nebo nezměnil.

[![](/images/2024/2024-04-09-12-31-42.png){:class="img-fluid"}](/images/2024/2024-04-09-12-31-42.png)

Tohle by určitě fungovalo, ale je tu jeden problém na straně klientů, kteří nemají zájem stahovat si všechny transakce k sobě a počítat (mohou jich být tisíce na blok) a v některých speciálních případech ani nechceme, aby bylo všechno takhle běžně vidět. Jak to udělat tak, aby wallet prodejce aut mohl ověřit, že transakce, kterou se mnou uzavřel, se úspěšně zapsala do blockchain aniž by musel stáhnout data celého bloku? Toho můžeme dosáhnout s použití merkle tree. Je to v podstatě něco jako binární vyhledávací strom, ale s tím, že nám nejde o hledání, ale jen ověření.

Vezme si tedy vždy dvojici transakcí a z jejich txid uděláme hash a pokračujeme další dvojí (když zbývá lichý počet, vezmeme stejnou transakci dvakrát). Pak rozjedeme další vrstvu - dvojice a z nich uděláme další hash. Takhle postupuje ve stromu nahoru (v mém příkladě tedy vlastně doprava) až nám nakonec zbyde jen jediná hash - merkle root.

[![](/images/2024/2024-04-09-12-42-25.png){:class="img-fluid"}](/images/2024/2024-04-09-12-42-25.png)

Bez merkle tree si potřebuji stáhnout všechny transakce z body, abych si ověřil, že ta moje 7d11 mezi nimi je a že výsledná hash v block headeru souhlasí - pak tomu uvěřím. V případě merkle tree mohu jako peněžnka nodu říct, že tohle je moje txid a chci po něm důkaz, že v bloku opravdu je. Bude stačit, aby mi node poslal jen ty červeně označené údaje a já na základě nich už můžu příslušnou část stromu spočítat.

[![](/images/2024/2024-04-09-12-48-27.png){:class="img-fluid"}](/images/2024/2024-04-09-12-48-27.png) 

Stačilo mi získat od nodu 3 údaje, nikoli 8. To samozřejmě není žádný velký rozdíl, ale je to binární strom - s každou další vrstvou se zvýší počet ověřovacích operací pouze jednu zatímco množství transakcí na dvojnásobek! Tisíce i miliony transakcí tak najednou nejsou pro peněženku žádný problém - v této škále si to ukážeme právě teď v kódu.

# Implementace v Pythonu
Napsal jsem si jednoduchou implementaci v Pythonu na vyzkoušení. Oproti minule jsem třídu Block rozdělil na header a body.

```python
import hashlib
import time
import json
from typing import List
from collections import deque

class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, hash, merkle_root):
        self.header = {
            'index': index,
            'previous_hash': previous_hash,
            'timestamp': timestamp,
            'hash': hash,
            'merkle_root': merkle_root
        }
        self.body = {
            'transactions': transactions
        }

    def to_dict(self):
        return {
            'header': self.header,
            'body': {'transactions': [transaction.to_dict() for transaction in self.body['transactions']]}
        }
```

Dále jsem si udělal třídu Transaction a MerkleTree. Není to nic složitého. V build_merkle_tree se vytváří strom ve smyčce tak dlouho, dokud nezbyde jen jediná hash (jsme na vrcholku stromu) a pokud máme lichý počet, txid duplikujeme. Všechno ostatní jsou vlastně jen metody na vytištění výstupu a debug, které použijeme později.

```python
class Transaction:
    def __init__(self, txid, timestamp, data ) -> None:
        self.txid = txid
        self.timestamp = timestamp
        self.data = data

    def to_dict(self):
        return {
            'txid': self.txid,
            'timestamp': self.timestamp,
            'data': self.data
        }

class MerkleTree:
    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        self.tree = []
        self.root = self.build_merkle_tree()

    def build_merkle_tree(self):
        # Build the Merkle tree
        self.tree = deque([transaction.txid for transaction in self.transactions])
        levels = [list(self.tree)]  # Store each level of the tree

        while len(self.tree) > 1:
            if len(self.tree) % 2 != 0:
                # Append the hash of the last transaction again
                self.tree.append(self.tree[-2])
            new_level = deque()
            for i in range(0, len(self.tree), 2):
                new_level.append(hashlib.sha256((self.tree[i] + self.tree[i + 1]).encode('utf-8')).hexdigest())
            self.tree = new_level
            levels.append(list(self.tree))  # Store the new level

        # Print the Merkle tree
        print("*** Merkle Tree ***")
        for i, level in enumerate(levels):
            print(f"Level {i}: {' '.join(hash[:6] for hash in level)}")
        print()
        
        return self.tree[0]

    def get_levels(self):
        # Build the Merkle tree
        self.tree = deque([transaction.txid for transaction in self.transactions])
        levels = [list(self.tree)]  # Store each level of the tree

        while len(self.tree) > 1:
            if len(self.tree) % 2 != 0:
                # Append the hash of the last transaction again
                self.tree.append(self.tree[-2])
            new_level = deque()
            for i in range(0, len(self.tree), 2):
                new_level.append(hashlib.sha256((self.tree[i] + self.tree[i + 1]).encode('utf-8')).hexdigest())
            self.tree = new_level
            levels.append(list(self.tree))  # Store the new level

        return levels

    def get_root_hash(self):
        return self.root
```

Tady jsou potřebné změny v samotné třídě Blockchain, nic zásadního.

```python
class Blockchain:
    def __init__(self):
        # Create the genesis block with index 0 and arbitrary previous hash
        timestamp = int(time.time())
        genesis_transactions = [Transaction(hashlib.sha256(str(timestamp).encode('utf-8')).hexdigest(), timestamp, "Genesis block")]
        genesis_merkle_tree = MerkleTree(genesis_transactions)
        genesis_merkle_root = genesis_merkle_tree.get_root_hash()
        self.genesis_block = Block(0, "0", int(time.time()), genesis_transactions, self.calculate_hash(0, "0", int(time.time()), genesis_merkle_root), genesis_merkle_root)
        self.blockchain = [self.genesis_block]
        
    def calculate_hash(self, index, previous_hash, timestamp, merkle_root):
        value = str(index) + str(previous_hash) + str(timestamp) + str(merkle_root)
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def create_new_block(self, transactions):
        # Calculate merkle tree root
        merkle_tree = MerkleTree(transactions)
        merkle_root = merkle_tree.get_root_hash()
        
        # Create the new block
        latest_block = self.get_latest_block()
        index = latest_block.header['index'] + 1
        timestamp = int(time.time())
        hash = self.calculate_hash(index, latest_block.header['hash'], timestamp, merkle_root)
        new_block = Block(index, latest_block.header['hash'], timestamp, transactions, hash, merkle_root)
        self.blockchain.append(new_block)
        return new_block

    def get_latest_block(self):
        # Get the latest block in the blockchain
        return self.blockchain[-1]

    def validate_blockchain(self):
        for i in range(1, len(self.blockchain)):
            current_block = self.blockchain[i]
            previous_block = self.blockchain[i - 1]

            # Check if the current block's hash is correct
            if current_block.header['hash'] != self.calculate_hash(current_block.header['index'], current_block.header['previous_hash'], current_block.header['timestamp'], current_block.header['merkle_root']):
                return False

            # Check if the current block's previous hash matches the hash of the previous block
            if current_block.header['previous_hash'] != previous_block.header['hash']:
                return False

            # Validate the Merkle tree
            merkle_tree = MerkleTree(current_block.body['transactions'])
            if merkle_tree.get_root_hash() != current_block.header['merkle_root']:
                return False

        return True
    
    def to_json(self):
        return json.dumps([block.to_dict() for block in self.blockchain], indent=4)
```

Vyzkoušejme si založit blockchain a v něm dva bloky, jeden s 8 a druhý se 7 transakcemi. Na konzoli uvidíme, jak se vytváří merkle tree a taky JSON výsledných bloků a následný výpis z ověřování. Jsme "velký node", takže si spočítáme merkel tree z txid transakcí znova a porovnáme výsledek.

```
*** Merkle Tree ***
Level 0: 2f1fc8

*** Merkle Tree ***
Level 0: 574cb0 c42fbd b87ed1 3a4596 71cf1b fbe4af 17a4c1 8477d1
Level 1: 8f8093 9b5dab 42d951 dbc688
Level 2: c19934 7670a9
Level 3: 98c366

*** Merkle Tree ***
Level 0: 77fcf7 5883fe 40e837 11e4f6 f1c7ce 3b5446 c28a4a
Level 1: 08e932 0be540 7acd2d 166520
Level 2: 9faa9e a30491
Level 3: fb23e3
```

```json
[
    {
        "header": {
            "index": 0,
            "previous_hash": "0",
            "timestamp": 1712639581,
            "hash": "8f4a70c190aecfa52140df94da64f35ab421f93a71215ce9ee925b4bae476e0c",
            "merkle_root": "2f1fc8f9a46e6b041f6a30e1edc333efdbc8439d45eda37483b57faeabdebe71"
        },
        "body": {
            "transactions": [
                {
                    "txid": "2f1fc8f9a46e6b041f6a30e1edc333efdbc8439d45eda37483b57faeabdebe71",
                    "timestamp": 1712639581,
                    "data": "Genesis block"
                }
            ]
        }
    },
    {
        "header": {
            "index": 1,
            "previous_hash": "8f4a70c190aecfa52140df94da64f35ab421f93a71215ce9ee925b4bae476e0c",
            "timestamp": 1712639581,
            "hash": "926fc5be2ba59f2dd99bcff1b7354afb2a2fbe859a6300cd477a1160cff7dffe",
            "merkle_root": "98c3662171cb67c678be2d3603537a1f5b78fbf0282929c674421a0777cdfb3a"
        },
        "body": {
            "transactions": [
                {
                    "txid": "574cb0eee99efe4ebf7e15c4cba2a80de481e439d712154f2322ce1ae9356fe2",
                    "timestamp": 1712639581,
                    "data": "Transaction 1 for the first block"
                },
                {
                    "txid": "c42fbd20b187e47f1633488f79c3356c5bb56643bf50c6b7493923a4646db713",
                    "timestamp": 1712639581,
                    "data": "Transaction 2 for the first block"
                },
                {
                    "txid": "b87ed193952dbe1961822099ba2f07cd3ab7ff772dca2f6fcfd92c63b84af0e6",
                    "timestamp": 1712639581,
                    "data": "Transaction 3 for the first block"
                },
                {
                    "txid": "3a45962d7b9bc2ea719158c5ea26e0febc8e236863b55aa9b779e36913345511",
                    "timestamp": 1712639581,
                    "data": "Transaction 4 for the first block"
                },
                {
                    "txid": "71cf1bee03a73b987f25e4f00f2da13185d046f129a4760b4e5e68b0de47b629",
                    "timestamp": 1712639581,
                    "data": "Transaction 5 for the first block"
                },
                {
                    "txid": "fbe4af2b99317925370c69e20abe314c24aa15e26cd2ac7431f61b1c6651a617",
                    "timestamp": 1712639581,
                    "data": "Transaction 6 for the first block"
                },
                {
                    "txid": "17a4c191f1b17aff53ac1f37a959f0e6de56d285fcd8039817e200c20db5dd2a",
                    "timestamp": 1712639581,
                    "data": "Transaction 7 for the first block"
                },
                {
                    "txid": "8477d1eb1ec4bacabbc3b688955ea9afa62cee2e3f6f16fc5a5ef63c295e7013",
                    "timestamp": 1712639581,
                    "data": "Transaction 8 for the first block"
                }
            ]
        }
    },
    {
        "header": {
            "index": 2,
            "previous_hash": "926fc5be2ba59f2dd99bcff1b7354afb2a2fbe859a6300cd477a1160cff7dffe",
            "timestamp": 1712639581,
            "hash": "3a8ba51c7048f789924bfb122bd52fc106559d044525466029c9081c76922b72",
            "merkle_root": "fb23e38310339f23d22eeb3da565566f311f042ef88b894c4dd0cbc43ace966d"
        },
        "body": {
            "transactions": [
                {
                    "txid": "77fcf7fe04863229815b2c3824465111b7484f0774f3662d7557332e0f0495fc",
                    "timestamp": 1712639581,
                    "data": "Transaction 1 for the second block"
                },
                {
                    "txid": "5883fe29fcd8de631a0d5258296aea79b48557ad500e31cec2b8724eed2a33ac",
                    "timestamp": 1712639581,
                    "data": "Transaction 2 for the second block"
                },
                {
                    "txid": "40e83746666f079f38b9da84e0c9a48bfd1f779346b69ff9154b8e6839bf9f4e",
                    "timestamp": 1712639581,
                    "data": "Transaction 3 for the second block"
                },
                {
                    "txid": "11e4f6dc14ecc40f0856dbf35c6d5d3e5915272db321b79e47265d4701ca749f",
                    "timestamp": 1712639581,
                    "data": "Transaction 4 for the second block"
                },
                {
                    "txid": "f1c7ce2f519c8129c58e59751af194025a4c87cfb61e17d6391f404bac272f04",
                    "timestamp": 1712639581,
                    "data": "Transaction 5 for the second block"
                },
                {
                    "txid": "3b5446982e7924fcdfa8a5091562fb97ca33d2a84b8b3213139fa497f95a9ac3",
                    "timestamp": 1712639581,
                    "data": "Transaction 6 for the second block"
                },
                {
                    "txid": "c28a4a574250d5f79955e660acbfdb1a02446c5f1b65fd7896990685c190f2d1",
                    "timestamp": 1712639581,
                    "data": "Transaction 7 for the second block"
                }
            ]
        }
    }
]
```

```
*** Merkle Tree ***
Level 0: 574cb0 c42fbd b87ed1 3a4596 71cf1b fbe4af 17a4c1 8477d1
Level 1: 8f8093 9b5dab 42d951 dbc688
Level 2: c19934 7670a9
Level 3: 98c366

*** Merkle Tree ***
Level 0: 77fcf7 5883fe 40e837 11e4f6 f1c7ce 3b5446 c28a4a
Level 1: 08e932 0be540 7acd2d 166520
Level 2: 9faa9e a30491
Level 3: fb23e3



The blockchain is valid.
```

Zkusme data trochu cinknout - nejdřív změníme data v transakci.

```python
# Tamper with the blockchain
tampered_transaction = Transaction("012345678", int(time.time()), "Some data for the tampered block")
my_blockchain.blockchain[1].body['transactions'][0] = tampered_transaction

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
        "header": {
            "index": 0,
            "previous_hash": "0",
            "timestamp": 1712639476,
            "hash": "5b78475eabc9cad18762ae856b5f663b08790406e8fdd43efbc6681183d6585c",
            "merkle_root": "cf282e724495fa8791e53b6950848209bbd3929d0f73374cd52af60d76810d5c"
        },
        "body": {
            "transactions": [
                {
                    "txid": "cf282e724495fa8791e53b6950848209bbd3929d0f73374cd52af60d76810d5c",
                    "timestamp": 1712639476,
                    "data": "Genesis block"
                }
            ]
        }
    },
    {
        "header": {
            "index": 1,
            "previous_hash": "5b78475eabc9cad18762ae856b5f663b08790406e8fdd43efbc6681183d6585c",
            "timestamp": 1712639476,
            "hash": "7aadce932d58f5a8c72c7600e349ee39a94ba72e27a7fd4aa05fbd4c6008b415",
            "merkle_root": "576d0882e35cb2fd3edf40a51c4f8400d3900e25c7d245845f723726ff480b1b"
        },
        "body": {
            "transactions": [
                {
                    "txid": "012345678",
                    "timestamp": 1712639519,
                    "data": "Some data for the tampered block"
                },
                {
                    "txid": "08b2cb7d5f73ffa2a5de6c9ca12ae49ee017f5622b33a8efed59e649838be5e1",
                    "timestamp": 1712639476,
                    "data": "Transaction 2 for the first block"
                },
                {
                    "txid": "cab62541057b9314d8463f7e792423f89f9658caea23f0282420f977ffe735f4",
                    "timestamp": 1712639476,
                    "data": "Transaction 3 for the first block"
                },
                {
                    "txid": "8605bc98bb69931553777004f25b566c48ada4bfe3d0e0486880511ba7d6767b",
                    "timestamp": 1712639476,
                    "data": "Transaction 4 for the first block"
                },
                {
                    "txid": "81d959118b3f28b8511ecac51d6498859da8d0e226d787e575abbe5d913e00b7",
                    "timestamp": 1712639476,
                    "data": "Transaction 5 for the first block"
                },
                {
                    "txid": "5cb6a8c659e10f07c8eac756ff9cbe2c9e1cfa62f2c71ff85fe11a61852d33c9",
                    "timestamp": 1712639476,
                    "data": "Transaction 6 for the first block"
                },
                {
                    "txid": "654dbc8a9acf74d94fd244717def0875c14bf7381228ff410b89bf00bf8e5f5e",
                    "timestamp": 1712639476,
                    "data": "Transaction 7 for the first block"
                },
                {
                    "txid": "2f7f119feb4a6d568e6b167992713fe97a66a0b60e62ab5f436902101ac5cc81",
                    "timestamp": 1712639476,
                    "data": "Transaction 8 for the first block"
                }
            ]
        }
    },
    {
        "header": {
            "index": 2,
            "previous_hash": "7aadce932d58f5a8c72c7600e349ee39a94ba72e27a7fd4aa05fbd4c6008b415",
            "timestamp": 1712639476,
            "hash": "7de79e826ad2b97788661a75ee8d7e135ab4afbd291c6b949e35ba4d28983a08",
            "merkle_root": "74a30d605ece659d477f15b208d1057aa7474b90283ea551430b9fd1de6504d8"
        },
        "body": {
            "transactions": [
                {
                    "txid": "e6a42b20068caea012a8a89814a11bbef43e6fc7a62f6f2a43e9012d90e5e03a",
                    "timestamp": 1712639476,
                    "data": "Transaction 1 for the second block"
                },
                {
                    "txid": "c5a5c5feec0f1b6a0527c1c0fd80c87fde0afa2660f24639ed7153a84d3f6dff",
                    "timestamp": 1712639476,
                    "data": "Transaction 2 for the second block"
                },
                {
                    "txid": "81eaa7d1d51a58b6489a312af7b02831c2ac16a03b49e3f6ce476be94376711a",
                    "timestamp": 1712639476,
                    "data": "Transaction 3 for the second block"
                },
                {
                    "txid": "5433a2f4f6bee30f6669a1e0d4ae84ea38dbc93f547dfad9463bfde6de4f9be9",
                    "timestamp": 1712639476,
                    "data": "Transaction 4 for the second block"
                },
                {
                    "txid": "25bc3000b773b0f8ea9a346bf8f1bb14d927c1053e8aa0cc9bc153404512fd8b",
                    "timestamp": 1712639476,
                    "data": "Transaction 5 for the second block"
                },
                {
                    "txid": "c694bd170acbdefaa8367add5191149e7e2c0cd7b2bc1d235c1802267687268b",
                    "timestamp": 1712639476,
                    "data": "Transaction 6 for the second block"
                },
                {
                    "txid": "092b61af600e2627322ce2f551e2f968f032585e102bc7f497f1f6e312ae1b88",
                    "timestamp": 1712639476,
                    "data": "Transaction 7 for the second block"
                }
            ]
        }
    }
]
```

```
*** Merkle Tree ***
Level 0: 012345 08b2cb cab625 8605bc 81d959 5cb6a8 654dbc 2f7f11
Level 1: 9cce19 b98c84 652199 a1bce0
Level 2: 1130a0 6ffbda
Level 3: 2b8de5



The blockchain is not valid.
```

A nebo zkusme jednu transakci nenápadně vymazat.

```python
# Tamper with the blockchain by removing a transaction
del my_blockchain.blockchain[1].body['transactions'][0]

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
        "header": {
            "index": 0,
            "previous_hash": "0",
            "timestamp": 1712639581,
            "hash": "8f4a70c190aecfa52140df94da64f35ab421f93a71215ce9ee925b4bae476e0c",
            "merkle_root": "2f1fc8f9a46e6b041f6a30e1edc333efdbc8439d45eda37483b57faeabdebe71"
        },
        "body": {
            "transactions": [
                {
                    "txid": "2f1fc8f9a46e6b041f6a30e1edc333efdbc8439d45eda37483b57faeabdebe71",
                    "timestamp": 1712639581,
                    "data": "Genesis block"
                }
            ]
        }
    },
    {
        "header": {
            "index": 1,
            "previous_hash": "8f4a70c190aecfa52140df94da64f35ab421f93a71215ce9ee925b4bae476e0c",
            "timestamp": 1712639581,
            "hash": "926fc5be2ba59f2dd99bcff1b7354afb2a2fbe859a6300cd477a1160cff7dffe",
            "merkle_root": "98c3662171cb67c678be2d3603537a1f5b78fbf0282929c674421a0777cdfb3a"
        },
        "body": {
            "transactions": [
                {
                    "txid": "c42fbd20b187e47f1633488f79c3356c5bb56643bf50c6b7493923a4646db713",
                    "timestamp": 1712639581,
                    "data": "Transaction 2 for the first block"
                },
                {
                    "txid": "b87ed193952dbe1961822099ba2f07cd3ab7ff772dca2f6fcfd92c63b84af0e6",
                    "timestamp": 1712639581,
                    "data": "Transaction 3 for the first block"
                },
                {
                    "txid": "3a45962d7b9bc2ea719158c5ea26e0febc8e236863b55aa9b779e36913345511",
                    "timestamp": 1712639581,
                    "data": "Transaction 4 for the first block"
                },
                {
                    "txid": "71cf1bee03a73b987f25e4f00f2da13185d046f129a4760b4e5e68b0de47b629",
                    "timestamp": 1712639581,
                    "data": "Transaction 5 for the first block"
                },
                {
                    "txid": "fbe4af2b99317925370c69e20abe314c24aa15e26cd2ac7431f61b1c6651a617",
                    "timestamp": 1712639581,
                    "data": "Transaction 6 for the first block"
                },
                {
                    "txid": "17a4c191f1b17aff53ac1f37a959f0e6de56d285fcd8039817e200c20db5dd2a",
                    "timestamp": 1712639581,
                    "data": "Transaction 7 for the first block"
                },
                {
                    "txid": "8477d1eb1ec4bacabbc3b688955ea9afa62cee2e3f6f16fc5a5ef63c295e7013",
                    "timestamp": 1712639581,
                    "data": "Transaction 8 for the first block"
                }
            ]
        }
    },
    {
        "header": {
            "index": 2,
            "previous_hash": "926fc5be2ba59f2dd99bcff1b7354afb2a2fbe859a6300cd477a1160cff7dffe",
            "timestamp": 1712639581,
            "hash": "3a8ba51c7048f789924bfb122bd52fc106559d044525466029c9081c76922b72",
            "merkle_root": "fb23e38310339f23d22eeb3da565566f311f042ef88b894c4dd0cbc43ace966d"
        },
        "body": {
            "transactions": [
                {
                    "txid": "77fcf7fe04863229815b2c3824465111b7484f0774f3662d7557332e0f0495fc",
                    "timestamp": 1712639581,
                    "data": "Transaction 1 for the second block"
                },
                {
                    "txid": "5883fe29fcd8de631a0d5258296aea79b48557ad500e31cec2b8724eed2a33ac",
                    "timestamp": 1712639581,
                    "data": "Transaction 2 for the second block"
                },
                {
                    "txid": "40e83746666f079f38b9da84e0c9a48bfd1f779346b69ff9154b8e6839bf9f4e",
                    "timestamp": 1712639581,
                    "data": "Transaction 3 for the second block"
                },
                {
                    "txid": "11e4f6dc14ecc40f0856dbf35c6d5d3e5915272db321b79e47265d4701ca749f",
                    "timestamp": 1712639581,
                    "data": "Transaction 4 for the second block"
                },
                {
                    "txid": "f1c7ce2f519c8129c58e59751af194025a4c87cfb61e17d6391f404bac272f04",
                    "timestamp": 1712639581,
                    "data": "Transaction 5 for the second block"
                },
                {
                    "txid": "3b5446982e7924fcdfa8a5091562fb97ca33d2a84b8b3213139fa497f95a9ac3",
                    "timestamp": 1712639581,
                    "data": "Transaction 6 for the second block"
                },
                {
                    "txid": "c28a4a574250d5f79955e660acbfdb1a02446c5f1b65fd7896990685c190f2d1",
                    "timestamp": 1712639581,
                    "data": "Transaction 7 for the second block"
                }
            ]
        }
    }
]
```

```
*** Merkle Tree ***
Level 0: c42fbd b87ed1 3a4596 71cf1b fbe4af 17a4c1 8477d1
Level 1: 61c0da 0aff40 523021 e86744
Level 2: 925f7e d42dce
Level 3: 45c4ef



The blockchain is not valid.
```

# Větší efektivita na walletu díky merkle tree
Na závěr si vyzkoušejme jak by to vypadalo, kdyby bylo transakcí mnohem víc, třeba 4000.

```python
# Create a new Blockchain
my_blockchain = Blockchain()

# Add 4000 transactions to a new block
transactions_data = [f"Transaction {i} for the first block" for i in range(1, 4001)]
transactions = []
for transaction_data in transactions_data:
    timestamp = int(time.time())
    txid = hashlib.sha256((str(timestamp) + transaction_data).encode('utf-8')).hexdigest()
    transaction = Transaction(txid, timestamp, transaction_data)
    transactions.append(transaction)

my_blockchain.create_new_block(transactions)
```

```
*** Merkle Tree ***
Level 0: 5ed52b

*** Merkle Tree ***
Level 0: d8c465 4c86fc c788fc f860a2 a42b1d db2d79 f94d99 c0c255 8054a3 0d2150 a1ac8c d0cb63 bc12fb 6504e2 737391 ddc113 8ed935 2792e3 63898d 802e62 d26a1b ec4186 649b24 d1d7b5 741c0c 4f8047 7928b6 9bfa32 7645d8 b08f91 900831 c663b3 ca98c3 004558 df35b2 043129 7c9fd6 b3f881 7228cb 855da2 53e6d7 cfb11d ccc213 fb2774 b9a4c6 51ff00 62091e 58a87f 4900a2 6e1100 942c89 1b1655 323a82 233b95 a96fa2 614036 8a1457 2d26a9 9e5ca8 61151c cadada becf08 97fa59 25f6e6 8e50c4 4e4aa4 d991e5 5bdfa4 4c1388 b21167 f60e74 95f1bc d81e6a 71cc14 afc6e3 3d7e22 d71ae0 036a3d ea3014 a9ea4b e131a9 f2b256 f8eb6d e776f7 180259 f32ee3 86be4f 0693ce 6ccffe 6d452d fe7517 f55104 8deba2 843e39 5504ea 4f4042 4ef261 bdbbf3 db3133 faf4a3 7eb24e f31c4c 79a358 72ec28 11bef4 c473ce 692ff7 043002 0ca651 a9a29b a2927d f30ea2 16b4e9 c9d286 9ec33a 4049f2 9900fe b87b5f 0f1de7 93e61c 65ecfe 7a6dd3 af60e4 1f122e 148920 23776a ce21a0 8ef4aa baa9a3 d0a606 3a74b7 c1742d 3a5834 1c7112 184da9 f8c753 725ff3 382f5d 373c9f e41c60 dbf7f4 fbfa72 a6a6be 0c650c a1c1c9 bd985c 73a207 ff15f6 e741f9 bd4615 982086 75fdf1 58ea9d c4fd0a 3b6094 b1e37c 1b90ae 047c1c fb3223 eb13d7 2f1093 d48aea 60b282 8b22b2 eb6e54 212810 c5607d d3ce74 f804d9 f95661 fd8004 4d6ca1 6fdf4f a09e5c b3f02a 9d3cf3 d67fae 98fbb2 ee87fe 333096 0f0e2b 7007b3 f54e2f 08119f def02c d2866d a3dee6 1d99a2 76e636 78941a 3fc043 049295 48e3bb f3cbec cebdb9 58bd1c 4789c5 ea7df8 912902 a0a665 ef3ad0 29e7aa 92c7d4 f5663c 5ae249 19bf57 06d42f 824613 85ffa5 b6ad0d ac6482 fd9f00 291f43 7d1eea d67281 cd4d7f ff0503 7c5c63 6c8f37 c23a0f 299f29 323dbc d0a7ad c88217 7ccb0c 1d35fc 1116c3 5a2a9c f296e1 b0c6f6 7219f2 d524bf 9e8674 5cc6fc b28d1d 289628 ff243b fe7e3b 7950ed bf0c71 8849dc 744ddb edc503 57d347 c2acf6 6453a5 3239bb 782a9c edc767 13bcb4 fda3d0 b093d2 0bf673 8cb138 b910ad e4ce8e 5dd2c0 28d64e 5f515c d56147 6c06ca 0891a0 40fa64 3bf212 8c8b0d 6fd552 ab79a3 3c07b2 509a64 882fa6 3fbc92 9425e9 bca9b2 b07b33 d51d8b 176c14 3b3899 148c87 f0fdf8 7785de d9457d 346363 01bba6 9389d0 0fd30a 8a3f7a 5d9e9e 7292cf f48e02 dc60e9 59c303 3a1dd5 a882ab c2f4ab 62fee8 d19797 3958ad 891246 66f20e 3aee68 cb8269 fc77ed 243812 482d8b 379c82 402623 24078b 29ff85 c91912 cd76c2 c826fd 3f053a 8d2361 f73d81 8b7b83 f37ed0 8c82d6 9439fa 0b5d91 e50095 b6bd8e 9a0127 4b5fb5 48d280 8ea119 c16e15 1768f8 83bd5b 6cf627 6ea264 200ab6 ddcd8b bacf87 4a9986 ca4fe9 fa9dfd 429c15 d63d92 3db71e 29c9fc 5ba959 c2d62b 18bedf 86970a 9e21a8 dd48f2 086e5b ab2df0 00013f e1712e 0f2127 c42058 f9605c d310db fe0d1b 058338 feb689 16bba4 7d133c 4322cc 85f940 524da3 639d32 d39ea7 d7dd8b ee1136 3524e4 e0f4c2 4311b0 11eafa 6e66ec 293988 289c15 81a3d1 810df9 742ddc 45addc 9827d7 cedf19 05f465 a6d7d0 a3033c d9e625 b4df1c 8ab23a 642c9a 030ae2 7be069 2428af 6c797e 2ce31a cb47fc 7e63a1 25ed08 ef7df6 b7c07e c705c6 068453 d4b5b8 007cb3 7bfea3 b6b722 a1e09b fd8576 8c9d3d 8ece48 b1cf02 54b3cf 3cd930 444a58 4bdfbe fcc8f7 741c08 212c24 7afc53 7b9480 472be5 beb09e 9f4ae2 1ed139 a223ef c93ad5 280390 60860e f3a971 3ff292 b12fbe b2bf62 bc3bf9 49fdf0 c2cd6a a78f97 a287ff d21501 40eacc 6b1b3c 628e97 49c1bf 0647cf 63ac0b 6cb66d ffb122 ede7ea 16a7b5 8b222e 1c2f28 67e02e d44731 1a7220 455a9a 0bf302 287c5e 25a2bf 0765a2 1d0a25 f28b3a 628667 2a74bf 1a31cd 3b2a6b a24acf 30cd31 3e2be3 d96884 809353 6d573d 294b27 978642 798858 cf4fc1 21b67b bf9204 ce322e f238bd e4f044 abe0a3 d19e9e fd4ded 630c12 e87c36 7932a6 0d79d9 2bc27f e36f88 cf6ca5 30c565 0c94c9 8f5adb f502c9 fcfd69 bb331f a400b8 89006f 69e724 7e7232 0fe74e 8747b4 d2edd3 15cbec 95a23e 527735 758d41 7fc269 7975a9 7ec1b7 700237 789a01 6a19b3 84f39a cd4643 eb5c60 9304c7 55fd4b 00497c 3d6de7 167e17 da2079 c99f1f 95e4dd a69ff9 aacef3 40806c 0031bc 13ea52 63fbb7 733575 7f209e 15160e cb0c21 cbdc87 e1fa98 c91132 e8a04b 5a9edf b96865 8f4975 cac010 9741c1 130fa5 f35d0c 6e3f11 27a178 e1ddbf efb94a c16f7a 50c7fc 0b9a26 6d0ade af7dac e3b792 b522b5 e54d7b b87bdf 1bef5f 7575e5 469008 dcb8ed b60301 301d4f fcd486 42cb0a 3aab12 ba8993 6f13ab 46243a 4490c7 ff9ae9 81c304 65ede8 0f3ffe b81b96 6130e1 8f1ab3 340b5f c5c1f4 20513c d383c6 88c500 b37233 36159e eb65d0 4c457c 69a502 e9955e 419d83 d8fed6 72f47f 8baa0a 961199 8027fe 79b404 e7c1bb c5d676 94a54a 9e09b9 a35705 bf17b5 a6f72d 9c4bfb aed578 baeb14 513a78 c98e4f b9082f 5a5456 308a32 2a636c f5d819 243d0b 82d03f 9937c2 b599c2 5cdb57 5ab6f0 4d1970 23ba2b 2d2ef0 a9d0bd 0d7654 819dd5 a31d27 e1c512 6285ad 60fbe4 5548ab 8f8c1c 726d1d 1e71a5 130b01 5de453 0e765c 22aa1f 0a504b a48579 7d3283 ba2acc c17fdd 6acbf2 360dfe c23cb1 b29fa5 1a19f0 246f3f 62c71b 618569 ac6aab cdd272 8a3f98 d2fda0 0dc95b 5a557d 8c2d0e 91bb66 e2f175 2eeed6 e2b34a 081dd6 7f733f 0a8dd2 5e2064 c0530c d1fd06 1903f8 743243 72d036 4ef9b0 e77c40 24640a f45f23 4f95ba aa29f3 abf25e 2d600a d06a94 58914c 358a3e 37efa0 8cd47f dc242b 84d993 3f2caf ed64ad 04677e a5864a 6e4936 719dfa 4d90e9 82a195 989018 c614c5 76a39a b1ecec d25d41 da3041 0f32a9 f3b6b1 5a37cf 389766 c299c8 3daa5d 7bd19b e2e888 226fa6 132e14 efc777 0777a4 e7f33b 86e93c 26f63b 1b9a9a 8d7639 53de80 49c44f b0f7ae 3d2e1b f78e0a 631751 c1c10e a15235 f16f3a b3b5ce f22eb7 91cc3b 962354 98d522 0ab157 c00a64 bf6eac 75e350 c1219e 979fa8 c06c71 cc347d 5cf9ca a08060 24879e 0ee6b3 f45a99 39ce37 e97b11 3bbf3b 2b5f6a 4a0912 b433ac ab2a2c 5a4f5b b2f048 ceab9b 8cc8a1 5960c7 955d1a 67bfbe f31f38 37ec31 867718 4b2776 661593 cb7c09 3462e4 943cbc 94547c c832df 628ecb 6d0b8e 65bc77 0b75ca 37bd39 f4363a 6e18ac 26a9a1 e057b2 d313ef 6ae19a 65874d 4022c4 b3c5e9 dbb79a 579624 a46bb8 66d462 dcb217 dab455 f933c3 25c031 2e8316 e1cda1 491a58 fca752 a972cf 53e1ca b22dc2 1eeeef 129a80 9ce466 f689e2 9e27f5 9f75eb fb94b1 45a379 7dea51 9c0020 cdab87 563ce8 fa228f 3a7240 3dd3c7 8a41bf 42fb8b 291c40 986718 6baf65 c0f4db 0e2a54 97d491 6e7b09 0f6688 88bced e07381 744e47 05d2b9 bd5d34 dd4fea 2b1227 f4931a a8f5c1 fbd2fd 3b5614 864e2a 817a59 531229 e7470e 81cdc1 e65746 b8cb42 158899 5c215b d851c9 8590ae 76a710 90ce38 4c2a4e 443495 400148 7aaa4e fc4869 13e030 450eab 3024ba 5c3fbc 16d11f 23ff1d 66f729 38af08 1a014b 5518d0 deadf7 66706d 7811e1 b324fc b8fb88 134156 1d9da9 f6f48f cdd441 17f1af 301fec 030d3f ce84a6 7183fd 9948a5 831fc1 d66872 3de4d2 29bdc8 8221d4 4033e3 e61b8f e7096e 00acd9 4514a1 69e118 df4cb9 c91c02 e0ae6a 8de4cc 3f1088 550772 3202b3 83850e 84efdc 5a8142 f60882 e254a9 2cb52b 1dc741 67660d 379eff cef13d 33d52c d1a7d1 b8dfd5 b95f84 fb81f1 ee079a f5e8d1 4c9f83 10c370 1dc1c5 86fb7b 41784b 55831f 7ba802 fa5453 450141 9a7cd9 5ec117 61aaef adfa14 a8a60d c75c03 773037 1feacd f193bd ec9474 2e7c3b b8132f cc4632 dca4c1 830d4a 669d61 c426d4 2f9137 67cdca 99e64c 7de8be c90a8f 461efd d01008 bf8ac6 0515b2 04343f a7c990 61c9cf 34f58b 8ca1a2 51eb3e a62544 347ecb 628a33 c320ce 16df87 fa9a9c 8e04e8 c38fae 9c3df1 228b16 27016b efac4f 6fd312 504307 b0c6f7 4b5173 d3f837 965e6b f84a40 11e1fb e3840c fb990d c283b3 a8d1f4 b92d44 eb1d9b 3d2f25 8848aa dd3125 37e29a 91ca7b 6f641f 6398cd f9fd2a c09a13 8bb2d2 068e13 0ed3e4 276404 2a77d4 cb6aae 42547a 69183e effb7c e51d52 cf2cc0 8713fa 939626 5055f4 52ac4b b29cbe 25a301 567a6e 225272 1081b1 f9849e 5fbce5 34e5f3 c5f974 e088fb 04ef4b faa48c 0de03a ce579e 8afe8f afa3d5 3fc8c1 cdf872 f79d0e efc0fb 5130d3 995981 7f5cd4 5c4d74 56db93 c3c36c a551d2 4cd83c b0b142 6d4409 1e9ef2 3bfe45 7e9e42 fb60a4 bda058 d6fbd9 9436e3 413f83 5030c7 c877fe 602159 822f22 89e606 bc960a bcdfdd fe6c6f 3a5ff8 1d234b 7a66b5 84cb5a 682cbe ce04a3 aa785a 972ab5 0049bc a14161 557de7 158921 250e0d 8ee2e5 4c0239 b949e4 1a08eb b9f5cd e9d1ce c6791d f88bdf 7aa91f e7b6bc 759b32 60949d 405d43 e4fbcd feff3d 6d4dd1 71dee2 b91520 9016a8 fc098e 937299 eb6dd3 f69e49 8256ca 580722 c0c255 ef7e7e bb4a1e 49ee50 38330d 87641f c74fdf d6261d 8952a5 ad7c16 9e11e3 d239d8 81356b 52e648 12c015 8da857 98fc97 ff1b84 275859 d5af7b 3c3bec 21ae1f 2360c5 0fe8d5 cee836 67b499 3bbc9c bfa5c6 f45469 e48219 ddecac fb761c d9bd5b efb25f d01911 ba24e7 b3444b 1e5615 0d4fcc ff2d24 04c33f d12bf5 b4e9a6 e99ec8 4dcf3b ca758d 6e9b36 de5e55 795ab4 96670c 286042 e2a167 5472ae 1718d4 3b6e28 5a163a 9863ed 238190 f94f64 2bdbf0 d2d6fd bb7693 17317d 28a11b 8b1f31 dc817e b01df2 df9735 10d33a 2dd6ae 330a35 bd46b6 159f73 b6f104 bf8b9b f14519 bef616 b1a207 a32c46 d64b2a 879089 4287fd b9c04a 9dbe21 763038 fd20d6 ba279b ee812c 56984f 5bd1fc 3c2c92 7fbf9a a27166 5110c8 1bd6b7 1e823a d64103 8df0c7 bcf98f 89ebb2 e713a5 9da15d 8ae9f0 6b2991 fdf1bc 645b61 bd41e0 754796 463ff3 123273 798275 ff10f4 41eaa6 096571 4fc001 86f838 ed8f13 4d85c7 dad837 c8c41f 3a47fe 4159eb 539b4c c9b3b3 a3479a 2afd02 1d83fe f56f61 d14d7f dccfcf b835f9 b4f834 d41c37 e0788d 1219a2 ee5be5 628eb6 8df63b 4d2cf7 afdda9 017b44 fedc85 066e65 a8fd7a 9b6175 dfbb2a 40c7b9 c22748 73aa8c d0a2d8 a0215b 47d069 452870 1a2720 81729a e51d90 d7e81a a783d4 f7938f f161e3 23ee82 265480 13c51c 922071 f04464 ae865d 0045d0 47fad3 18d1c8 079005 e8bcb9 4a2e7f 4f9538 3b37a5 4808c1 813549 306613 f9e8b3 7b9d6b dd97f9 617688 d9c945 a69ce2 6f0cde e88907 7bfc2a 668527 19f37b 1c7999 c0c784 45c17b 3205d0 50005e 04d79e b1ce2a d74051 3b915d 187da9 6ac316 2712ac 1a4019 301b50 a38055 54d0ef f52c49 8c95bc d6b66d 1d721d 9718f0 2adbf8 cc55f2 42e399 fd94eb 5c2c75 e52cc4 e8657d f87f81 6955d1 8707c7 61b353 59112e b9f8fe 496cbe f80608 7adb80 84a767 e09911 d98347 b2bb21 b2806a a896cb 3ea7fd 431d1d 885bbc 207b28 dee664 fa95a7 e987fb 7fb146 10f49a a16597 0ddb02 f8e914 7b9816 597fdf 83c8fd 5eb13d 478a75 bed9f2 559228 02d3e9 7eeeef 49f1b3 2fba38 2ccf82 37e0d7 d682fb 5b4ac1 09d76e f7ee86 5b0bb7 98ddcd 60bbbd 81adfe 8f2052 5628d1 bd30b3 696de1 d2ca4b c2e5a9 f2bdcf 2cccf5 ffd809 cce316 c400e4 aa1adc 4c05a7 5ddc5b c235fd aa940c 8f5396 f2389b 12ed6a 57f51c 85da45 b046a3 8d1c6f da2ac7 3d08e4 713e18 941f40 d5de09 a28a67 58cd33 2db0d1 30a25b 9383cd fa330e 4ffcf3 12e21b cd5e52 3c8b17 a76913 d58851 81b510 843552 a733eb 4cedbb 65aaf2 478a75 d5f742 c5d6e8 c54f1e fdc106 482574 9ff2be e19617 5d8452 04ae0b 908386 909c8c 536c10 bc48bc 00a27c 33836e c86aae b99b2e 86beac d699ff 28e046 92596b e8e803 ea6b32 ff7859 3e3b73 3768b1 a019da 9e72b6 91d955 68ca8b a8f2a9 3223a4 afbafd 1f94cf 42c6da 3e1d7a 697d6e dc7fa4 629fe4 858d1c 479e3f 0fa9f9 28a3e7 59a8b3 e879f1 bd6ff5 f2d40c 45ce04 3ecc08 8441ed 927e7e 9ddaee 9f0cea f86ab2 6f60fa 0e35dc d22f86 55eaf8 b2d91f cea2b9 7978f8 eb389b aee969 ba4729 86fdfe 5df76f dfdeec 1873c1 2a0a35 230b51 3f147d eff129 f766cc 0b5622 ac915b 7d6ec3 4a7f25 49da33 0e9629 85d83c 7da545 ab2e85 e2c556 51edbc d90060 d4d1d8 94a5fe d63cca 2789b0 0a6ee9 5e6607 b7c01d d267f4 f98d2e be2aca 6ca841 3cdf70 6432a9 e22534 4c5a82 7f3416 286554 e06917 e3a1ff 3ec6a0 b3b0bc 677940 55d987 720e00 33cda8 f80c83 719fad 23dc96 e32d94 7f083d 1330c6 141be4 271d0a b25f83 7f7df8 1e7515 42f78a 2ed751 374f21 bd346b 9dc587 1163f8 b61c18 8dd031 abce4b 4bb329 9812c2 7e22e3 24b011 6f8ca4 20ee89 e154cd e4cc83 79b8c0 271b5f ba48be fd927e a0fb83 446f6b 6a02a7 eb9d4b 81e4ef 64c931 2855cd 67b5b9 d217de e3b5fa e8b39a ccacfe e7fe30 de22f9 bedd71 2c57ec a80cbb a6d46d fa9af2 d967fb 657ca8 87bcbc 529460 ba5f90 4c883b aac74a 5e2578 fd51c1 21d9f2 f8d365 3defb8 9d1d3f 53804a dc28de 1e9a3e baeca1 1de202 526fc5 d075de d43557 34df85 d6d289 fda85e 5a354d bbe435 725600 341c72 bb8fc8 c70d97 9d7608 fc894f 03f268 9b67c6 914210 3ec357 f21d39 1879b1 57807b ad440e 49cb14 a4cb67 2cec0c 861de6 6467c5 895997 1f772c e912e1 e7ae20 04bf4d b83168 1f172d 8ff3d6 76d806 d71bd1 fe8cae f31369 590915 4c3387 170f37 8de0cb f6f227 bd9ad6 943df8 ca2e63 495312 8345dd b0b52a 5b40b9 a04b28 717a6e e73167 32d128 d1f237 78714d d994f6 404af0 121b8a 12c409 cd4b93 228408 651543 3872fe 28461d 8eae76 321a74 216e92 3aafa4 5a4f08 c78ae1 d1911c 67bbb7 ecf253 2700f3 732761 621737 a2e859 6fc10d d55ea1 12d267 430a02 8ed7ed 545502 b5d424 487901 8c78ae e2b29a 56b5f3 cdf19c 561737 61a192 58ee0e faacd0 e95933 bfceb7 a57b48 e4c203 3c65ac c86872 eef321 4cc458 757fd4 e2ecd2 06bfc3 c2b740 7355d2 1a530d a5d57d bb8eea a723e7 659bc5 1cd46c 1467f6 766958 ff3eb8 34fe60 fda8a9 720349 626eec 848cc6 352965 dc4af5 52965b 37bd38 c674f6 89b11c 48adc2 831404 91f87f b17ce9 9fe32a c073c2 29fac3 ff5abf b61e20 22df38 0ecbe1 3c5dd9 ba399c 246922 484170 c9a10f a22a45 050903 9f11bf d4bfbd bec6a4 6d542d 32cb99 95ae14 843210 21e2e6 993231 e055f4 b9a2fd 135b34 d87f08 104eb4 ee2e89 cb18a0 b10a23 a9fd7c 391441 498cfd 494645 67cedd 3ae619 3a3dd9 7600cd 094bd7 f1359b 397c1d 594677 13578b 86d2e4 bd0da7 bb3f0e 5714a9 06bcf4 ea54e1 ef0e5b c47c74 e0b4a0 8bd4e9 82234c 7181d4 3cffdc 6b6063 f12713 e2ec2f bbbc3c a4fc54 523d1c bf801b cf81c0 2e6d0f 67a5e9 7b217f 40284e fca1b7 86a582 74ed69 c31404 e7bca8 5169a0 eb3410 2ccf77 c3902d 4a29e2 cd5e3e 0e429b 5c1006 309f9c 3c43a4 25d5d3 ce4948 126ba2 7392fa 42ffef ea5934 ff9c36 20ae92 3cee37 69b92a d5c80b 2e00dc 59ca7f 4ca8ab cbc43c 4caae5 a12542 c1f458 98af66 f4d51c 86fdcb 91fa96 e274a6 871b72 a49a29 f1b819 714138 30b141 3b8425 d40531 add3d1 66faa0 f2aa49 10b55e e8ace6 d23911 9e9660 c4a894 38e24c 584f12 b6cfb8 c9d1ed 0e46a2 42e43d 452e42 1ff6c1 465fed f0404e 154961 8df9f1 6fa22f 58359e 305c70 71bf52 bbd2be 49b52e 5607b5 129ecc 3e2acc 4575f7 1f7cc4 beb0e5 45df95 8c6a8a 47fdfa 5d2eac 900475 14e3c1 57b1a4 d73507 2feadf 484928 3e0cb0 d23b6a a3b70d ff5fc0 90d335 d00946 1380bf 736920 d9309f 637537 0058d4 4cc844 af962b 8d2289 624001 c67550 dbcc7e 4f545a d78bb8 5569dd 3e8b09 bbb92c 465a1b 5765b9 c43270 328cf4 6d2e67 8a4da8 c271f8 11c05d 56ba02 ef59bf 2a3d2d 14de71 7cdd01 a97330 07374d be8231 0e50b7 2a3e0a 01f709 07da39 514129 df7190 b64d6e ceb119 d9189c 92bd37 9a9961 b22b44 45c59f 7e34c2 6d759a 04ce47 375f2c ea7dd3 d2cd8a 9a3a4a 74e3db 23e90d 12b35c 48c077 2d3ac2 3b9791 8259e6 9d4eeb a70338 929558 45d5a9 1c4ab1 10d778 b3383f c4879f c19016 e23803 1983c8 475c8e a4018a f9bf2a 08f111 73e9d2 0af24e d3e510 c94fca 82e9d4 aef994 1c056c ec8a3a 956054 286d45 59663f 3a9b44 b16727 cb9ddd bc0fdc 60d5a3 11f8d1 c4357b 38de65 449b71 5c041d eabd5f 59f341 539d96 a7e36c 542dfc 479d5a 0643a7 b14ca6 ce49bb b8a48b e22fdb 4e1e51 737f0c 472efe b43f02 0ef169 9c8c8f 777685 9356af 08d4b4 e65636 d4d1d4 0d78ac 1dba66 7f7e57 bcf855 e3f607 93ffc0 737ce3 1fcc34 91d84f f2ca21 c43e27 410390 3073e8 e2dc81 5e8c04 988259 196b65 8b0548 545e93 a9b97d 33b15e 85540e deefd0 fc57c6 8dbfad 5c5bf4 d29913 aa3f5b 502f3e 538da4 3011ed fea20a 517bc5 67416e 9bf5be 51a369 4161fa 99bc67 7865ed a842b6 cc1de2 77c8ea 3d259e dbc5c1 7d2b01 f03294 39612b 39a3f4 efcf05 45b7c4 abfc9d d1dbb3 c1588f 85efb2 a6ff5a 067b46 5dc22f 155456 974813 d71bfa bb793d b1ad21 043346 96eb9e 090d0c b72495 bfa9d2 bc0a32 10e7b4 be7297 29fd99 e6516c 3029e3 24ae22 80d355 48e1d4 289f8b 4d4de4 5273eb 1b7d20 04bbbb 59cce1 8ef562 605e3c bbe0a1 ced69b 444a07 00ad3f 41f741 d4693a 9c6ad6 dbaca5 26c117 6429bf 84d26a 95c296 ecc50f 2913a3 9e02f9 9df062 e85d80 f15438 33d317 44bc54 d12de3 d8bf99 4d05ef e8f00d acdcda 1032f3 a065cc 341b34 eafa2c d8aef6 abd81d f5cd0f 85e4e6 acf8ae e4cf5a 21a696 3a0eaa 90bfdc e0b456 e67e10 1f5152 a12366 1d415c 4187ea 80ea09 0ee57a bf1451 bc0204 d51d30 6c1bf7 96873b 6abfbe a95240 6ff39a 066408 2f770f 6d93a1 c4ce53 65265c 219f34 81abba 05840f 8d9d94 245bd2 84d1c1 fbb69f 6bfcca cfed4b bcc268 6d41b0 090edb d17be7 642534 8c1509 995558 b5624b 29a6f6 18e954 03ad73 2b24ad 414a2a 698f48 c437df d81eea 170e0f 5c1888 e41fa1 ade205 1c833e 9c90e3 eae05b 6a5368 e71be7 7fde48 42234f 5425d7 76b2f9 e0d47a 4f1527 9a17f8 25e947 24beb3 9f23ab 53ae82 fbabe0 b507d3 f3aa92 770435 1f71a9 ce2485 dfeeeb 631b93 104b6d b70065 a4e43d 339f6b 86ada3 331d3b c0c127 04c114 201f3f 1dc8f3 17e8a6 8b3895 e80800 f00ab3 b1ede7 34a667 9064c2 620500 d34784 d59189 5ec10e 719cd8 4b2b62 27a3f9 a11e60 1d93bd f23ffe 19a91c d844f0 159cd9 9f545e 2d1281 772b35 2411ba 96a87d 653e02 226e7e 4747e0 f4718a 74bf75 bc7ee5 28c61e d351a6 0cd5f8 c0a6a2 34b68b cf9af9 f34a70 aca05a ee12ff 2901ae 86d7a8 4e6f86 c18a0e d62810 2c8d28 946625 0ddb0f 077716 0dd994 c4a54b fdf11a 5d7226 f47e84 b77127 cc634d 1ad47e 1f0ce9 c9971f 6a0800 2869ba db508a 13d52d e6bd4c ebd392 82d97b 76a863 fd58a2 86a11d 0e52eb f9d47e e1a132 3ea7cc 0b6111 8f55bc a1fa41 c5312b 2550de d68be0 2581e3 5248ff f851e1 ffab8a a15342 23c9ce f9687a 22a12a 3bcebe e52ad5 bd7c16 f19952 f7baf1 70f1c3 131fd6 891748 fe9fff fa8f99 61a5ca 8dbe45 1c0de6 b667ab eac5f2 aa728c ef12da 1a465a 527cdf 2f6542 99daf0 7ce816 4fd559 335510 5d2078 f7b381 23e008 067c3a 871237 b996bc 4a0caa 5e4ae4 a58d44 80b985 0b2906 4ed41e 1899a2 935610 5adc65 792ded d50639 30cbda 36d95a 5c1418 34637d fa8d2b 3387d4 dc6aa5 9cd1d7 b7596e 14411f 1a2bf5 70b9aa a10272 483379 35138f f7c2c4 aa9c7a 82ed62 f7aaef 39edad 897f4e b47cdd 72bff0 3d6984 05c0b3 b69b58 5af2ca 5cc522 78e1aa 2cf87a 016b5d d5e1cb 7737e4 2c9df5 38e80d d937a4 23cc13 5f1bb6 cf9b3b c027ac ce4224 460786 8af6be 7a6956 4afedf 3283c0 2b3e6d b4c29a e3d72b 51c84e 9bb0df 17bd74 033613 c296f8 2fbae7 a5a5b6 08a8af 08a487 35b29d 704767 e26f09 1d2c9e 6b9123 def681 92c7bc f7c3d4 53a14a 0008a5 f659f3 8474be 27a533 b41c44 439516 e0193f 3045df 262292 776d64 9f76e3 968d5b b8b802 cf7ec3 2de620 6d2e0c 260788 4547aa a5da65 97565d a98ed8 be6253 67c8e7 5927c3 52f4ee 75a3b6 fd4ec4 25b025 2b4b1a c9c25a ee2fd6 4d04ee 905a0a 23d7e8 788ce1 3b1c85 9ab169 23e660 eeacb5 1d92f5 458200 c21cb8 37f420 c62570 8b1159 ad8ca4 e44fba aabfba be4662 8e6c95 fc6c43 4d073d 8195a4 b08f32 d98be8 c4af73 eb0e9d 850c8f 829c3f 03f7aa 849075 ea948d 26c028 f20796 6bdb0a 2d1a37 6797ba 1f8fda c03077 e3ee65 b1084e ad2207 6558ca ffe666 004b43 8a40b2 f9fda2 8d51cb 6db748 5e0623 d89ef3 a525a8 7fabc9 782750 09517a fbcca2 b1537d e2b3ce be382b cc7914 82eb35 eefee2 0bd458 dcbdda 43b746 92c50b 5f720b 44f759 c5901b 63c4e9 43a376 005834 301a08 103d9a 2b60ef 0f6f0d 323c96 aef71b 9ae380 7d28cc 5ad0da 8b3f68 167f0c 0fa1b6 e4522d eae101 126095 3ec7b8 4e14ff 3c8477 c3d6b8 d205b8 49c944 09cefe d87251 8d11da 14755e a618b1 2cd5d1 b0f8d2 eb2bd2 5c3036 d56a4f 6eb676 9dc89a f46778 1e54b8 e56b1a 69955d e319dc 8648a7 5b0fe0 aa6003 0fde16 d5b3e1 3ac5fa 385d81 07ba5d d5e5b0 8c1b46 b931fd 30774d cf30b1 794f98 6a2ef6 12d0a5 f6132f e45f42 bf0799 539c46 b37225 447ef5 3d6c18 71b5b5 feb0d0 eec8af dcaed6 60ab11 7663fa 40da63 7c01b1 e71d6a 71c0f9 25a63b ded66f 253dc0 bb1035 28eadd 5d3968 997012 352df1 b59d1c c1fd9a de6930 c59158 cad73b 39fa64 a55f06 c9095f fa8752 ae89ee 19730b ca14a6 eb7d23 30be8c 89a970 1b981a 196bb8 3ec696 c609a7 600ffe 31da3d 34c268 4090ad 3d558d 312cbc ae5261 c70d77 38950b dc458f dfe88d f62a75 f10add ae878d 918c5f df4e43 957810 68e38a fe3627 014ddd ee4927 58264f ab04f8 875370 3f4945 434b7b 46cf5d fcc8af fa39e9 0957d9 bfb376 cfe19b 6f6467 093501 9eb6e4 00f3f5 79372d f732ea a0b575 49bba0 3b441f ea9cfc 7d217c db287f f9d76b 56f08c ef3ac6 804e80 7a8e4f 90b83d 8209be b037fa e0bee2 ba5ba7 323764 5e6179 d35336 941698 d0e768 bb6b14 93be65 1ffa12 e2d502 bb233f b90ef3 afa234 571288 6c6a0a 9dae28 7b17cd 86f869 cbf27b 388676 9b32e1 a24420 58f195 da84f5 42ef27 de4e4b 49aa53 7bb937 32fd96 1a5e64 07062d 3023f8 923d77 2d2786 5a83d9 19c4b6 27eec8 9723e8 f7549e 36dc91 761616 615e6b 8deaa0 db52a6 5fe7bf dc17a1 2149c6 5d4141 8b8574 99f592 21d363 336908 9fcdaf 03b92b 59fb58 327873 97f995 937028 29cb5c d75ce7 ec42a6 e25cea 959ac1 f8a828 57406e 4d5505 82bbc3 0e070e 91e70d 491813 d53f23 5054ae ca799a 90d7ca 36d461 676c2b ef7d72 b5a615 232e63 172fec f71a57 7fcf6b a1c927 31f3ee a60d1b 957198 7b5d6f 28aa03 cf9790 fe4b51 892c31 39f3e4 6e6599 c78875 e81e10 aabe09 bca123 b4d988 4d858f dbf819 538803 0b930e ea225a 607593 757828 dc04fc 65a136 d7e90c d9984f 17a1c6 855fa0 a06160 bc589d ef429a 4af45e 4fd2f0 8f64d5 abce68 ab96ac 65d457 6bf09a cb17bd ad6ea3 c812dd 4b6600 1a2f8b 93b9d6 89c455 a50b1d 1db9c9 4b14f6 e8f17b 0a64fa 927af2 12796b b00240 b557d5 c7b4d7 9696c7 90fe8f 5ba1be 6075f7 dbe15f 1bb0b5 57ee6f 5426da 43ef9b d52bcc 7ea1bb 00e5cc d52993 c67c05 036031 b08dcb dcd740 6a5a58 a2d9e3 220dee 2501d0 621631 e01466 d76d81 4a270d 6ffd77 78cadc a14a47 9d577e 38026c 94bbaa f08120 a381c5 96a701 3d8cc9 66ad70 171b75 b0a76e 08448f 286be2 1932e7 ee9f3e 34db62 da4b88 c83ff7 ab1027 80b1f9 ec44dc dbfcf6 25d79a 5cc1f1 cd18ef 72ab74 736683 5c1815 e4ac05 acdf2f 8ba3eb 08373b a787a5 a614f2 ef7d7a d1a150 9df18c a4391c e6de6d 7df8e8 6d1b47 ca7e2f f0e78c f87a85 9d62e0 31648d cd69f2 e2b0ad 251cc1 6ad6e0 2e2b72 6b8033 79b321 e2318c fda0b7 060ce9 0a04a8 b94514 e58d19 4e34b1 4ff391 a9bf11 711a64 33617a 5c17a3 c77765 677503 c94c44 77c45b 55ca46 d8b36c 1e0e01 9e25ef 8f76fa ca093e 1b6309 6c3136 7b8a0e 552383 a755ad f450c0 97a2f4 ab7ed6 b39a14 8c43b5 a3b56f 21b079 ebe354 5f019c c126ee 15364a 2456d3 ea6bca a8590c 63358f 4cc1cc b4e798 a4acde 3a1f89 63c6ed 68c20b f37762 0ea777 6a9c3b 1e4938 9e2105 a4d103 f323c8 56a785 dababf 84e81b 5f3be2 70f89b 6617c8 cf37f7 ea5d4a 10c373 a6f581 cffbf7 7d1f9f fa97d5 43e5da d32b3e 16e148 a628ac ab6943 07c18d 48ba9f f62e1f fd6bdd c2e60b bb6b22 da2ea4 5a10fe 14b044 a89f42 2725c2 957c55 d2712c ba1550 8dfc79 a8b509 a27acf eae418 824430 4b6a8e 96eace 7be1b1 5aab3e 2aa33c 62ab45 cadec5 171746 9cb307 ee894a 979411 49c140 a5e174 14e8cd e0cdc2 fa900d e12e44 3ebd48 0e736d e7d769 4d892f 7c24a5 bff52f 8b62ee 854fa2 73bd1a 0e7af0 3418a7 d42b70 18f333 925d80 f47760 733fd2 6a22eb 8ad938 39e2b4 3e045d 4a8f63 12721b 374ded 4229d7 0371d4 ac5893 23ac6c 42a112 dc63a3 cf1310 1f53ed 973259 bc37ae 11fb7f 4c79a3 275555 4a0e48 43af56 7151b9 91b70b d2eb04 59e19e 8be751 9b0e6f 090a59 1441b4 ee868c 07a05b bd3c1c 29f242 2b4bc8 bed465 84424f 07baaf 17759f f2f086 7f6b94 0d6e8f 7c951c cf3953 bcbe54 42ad41 bf29ce dc3586 2d003b a9b651 555444 df07f1 8bd4b0 254968 cfd1cc f7fe0a 48e5bf e67294 87f362 996d36 8ff92e a0f9c2 be544b 9df371 eb1dd8 43797b 33dbd5 3e4e35 e965d6 1fa4af 0e498d 92f705 939dce 366729 a106a2 3058c2 f83b37 4b5e6f 7f33a1 fc99db 43a036 5dc3e5 75a06a fc9eaf f1d4c1 2f77ff 2b1a58 5a7ef2 c1cdae a7f756 2fc806 1e8206 057a49 def51d 77ef57 bbf4f5 a6435a 6ca6fd 5fb7f0 f6028e cc6e52 4892c0 c73e25 292b2b f43e2f 0a4847 8bd987 c33b06 36edec c07829 fa9d49 7dac34 136149 9eb2d4 86a7cb 07709c 224e3a 743606 26465d 6512ba 4c555d 19a0a4 0517b1 68e1e7 3f3e5b 4f1076 3204a8 042292 380d63 c3269a 551603 bf0d55 b2f6d8 bf80f0 06a39a 453046 b3bf35 f4a8fe 9f61f8 46461e 9b661c 54521b 661018 8d3980 95a8c3 873093 4762a5 b0b3f6 7cd25e 1a7347 ba7cd3 e0a2c2 e7bb94 b50ca1 8ca827 a9008d 7525b5 7c6167 e3bb7c 00f6d9 1e3b5f 0a6dee 500a7a b53990 521faf d11cda 5c7292 a80f51 80d3c1 bd11e8 592038 012797 9053cf 127c39 bd1318 ffe728 5cb8a6 31331c ff1933 08e49a 067a24 fb5bd9 60207e 872752 b2489f 7eece0 083919 86e390 4d9830 6f65bc f9138a 91cc72 973909 0fbee4 f309f4 2da4b5 f018b0 783ea7 b8b26a baf258 ccf98a b04275 b7e808 4199d1 13dc80 d864d5 817fbb 80b991 84e5d8 0d50d7 fa7bb6 a44c4f ef100c 0dd260 e85195 c1490f 9dc648 a7b905 df6531 c81a2e 643472 68b514 21bfcb 19f457 2654c0 63d88b fbeaea b9f186 c92175 132828 4db993 7b6dcb 979d9f 8c0d81 78a959 d6e48f b7dba4 5de8ae 71aced 860f30 3af240 62d517 a4a329 88bf56 8d9c6b 2786a2 ad3af2 6bddfe 71bcf6 409f06 cfd084 2bc95d 93e54a beccff db2101 f94aa4 43abd5 8a3cf4 6f1182 19c51f 9e2f50 2cf0b2 fef0ad a0e4e5 2866ec d85453 a2463c 74b026 a35dd3 d78104 640220 b93668 c8b68f f9a1af 64c9b4 e9c05a 816c91 8ce64f 576a73 e76481 d19fde 737a24 5ce8fc aa6e0b 219cd0 0e850e fbb9e1 b2c5a9 de901b cf06f1 4cbe4e c7a247 43d50e 6a1c3f 69714e 64a272 2f84ae 728168 fe3ef2 130ffc 20c047 f827c5 43fce4 b9aa30 85749a ab9223 059306 aff8e2 622596 baa636 c5f624 ccf468 4b0336 7ed6e3 3ebc86 aefee2 d13b5d c17bc7 fce92e 8a7863 67113c 5c8a26 18ad6d bbb506 fafd10 3420e4 23edf6 f54a21 13b09a 817517 56f674 29719e 28ade1 ef5638 47734b 423db0 26e80c 81cbc1 43620a 01a954 d92dca 50c7e1 e77f06 3063c7 59369d 1e679c b7d1a6 f5b54f 8f1fb7 ea6d73 6d0a06 b1e37d 75b63d e856b4 6e620b 883480 f9a655 98a721 2ce3aa 25bd04 761e6b d5c176 e71e2d dde7fa 6b040c 31a9db 69299a 925e05 c1aae9 b20cbe 302705 10aa7c 069df3 8cbdca 3aac4b b82ef9 27fc5b c6c441 3e432d 95d4c3 7578dd 286b81 99b90e b92e50 a4e0e8 f95b0d 566016 67abfe b34d3d 5c8531 c8cfee 696875 09eaa0 0d71c9 abe2cf 501c83 0216db 4fd193 4ad42b f7e5b6 092516 cd6945 928f55 ee9246 4e5af7 75001c b39679 a6ce82 995900 2ee8e7 99f2cf 2fa3fa 5e6071 7e6049 3d7def 44ac4f df46b4 c8f7b1 0b2f39 5cb8e5 aae082 9bce3c f642ed 77c9a6 b1e019 cc0447 e71282 77c6d6 1fb948 7c8ab0 e4ebba 5bcf06 8d636d c474cf d11cee e1ce87 9511b8 16fb25 8da2d1 14e8dd 95227c f5ff09 8287f7 5dd0ef 92f78c a68d93 290214 1d7ce2 a80d2c d64ac6 ca23db ae5f82 ab7535 cbd3ca ce448b 957c0f 5fa775 14f0eb e74356 2bcdd8 10ec3f b44d20 d0141f 3319ee e6a734 b59949 599666 3d3889 21440b 525990 bd48f6 7c6db8 99e63d 3da17f 43ec28 c71fa2 66a376 7e7803 ca3189 cee203 e76247 84ca8f 82055b 3cc9fe 70cecd 100271 e26211 7657f7 04d00f 2f2661 4245db 67d6be 929274 d948e8 746101 cd6e7f 39dabd 7b6059 ba3845 f6db94 732a32 21fa0b 845796 ab85a0 89aef8 d39475 86ca75 5742d3 04c77b 245b68 948edf 299e6d ad2914 56e2f6 3b82f0 541c96 3908dc e2d483 a4521f 1d75aa 384537 c0bceb 2f3266 739b31 1c4144 94d55a f69aec 3742f5 7f87d3 2454df da95cc 41bc65 019dd0 4c3a36 f8756a 5600b4 c665ff da2e1b ccd5df ee1389 b5c1ee 9f2763 e3a8b1 f9b258 17f0c3 3b64b5 572e1b e0a4f6 cc71b8 debd18 de599d d1ea2d f83027 2de2cc f7769e b071a1 aa556f 59558b 845159 ab9736 9d4256 8fc234 39addb b81efe 4be8b6 102a29 bd7006 c57cf2 40ad3b 9ed262 e329f3 9b4e6c a0f78b b3d492 f8444c d04cf0 a8a31a 7a8438 03a27e 8bd8eb 53bb36 3ce38e f929af 483087 becceb 84d193 76052f 60fbb6 25d420 ac8a7a bd8368 ff3ea6 5d6f12 212cf9 1a83e4 8321b0 cb2c92 b2c21e 92ae09 6774f8 e0c2f1 7eba5c 88e833 87555a 09a5c0 4a4cd4 a6f0a5 b23f10 4bae51 0c83a8 4f9440 20ad3d a2156c 2eb50a 7469ec bc05e3 a5042e 6be16f 72272b 3d3b59 e643b8 6cc70c d3056e 3716ea 6993ba 5087c2 351472 ff6c52 0b493c 9693c6 a9a9db 2ece30 c9eded 114cca c2d731 774472 39227e f1ac92 88b340 516e26 c7b9ce 81d70c bef609 79e0fa 12571b 5dd974 285626 c86ceb 6ee46e 491826 122d11 b322b2 2b78f0 ba6f82 d5433d d34559 cbb4fd 6909ba d6e6af 04a7bc 58db68 2c6a4d 9348ae 2b91eb 088835 5b9bab ff2728 cafed1 b64b4f 523666 dec419 e8c311 12f685 d52770 05c04c 5e1caa 6637a9 2df24d 41e08a f422e0 174af1 4cd94e b36bf8 1a1610 739450 992601 9dc365 6089ab 2aeeb6 ec9623 595bba dab72b 2be9bf a16705 d23ebb f7500c e7e5ef 27eac6 dee58c b14ba8 f2a471 32e49f 54f921 407db0 8991c8 56e951 04e2d6 7a5e2b 48b4c3 69758e f762af b5a0dc b08c6c 541271 0dda79 9a8f8f cfb4ae fe153f ba1a87 326fb8 b42188 bba078 f0f1e4 243a13 bdf45d b5b1f9 a387c0 c04627 5a051f cbf570 77e1d7 e9c202 4a6ddc 72078f 9d826f a4c414 d9dbe4 a374da 722777 cdd20f f6ae7f 702716 c04ced f49189 f23daf 67e854 f85db4 69dc6f 6c912a db6f37 6cbef8 4eaae4 dabcae 8719ba 0f6957 bb199b 1e6ab2 e59bb9 aac6fb e17f63 b189c4 56946d 358e43 545308 6ba95a 3bed26 a22918 bdb4a9 0ff81a 8e36f9 1fdb23 d1dec8 1a3c4e 7e6ffe 036641 f2afec 6f8c0f 632e7d 76fea9 30a91b 3b0af0 a1be0d c047b5 dd08a8 9aa97f ee1997 5a8406 cbcd60 708b7a 587eac 0b344f 6a203c 572940 e07164 f1d302 135622 89bcce 3ed4ae ad30cb e45eeb 4110f7 29410e 765a3c 37e88e b41cdc 10ebb5 5916de ec1a54 bf54ad 42f6e6 fbf235 e7d6e8 3987f8 6a62e3 163628 2a7f03 771f85 bf3cb3 dada95 9adb09 603689 11bfe3 0e6830 653e14 35ba50 e8751f 8a8962 e4070a 91f0ca ade5f4 b98356 568a2b e0831e 370b80 f05c2c 7094ad b08022 53272b 168413 0fa1ed ec61da 21ce1a 09fa83 ad0105 658567 6fbbb2 6ecf73 6795a8 c43c28 4099a3 7f3f22 119cca c3414d 2629ef fa8e32 37faab 809006 6cce1d 809e86 75df17 b99850 d9c68d ec4b5c b77bf8 162c14 49493e f6792b 2d6b92 d3ee78 7a5f7b f2813c 3235af fd0454 dc94ef 3ed7f5 4f50d6 81ed9e 65f87a 0c504c 7707ef af47a2 b1d7e8 157099 01eaf1 418d98 47330c f9e1cc 53c4ee c7fb66 5f11dd 3bef09 1e7b77 ec851f bff8ea e4b42f 1afa06 440ee6 b89702 325174 b70263 9ad2f2 44d9b0 df87f9 91f89d 747492 cfe381 b00940 142b57 413daa 1d2f9f 05eb51 28bfe8 35bd11 45b701 a2dcbf 992e7c a8dcbb e26d5c 9f1195 b88764 f488f3 3317c9 c224d1 c251da fcb3ed f9036b 8e8903 40731b 1cd6c9 6237fa a06e68 d055a3 8f8745 48d49f 9364f3 86df06 a21a50 505021 75a063 e5cfa1 6e335b 49ee64 fad957 e715ee b88fbd aa8dc1 4e735a 102052 8e640b 14dcd6 ce5c4d 771030 0d8d07 1ea9a8 1f5c88 755451 d2a743 58642d bced7b b41e7c c31688 df38c5 d8443c c0baf3 d66830 94ac69 1dbcb2 ad90f5 087ae4 9e1135 c9a73b 706785 a866a9 40aa1d 6c77cd 7bdb57 206101 9dbe7c d51cae 02f117 cf562c 3434a8 ade749 f523ab d93d8e 8d4bde c3435b 5402eb 664c72 9e35be 61c5ca 163876 40b667 07147d a822e1 468422 2aecbb ad59c5 ef3509 004266 bd4f16 4b4774 6626e8 0f191a d39b28 bb0f00 142af1 5f9c3d d6131f 1659c0 95a1ed 31ff7d 6ca476 4a4dae daaff8 8fc6f6 66a8dd 914e7a 787f8d 6bed0b 704520 79f88f 822e8f
Level 1: 2052e3 9837ff d9444c 05e524 4297b0 975ac2 ee22ad 23810f 51d26e 9e3bb9 70384f fad847 58a2ea 90766c ade6e8 8d2b8a 1a2350 a83610 f49996 02736f 4d4b25 7871c0 a51151 856661 e6f0a3 3d4f12 b3b79d 0eafa5 0b343a 4cc78f cb62a9 b2fcc3 2f8c5f cbaa7f 442bfc 3acdbb d5002e 3d3687 5768ff f1ac8a 5098ae dd3c63 dba856 9fd814 df52d4 7f974d 4bb101 16f446 b8ae56 15c777 fbf84c 2844ab 41b56d e4f9f7 8e92b0 a3a62e c727b6 495c0b 90c79d bf4026 8622e9 b1760f 09acc9 83410f 896daa e44676 0269f9 efb4cd b2c954 59dfc8 808586 387c94 9c77a3 da4acc 8d18ce 4e6df4 3ac3ae df78e4 e463c7 8bcfc4 fc6df0 b32b90 d0b368 92e285 16f59d 888e53 685a32 44136e e25899 3cdfdd 11fe44 c942b6 4d7a84 c0f21f 51fdfa b3d536 cf0d68 b4a204 fec4da 1f111d 95d1e7 83a686 bf2807 490b78 c0627b fa3502 878c60 cad322 64bf82 bb9fcd a8f5b2 4e0f4c 57ef72 59bd5f 5152da d45d10 a40b1f 8bbcbb f4c59c 1d0f3d 3e9ce2 1b4d6b e19668 97d1f2 dcb29c 7ce388 472ea4 ac5624 228788 30e599 269575 eb976d b17717 890307 1e4f2b f60c37 c4b332 f8c3c0 d5ebc7 0a5145 991e9e 081052 608c2c 5295df 83b8cb 58b90a dff2cd 99601e 9e88f2 14229d 744168 a8a55b ec9c2b 4ee2bd 602135 0fc427 4451e1 450749 95211a 4922ad 8fd697 766de1 90cd0f 671c04 fc7e15 b450d1 2ec922 a35a99 9e4c92 25ed02 72f59f 487d17 b02d7e 4eedc0 8d3023 ff124e e30277 0e767b f511c7 c0a5ac 9536ad 4fa240 02454e 3e47c0 435402 a959e7 2f3e39 cc8ea7 fbfcec 87c38d 16c9e6 0384eb 69c3a6 724230 25585d 936767 dd8df7 71bced 656b0c a36790 4abc28 17cba7 c1ec50 2d5da4 d77809 d7032b 53fceb b441fb f4752c f9ba37 cc001e 465193 e1c2e9 e61845 361dcf 83ec89 c92d92 cb8645 9d6b2d 8be0fd cbc096 d47508 814e4b d7c1ba 2d5fce e2a7a6 646e81 bdbb0f b0cf3c 2eb047 755a60 8a7ec7 b8154e a11da2 aad406 e9cb5d 311974 7461be 8ef499 0580d9 b7be4e e90f21 6d4802 f2c620 a5a754 f3e300 9873de 1904be 37dc55 dc925b 07ef39 9ae0e4 80e061 f678b1 41b722 c1cf35 4dc610 1b67bd 36b6da 980fb1 a0ef7a 2bdeac 8b7441 a86108 6b9861 bc4b73 c78603 fb8963 dce046 7a3a9d 009b45 0f28f5 83b4bf fc4342 ed41df eb3de1 a80d79 edb9e7 47aa89 c2774a eeacfe fbf74c f1e8eb 798a53 47f4cc b551ef 2959b4 a7cdd1 29c931 6b0f78 7c4c2f 96a01e 200d57 29847e dbf71b 3a4830 6eeb4c 7ad00c 9561bb 925a99 35d1d0 ffc157 456a9a b9dc1b 2fcb1a b241b9 84ac1a f74382 2e9c08 c3916a 7a4803 94365f 1e66ec 706dd6 1ec3d4 073c8d 4c8221 cd9cf7 51866e 1c33dc 639165 3f8930 171a68 5b3a54 c9fb32 fdf72b a4e8fc dc8329 e1a69b 691ae0 ce4408 eeb75b a06544 d25e7f 359a96 726fcb f7e56b bb0c93 6b3350 2e22ee b3ecc8 b70d05 c09334 771cdd fe6a52 3328f9 2e9efe 968b3a bbd2f7 619538 f2a22e 205d2f a0db58 c6c8fb 6b22ed 102cc2 47c06e 75c6d8 20818f e747cd e61b98 60b623 c820ad 911432 e97ff7 d272e0 b144ab 771ad1 fdaee4 878339 953391 31d0de a52a0b a872b2 582b31 047eb5 edddb7 c64dab b8378d b3384a 484d7f d4b814 82ec56 3a42ec 21420f 11f9e7 a34068 0fd103 f2507f 2f6962 7cbf8b 4cc965 a311d5 3ced45 bc5f7b 35e132 6eb84c f69afc 2e8ea3 196f88 cf12dd 3f11b5 60601b e21d04 8f070c f488df eb0662 f79681 990c3c c57dda ec694f a57290 7d0598 89bc25 126597 30d340 22bed4 3e9004 594886 5f5edf 1e99db b04155 77a545 59ae49 f97fa8 a5b84d 53b887 b42c73 dded61 61f1ec 307244 119772 cc101a ffa1f6 4e95c8 376c8b ec7982 b873b0 7bf2e7 d504dd 8003c9 9cbdaa 79aa15 f1b843 17719e 29892c 0c114c 0a0f55 571681 686bc4 12e0a7 fda50a d615fe bc74d0 f217fc aa3255 d6f89b 959375 c57a60 0861b6 331ced a53d4b 8ed5bd c5b6e3 d205e4 1d1b7c c87534 415d17 936dab abe505 2420d2 6a1a1a d28dd3 f3c351 9e4c6e cbfa11 55ae9f 1d5ff4 c699f9 12720f 5df108 45c74b 4cdee0 69b62e 088910 9cf27a 9f4a2b 4b5eb4 fbf291 918f03 4db94d 8c4998 80a318 d67d7c c36f4c 284d5b 2f6333 8bc7ae a37629 496b80 7443be 829319 16ab32 6d2a08 ce0dc5 76563a 985bf1 73250c 43b860 8dc854 afffa2 2e2dd5 d60fc4 c221ae 33200f f0fbb3 9371a0 5cd95e 1257c0 d7958d 8ccb91 e5723a 2f623d 327a30 657e1a 1ebf2e 73a603 5da2b4 903ef2 4c69c2 cec89f d8b499 36c924 05aa7c 6ca9c0 fc363b af53ca 087024 f6bd5b cc2344 5a3036 dc01fb 17dc7c cac838 9bc01d 280a1f d6ec9f 1a07fa fd7882 d1e263 30121f edfa8d ce62a3 c04b26 daf3fb 47b38f 3a04bc 87fed9 0ff673 affbc8 a594af 51e503 e1e2e5 985a88 f358b9 74dd15 57bfc1 1ed813 8f9aa5 2d689c f833d1 39af93 118f8e 0512a0 4ee86d 547a8c 9dab23 4e5979 fe7c42 5a3a50 519105 3c6e7e 5c7921 e2e054 77977f 77f12c 83440f b8e414 d25eaf f04b59 e5206e 983108 259f39 1c6621 54ac3f 5d8dbe fc0e90 24165b dd36a8 c356ea 8bffd5 147d05 0b5af0 0a00ad 700c68 675b92 6cec66 dad7f2 0c08c1 5bea96 d5b3c8 4bb37c e37ab3 c6be83 7e8a9e 432343 1c7763 1bc083 438c94 ce593c 343957 7d0832 9a05bd b8d075 2fce12 66d2af ecf99b 0c6507 dd9ab9 9cf8a0 2b3b3a ba1f85 a2f64a 457b14 1b6b82 84f115 e8a57d 42f3db db4556 9d1d56 87664f c21f9e 017c1b 21cb20 f7081a 318f70 42c9ad 7f3e4a ed8835 a67e70 67360b 3a3321 f9c811 e213ba 1a945d 78b09e 509b4a c79d70 af7678 70a5ce a8f7e8 bc7a03 03382d 4b43c2 a03532 d40b8d 95298e 5bd03c c59e9d 0ea74b ef2792 4645a1 3d5d8f 59dda4 57a1fa c51bb7 7a5bb6 10335b 28777a d76e98 a9fe08 1a31ab 9c348e 020929 70118f d9b6c2 2ee97c 577b08 6f574a 4b5343 cab72b 3fbd24 c35b91 e1203a b56740 196c3f 62f90b f1a949 d0e10e 05eb70 60febe 2dc63d c5100b 5f2edd efccbe 224fd5 4bc792 6c64ca bc4a23 e95b56 1d992c 59542e fbcbd8 39d949 8afab0 63602e 25c2ed ec3bf3 e4f408 9cbd50 e2cacc d0dcac a07a76 88b17c 54569d 6be036 78a689 67bb6c a7d9e1 1e89e2 60fa68 afcea2 b4c89f 7be92f 9aed23 baf072 a6da78 3d4022 d8864b 8f9ad0 842b50 85e1e7 d68981 db1d45 34715c 6a2cde 7a05d5 186782 e02b33 4b78d2 17292f 5dff0a cdee29 eed704 985191 376348 8146b7 f6b4cf 6df3ef 91f9ca 92e76c 7926c3 14125e bdc0fa 8f39c5 0704de 8af7e6 0c2c01 b00c2d ca1949 821777 8a6fdd d85cc9 21f4d2 914cb4 a9198b a8c9c9 5b37d2 5f1667 fecc4a 8d41b5 018ad1 431ac4 439944 91bc43 018f85 86b7e1 2bcfee 22dc6f 63e198 ae3bab 872124 266a21 7e732a d465b6 0ee5a8 784e86 b63877 b98299 49ea0a 8b3801 0ded93 89dfcc 4672eb 1a9014 6f2616 5635cd 49258a f1696a 0cf753 815360 520323 a56e31 45eba5 ab071b 25e78f 985aab 8d2b49 384096 619b1c ae7082 1f81ee a0706b ad7fd2 2bc866 caa45e 861957 12028b 3fa62f b90578 1f83cb 82b926 781404 ad0dec afff09 d509f1 c524bf 64b5ca 3687c3 a9d556 b29131 645747 d979da d629cd 8b25c9 b2ad2e 331687 316929 8699f1 2f248a 3cccde 90cf08 761b52 22f572 850c0f eddd50 f4ce4e 058a9b fb5d20 75a50b a25c8c cf7f97 720651 f27ede 2e6e24 9ee92a 0f2af9 b9fdd8 c2289d a95017 5c9d36 b5c687 21384d a461ce ab27f4 a41737 ef2c94 c3f635 fa5173 317176 cba1d3 e9eba6 4a0568 56954c c8312b 8eaf5e 625026 cb565e 6bd1c8 f6034f 8198ad 313bf6 0b3361 7dfe5b de111b 7f026f 5033a0 89df3f 527352 629b86 2b0fdd c43dfe 7d0889 912865 bb8ee8 ae999b 5d011a a60687 8e970e 93a776 bc7b70 ad884b fe3ff8 e4c0ad 2200e0 d1b5ad 23a3be 003244 e228fe 7fc285 bf05e0 fae0ae 946cdc cf3b33 1ebb00 8ba8ea 4466bc e5bee7 3e973e 0caf34 c893b3 e6b533 5587f1 a1c2b1 dcf2ec 30c438 0ac413 226d47 9256ca 000cfa b9850e 728407 ef124e 806d37 789bad 3a359e ba9dff d333ab 8ebd18 3327a7 04e617 a2a979 8fac13 3fc5e5 4c7540 6eff98 af0070 f25616 d7f3c6 cb5c41 215672 048c4e af55f8 244508 d86ee4 afadd4 0e6a6b 66ea88 09b142 c38e19 456792 cf88c7 d0bf05 f5f139 4c1ef1 97cd71 721063 950e23 54d6de c35025 b4f4e5 50f8d5 4cec18 c5bc6d 2f7928 0b1a02 d5ad2b 429e1f 0abf25 678595 046b3e 22d0fd e38584 ce6707 eb378f 3bd813 adcb60 20b219 4ff426 37bfe8 cc6ab2 721fe9 ed50b0 f2caa4 55b187 849b50 7e1998 5c391b c42b1a 6a0ae5 6605cf ed5dac 3f2bc3 ae5dad 2b7f63 c636bc 823230 a1d020 80b44e 157243 faa118 728508 418af3 bf8f58 5cd1b9 a31ff0 9b8166 42ed15 dbee52 c5751c ba7350 626a78 1055a0 9e6f3f 67d4ac 2948c5 0c28db af5a23 043c64 f06863 ff7a7c 86a191 26ab32 92762b bbf9eb 44c569 e031e6 962afa 483a7b 497fc2 8961c4 e25694 725598 562cd7 ddd894 916bb2 bdfa32 5ecefd 1a540f fef0eb cf6599 e71bf5 2e26d7 f3bb9e f70003 c39efe d0b800 1201ed 7c3cdd c4cff2 34bcb7 f166c3 a4c2b4 fdfd92 0e7d55 8eec17 2ae4fd 70bb2f 68316f 74d58f 837e76 504715 3b080b 650f5e d848c6 694a53 7bf667 157f74 d1b3f6 2729ad f9c955 0c3274 2eeaef 5483d9 cc367e 879a9f 9f8a3c eaceca dc93a6 0937f6 b8fa60 6486b8 9df813 10e978 92830c 92b19d 5fccec 69c5f4 6b5ba0 f43944 a109cc f12535 543c69 b7089d af50a9 ee15d9 d281af 2358b4 cbdfe9 afb76e 74dd4f 3a0fdc eabeb9 b11c4e 8bf552 2ebcdf d6a8bb b951fe 7da608 842d8b 0bef81 d01f51 2e6375 61097f f3bae8 57b716 5a2cd4 0d802a 6a3d7b cf080d 462e10 582eef 6688a6 f384fd 83963f d859b7 8fc850 b4b72c e4eae1 991bd9 308196 508437 926d3a f0bb5a e3d947 1cc9c9 534ff0 44dc77 4848c9 4bef5d e7c24a d8e1a2 8e2fde 5f4deb 4bed60 df3f20 8b59d3 9c96d6 59bca4 dbf588 c1f87e 062ae8 c4988f 6e5793 d29d67 8c88d6 fd57c5 932799 f1b6c0 5d6609 238e2b 134f91 bea5cf 1fc308 cc02f2 0457cb d0bac4 f25d50 2a32e8 f758cc ae1228 926e9c 3ca9b7 74b901 79b7e3 1b3308 4d1452 af19ee ff23db fbc681 372028 54b3af f62b98 055b22 66aad5 c10200 46f238 96488a 1fb65c 1bbeab 4d47a3 6a1cd4 98ade3 3eebc6 1e6257 a2bd83 936616 877b7d 088ede 381688 c2d877 785e89 60648b 3143d2 15f90b 59f2c5 6b91c0 a83347 cf522c 7ea4e4 690a1b b25859 f8ab6c 03f346 8ad4f8 1f678a 8eb615 2bac00 ece8ff edfe20 00d2f7 d657de 5d8b4b 70de17 d29dae c14f3c 9f81e7 330b25 a45804 0c4262 af35d6 7a9260 35adb7 586745 991455 b74c36 f3ae71 53880f 14056c a88544 127d1a d33e74 92b829 e79417 a21862 fd2760 289d07 2eb1a0 fc5d3b 960104 d7174f a52002 4cecc6 642a0f bee5ed 334a9a 1b8e92 dbd126 df424f b078c5 3da1cc f70e70 bbd4e1 dd22ad c01bf5 22cf85 92797e 0fe515 2d3c13 57ca77 473009 ce97e2 92d09c fbd403 9e2bae 78a2ef 2ad5a1 3dc15c 3ab3c7 3efda3 f60291 4140ff c15811 705df3 6fd147 c85fe4 3e33f4 192bd0 7c8994 67a1ab 99e823 dff2f6 55f6ab 8b2289 5a5ab8 dfc2f8 c21a9d 99d8e9 f2fc44 83de38 4cc809 58435f 64354a 305c1d be0390 f8e385 9a2532 0693e4 65e40a a0acd4 a22aca c230bf 76524d 0a8daa 9b8cd5 c286dd 860c29 7786a4 ddf714 85e451 a5afae eb90e9 4cca63 64788b 452afd 1dff9f 7009b6 57f8df 3f9420 336c21 9fa0e4 b9ae2e 4089b6 39b842 e2e178 de63de 636d4d 35b0ec 1ebdec c08653 0ae542 10a5d2 59fe77 e5114e 0a92d8 35b66b 6bd93d 51482a 7143ff a604ca c89c13 392d5f d28e9e 275fc6 c1fc1c 11cde4 138c0f eeecd5 1b344d 5b0f5e 244f32 150b73 8970a1 7d7ae9 1ba551 3df048 74fe2c 0fa0aa a1e812 944b92 2d7fdb 300613 56d26c e22ba0 170a88 8ee0b6 44e66d 306c2c 7a9ab6 32d588 8214d4 63e3af 542208 454aff c40cf0 311279 d2a2ad f8ef11 303c21 bbdbcb bc3875 4f1475 961c8e e2f613 d26147 7b9c82 573a02 8291e2 62cd46 b4c97a c8858b a7d238 940229 a5470c 009599 1b6e3e c5f306 0999fd a2ed3a a5b624 879bbe 0fb76d 65e715 a6dbd2 a7c396 0f37f1 911650 516d2a 71e1fe 6b93df 12789b c2db6c 8e12bb 5543af bb78da 9ff57f e52448 fe2f09 d85ce9 5bd4b1 efee73 42c141 19bca9 1fd18d 6bd0a6 70fbb6 eb6454 f03b49 e7dd6d a60bc4 88de95 a70dac aac413 edb288 9a1db1 91d3e7 2ebd2d 4b5a96 d96666 2a1b08 4dc9f8 4b64e9 697706 3486b3 7f5934 12e8dc c917aa e5d570 36f965 02fc37 361900 1d1266 df0e90 9409ff 799543 d97b07 3b5177 536ff8 8911ef 6925e1 abf94f 9ea8b0 996cfe b138c3 e56f3d 581d6a e40430 47276b cb04b8 c7df85 292b9d 97cac9 c361eb fa6133 d8299e b52d34 82a749 687347 b6f59e 078c9b 70e69f 7528b7 0ac07a 97fce3 5182eb 6b376e f36588 077443 9ed472 0df9f2 a86a4a f11701 653536 da1730 0556dc 1581f4 848bff 17a5f5 e7ebfb ee2828 380599 006926 6bf0ad ce8042 893206 c4bbd4 74b727 39923b 038e09 8cca39 803bb7 22a7d7 26c424 3a95da c80896 34b2a6 980528 1a4a95 a88fcc 166762 a0a0df d4d067 2a7c6e 545395 3495e7 761ab9 074243 008887 861669 bdedbf 351a0c 060253 6707cf 47baa0 9a1789 0adb39 e7a92b f153a8 65b72e da83d5 3e3bd6 b142d4 050372 1d3ad9 4462dd d7f45d 67901d d69ae6 9f337f 659f6e db0904 b7beb7 5a3b9d 731099 eae44c 888230 944f17 ad0a21 439070 ff384b 65ea6f a54abc 19222f 73f608 159601 5488a2 6548b7 31e172 b388d2 51ce3a 382fb2 2fd431 2fd537 b812f9 6240e3 89830e b4ac2e d2766d 8a85ac cc57b4 955529 c6eaab 98ef24 cdce4f 6a9e4d 087138 006329 51ff25 ad09a0 ff7696 a7ea75 990988 b74295 7869bc 3bb6ac 050d06 df33b8 27c49f cd1997 f5c812 fddb27 9880cc dbc5fb cd75eb 0b3fb9 bb2115 2a5f30 645e08 b672a0 0b163a a18616 5ea141 a6fe9c 1540c0 81c5c1 1bf11f 0c7c66 7c46b9 dab366 e6142d f2f784 441632 6d7265 426329 467673 7d891e 6a54ce 2a11c5 39884b 51eb60 37433b eb1040 8561ad 44f5f3 99bbdf f46596 83c248 1ee77c 807999 233094 d443c3 934efd 134799 f69357 a43080 95f8ff a26077 278104 957f19 d5229f f81f62 7a79d1 050f68 80407d 955658 fc03ff 713429 ce698b ef39b3 e9af9e d4d51e af86d2 5b689a abffa8 e7ff2a 026827 a2877e 648cec 0d2c82 8b5acf 94780a ea85b9 35aa1f 812683 23a076 1ecc7f 76c982 d735db 1f2147 20be4e 3a1299 2219d7 416f82 d1e4be 965113 5b3cc1 2d317f 88bf60 0be220 733aa5 663980 ccaa64 1a27a1 a638d2 59f138 a7cf9c 43b5bf 2346f5 5d8b93 91d92b 219b7d 3b9b2d fcf22d 50e980 0d74d8 071cfa 69d674 2cd3c0 edc257 277362 2bb053 b2febf 7e5b24 3d0e9e de9f84 b3668d 5550fa 3bc0e4 9752da 45bc05 a11273 934211 11be8c 04ea7a 48f8a1 f5534a 852ac2 e71f27 20e989 814c35 38f955 c68218 c6dfa0 8c2200 4edf77 98ce0a 6dd6ed 9659ce 940719 ff7262 0e3a30 3746b4 0a3c5d 5ef19a ff7dde 5c574b e4a705 4de56d dbc196 e42f64 22f3e3 83155f d294c0 54bf58 e5ff07 89b431 9f3d31 a3804a 92a535 a5c53d 4d1922 2b2bae 09ed2c ba3781 a96dab 695d6c 6e43d6 7cbe76 93f6d8 57c894 9817a6 17952d 6abfe5 29aa38 bd2911 66b767 1d37b2 ea6449 261aa2 f86fb6 1090c5 a3a8fa 080e6e c72138 3df4a7 fc7553 94a25e e1bbc8 8e7002 316070 805ca2 e8d244 c23a2e fbe78a 6771f7 aa9800 a360db 0f07e3 5ee773 8385d6 b5f0d7 3adef2 ad785d 43ba1d d83b7f b424d5 c7b1ec d87ba4 6ab9f4 bf29e0 faf104 d470b0 e86cf7 fd219b 787e70 82c8d6 1f3fa7 794e5b 605991 d02332 6bc17e 96d7aa 921142 b299f5 2c57ee cb7346 77a203 7ecf6b 3fd904 1120cc 57b2d1 66e285 97dc18 cf95c9 2dded2 be45a0 4d30cb 109ca1 73b52d e0332f 5d84e1 2fdf89 0de005 ef5624 a2c2f8 9e4e40 4b3839 b18170 76941b 177894 67a697 a97162 af5730 3f656e 3bdccb fb3d03 7680e6 dbd7e3 404d98 b6e828 34e92f 7dbc66 8b3231 7433bf 5dabb3 0f66c4 d1585b 3e9fa4 079d36 0d9579 95a8d9 f8a385 6a7b20 d59274 347430 09d081 306533 0b9b58 75c3a8 463e4d f128ac a85aa8 9b085a c3f95f 9297dc 662f07 144bd0 f0b27f 223ead 64bc0a 731503 370ee6 267e21 a14858 f5ad36 5462ca 397181 663fc9 d724c0 a87077 b47d96 af0d75 316403 8859ae b7e8ff 3e6357 17eb8e ba778d 0e2016 6d4ff3 362e0f 470562 16ad24 402ab7 71df93 1a62f0 a193e9 f0d2ae 364c17 51ad0e 0374c6 acd44e 489ee0 a7b938 d9fd30 8fb328 601b44 a49d2c 989466 ac3174 723366 98fa29 8e7ffe 11a10f 3635d3 695479 1967a3 13527a 3a3dc9 6e4cc9 89df23 c7f5b0 f6a88b d6636b bd5a1a 14afeb 06980d a48ad6 c0dd88 8b684e 1d8761 c7b123 308eef 014b8d c0323d 4d51c0 449fb8 c0cc50 d6c808 6be7b0 17e0f8 9651ca c57309 a76edb d15dd2 eb4b33 48d24d b66164 dd4f5c 9f335a
Level 2: 675452 09c19b a7db95 17ac18 f8596e e72897 2a2f52 4f67c5 901b4f 5e3664 475c50 c680b2 172460 b8ecd1 52052e 60ec7b c4bf94 853cf1 1c2a72 847987 896ed7 bc8a0e 0c3330 d5d677 0bc73a 65a20f 83e21a e1f737 c86ca4 3ff235 4bef59 2f5ba1 10b6f7 931483 551f68 7eaf55 61f44f 9c48f5 0a61be 2e86ab cce1cf fb2516 973337 7e970d 11b54c 9b6b17 c4abfb 7aaee6 1b2b05 81872a 48259b d00734 dd191c 25099f dd9b03 91c3fb db10ad 746015 d0bfd6 7e4e26 37f378 57302d 3df477 4a2511 c93d64 9e7377 911f26 51537b 08782d daff61 31978b 98fddf 8964c8 d3dcbf ffaaf2 8d7168 508117 fa0dd0 8970fc f438fa 88efe2 d46af0 a2a6bd 8a248b 494510 7fe454 81205f 2e3a41 d3f966 9a336b acf34a 8928c6 aa6bd2 cf9072 45f0ec d4fe65 1c2a66 e6dcb1 5ceb7c 2b6390 8156cf f6ec85 412ea0 1459ec de4a99 e06a15 d6f8c9 688d4e 2af7a2 6a8cc7 5475af 518d43 434296 39dc51 fa8673 0a01ff 3f2874 b49980 3d7985 6ed32e 74968a d72822 670e01 6bbaf3 8ffc6d d97835 ff93ca 9a1702 7a2013 76eb0a e4f83e d8ac1b 0564d4 4cc1ea fa2c37 7b50c9 45b217 3cd2b5 33fc40 c11685 9bac76 0048e1 4a8dbb b3a1a0 c108d4 ccf0d6 b6f56a 8f02fe f8b1c0 d30593 f6392f 75a527 7f1df9 803b72 12ea39 748e81 8a12d9 2a23c1 46bd99 8b48c0 5c364e e50009 a80f1e 9e8b8b 574d17 8af606 7ffdcf 5d19ff ac1336 ad37e4 3e3966 0508e3 e2d545 980767 75a545 45d8be 59fd32 96fee3 341dce 62815c 76ca9e 0d926a 30d105 c0f585 68e776 13127b b3d234 db9681 d25001 ac2575 99a480 ed892a 5825ae 2bfba7 15224a 1e3b34 dadde5 6dd040 eeefeb 269e00 0059da 119526 e48197 ff3d05 8f34be 124da8 0ead67 dfa4bd c0d54f 68063f 7b26c7 746261 ea5acc 14795a 1295b1 e3425d f09090 2807af 280f42 8cd8d8 6af3b1 ea17a7 2eb4da 967750 f8a5bf 7652e0 89c7ad 4ecae6 240b6c 3403ab 7bb295 b9004b 45c9fa 000211 4e07b4 1f51f8 df1575 d0c9f2 8ef3fc aa51f6 17131b 27afa0 3220c4 5294e5 ecd025 d46fb6 4b235c 27c13c d831a4 cc7632 b01cd6 2eccb3 d5d338 b79f1b df9a18 5035d8 b508bf fefac3 abe5b6 342f49 bc57a0 56bba8 4aa710 057f76 b51e09 420948 687d37 f20906 47fdd3 1de08a e709dc b48cbd b52b19 c75879 05b9ff 73d623 5c9954 a3270d 640623 4eb808 cd4af8 0a6a36 6f9e30 43c0e6 7de93e 5213cb 4acf93 0ed56c 548f18 9697a7 6bb4ce 352489 1e0ee5 eefd6e 468d5c cdbd1a 013faa b9b1aa a850c8 a194ba 92bccf ff7339 b0aaf8 da49ae 8c3279 e3f2b3 a335f1 6d4efc 0076bd 5a269b 887298 35819e 0c0896 530c34 14f7b2 ef412c 411677 4fc864 9ad4c8 f6b2bc 7f29b0 84f01f d6653d 5ebbda 6f4ed2 3e07fe 042559 38b91c be4b90 5f69e7 96e6d7 8b32f4 346bd2 2f95ce 8757ef 914683 99d52b 2b9c69 db60de 34f2de 8f9a5a 423f1a 0858fb 19417c f3ff57 df6145 7acff4 941b6b aa72c3 d4bd4b 013e16 1268b8 78e695 49b3f0 39da01 8fde7d a82436 85c4d1 15fa3f 27d734 b77a09 5e60dc 37b9e7 3afd5c 3e05ff 2cb3c7 65cb0e 7d71fc e139bb 191f79 2c5fc7 a34298 ab2f87 25688d 65fdfb 4b4e7c b576a4 69fa47 bdd0fd 26c2ea 58b210 4d05be c1c5b3 211b7c 92bb37 b024c6 383388 1f4c64 5eab29 d04731 ce821a 2f79ca 5fd37b 329118 e14f4e 1fb987 bc074f c7a2e3 e38e30 23690b 2a289b c192d1 b77f3b 3b96d2 60e7ab 29888c f5fd71 9bbae3 a61330 c7aa41 4a9a0c 2c7885 87c4f8 521219 84c0f6 2bc898 ac5e2b 569824 57727c 4aec01 086e7c f257a8 0f3207 5afcd2 e61fbe b67c39 129e9d 44928c cc2209 8a11b3 7d2992 ab988a cdb90a 51b820 21d22e 071e38 ce7acf 042a3c 95b096 7c9602 fa4201 86cd6d 9268f3 2b39b0 fc7870 8e1de8 87c33e 73bf7f 344baf e81b58 4c8f9c a9b717 fd116e 7bc85c 5bd7ad 3bedcc 1fb691 bb7e56 af008f a88e14 e16fed 006222 ca23e7 93ab60 95a677 3a4a4d be8acd c0e60a 407a4b d1f4c6 c9d678 10789e 5ea0b3 7bb164 d09dd7 919166 8308de a2da0f f60ef0 c48fe9 ea2de0 b8f56b 810fdd 10c2b8 0069c2 a7ebf5 8ad0ec 1811a0 e5820f 80a616 9f6c15 aa01e1 fc699a ce927c 443ec7 c92c9b 486d7e 6bf037 d70c3c 9886f7 cec530 b5e2d7 5db347 c3f4ab 7a04f6 95946c ab797b 28dd1b e25be1 e70ca4 42f2fd 3b825b 5fc4a0 8891be 9bbc22 7f3cca 553596 6d840f e8d1ff 947d1f a720da 29611f ddf230 5c7ac1 c44d4d 49e896 69ec60 2367d3 038bd1 c00b37 fbc87e f5840d f16ee4 c112ed cae5c5 d1974f 8a347a 8b8f3e 7b643a 1801cd 8827d9 f642bc 1af703 050cab 451b80 0004af e4d491 441214 62b5d1 8a8a1b ea45a2 4f2b0f 02cbca 45831a 58aab4 7b5474 11822b a9d853 4e3453 411896 9051ce 73cac0 c442e0 29b636 b62ed3 2937fe 5d9fbb 449f43 e19eef 1140ae d5747a 1cfce8 749738 0d4709 b59296 8fa167 af8b6d 6f0007 6010a0 889ed3 fb3784 dc472a 376705 cc69ba f45421 8e29fb 983141 26b9b9 c8d89b dd27f3 644987 38fb70 5e882a dc6106 aa7495 fa668c fe4d82 fe2a94 94baba 68d7c8 742519 2766c0 d4cc05 322279 cbf629 437722 65ad84 92f406 eb48b5 40a3c3 718408 fc8fb4 eef916 07e684 9c41df 2a603f 2d2f45 750038 0a198c 752fc4 a822eb 90df5b e14e83 e9b0a2 8e226a 21e944 981d6e 176022 b6c4c3 d270c8 08eda4 c3712a c0afc7 1740a8 5b7343 9253a6 2dcaf8 df0cc6 25d200 793027 84232e 445558 ab85c1 c68905 d6b690 d68e46 75474c 7e9a9a 19af78 9b6858 c712cd 169e46 170dfa 18ec60 c0ace7 84918b 4a0f3e 614ce0 3ebdfd de4cfd 936c79 ae259c 53193b 3ee35a be09e3 558b9a d511ea f58de3 c8a166 4e42b3 373506 992075 b89a4b 30d1b4 499989 5d0bd3 21f146 bb1409 4fc82e 33248c bcc429 989afa 573e59 c01ed3 af9690 5c0264 91d344 7c0839 0e4502 e07a35 8945b1 29c98a 9a91e1 1c69f7 faf254 53c101 969c06 4e3243 5816e7 1a0f87 f3cd3e f9bc28 e8841e 0dfc99 e9334d 9e315d c35e88 568282 3436b3 fca761 789759 33d8f6 d12486 b9f0b1 fba221 8de0c4 178266 469cf3 79e26f d7119f f7e9b4 1b58a2 5eb059 6e0761 73b7b8 186c94 3e3769 b22c6d 5c53c7 15f28c 1a7c9c 4afb33 67bd0e d4b645 f7590c 33839c dd188e 8e7afd d066e6 84b633 a50a19 423ac5 74f496 4f4e87 237139 444ceb fe0b2c 02c2ed 48b3ef e1454c 5c9061 223ad5 9b782b 1459e0 f972b8 94c886 a533ea 4430df d7da8c 355e39 d208a4 7801ec df9da4 2459c1 f04f70 d28ce6 43e4a1 e2a817 53f41a c95174 232c89 b3cce1 706060 9168df bf62e7 ee5c39 8a6732 23ca1c 8c7d02 3fab68 3f9901 e52323 a46ded 356bda e814ef f7f096 b1c762 59f63e eecd39 51e0a8 ba46fb 3eba64 f40295 02480e 4b7bab 1b2a7f a3fb2f b749d1 ba6337 a164e5 dec72a ce8d4d b51ca3 646afe 66d224 1f7dee d34b08 9d77cf df091e 91d780 1a3a3a a23870 002470 376296 25a94f aeb63a 80cfc0 e42b13 9c6a92 5a759c ea959d a1dd20 e821ae a00f4f f168a2 d23ae9 9528d4 1eb459 08029a 4c7e1a 304aea f40c01 4b915b 5b1299 1d5690 c95160 6bf65d 3ea7e5 7933cc 5a664b 614b64 bfe079 86dc36 502132 4251f7 f314a9 616631 7bbfa4 60a6ad 4c50a6 a32f13 3fcc25 8c18b1 72b927 919f15 1907b8 141abf 76f594 e7ed48 a10bc7 466b19 ff6ae5 4ee7fc e70ded c707d6 fd93a9 124e05 1f94a3 6bf69b 14b597 1ffdce 8ba238 0daf75 a50ee6 bf08b4 40a54d 50cf5d a144bd 430715 1244e3 71b926 ff9ecf 518286 a45ba9 235c03 501554 3fbec2 6b0e63 06c736 008d58 05fda3 875d1e 2da51d 6d703c 8fb4b9 181970 68392d eab88e 86c310 e63a3f 1d2f15 5a5131 132d31 d6e448 c5cbbd 4fbc7c 874ad4 8611d7 39e2a5 2ac455 b76a50 cd3edf 706add b6dcd8 bf4cd0 ec0200 6d974d 297287 d190f5 67927b bc00e2 a037af 1b80bc 41b9bc dee81d 1ca931 196b1a f02a3c fafd8e 55b297 17eef3 e9d747 604122 9930bd 4d95d4 a2e45d 0151c2 389433 bbabba dee040 5e1f05 9cd293 cd1836 d3cd5a 06f665 acbde4 a4ea11 9af807 0ce117 5e5253 fb0e53 06cb15 98f593 526310 540a08 1c76d0 bbb5a8 bf97c6 cecfe1 b1dcbc f248b5 d9832c c31049 de254a 0032e7 f9fc91 e89cfa 8b420b c12699 1d918b 7b4733 d94253 6c3515 db9411 25ae66 55c10b 0cf297 753546 72a8e4 68b223 fb2ab2 60bcac c94e10 4198cc a7941f 05eb6e 56d04d 44b429 cb1608 f7f0ac 46b5c2 269408 482282 7a71a5 833a65 8c4021 854c90 c22877 ed35f2 26b380
Level 3: d82e04 406cc0 afda40 0bcb46 890110 3ebebb 4a0df2 cf3430 f78aa4 8feba6 4e78f7 8d6bc7 d0780d 28aaac 7653d4 4416d4 e96c49 f48ba1 7e4377 8fd6ba 440362 930eb5 197024 b612bd 41ae7a 23bfcd 94f063 e5a9fb e1906e cc52f2 953913 737fcc 55e549 86d549 e157b1 c7b2a4 851ec9 731b4f 771c24 bbb4ff dc489f 9d9f4f a152bd 9e01da 336acd effe1a 925d1a b2efdb 1dc4e4 251e83 8a8fbc 22be05 766a72 e11b5b e2ed33 11dc0b e7dfae ecd834 60a1ce 7394e6 e866a1 5c2530 4f7642 83b26c de9d46 f45921 4b4c1a 72d391 048052 3b0b39 96d641 540d83 1183e2 2c20b8 c6ac91 1b8d27 a1fdd2 75a3ef aa365f b8921b 822a55 d04379 3f4174 cabe72 b7b3a6 a60805 4a0705 e113b3 15a2f0 cd53b2 24bbe8 618068 42f99f 545469 6db5f7 a1411c 37f07c 1582f6 88eb48 5c608d 566f35 d194a1 044e06 262a65 a16d26 e272b6 0ba302 2ee457 fa6926 230220 993d22 d612ad e4514e 80a1ab eb63e5 720ad6 497ba4 eaf45f 5fd43b 46d3ce 80b1af 285fdb adb18e 709cdf d268da 5aa6e6 53f9d6 1277ba b31de0 c822ac d89789 d9cdff c54529 d102e5 897fc8 4b4a00 66f014 cd2363 a32954 2efeb6 557480 c2197f 6dfb60 7936e7 47cbc7 958c8f c81a60 dd3b3f ca04e2 bbcafb ca4c2d 63d246 047cb3 26aa88 5a911b b33a16 cd2ed1 88b334 5f1563 095295 02a145 972f7a d74f4c 2884b3 fa0b79 4e4ccb b18a17 8fa1b5 8d63ff 91523a 316cc8 7ac292 6bbad9 6daed8 55d181 db6b80 ad2aa1 967dde a0347a 219b1d 2de0d1 19e4dc 0d59c5 b084ba fc63ea 67d275 9d1a23 b1b89d d1c20a ea76a1 74025a 3fa535 92028d c99060 f446f3 171361 f4aab9 f15250 047925 f4ae12 406c0a 9199f2 45e278 f56e64 381167 87cbbd 677de6 52ea81 17f660 227d2a 992343 19f8a0 f27f95 dc849e 2120b0 7380bc 42327c a80de0 4194bc a99abf 69080f 71eb4e 651acf 3be69e ee3213 545a10 fb0dee d32fbd 2727c6 623e48 cd21eb a570a0 de81f3 675c4b edcecf 43171f 6e511e 04b40a 613e8b e8505c bcf031 1ccfbc 9f6cdc 757ed9 0b4f71 8be66a 339d1c 718f63 6a7743 7258aa 3e058e f0d206 e597c4 140a1e f7085e 3725d3 335512 f431ed aa415d 6a32f5 7cb956 b23a83 cc78c4 8a22e4 7ecf15 e9b507 2aa179 39ee7c 3b5fbd 83e0a2 6aa5b5 c89e97 96931c 51bb66 583308 988cfa b0c98c a6b4bd ade8fe 8614de caaac3 d2f40a bf070e 6ba3e6 7cdc71 4ff1d0 97d289 b06230 18a959 df1237 e28b8b c5027a d9b9bb a2139d 3cc9c1 63b2e4 3f9bf6 1b6ad4 53f2ad 0dd876 750601 fe2359 cdcd47 782388 8235fa 4557fc c3aeca 5ce51d d49738 ff4b2b 57113c 3e6bca c5d148 444f00 2ac06f 8a2f07 07a349 83c803 db8a05 97691f f442ba 6cdb20 9b207e 101ed8 ef208a 0d15c6 5e9660 4746bb d0bb30 090540 334733 e76d08 e549f2 dd17ef 142f99 7ac95f b46274 fcfa46 4607bf c51cfb 885272 1da882 c03628 e2d70e f8d482 cca021 31e412 e6548b f8ec78 faa22e 8ca089 c5fbba 794096 0b2e60 015ff8 55e1f3 a2cc09 4df5a2 d83db5 f51d6b 694976 0c43fb 5b07a2 1e56a7 811cbb 3c0b9a 084733 c7279e bd8608 e1929c a4a7a8 fa1033 fa182a c09368 f4d508 91975b 400073 bf2111 99eb3c 300f64 b615b1 b84d19 a3f7af 5568b8 2c42b3 9b7a69 5769a2 39cae2 97a9d4 98bf98 a75b13 a2ecdf 33b82d 3d2358 6e642e 89a84f ebf124 895211 028ce5 8d93d6 00eb4a cd8caf 8b0e56 84d3bd 437f89 fd9c3f a889c9 3fb3ca 733122 b9fca8 c8fac4 44b624 caa796 f8b1ef 7e45d6 179155 cb84f4 0e100d 3e7718 9f99f0 d59355 12f62f 9f6868 62d9c8 55aefe e78077 22d482 755340 13299c af860e d1d094 42f6b7 cfa316 2898a5 4f620d 41e36a b101d4 ee5d6f fc016f 673f41 62d375 caf5cb d601e1 f9bb6b 4f248e b84ee1 0dfaa5 db56e9 393b77 08d51e 89a5f4 a90819 9a2ef0 98eaf3 6fee12 0e7969 1be914 56a8b7 5b235a bfabc5 1af18e 48536e 65f498 15cc43 691dc9 dc3687 9f9000 933525 a0e068 1d2257 acf96c 3eced2 8598f4 eed931 25043b 29a6f8 d91752 3888c4 c03b6b 6b5b05 f27f34 b7dfe4 a569c5 b741d7 a1aca4 530aad fbcd19 e52b0d f5b2e0 34be4c 8b2337 825506 75b9ce 2026bb ecdfba ca3728 8e0686 c961c0 80cef9 e9b228
Level 4: 785023 4fcd7f bb4051 d5f20f 041600 ba3520 c1c32f e558dd e2a288 c3e65b f37a7d d85d85 7a75ae 65967a 7af0b2 66b6e4 49528b acac72 5a153e 0b5184 219f25 a69909 bb97bd d03511 a007fe 6c0eb3 8d4286 6b29f4 20e053 702894 459366 57a92c 5feae1 eb8bb2 b5b51e ed0925 01929f d44463 434d01 8f4839 b91786 6f00f9 f3dd0f 60ce55 30935f d8bb8a a25f77 17a014 c1a374 559e6d 71338d d6e90b a23500 50a9fe 977df5 c450a3 2937fa e44ffd 399e72 c3354e af8827 e4d18e 6fc810 e551bb 3c0c54 02515d f50985 ddaeff 16968a 48f99f 1dc06e b07995 910b24 d8b51c 8d6463 f295b4 4c28f8 8237d2 7a19d8 0df04b 04464d b18430 dba147 2f0783 592b79 347c88 180af2 0de207 91ab97 7b4426 710249 c17598 90a8e9 34ae14 84db2f aec966 917ce9 d33d72 582770 777564 404428 c1fe87 c63083 d80788 b5673c 575f8a 927730 9ebeb2 696dd6 e373af d8bd3f af5d46 c16f43 05a6a5 0ad2e0 5a44e6 57e85d d6d8fe 7f1b1c eb7159 921226 c70b55 2dc774 bf8b37 888ced 6eed0f 31b520 ab5ca3 1efdf5 4882ce 44fc22 af0c81 89a6be 093363 d809d5 abfa91 640035 f9c020 625774 314cf0 bbfb27 80a12c 27dabc 8cdacf 4b04e2 3f970f d9e5d6 9637b1 e69cfb f97114 efa0ba efbf9a 4bfb4f 1b6707 5243cc 52b5ae 504366 351a97 efc089 eea98a ca13f2 636dec c4be4f 13cb03 f41749 5dcf1a 70d5f4 520e5a 0ccaac fd47a4 ad1221 8626d8 0728fa 72e4e2 1aa2f4 a137ae 3ecaa0 0d5433 a9fd8b 50a69c 4b8887 9467fa ec9e17 03815b 4b2536 37b777 062be8 e4e163 14bed8 5f0c4a 04f3e4 4c9855 ae6e5d 395b7c ddaf72 7cd29f 332a05 8da12b 2427c4 cb753a 5315c4 692fe6 b01d8a 744340 e8ed5d d7184b 17d7ad c32713 fd8756 d831e6 a1c155 898d82 531e48 e015eb 7128f0 38684c acb721 ef0217 70f5bc 925dd1 1ea2e1 3f8bb6 2a08d7 1a23ca 93d21a bd148f a48894 543ea2 103c52 f08262 e8b61c 7d4612 4a8559 4dbe69 019d56 868830 25b570 80b50f 2d5330 026aac 745b4e 09914e 022640 3c6dce d13a3a d5fd4b 5c6e59 fa5888 c0fb33 2d9dcf
Level 5: 0a6b0f f9cd19 290e9e 62e64e 5fd192 6b82ac 54fd90 9235e7 f5d5f6 d47d8f 6e8f7f c1e935 2db7c7 72d51c 37bd04 b9f74e 9388ee f7e10f 32d3df 0123a2 4a987a f62eda 11b4b4 19e41c ba0957 7720fd 2f54c2 257e9e 1f159e 62a597 c52d3f 3daea3 507d62 03e6c5 3bdb80 476fe4 e266df 879892 9dde2c 1f3fea f14aee dfe2ce 750794 e72434 43b1fe 0d76d8 3d5d87 a2750a ef863d e1e942 4dd739 be7996 9635f1 591971 afc482 39574c 410012 3deb4e 3e59f4 7bdc63 b49674 8cbc97 ae7216 51eaba ffd608 11685a 413c3e 30c680 a3ad3b e99804 855806 5d96d3 3a2959 cf9fbd 0b190e 6e2822 c8a8b5 bc97bd a12a37 53c131 16297f 594466 7e8fbd 0572c7 364c46 26034c aeefc7 e9d3cd 382242 ee99ce 5c873d aaa420 f00eee 9a553b d715f9 895750 8e8cae 782c8e 402384 f33ebf f3e563 ce97b1 9825da 76141a 9a8483 2520f2 c390fe a2f135 46e6b9 2ef684 b9546d 521ca5 e75101 932e28 8c18a0 9ed2b4 ef5739 cf216e 4a0833 66b189 3abc7f b23964 27a34b 91ebd9 71a85d
Level 6: 548509 ca0a4f 7b63cf d183cd 867fa8 813f60 5e7952 1844d0 4e06e6 44c98b 7eef0a 62b4ed 28931c 416690 6951af 7a7e2c d46236 fe4cd4 b1620a 778991 27392c 2cf755 694969 be4421 5f36db d970f7 87fe5c 591f56 917218 71a4d6 b91154 ec1aac 827c55 6d421d 27426b 9f2134 d5dab1 e5d134 e14e2f ce77f4 82d567 9ba14a 47b54e 8e7721 ea8122 ad1573 2603be e65713 c03cff 975af6 eceff0 85c486 3dcde0 b6beb5 bae648 c1c8d1 811c23 8ab8bb 929492 98fbcf 25bc47 826332 521405
Level 7: eb77c9 638cf5 a465aa 938873 1687f3 eb7d0b 3c221f 3ea5be 8c5029 eacfb3 876b01 cce3b8 c5f080 3905c5 693122 23bdb2 ec515e 574216 8acdac 1eb662 8a227c 0bc426 7ec3b8 39ccc7 bf70ec d4bdb1 ba505b 0c8264 bb1280 ed7c75 13f414 bf0012
Level 8: 141c83 5f13db 3e3cdc d93328 740c56 87ac14 d76463 ebe6d3 be6fea 4e2a08 f9e4ca 5d82ca 613e08 96f877 a9aa4b 1bd43f
Level 9: e535df 242cb2 0949e2 afdd7b 979b04 2d7a02 9bdf97 97ac8c
Level 10: de4d11 29aea8 b8c100 d30783
Level 11: dbf0cc 4c24ef
Level 12: e8d835
```

Tolik transakcí a přitom v merkle tree se dostaneme jen na 13 úrovní. Jak by pak vypadal příklad ověření ve walletu? Nejdříve si v roli nodu udělám celý strom a pak si představme, že peněžence pošlu jen ty části stromu, které se týkají její transakce. Šplhám tedy jen po relevantní části stromu. txid své transakce znám a merkle root si přečtu v headeru a k tomu mi stačí od nodu dostat jedinou hash (tu druhou do páru) za každou úroveň kromě root - tedy jestli dobře počítám, tak si musím stáhnout 12x 256-bitovou hash. To je o poznání méně, než 4000x txid. Výpis jsem tentokrát useknul, ať je to přehlednější a není tam tolik dat v nižších vrstvách stromu. Protože si ověřuji první transakci, která bylo v Level 0 hned nalevo, tak je krásně vidět, jak jdu jenom po té části stromu nejvíc nalevo. Co zcela nalevo vím a o jednu doprava potřebuji říct a nakonec musím dojít na stejný merkel root hash - tím je dokázáno, že moje transakce v tomto bloku opravdu je!

```python
# To validate single transaction we do not need to see others and can get just one hash per level

# On regular node we can build full tree
merkle_tree = MerkleTree(transactions)
levels = merkle_tree.get_levels()

# Let's validate first transaction
next_left = levels[0][0]
for index, level in enumerate(levels):
    if len(level) != 1:
        hash_left = next_left
        hash_right = level[1]
        next_left = hashlib.sha256((hash_left + hash_right).encode('utf-8')).hexdigest()
        hash_provided = levels[index + 1][0]
        print(f"Level {index} -> left {hash_left[:6]} right {hash_right[:6]} --> Level {index+1} --> calculated {next_left[:6]}")
```

```
*** Merkle Tree ***
...
Level 7: 39d98e e283e5 08eef1 439065 7f811c c8eee1 3524d5 76c72e c46c0e c9c07a 0e226b e187e0 ee11c7 b77d15 97d54a e69842 3f80ff 4d66a1 d801c9 70b20d 81f7d8 c85947 92c77b 319724 ec433e a5fa70 79ee9c 4c23d8 3dd579 abf50a 4ecce5 d9e1d5
Level 8: ccb90c afc40c 1d27ea 6f5aa1 4720e0 a12979 683605 1130f4 0f74e7 c172b4 5d45b6 f4cda1 8421e6 277e63 3ae87e af02d5
Level 9: 232000 cd54cf 1008e5 6066cc 5e688f d7b1bf 4b6ca2 f8ba28
Level 10: 6de5fe 56b6f6 7a77ee 7d797d
Level 11: 7c1208 7e6da8
Level 12: 4dee3a

Level 0 -> left 401e90 right 74e167 --> Level 1 --> calculated 94c6f7
Level 1 -> left 94c6f7 right 7452e4 --> Level 2 --> calculated 2a64e9
Level 2 -> left 2a64e9 right d7026b --> Level 3 --> calculated c0fef4
Level 3 -> left c0fef4 right 52f798 --> Level 4 --> calculated c78419
Level 4 -> left c78419 right 6c42a4 --> Level 5 --> calculated eb9bf5
Level 5 -> left eb9bf5 right 85a86c --> Level 6 --> calculated 029fdb
Level 6 -> left 029fdb right 084481 --> Level 7 --> calculated 39d98e
Level 7 -> left 39d98e right e283e5 --> Level 8 --> calculated ccb90c
Level 8 -> left ccb90c right afc40c --> Level 9 --> calculated 232000
Level 9 -> left 232000 right cd54cf --> Level 10 --> calculated 6de5fe
Level 10 -> left 6de5fe right 56b6f6 --> Level 11 --> calculated 7c1208
Level 11 -> left 7c1208 right 7e6da8 --> Level 12 --> calculated 4dee3a
```

