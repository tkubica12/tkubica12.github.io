---
layout: post
published: true
title: Jak to vidí počítač - Convolutional Neural Networks pro zelenáče
tags:
- AI
- ML pro zelenáče
---
Opět bez záruky správnosti sepíšu pár poznámek, co jsem se zatím dozvěděl o tom, jak počítače vidí. Projel jsem nějaký kurz, vyzkoušel pár praktických příkladů s Keras v Azure ML, poslechl nějaké přednášky na YouTube a vysál chytrého kolegu a zjištění jsou pro mě fascinující.

# Proč potřebuje vidění něco jiného, než plně propojené neuronky, které jsem popsal minule?
Posledně jsem popisoval, jak klasická neuronová síť vezme ve vstupní vrstvě jeden neuron pro každou vlastnost světa, na výstupní vrstvě jeden neuron pro každou kategorii nebo jen jeden neuron s číselným výsledkem regrese a mezi tím skryté vrstvy tak, že každý vstupní neuron je napojen na všechny členy další vrstvy v pořadí s tím, že svoje výstupy často ještě nelineárním způsobem modifikuje (například odřízne všechny záporné hodnoty nebo svůj výstup přeškáluje na číslo mezi -1 a 1 atd.). Postupným laděním parametrů weight a bias se najde řešení, které dobře funguje. Zajímavé pro dnešní téma je to, že jako prevence overfittingu se mohou použít dropout techniky, tedy efektivně se náhodně občas nějaké vazby zpřetrhají.

Některé mořské řasy mají světločivnou skvrnu, která jim umožňuje pohybovat se za světlem a nic moc víc se s tím dělat nedá. Naše oči ale mají rozlišení podstatně větší a každý pixel je vlastně neuron vstupní vrstvy. Tak například obrázek v dnes bychom řekli dost mizerném rozlišení 1024x768 má 786432 "vstupních neuronů" pokud je černobílý a třikrát tolik pokud je barevný (snímače ve fotoaparátech s tím trochu švidnlují a něco dopočítávají, takže jich pro barevný obraz tolik nemají, ale oproti šíleným fintám mozku je to nic). Jaké rozlišení má lidské oko? To je hodně problematická otázka, protože mozek nám jeho nedokonalosti bravurně tají. Ve skutečnosti je většina toho co vidíme černobílá a rozmazaná, ale oči neustále kmitají a mozek to skládá dohromady. Přestože tedy pocitově prý vnímáme rozlišení oka jako asi 576 megapixelů, tak jen 2 úhlové stupně ve středu vidíme ostře a s pořadnými barvami a tahle oblast má asi 7 megapixelů (a zbytek už tomu moc nepřidá - je to neustálé rychlé scanování okolí, které nám dává pocit velkého rozlišení). Buď jak buď pokud budeme mít neuronovou síť s plně propojenými vrstvami a ta vstupní má několik milionů neuronů, neupočítáme to.

Nicméně důvodů proč to není optimální je víc. Tak například u obrazu nechcete seřadit vstupy jen tak za sebou, protože jejich rozmístění v prostoru je zásadní (nechci přijít o informaci jaké pixely jsou pod sebou). Takto trénovaná síť by měla zásadní problém s overfittingem - stačila by nepatrná změna podmínek a všechno by se rozbilo. O stupeň jiné natočení, drobný posun zarámování, drobné rozmazání, jiný kontrast daný změnou v osvětlení. Potřebujeme spíše něco, co nebude od začátku vyhodnocovat obraz jako celek, ale bude v něm hledat nějaké vlastnosti a teprve z těch pak skládat další zjištění. 

