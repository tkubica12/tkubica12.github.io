---
layout: post
published: true
title: Proč je snazší rozprášit lidstvo v šachu, než v Halo nebo Battlefield aneb Reinforcement Learning pro zelenáče
tags:
- AI
- ML pro zelenáče
---
Počítač sice v roce 1997 porazil Kasparova v šachu, ale v té době se ve střílečce Quake v podobě nepřátel choval jako dement - snadno jsem ho porazil díky lepší taktice. Vypadalo to, že Deep Blue je prostě jen nadrcený - v něčem variabilnějším, třeba ve hře go, nemá šanci. Smutné bylo, že nadrcenost superpočítače by se dala nějak okecat, ale v roce 2009 na mobilním zařízení HTC One Touch s operačním systém Windows Phone dosáhl jeden šachový robot ranku 2898 Elo (Kasparov měl nejvíc 2851), takže místo aby si velmistři takovou hračku strčili do kapsy doslova, ona to s nimi udělala obrazně. Takže tu máme tlustý starý telefon s Woknama co poráží nejlepší lidi. Pak ale AlphaGo vezme všechny historické přepisy zápasů hry Go a poté, co se na lidech vytrénuje na jejich úroveň, pokračuje dál a dostane se k hladinám mimo nás. V roce 2017 porazí nejlepšího lidského hráče Go. A aby toho nebylo málo, tak AlphaZero dosáhl v šachu Elo nad 3500 ale tak, že nikdy neviděl žádný tah lidského hráče. Hrál prostě jen sám se sebou, už se nepotřebuje učit od nejlepších lidí. A od prvních krůčků po šachovnici k eliminaci lidských šachistů mu stačilo 24 hodin trénování (pravda - na masivním clusteru, žádný Windows Phone), ve kterých se ještě mimochodem naučil hrát Go a Shogi. Depresivní? Nebojte, v Quake nebo něčem podobném už možná nebude úplný dement, ale na dobré lidské herní mlaďochy maniaky v otevřených světech nemá zatím šanci (asi jako já).

# Základní principy Reinforcement Learningu
Sithové v Hvězdných Válkách mají princip dvou - žáka a učitele. Žák se nejdřív učí, ale když se učiteli vyrovná, zabije ho a dostane se dál, výš - a vezme si pod sebe nějakého nového žáka. Pokud se vám stačí dostat k úrovni učitele, můžeme použít supervised learning - tak jako Deep Blue (Kasparova porazil protože získal hráčské zkušenosti ode všech, jeho učitelem bylo celé lidstvo). Pokud ale učitele nemáte nebo se chcete dostat ještě dál, musíte si poradit sami. Nicméně pricipy jsou to velmi podobné. Pokud máte učitele, sledujete, jak interaguje s prostředím a on vám říká co je dobře a co ne stejně, jako když CNN předhodíte obrázky s jasným popisem co na nich je nebo necháte Deep Blue studovat celou historii šachových partií těch nejlepších lidí na planetě. Když přijde čas, že jste už zabili svého učitele, nezbývá než zkoušet nové věci, experimentovat s akcemi v prostředí a sledovat jestli vedou k cíli nebo ne, tedy dostávat zpětnou vazbu, nějaké score, odměnu. To je samozřejmě proces daleko pomalejší, protože budete muset zjistit, že vyfukováním tabákového kouře do vody zlato nevznikne.

Architektura neuronek pro Reinforcement Learning je vlastně dost podobná těm běžným, třeba DNN nebo CNN, ale rozdíl je, že nevíme hned jestli provedené akce byly dobré nebo špatné. Musíme tedy udělat mnoho akcí za sebou, než se teprve dozvíme, jestli to vedlo k chtěnému výsledku nebo ne. Místo toho, že vám trénér řekne, že je v tenise dobré vracet balon tam, kde protihráč není a navíc ideálně do opačného směru jeho pohybu, protože změnit směr trvá dlouho, vás nechá zmateně běhat sem a tam ať si na to přijdete sami. Provedete tedy mnoho pohybů než konečně zjistíte, že ne, tohle nevede k cíli. Problém ale je, že z těch stovek, tisíců nebo desetitisíců akcí, co jste provedli možná ne všechny byly špatný nápad. Je přece rozdíl běžet opačně než kam jde míč versus běžet za míčem, máchnout a jen o kousek minout - výsledek je sice stejný, ale pro učení je dobré vědět jak moc jste mimo.

