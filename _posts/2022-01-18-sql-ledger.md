---
layout: post
title: 'SQL Ledger - kostičky, řetízky a kryptografická auditovatelnost vašich dat bez složitostí'
tags:
- SQL
- Security
---
Azure SQL Database a SQL Server 2022 podporují funkci Ledger, která dokáže všechny změny v datech kryptograficky označovat, zabalit do bloků a ty navázat jeden na druhý - udělat řetěz bloků, blockchain. Ne - není to ani nová platební měna, ani platforma pro NFT nákupy puberťáků, ani nevytváří nějaký distribuovaný systém, kde si účastníci nevěří. Ale některé vlastnosti blockchain tím získává, například ochranu před neoprávněnými změnami dat, a současně netrpí jeho nedostatky jako je nutnost přepsat aplikace, omezení propustnosti transakcí nebo větší spotřeba hardware. Zkusil jsem se na to laicky podívat.

Pozor - nejsem datař a ve skutečnosti tomu moc nerozumím. Ale přišlo mi zajímavé si to ozkoušet a trochu pochopit, třeba se vám to taky bude hodit. Pokud chcete jít do hloubky, zdá se, že v dokumentaci je detailů opravdu dost.

Kde to bude mít využití? Pojďme si to nejdřív zkusit a pak se nad tím zamyslet. Je zřejmé, že to bude všude tam, kde je potřeba prokázat, že data v SQL nikdo neoprávněně nezměnil - audity, dokazování jiným subjektům (třeba klientům, regulátorům) a tak podobně.

Funkce Ledger v Azure SQL Database se dá zapnout klikáním v portálu - fajn, to zvládnu.

[![](/images/2021/2021-11-26-07-49-28.png){:class="img-fluid"}](/images/2021/2021-11-26-07-49-28.png)

[![](/images/2021/2021-11-26-07-49-49.png){:class="img-fluid"}](/images/2021/2021-11-26-07-49-49.png)

Teď přijde důležitá věc. Mít bloky uložené v SQL asi nebude plnit svůj účel - pokud se útočník do SQL dostane a může bloky měnit, není to dobré. Změní data, přepočítá bloky a celé je to k ničemu. Bloky tedy potřebuji dostat ven a to jde buď manuálně (kamkoli, třeba na vaší USB flashku) nebo automaticky a nativně se podporují hned dvě technologie:

- Můžu použít Azure Blob storage v immutable režimu (WORM), která zajistí, že data nelze smazat ani modifikovat. V tento moment musím věřit této službě, že to opravdu tak bude (s tím bych určitě neměl problém, ale rozumím, že v některých situacích nechci, aby neexistovala žádná autorita, které je potřeba věřit).
- Použiji Azure Confidential Ledger, tedy plnokrevný distribuovaný blockchain. Tady nemusím věřit Microsoftu a potažmo jsem získal technologii skutečněho blockchainu a přitom používám stále svůj SQL, který znám a aplikace se nemusí měnit. K tomu se ještě vrátíme.

[![](/images/2021/2021-11-26-07-50-11.png){:class="img-fluid"}](/images/2021/2021-11-26-07-50-11.png)

Výborně, databáze je připravena. Teď bych měl vytvořit tabulky, u kterých tohle zapnu. Ledger nabízí dvě varianty:
- Append only tabulky - tam je to samozřejmě jednodušší, protože jediná povolená operace je INSERT. Čili data nelze mazat ani modifikovat, stačí tedy při každém vložení vytvořit příslušné hash (obsahují hash řádku, transakce, timestamp a uživatele) a je to. Takový přístup je určitě dobrý pro záznam událostí (někdo prošel turniketem, přihlásil se do systému), ale nebude ideální pro aplikaci, která drží v tabulkách stavy účtů nebo zásob (resp. aplikace může využívat patterny jako je event sourcing a append-only je pak pro ni ideální a místo transakcí jede saga pattern, ale to znamená to víceméně celé přepsat).
- Updatable tabulky - ty podporují INSERT, UPDATE i DELETE. Tím je to trochu složitější, protože kryptograficky potřebujeme dokázat nejen, že vložená data nebyla neoprávněně změněna nebo zlikvidována, ale zaznamenat i historii změn. To se řeší tím, že je přidána history table, která drží předchozí verze hodnot řádků, které jsou změněny nebo smazány. Tohle by mělo fungovat i se stávající aplikací bez potíží.