# Image kernel - jednoduchá pravidla pro složité výsledky
Bylo pro mě překvapující zjistit, co filtry co znám z grafických programů ve skutečnosti dělají. Rozostřovací filtr pracuje tak, že začne vlevo nahoře a vezme si malý čtvereček, třeba 3x3 pixely. Filtr každé místo reálného 3x3 obrazu vynásobí svým "vzorečkem" nebo spíš 3x3 maticí (ta definuje chování filtru), vynásobí každý pixel, sečte to a výsledkem bude jeden pixel ve výsledném obrázku. Pak se čtvrteček po originálu posune (o jeden nebo o víc pixelů, podle nastavení - když to bude o jeden, tak bude mít výsledný obraz stejné rozlišení) a všechno se opakuje. Nádherně je to vidět [tady](https://setosa.io/ev/image-kernels/).

Blur filter bude fungovat tak, že prostřední pixel má váhu jen jedné čtvrtiny, tedy okolní pixely do značné míry ovlivňují výsledek. Rozdíly se tedy stírají a vzniká rozmazaná fotka. Sharpen filtr funguje opačně - akcentuje rozdíly, takže fotka bude působit ostřeji. Pokud s tímhle ale půjdeme do extrému, tak se dostaneme na Edge filtr, z pixelů sousedících s podobně vypadajícími kolegy udělá téměř nebo úplně černou a naopak pokud sousedí s rozdílnými pixely, tak bude výsledek skoro bílá. Takový filtr tedy detekuje ostré přechody, obrysy objektů (jako kdybyste obrázek překreslili jen tuží bez vybarvování). Nastavení Top Sobel zareaguje vysokým číslem (bílou barvou), když první řádek bude hodně světlý a dolní hodně tmavý, čili detekuje horizontální ostré linie ze světla do tmy, ale ne z tmy do světla nebo ty vertikální. Filter (kernel) tedy prochází obrázek kousek po kousku a detekuje v něm nějakou vlastnost a výsledky zapisuje do nové mapy, feature mapy, kterou lze intepretovat jako další obrázek.

Základem convolutional vrstev neuronové sítě je právě tohle, ale parametry filtru nejsou dopředu dané, ty právě chcete, aby neuronka hledala sama. 

# Convolutional Neural Network
Po vstupní vrstvě představující pixely tedy nenásleduje skrytá vrstva, která by byla plně propojená, ale naopak neurony (pixely), které představují výsledek operace (a aktivační funkce) jen na malém lokálním kousku vstupních dat (třeba právě ty 3x3 políčka). Pokud bychom zkusili jen jeden filtr s posunem o 1 pixel, bude výsledkem feature mapa ve stejných rozměrech, jako vstupní obrázek (resp. při použití paddingu, abychom se dostali až do okraje). Můžu mít ale políčko definované jako 4x4 a pohybovat se po dvou pixelech, pak bude výsledné rozlišení menší. Podstatné ale je, že ve vrstvě bude víc, než jeden filtr. Necháte si takhle projet obrázek jednou, ať se detekují horizontální hrany, jednou ať ty vertikální a tak podobně - ale s tím rozdílem, že ve skutečnosti zadání "co má ten filtr dělat" tomu nedáváte. To si má právě síť trénováním zvolit sama. 

Výsledkem je, že z jednoho obrázku máme několik stejných nebo menších obrázků ve formě feature map. Typicky teď uděláme downsampling, například max polling. Rozsekáme obrázek na čtvrečky o velikosti 2x2 a nahradíme je jediným pixelem ve výsledku, který bude maximum z těchto hodnot. K čemu je to dobré? Dat nebude tolik, sníží se citlivost na overfitting (trohu se to "zamázne"), ale asi nejzajímavější je, že tím vlastně odzoomováváme. Nejprve tedy síť hledá vlastnosti v malém měřítku, třeba 3x3 originálního obrázku, ale jak postupuje sítí, tak se zaměřuje na stále větší a větší záležitosti. 

V další vrstvě postup opakujeme - už zpracované obrázky prochází další filtr, pak se downsampluje, pak zase jedou filtry a tak podobně několikrát za sebou. Ve výsledku v prvních fázích si neuronka vytahuje spíše jednoduché vlastnosti typu detekce hran, přechodů, obrysů apod. zatímco později už nad těmito vlastnostmi začíná rozpoznávat složitější kousíčky, třeba uši nebo nos. Nicméně ty "kousíčky", vlastnosti, možná vůbec nejsou takové, jak je vnímáme my. Pro počítač je možná důležité něco jiného. To mimochodem přináší zajímavé problémy v hackování AI, kdy jste schopni navodit situaci, kdy model donutíte klasifikovat naprosto nesprávně, ale lidský pozorovatel si rozdílu nevšimne. Viděl jsem třeba obrázky, kde jsou změny na úrovni pixelů, takže při pohledu člověka je to pořád panda, jen trochu "zašuměná", ale AI je kompletně zmateno. Umím si třeba představit, že abyste unikli rozpoznání obličeje na ulici, bude se dát nějak nenápadně namalovat tak, že ostatní si sice řeknou, že že jste divný hipster, ale určitě člověk a poznat vás dokážou, ale AI si myslí, že jste pes.

# Klasifikace
Na konci toho všeho už se asi nedá úplně mluvit o obrázcích, ale skutečně spíše o mapách vytažených vlastností, takže můžeme nasadit klasičtější neuronku na klasifikaci. Nejprve přes flattening sťukneme data do jedné vrstvy a nasadíme plně propojenou další vrstvu (dense layer), jak známe z předchozího článku a zakončíme to softmax funkcí pro detekci kategorií.

Takže někde na tom obrázku je kráva a vidle. Super. Ale kde?

# Jak dál k detekci objektů nebo sémantické segmentaci
Nejdřív mi nemohlo docvaknout, co je na tom ukázat, kde ty vidle jsou, ale klíčová vlastnost CNN oproti jiným postupům je právě to, že není citlivá na to, jestli jsou vidle vpravo, vlevo nebo jsou nějak natočené. Klasifikační vrstva nad tím pak informace o umístění ztratí, takže první pokusy o detekci umístění objektu se dělaly tak, že si odhadnete obdelníček z původního obrázku a zkusíte ho prohnat klasifikací. Pak ho posunete a opakujete až na konec zdrojového obrázku. A pak totéž pro menší a větší obdelníček a pořád dokola - strašně neefektivní. Pozdější postupy přinesly určitá vylepšení, tak například místo zkoušení všech možných variant vám R-CNN (R znamená Region) nejprve navrhne, kde by mohly být nějaké objekty (zkusí vám navrhnout pravděpodobné rámečky případných objektů), takže místo nekonečného množství variant jich zkoumáte třeba jen 2000. 

Jedním z dalších evolučních kroků je následující myšlenka označovaná Yolo. Rozdělíme si obrázek na dlaždice a pro každou dlaždici provedeme klasifikaci. Ta sice teď bude méně přesná (místo celého psa vidí klasifikace jen jeho nohu), nicméně dostaneme třídy pro každou dlaždici, které pak lze spojit do rámečků a v nich vyzkoušet klasifikaci. Problém ale je, že čím menší je dlaždice, tím horší je klasifikační výsledek.

Jiný problém (a s ním spojený přístup) je sémantická segmentace, tedy to, že chci objekt najít úplně přesně - ne říct, že je na obrázku, ani ne, že je v nějakém čtverci. Chci každý jeho pixel znát, vědět přesně jeho okraje. Proč? Když si v Teams zapnete virtuální pozadí, je potřeba najít váš obličej, ten nechat a vše ostatní přemalovat pozadím. Nevím tedy co se na to používá, ale je to takový jednoduchý příklad situace, kdy potřebuji vědět přesně kde jste a to na pixel správně. Samozřejmě ve vážnějších použitích se to bude taky hodně hodit - tak například ve zdravotnictví je určitě užitečné najít snímky s výskytem rakoviny, ale schopnost ji i přesně lokalizovat to posouvá na novou úroveň.

Přístup, který tohle zdá se dokáže, spočívá v tom, že se neuchýlíme ke klasické klasifikační vrstvě, ale budeme pokračovat v CNN přístupu (F-CNN). Tak jak postupně ztrácíme rozlišení (s cílem identifikovat vlastnosti na úrovni větších a složitějších objektů), tak se můžeme pokusit vrátit ho spátky použitím upsamplingu. Výsledkem v zásadě je, že takto nakonec provedeme klasifikaci jednotlivých pixelů. Zní to dost šíleně, ale budeme se ptát, jestli tenhle pixel je spíš součást psa nebo kočky. To, že to jde, je díky tomu, že nedochází ke ztrátě kontextu a topologie. Díky tomu jste pak schopni identifikovat objekty s vysokou přesností ohraničení - moje Teams evidentně takhle daleko ještě nejsou, ale dává to smysl.

Počítačové vidění je úžasné. Pokud máte nápady a připomínky, piště mi na LinkedIn. Příště zase pro zelenáče na další oblasti strojového učení.