# Policy gradient a sparse versus dense reward
Právě to, že vaše odměna se nevztahuje k jedné konkrétní akci, ale tísicovce vašich kroků (mluvíme tu o tikotu obrazovky, mozku nebo něčeho takového - v každém frame počítačové hry se rozhoduji jestli jít pořád dopředu nebo teď už doleva, čili skutečně v jedné výměně jsou to stovky okamžiků, kdy se lze rozhodnout - pokud trvá jen 15 vteřin a v počítačové hře je FPS 30, je to 450 okamžiků pro vyhodnocení a rozhodnutí). Je tedy jasné, že ne všechno bylo šmahem špatně nebo dobře. Při učení tedy postupně utváříme politiku a počítáme policy gradient, který velmi pomalinku mění pravděpodobnost akcí. Pokud nevedly k odměně, o ždibec ji sníží, pokud to vedlo k získání bodu, RL bude s o malinko větší pravděpodobností tyto kroky opakovat. Stejný krok se tedy určitě běžně stane součástí událostí, které dopadly i nedopadly, ale v dlouhém horizontu přecijen převáží na správnou stranu. Tedy doufejme, je s tím pár problémů.

Optimální je, když RL jde za cílem a ne prostředky - výsledek je ta jediná důležitá metrika. Chceme úspěch a nic jiného než úspěch. Jenže - co kdybyste dostali za úkol zjistit co máte dělat na území celé Prahy bez jakýchkoli návodů nebo indicií? Dejme tomu, že skrytým cílem je dojít do jistého bytu na Praze 4 na sídlišti, tam otevřít poklop na půdu, otevřít střešní okno a zakřičet, že Babiš je bačkora. Teprve pak dostanete zpětnou vazbu typu ano, tohle bylo ono. Jaká je šance, že na to přijdete? Moc velká ne. Jestli to máte v rozumném čase rozlousknout, musím vám dát nějaké nápovědy typu "přihořívá". Když jste na území Prahy 4, když jste na nějakém sídlišti, když někde vlezete na půdu. To vás lépe navede na řešení. Místo sparse odměny až za skutečně vyřešený problém budete častěji dávat přídavné bodíky, ať má model zpětnou vazbu a může se učit. Jenže tohle má obrovský potenciál vás z cesty i svést - model se začne optimalizovat na odměny, které ale nejsou cíl, třeba si najde hranice Prahy 4 a bude jen dokola dělat krok dovnitř a ven a vydělávat. Existuje mnoho dost vtipných příkladů. Tak například tady má virtuální ruka dát jednu kostičku lega na druhou. Aby učení usnadnili dávají odměnu i za to, že bude spodní hrana stabilně výš, než na podlaze (aby model pochopil, že dává smysl zkoušet tu kosku dávat na tu první a pak už jen doladil přesnost tak, aby to zaklaplo do sebe) - hajzlík ale zjistil, že když ji prostě převrhne, dosáhne toho taky (spodní hrana je teď stabilně výš).


<iframe width="560" height="315" src="https://www.youtube.com/embed/8QnD8ZM0YCo?t=29" title="Deep Reinforcement Learning for Dexterous Manipulation -- Grasp and Stack" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Další slavný příklad je tahle lodička, kdy model dostal incentivu za sbírání vylepšení po cestě. Nakonec se na cíl vykašlal a jen si jezdí dokola a sbírá vedlejší odměny.