```
CREATE TABLE dbo.TestAppendOnly (
    Message nvarchar(100)
)
WITH (SYSTEM_VERSIONING = ON, LEDGER = ON);

CREATE TABLE dbo.TestUpdate (
    Message nvarchar(100)
)
WITH (SYSTEM_VERSIONING = ON, LEDGER = ON);
GO
```

No vida - kromě mého sloupečku Message nacházím v tabulce záznamy o transakcích.

[![](/images/2021/2021-11-26-08-25-33.png){:class="img-fluid"}](/images/2021/2021-11-26-08-25-33.png)

Je načase naházet tam data.

```
INSERT INTO dbo.TestAppendOnly (Message) VALUES ('My first message'), ('My second message'), ('My third message');
```

Jsou tam?

```
SELECT Message,
       ledger_start_transaction_id,
	   ledger_start_sequence_number
 FROM [dbo].[TestAppendOnly]
```

[![](/images/2021/2021-11-26-08-25-11.png){:class="img-fluid"}](/images/2021/2021-11-26-08-25-11.png)

Jsou - vidím číslo transakce i očíslované změny řádků (každý řádek v transakci změněný bude také mít svou hash, takže celé je to kompilát hash řádků, identitifikátoru transakce, časového razítka a jména uživatele a tohle celé se pak nahází do bloků, z kterého se udělá hash a to tak, že ta zahrnuje i referenci na blok předchozí).

Jak se bude chovat updatovatelná tabulka?

```
INSERT INTO dbo.TestUpdate (Message) VALUES ('My first message'), ('My second message'), ('My third message');

UPDATE dbo.TestUpdate 
SET Message = 'My modified message' 
WHERE Message = 'My first message';

SELECT TOP (1000) * FROM [dbo].[TestUpdate_Ledger] ORDER BY ledger_transaction_id
```

[![](/images/2021/2021-11-26-08-39-46.png){:class="img-fluid"}](/images/2021/2021-11-26-08-39-46.png)

Zdá se, že stroj pracuje, výborně. Podívám se do storage a vidím, že Azure SQL už vyexportoval nějaké bloky.

[![](/images/2021/2021-11-26-08-31-30.png){:class="img-fluid"}](/images/2021/2021-11-26-08-31-30.png)

```json
{
    "database_name": "sql-ledger-db",
    "block_id": 0,
    "hash": "0x791A1A5F475863757F8FE2241699C66F54DE870C01C7496F695FEE1D55998FE7",
    "last_transaction_commit_time": "2021-11-26T07:04:22.5233333",
    "digest_time": "2021-11-26T07:04:45.9463904"
}
{
    "database_name": "sql-ledger-db",
    "block_id": 1,
    "hash": "0xEC846DAB2D3B4CD7CA2DBA94C2B2492DCA856B0E350C5B2427D20E49EADCFCBA",
    "last_transaction_commit_time": "2021-11-26T07:19:26.9133333",
    "digest_time": "2021-11-26T07:19:28.4231909"
}
{
    "database_name": "sql-ledger-db",
    "block_id": 2,
    "hash": "0xC547DB659022927872B8DA601678B07F3CC9B5E26DFA51D5F0B614459835F5F2",
    "last_transaction_commit_time": "2021-11-26T07:28:57.5900000",
    "digest_time": "2021-11-26T07:29:10.2101949"
}
{
    "database_name": "sql-ledger-db",
    "block_id": 3,
    "hash": "0xB15A5E94FC4533356A13E628C856FFF68B7453F3F0036B4A6CF9932F184F9016",
    "last_transaction_commit_time": "2021-11-26T07:30:37.4600000",
    "digest_time": "2021-11-26T07:30:55.5079230"
}
```

Storage mám aktuálně nezabezpečenou co do Write-Once-Read-Many, tak bych měl tuto funkci zapnout. Pro moje účely si to zamknu jen na 7 dní, ale šlo by to samozřejmě udělat na neomezenou dobu.

