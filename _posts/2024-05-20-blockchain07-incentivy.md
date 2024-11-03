---
layout: post
published: true
title: Blockchain od začátečníka 7 - co za to mají (ekonomické pobídky ve veřejných sítích)
tags:
- Blockchain
---
Pokud si postavíte blockchain pro sebe (tam je samozřejmě otázkou, když sami sobě věříte, proč nemáte raději databázi a nezměnitelnost neřešíte kryptografickými důkazy jako je to v Azure SQL Ledger) nebo pro nějaké konsorcium firem (např. banky), tak náklady za výpočetní uzly buď prostě přidáte do své finanční rozvahy nebo budete mít něco jako členský poplatek. U veřejných masivně decentralizovaných sítí ale potřebujeme nějaký finanční mechanismus, pobídky, incentivy.

# Od těžby k poplatkům za transakce
Když vznikl Bitcoin, dostával ten, kdo zkompletuje blok (ted kdo první splní PoW), říká se mu těžař, odměnu ve formě Bitcoinů. Ta byla na začátku v roce 2009 ve výši 50 BTC. Tohle přiláká těžaře a ty nutně potřebujete, protože čím víc jich bude, tím je síť bezpečnější a vy jim chcete dát dobře předvídatelnou odměnu. Zároveň vyvoláváte mezi nimi soutěž - čím víc výpočetní kapacity do sítě vložím, tím větší pravděpodobnost, že dokončím blok, tedy že víc vydělám. Kromě toho těžař dostane i poplatky z jednotlivých transakcí (zaplatí ho konkrétní uživatel sítě), ale o tom ještě později. To ale znamená jednu důležitou věc - jde o nově vytištěné peníze a ty tak samozřejmě budou tlačit na inflaci, pokles hodnoty Bitcoinu. Faktem tedy je, že těžařům tak platí každý držitel Bitcoinu bez ohledu na to, jestli ho používá nebo jen drží. To není úplně fér - kdo nedělá transakce, nepotřebuje od sítě výpočty. Nicméně bez této incentivy by nebyli těžaři ochotni naskočit do hry. Mimochodem pokud si někdo vytěžil 50 BTC v roce 2010 za jediný zkompletovaný blok a drží je dodnes, má v peněžence asi 3,5 milionu dolarů.

Bitcoin je nastaven tak, že každých zhruba 210 000 transakcí se odměna za uzavřený blok sníží na polovinu. Protože Bitcoin se snaží upravovat obtížnost průběžně tak, aby výpočet PoW pro blok trval v průměru 10 minut (výpočetní kapacita sítě se může různě měnit a obtížnost to reflektuje), tak k tomuto snížení odměny dochází zhruba jednou za 4 roky (v dubnu tohoto roku se právě šlo z 6,25 BTC na 3,125 BTC). Nicméně popularita sítě už je v tento okamžik enormní a tak na rozdíl od začátků budou lidé ochotni za její používání přímo platit. Ne poklesem hodnoty Bitcoinu, ale přímo poplatkem za každou transakci, což je určitě spravedlivější. No a protože transakce zapisují těžaři, kterým poplatky jdou, tak logicky tyto budou mít tržní hodnotu a případný propad příjmů z těžby bude kompenzován tímto poplatkem. Je to nabídka/poptávka, ceny nikdo nediktuje. 

# Spropitné v transakcích
Transakce pro Bitcoin se uloží do mempool a z něj si těžaři vybírají transakce do svých bloků. Jaké si vyberou? Každá transakce umožňuje přiřadit spropitné, transaction fee. Těžař bude postupovat ekonomicky, takže si vybere ty s nejlepším spropitným. Problém samozřejmě je, že z pohledu výpočtů je řádek jako řádek, je úplně jedno jestli převádíte 5 korun nebo milion. To znamená, že u velkých transakcí můžete dát rozumné spropitné a pořád je to procentuálně v pohodě. Posílat 5 Kč je ale opravdu problém - běžný poplatek je minimálně v řádu jednotek dolarů a klidně vystřelí až na 50 USD v okamžicích, kdy je síť hodně zatížená. 

Tohle se v Bitcoinu dá řešit leda tak, že počkáte na nižší ceny (ale nikdy asi nebudou na 5 Kč) nebo u některých peněženek si můžete nabízené spropitné nastavit ručně a doufat, že na vás někdy přijde řada (pak ale můžete třeba měsíc čekat a stejně z toho nic nebude). Další varianta pokud například chodíte na pivo do stále stejné hospody, bude zapisovat si to s hospodským do sešítku a Bitcoiny pak poslat jednou za měsíc najednou. Ve finále pro tyto částky bude asi rozumnější využít nějakou síť druhého řádu, třeba Lightning Network (ta defacto dělá ty sešítky) a k té se určitě ještě někdy dostanu.

V novějších sítích jsou incentivy podstatně komplikovanější a chytřejší. Vezměme si Etherum. 

# Incentivy v Ethereu
V této síti dostane ten, kdo smontuje blok, také odměnu a ta se nazývá Consensus Reward. Na rozdíl od Bitcoinu není ale fixní a dopředu daná a ani tam její cena nějak plánovaně nepadá, ale je počítána na základě aktuálního zatížení sítě, nabídky a poptávky. Nicméně stejně jako u Bitcoinu jsou to nově vytištěné peníze, takže mají inflační tendenci a platí je tak každý majitel ETH bez ohledu na to, jestli dělá transakce nebo ne.

Tady ale přichází ke slovu další mechanismus - base fee. Jde o stanovený poplatek, který musel uživatel za svoji transakci vždy zaplatit. Síť ho používá k alokaci transakcí do bloků, ale to podstatné je, že po dokončení transakce se tyto peníze spálí. Nedostane je těžař, ale odeberou se z oběhu, takže tohle má deflační efekt - roste cena ETH. Tím zůstává těžařům incentiva za bloky, ale ztráta hodnoty ETH kterou tím všem způsobují může být kompenzována spálením poplatků, které hodnotu ETH zvyšují. Dá se tak říct, že base fee, které platí každý kdo udělá transakci, platí těžařům jejich práci, ale skutečně jen nepřímo.

Kromě toho, stejně jako u Bitcoinu, můžete přihodit priority fee, spropitné. Tohle je poplatek, který už jde přímo těžařům, takže ti budou do svých bloků vybírat transakce s největším spropitným. Typicky to celé vyjde třeba na 1 USD.

Situace je ještě ale složitější v tom, že transakce mají různou náročnost na výpočty, protože tady už nemluvíme jen o jednom stejném řádku, ale o podpoře Smart Contracts apod. Jednotkou spotřeby je gas - ale tyhle věci si necháme zase na jindy.

Ve skutečnosti může těžař v Etheru vydělat ještě víc tím, že bude různě spekulovat v jakém pořadí a které transakce si vybere. To se označuje jako MEV-Boost a je to jednak složité a jednak ne vždy úplně etické alespoň z pohledu spotřebitele. Tak například - front-running je situace, kdy uvidíte nějakou transakci (někdo nakupuje akcie třeba) a pokud byste tuhle informaci věděli dopředu, mohli byste toho využít (nakoupit rychle ještě levněji nebo tak něco). Tím že o transakci víte, ale ta není ještě v blockchain uložena, můžete toho využít a před tím dříve provést tu vaší transakci a něco na tom vydělat. Podobných situací je víc a je to dobrý přivýdělek. 

Příště už asi bude na čase vyzkoušet nějaký Smart Contract, protože na nich bude postavena řada dalších mechanismů a sítí druhých řádů, ke kterým se také dostaneme.