<iframe width="560" height="315" src="https://www.youtube.com/embed/tlOIHko8ySg" title="CoastRunners 7" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Vyladit odměny je tedy nesmírně obtížný úkol. Sparse reward rozhodně vede jen a pouze k očekávanému cíli, ale možná za téměř nekonečně dlouhou dobu - třeba musíte mít neuvěřitelné štěstí, aby na to model náhodnou kápnul a pak se toho držel. Dense reward může dramaticky zkrátit učení, ale možná model začne dělat věci, které vůbec cílem nejsou. Je to delikátní a náročné. Ale víte co? Ono to u lidí existuje taky - vezměte si třeba problematiku nastavení metrik odměňování v komerčních firmách. Cílem přece je maximalizovat hodnotu pro akcionáře, prostřednickým cílem je asi maximalizovat kvalitu produktu, spokojenost a podporu zákazníka, minimalizovat náklady, ale ve finále to skončí nějakou metrikou kolik jsi prodal zboží této kategorie, jiné kategorie přenásobené bulharskou konstantou a to všechno má výjimky a speciální incentivy jakože když prodáš tohle a k tomu i tohle, tak dostaneš 20% procent navíc a tak podobně. Pokud by byli lidi tak krátkozrací jako Reinforcement Learning (mno a upřímně občas takové najdete), budou výhradně maximalizovat tyhle metriky a nepřemýšlet o užitku pro zákazníka nebo maximalizaci dlouhodobé hodnoty firmy.

Druhý problém je u lidí taky k vidění - přeučování zlozvyků je náročné. Najdete si pohyb raketou, který vám umožní rozumně hrát a tak se ho držíte a jste úspěšní. Možná se ale v budoucnu stane limitem dalšího zlepšování a co když nebude po ruce trenér, který vám to řekne? Vrátit se na začátek, zpochybnit všechno a hledat nové cesty se ani lidem moc nechce - natož RL modelům. Tak například jedna z klasických úloh je dvourozměrný gepard - tělo a dvě nohy. Úkolem je naučit se takové pohyby, které geparda dostanou dopředu a to co nejvyšší rychlostí, tedy naučit se používat nohy k běhu. V jednom výsledku učení ale bylo vidět, že gepard nejprve udělá dopředné salto a pak se na zádech začne vrtět a kmitat, čímž se posouvá dopředu - a dělá to upravdu nejlépe jak to jen jde, nalezl lokální minimum. Ale z odstupem víme, že je lepší být na nohou, to se dá běžet rychleji, ale to by se musel zlozvyk přeučit. Stalo se to asi tak, že nejprve náhodně objevil, že salto dopředu opravdu vygeneruje dopředný pohyb, za což jsou odměny. Protože měl smůlu a všechno jiné co zkoušel nefungovalo, začal si to vštěpovat a to tak dlouho, až mu to zůstalo a pak se naučil jak se vrtět na zádech, aby pohyb pokračoval dál. 

# Jak si s tím pohrát
OpenAI má nádhernou knihovnu, které říká tělocvična. Začal jsem klasickým případem převráceného kyvadla (cart pole) - vozítko se hýbe do stran a tyčka směřující nahoru, která je tak velmi nestabilní a model s tím musí žonglovat (selže pokud mu spadne tyčka nebo pokud vyjede do strany z vyhraženého manévrovacího prostoru). Už na těchto příkladech se dá zažít dost zábavy i duchařiny - tak například v jedné kombinaci hyperparametrů (použil jsem dvě plně propojené skryté vrstvy - DNN) model zneužíval toho, že je stanoven maximální zisk (jinak by úloha běžela do nekonečna) třeba na 500 "snímků" (okamžiků pro změření kde tyč je a rozhodnutí, jestli se s vozítkem pojede doleva nebo doprava). Zhruba uprostřed času našel polohu, při které byla tyč mírně nakoněná do strany a on mírně přerušovaně šoupal vozítkem ve stejném směru. Strašná lenost - našel něco "stabilního", čemu stačil algoritmus - ale to jen díky tomu, že přes 500 už jsem mu to neměřil (v ten okamžik už vyjede mimo a prohraje). Když tenhle hotový model protáhnu na 1000 snímků, nebude dobrý. Změnil jsem pár hyperparametrů (zvětšil první skrytou vrsvu) a ejhle, už si žongloval udržitelným způsobem pěkně blízko středu. Sám jsem tak viděl, že stačí dost málo na to, aby model nedával dobré výsledky. V klasickém supervized learningu mi věci konvergovaly k řešení, tady i malé změny dělají divy. Říká se, že jsou i situace, kdy model dojde k naprosto odlišnému chování jen na základě náhodného rozložení startovacích vah (seed pro pseudogenerátor náhodných čísel). Prostě duchařina.

