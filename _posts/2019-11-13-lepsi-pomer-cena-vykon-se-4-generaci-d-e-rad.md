---
layout: post
published: true
title: Ještě lepší poměr cena/výkon se čtvrtou generací D/E řad v Azure
tags:
- Compute
---
Microsoft uvedl nové typy virtuálních mašich rodiny D a E. Čtvrtá generace je postavena na AMD procesorech a přináší nemalý nárůst výkonu a při tom nižší cenu. To je síla cloudu - jedete na vlně inovací trhu místo vlny pětiletých odpisů staré technologie.

# Řada Da/Ea v4
Novinka v Azure compute portfoliu je postavena na procesoru AMD EPYC 7452 v taktování min 2,35GHz (s možností burstingu výš za určitých okolností). Z pohledu konfigurací, tedy poměry cores, paměť a disk je stejná jako v3, ale na horní straně spektra umí nabídnout větší stroje. Maximum je Standard_D96as_v4 s 96 core a 384 GB paměti a Standard_E96as_v4 s 96 core a 672 GB RAM (v3 končí na 64 core). Nicméně v době psaní článku jsou plně dostupné jen modely do 32 core, větší jsou zatím v Preview.

# Proč se vylepšuje poměr ceny a výkonu
Z fyzickálních důvodů se taktování procesorů s posledním vývojem příliš nemění, ale inovace pokračují stále vysokým tempem. Jednak se vylepšuje architektura a instrukční sada, provádějí se optimalizace designu, zvyšuje se počet specializovaných součástí core (i uvnitř jednoho core je několik, třeba 6 a víc, pipeline obsahujících například aritmetické výpočetní jednotky, takže i uvnitř core dochází k jisté paralelizaci), velikosti a rychlosti cache a tak podobně, takže výkonnostní charakteristika každého core se zlepšuje. Druhým efektem je, že se na socket dává víc a víc jader, což ve finále snižuje cenu na core.

# Poměr cena/výkon od v1 do v4
Pro srovnání budeme potřebovat znát ceny VM a já ty historické nemám, takže se na ně budeme koukat v dnešních cifrách. To samozřejmě není úplně ideální, protože za těch pár let, co jsou v Azure k dispozici, se několikrát upravovala cena směrem dolů, takže historický kontext mít nebudeme. Nicméně i tak platí, že starší hardware je zkrátka méně efektivní a předpokládám, že to na ceně uvidíme.

Druhý ukazatel musí být výkon. Ten se v Azure dá najít v relativní hodnotě ACU, díky které můžeme systémy mezi sebou porovnat. Pokud vás zajímají i absolutní hodnoty, v dokumentaci najdete i standardní benchmarky.

Všechno budu srovnávat na konfiguraci D-řady s 2 core.

## v1
v1 odstartovala abecední polévku v Azure, kdy v roce 2014 doplnila stávající řadu A. U tohoto modelu jde o Intel Xeon ve verzi E5-2660 (původní varianta) nebo novější E5-2673 v3 nebo v4 (starší hardware se už neobnovuje). ACU je 160-250. Rozptyl je daní jednak turbo technologií (procesor se umí, když mu není vedro, přetaktovat nahoru, ale nikdy dopředu nevíte, co dalšího se na stroji děje, takže s tím nemůžete napevno počítat) a také rozptylem technologie (horní spektrum rozhodně není pro originální 2660). Budeme tedy brát pro jistotu nejhorší scénář, tedy 160.

Mašina stojí 103 EUR měsíčně, tedy asi 0,64 EUR za 1 ACU.

Největší dostupný stroj s poměrem CPU:RAM 1:4 má 8 core (16-core varianta měla víc paměti a dnešním jazykem to byl předchůdce "Éčka").

## v2
Druhá generace byla postavena na E5-2673 v3, později v4 a případně 8171M. ACU je 210-250.

Mašina stojí asi 84 EUR měsíčně, tedy 0,4 EUR za 1 ACU. Je tedy v poměru cena/výkon výrazně levnější, než v1.

Největší dostupný stroj v general purpose má 16 core.

## v3
Třetí generace přinesla výraznou novinku a jistou anomálii. v1 a v2 nemají Hyper-Threading, každý zákazník tak dostává fyzický core. To je samozřejmě dost neefektivní, protože HT z celkového pohledu přináší vyšší výkon a nebylo možné jej využít. Core v3 uvedené v roce 2017 už jsou HT-cores a aby se zabránilo efektu hlučného souseda, není k dispozici 1-core varianta (tam byste sdíleli jádro s jedním sousedem a to z důvodu předvídatelnost výkonu v běžné řadě není dovoleno). Protože je jádro HT, jeho výkon je nižší, než u předchozí generace, byť je hardware novější - 160-190 ACU. Nicméně s touto generací došlo k masivnímu nárůstu na vyšším konci spektra a provoz náročnějších systémů se tak dostal na výbornou cenovou dostupnosti general purpose řady (v předchozích generacích jste pro takové servery museli použít řadu G, která byla hodně drahá). Navíc má o 12% víc paměti na core.

A ještě jedna věc - licence software společností mohou uznávat, že v3 core je HT a tedy jsou dva HT na jeden fyzický, jako je to napříkald u Oracle. Jinak řečeno na v3 potřebujete poloviční počet licencí Oracle, než na v2.

Mašina stojí 74 EUR měsíčně, tedy 0,46 EUR za 1 ACU. Cenově tedy žádné zlepšení v oblasti malých mašin, ale dramatické zlepšení na vyšším konci řady díky možnosti použít D místo G.

Největší dostupný stroj v general purpose má 64 core.

## v4
Čtvrtá generace už nebude trpět přechodem na HT core, který už je od v3 standardem, takže bychom očekávali, že poměr cena/výkon bude příznivější, než u předchozí generace. Jak už jsem psal navíc dochází k dalšímu posunutí vyšší části spektra. ACU těchto AMD procesorů je 230-260.

Mašina stojí 71 EUR měsíčně, tedy 0,31 EUR za 1 ACU. 

Nejvyšší dostupný stroj v general purpose má 96 core.


Provozujete servery v Azure v rodině v3 a jedete pay-as-you-go režim (tedy nejste vázání rezervací)? Pak bych neváhal. Něco mezi 37% a 44% výkonu navíc a přitom je cena ještě dokonce o chlup nižší.