[![](/images/2021/2021-11-26-08-58-12.png){:class="img-fluid"}](/images/2021/2021-11-26-08-58-12.png)


SQL obsahuje uložené procedury, které mohu použít na ověření dat - nehrabal se mi v nich někdo?

```
EXECUTE sp_verify_database_ledger N'
[
    {
        "database_name": "sql-ledger-db",
        "block_id": 0,
        "hash": "0x791A1A5F475863757F8FE2241699C66F54DE870C01C7496F695FEE1D55998FE7",
        "last_transaction_commit_time": "2021-11-26T07:04:22.5233333",
        "digest_time": "2021-11-26T07:04:45.9463904"
    },
    {
        "database_name": "sql-ledger-db",
        "block_id": 1,
        "hash": "0xEC846DAB2D3B4CD7CA2DBA94C2B2492DCA856B0E350C5B2427D20E49EADCFCBA",
        "last_transaction_commit_time": "2021-11-26T07:19:26.9133333",
        "digest_time": "2021-11-26T07:19:28.4231909"
    },
    {
        "database_name": "sql-ledger-db",
        "block_id": 2,
        "hash": "0xC547DB659022927872B8DA601678B07F3CC9B5E26DFA51D5F0B614459835F5F2",
        "last_transaction_commit_time": "2021-11-26T07:28:57.5900000",
        "digest_time": "2021-11-26T07:29:10.2101949"
    },
    {
        "database_name": "sql-ledger-db",
        "block_id": 3,
        "hash": "0xB15A5E94FC4533356A13E628C856FFF68B7453F3F0036B4A6CF9932F184F9016",
        "last_transaction_commit_time": "2021-11-26T07:30:37.4600000",
        "digest_time": "2021-11-26T07:30:55.5079230"
    }
]
'

Query succeeded: Affected rows: 0
```

Počítač je spokojen. Neumím uvnitř SQL teď udělat něco nepěkného a data změnit beze stop (možná nějaká machinace se zálohou?), ale vyzkouším si to obráceně - pozměním hash záznamy o blocích, takže by data už neměla sedět.

```
Failed to execute query. Error: The hash of block 2 in the database ledger does not match the hash provided in the digest for this block.
Ledger verification failed.
```

Funguje to. Prohlédnu si i transakce a bloky.

```
SELECT * FROM sys.database_ledger_transactions
```

[![](/images/2021/2021-11-26-13-22-22.png){:class="img-fluid"}](/images/2021/2021-11-26-13-22-22.png)

```
SELECT * FROM sys.database_ledger_blocks
```

[![](/images/2021/2021-11-26-13-23-01.png){:class="img-fluid"}](/images/2021/2021-11-26-13-23-01.png)

Pro mou úroveň (ne)znalosti datařiny tohle stačí. Jak by se to tedy dalo použít?
- Možná jsou třetí strany, které si principiálně nevěří a já mezi nimi zprostředkovávám obchody (jsem třeba realitka, galerie nebo Airbnb). Jasně, blockchain by byl skvělé řešení, ale jeho propustnost může být pro účely třeba Uberu moc malá. Navíc je to složité. Mohl bych tedy provozovat na transakce klasicky SQL, ale kryptografické důkazy poskytovat všem svým partnerům.
- Mám systém pro zabezpečení přístupu do laboratoře a k jednotlivému vybavení. Kdyby se cokoli stalo, musím mít jistotu, že uložené záznamy nikdo neupravoval (po té co v labu vytvořil novou smrtící verzi Covid Fí). Jsem ale chudý ústav, granty mám na přístroje, ale programují to dva studenti. Trochu extrémní ... každopádně zapnutím Ledger nad SQL, pro který je ta stará aplikace napsaná, a exportem bloků do cloudu, bych měl auditovatelnost získat.
- Potřebuji systém s vysokou transakční propustností a přesto bych to potřeboval zabezpečit v blockchain síti. Použiji tedy SQL jako off-chain transakční systém, který ale z velkého množství dat vytváří hash bloků, které pak ukládám do blockchain sítě.
- Potřebuji vyřešit ukládání auditních informací o událostech, umím SQL a potřebuji to rychle a levně. Použitím Ledger nemusím vymýšlet žádno složitosti a novoty.