OpenAI Gym má i mnohem sofistikovanější prostředí, například celý seznam Atari her nebo 3D model pavouka. [Mrkněte]](https://www.gymlibrary.dev/)

# Zajímavé aplikace
Myslím, že je hodně zajímavé zjistit, kde Reinforcement Learning vlastně spíše není, ačkoli by to na první pohled dávalo smysl a čekali byste to. Tančící roboty dělající salta z Boston Dynamics jistě znáte.

<iframe width="560" height="315" src="https://www.youtube.com/embed/fn3KWM1kuAw" title="Do You Love Me?" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Podle náznaků (publikace, které vydávají) je ale celkem zřejmé, že tady není Reinforcement Learning žádný (a i strojového učení jako takového je celkem málo). Těchto úžasných výsledků pohybů podobných lidem a zvířatům je zatím lépe dosahovat tradičnějšími metodami typu ruční naprogramování nebo možná trochu supervised learningu, než RL. Stejně tak bych čekal u chatbotů, že se budou chtít takhle učit interakci s člověkem, ale když to zkoušel Microsoft v roce 2016, tak z něj veřejnost během 24 hodin vytrénovala nácka a muselo se to rychle zavřít. V případě autonomních aut zase úplně nemůžete říct "jejda, mrtvolka, tak příště to udělám lépe".

Ve finále RL aktuálně exceluje v hodně ohraničených problémech typu šachy nebo go, ale má své místo v kombinacích. Asi nejkřiklavější potenciální použití je autonomní vůz, kde se používá reinforcement learning v simulátoru, kde toho auto dokáže opravdu hodně virtuálně odřídit a učit se, ale kromě toho se pro takové auto používá ohromné množství supervised postupů. Ve finále při samotném řízení už tam toho RL zatím zas až tolik není. Podobně by dávalo smysl použít RL na časové řady v IoT oblasti, třeba pro automatizované řízení továrny. Zatím ale komerčně většinou dává větší smysl použít třeba běžné RNN pro detekci nějakých anomálií v reálném čase, k tomu mít DNN pro hloubkovou analýzu (například predictive maintenance) a řídící algoritmy mít klasické. Co třeba analýza léčiv? Zase bude dnes asi dávat větší smysl bezpečně data spíše analyzovat - zpětně vyhodnocovat působení léků nějakou neuronkou (DNN) a kombinovat to s matematickým předpovědním modelováním. RL by určitě umožnil robotům například uchopit objekt, který před tím ještě nedrželi - ale při výrobě aut to vlastně není potřeba. Díly jsou dopředu známé a po celou sérii se nemění, takže supervized learning by stačil.

Přesto - reinforcement learning má zdá se ohromnou budoucnost. Ostatní přístupy se snaží papouškovat lidi. Možná je předhonit v rozlišení, rychlosti zpracování a přesnosti, ale nemění základní přístupy k věci. Nedokáží se oddělit od svého učitele a přijít na to, jak dělat věci od začátku lépe. Dříve se prý při hře v šachy odhaloval podvodník, kterému tahy pomáhal generovat počítač tak, že jeho tahy byly moc předvídatelné. Dnes prý se odhalí spíše tak, že jsou jeho tahy inovativní, jiné a při tom velmi účinné a to díky reinforcement learningu. Zatím jsme asi stále schopni robotům ukazovat směr a učit je, ale to se může rychle změnit. Jsou oblasti tak složité, že nám možná unikají účinnější postupy - v řízení letecké dopravy (efekt jednoho zpožděného letadla na zbytek letů a cestujících je překvapivě nesnadné spočítat) nebo v ekonomice, na akciovém trhu, v biologických procesech nebo fyzice mikrosvěta. Je také jasné, že pokud je cílovou metou obecná umělá inteligence (taková jakou disponuje třeba člověk), tak na cestě k ní je reinforcement learning určitě dost důležitý. Ale i tak asi pořád trpí tím, že řeší korelace, ne kauzality. Klikání na šipku posunující Pacmana doprava koreluje s větší pravděpodobností vítězství, ale proč? Takhle daleko AI evidetně vůbec není, proto ani až vyladíme reinforcement learning dokonale, obecná inteligence to ještě asi nebude.
