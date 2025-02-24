---
layout: post
published: true
title: Vlastní data (RAG) pro vašeho AI agenta krok za krokem s Python a PostgreSQL
tags:
- AI
- PostgreSQL
---
Když se vás zeptám na nějaké faktické informace, třeba na něco z firemních směrnic, dám vám otázku z testu na Azure nebo jaký film doporučíte někomu, kdo viděl Matrix a chtěl by něco podobného, tak se můžete pokusit to udělat z hlavy. Budete mít možná problém si vzpomenou úplně přesně, možná uděláte i nějakou chybu, něco trochu popletete a když budu chtít, abyste citovali potřebné zdroje (na které stránce jakého dokumentu se o tom píše), tak často nebudete vědět, kde jste ke své znalosti přišli.

Srovnejte to ale s tím, když vám řeknu, že si klidně můžete před odpovědí pohledat po Internetu, prolistovat poznámky, prolétnout vytištěné směrnice nebo si zaklikat v Azure dokumentaci. Předpokládám, že tím se jednak výrazně zlepší přesnost vašich odpovědí a také mi řeknete, kde se o tom píše, ocitujete zdroje. Výborná věc. Jenže co když místo dobrého zacílení na určitou část dokumentace nebo směrnici vám nabídnu stránky z celé knihovny, ale bez přebalů a jakéhokoli řazení nebo indexování titulů? Pomůže to? Asi ano, ale bude vám to trvat mnohem déle, spotřebujete daleko víc energie a může se stát, že pokud naprostá většina stránek není pro odpověď důležitá, tak ztratíte pozornost a správné odpovědi si tam někde uprostřed nevšimnete.

To co jsem právě popsal funguje ve velkých jazykových modelech (LLM) taky a říká se tomu Retrieval Augmented Generation (RAG). Ideální je, když se model dostane k co nejlépe zacíleným dokumentům, ve kterých se skrývá odpověď a on tak může dávat naprosto přesné, rychlé a levné výstupy. Když se netrefíme a dáme mu dokumenty, které moc relevantní nejsou, odpovědi se zhorší. Když budeme mít model s velkým kontextem (podporou velkého množství vstupních tokenů) a nahrneme mu celou knihovnu, bude to drahé, pomalé a výsledky stejně nebudou tak dobré, jako v případě dobře zvolených referenčních dokumentů.

Dnes se chci zaměřit na problematiku hledání těch správných podkladů pro vaše LLM. Nebudeme tentokrát řešit přípravu dokumentů a jejich krájení ani složitější znalostní báze postavené na grafu provázaností a sumarizací. O tom jindy.

