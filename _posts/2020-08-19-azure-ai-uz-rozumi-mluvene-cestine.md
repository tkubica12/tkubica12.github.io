---
layout: post
published: true
title: Azure AI už rozumí mluvené češtině - jak si v tom vede cloudová trojka Microsoft, Google a Amazon?
tags:
- AI
---
Tento měsíc přistála do Azure kognitivních služeb příjemná aktualizace a to konkrétně podpora češtiny pro speech-to-text API. Nechtěl jsem se nechat zaskočit celkovým počtem podporovaných "jazyků" u třech cloudových hráčů, protože občas tam naleznete 20 podob arabštiny, 20 podob angličtiny a 10 variant španělštiny. Co mě zajímá je zkrátka čeština. Jak si v této oblasti stojí Microsoft ve srovnání s Google a AWS?

# Podpora češtiny ve třech hlavních cloudech
Kupní síla celkového množství osob mluvících česky samozřejmě není v celosvětovém měřítku nijak závratná, takže nezbývá než se trochu smířit s tím, že v seznamu priorit globálních hráčů není na samém vrcholu. Čím víc produktů a služeb by podporu češtiny využilo, tím větší šance, že se objeví. Základní věci typu překlady z a do češtiny jsou ve všech třech službách na výborné úrovni. Ale co převod mluveného slova na text a naopak? U Google díky konzumerskému zaměření, telefonům a méně štráchám s ochranou dat bych očekával podporu nejširší, u Microsoftu naopak díky jeho firemnímu zaměření a brutální ochraně dat (méně "dobrovolných" testerů) slabší, u AWS vzhledem ke cloudové pozici a Alexe někde mezi? Pojďme mrknout jak to vypadá.

V době psaní článku, pokud to dobře čtu, umí Google speech-to-text i text-to-speech (syntézu řeči), AWS neumí česky ani v jednom z oborů a Microsoft od tohoto měsíce umí speech-to-text a už nějakou dobu text-to-speech (ačkoli v režimu "standard", některé jazyky podporují dokonalejší "neurální" model a v něm čeština ještě není). Pokud tedy potřebujete řešení od globálního hráče za velmi dobré peníze bez závazku a licencí a chcete mít jistotu ochrany dat na nejvyšší úrovni, Microsoft je od tohoto měsíce myslím perfektní volba. 

Pojďme si Azure API vyzkoušet a nevědecky ho srovnat s Google.

# Vyzkoušejme Speech-to-text v Azure
Nejprve si stáhnu CLI, aby se mi to dobře zkoušelo.

[https://aka.ms/speech/spx-zips.zip](https://aka.ms/speech/spx-zips.zip)

Vytvořím si v Azure Speech-to-text službu a poznamenám si její API klíč.

![](/images/2020/2020-08-17-21-06-39.png){:class="img-fluid"}

![](/images/2020/2020-08-17-21-07-57.png){:class="img-fluid"}

![](/images/2020/2020-08-17-21-08-43.png){:class="img-fluid"}

V CLI, například v PowerShellu, nastavím klíč a zapnu nahrávání z mikrofonu. Rovnou na obrazovce bude naskakovat proces zpracování mého hlasu.

```powershell
.\spx config "@key" --set SUBSCRIPTION-KEY
.\spx config "@region" --set westeurope

.\spx recognize --microphone --source cs-CZ
SPX - Azure Speech Service Command Console, Version 1.13
Copyright (c) 2020 Microsoft Corporation. All Rights Reserved.

  audio.input.type=microphone
  diagnostics.config.log.file=log-{run.time}.log
  output.all.audio.input.id=true
  output.all.recognizer.recognized.result.text=true
  output.all.recognizer.session.started.sessionid=true
  service.config.key=001122334455
  service.config.region=westeurope
  source.language.config=cs-CZ
  x.command=recognize

SESSION STARTED: 3a39059ce7bb43589ac80e6fb1abb3b5

Listening; press ENTER to stop ...

Connection CONNECTED...
RECOGNIZING: ahoj
RECOGNIZING: ahoj nebo
RECOGNIZING: ahoj robotem
RECOGNIZING: ahoj robote
RECOGNIZING: ahoj robote umíš
RECOGNIZING: ahoj robote umíš už
RECOGNIZING: ahoj robote umíš už česky
RECOGNIZED: Ahoj robote umíš už česky?

<ctrl-c> received... terminating ... 
```

První pokus je úspěšný. Syn zrovna poslouchá nějakého YouTubera - dávám mikrofon k jeho počítači a zkouším.

RECOGNIZED: Sponzor tohoto videa world of warships týmové námořní bitvy, které vyžadují odlišnou strategii. A tak to samozřejmě můžete hrát i se svými přáteli. Hra obsahuje více než 200 historických lodí, které můžete ovládat krásné mapách a jedinečných realistických krajinách. V bitvě se dokonce mění počasí a má to ohromující grafiku.

Funguje to velmi obstojně.

# Nevědecký test Microsoft vs. Google
Už z předchozího je vidět, že systém občas udělá nějakou chybu, ale obvykle ne takovou, aby se výsledek nedal pochopit. Pokud s klidnou hlavou čtete výsledek, určitě si chyb všimnete, ale pochopíte o co jde. Pokud jste ale neslyšící, tak je možnost číst titulky v reálném čase bez nutnosti u všeho mít živého zapisovatele výborná věc. Představte si kolik přímých přenosů může mít titulky? Kolik asi existuje archivních záznamů a televizních pořadů, ke kterým titulky nejsou a není v lidských silách je dopsat? A co takové Teams meetingy, kde se bavíte o důležitých věcěch, ale zapomenete zvolit chudáka, který má udělat zápis? Co kdyby místo toho nějaký robot přepsal rozhovor do textu (pokud s tím všichni účastníci souhlasí) a umožnil v něm fulltextově vyhledávat včetně metadat? Kolik hovorů na lince podpory končí v archivu jen jako audio záznam, na kterém se nedá nic analyzovat, jen ho otevřít při řešení stížnosti? Zkrátka chci říct, že drobné nepřesnosti jsou nesnesitelné pro knižní vydání, ale dokážou přinést výborný užitek i bez 100% preciznosti (ostatně ono řečníci často už při "vysílání" dělají chyby, které náš slyšící mozek opravuje, aniž bychom si toho všimli a jsme v tom hodně dobří - když to pak vidíme doslova napsané, vypadá to jinak).

Vzal jsem kousek ze zpráv Radiožurnálu, uložil jako WAV a prohnal to přes Google a Microsoft.

**Google:**

Pokud naše 50000000 na by podle návrhu ministerstva zemědělství mohla hrozit za prodej potravin v různé kvalitě, ale stejném obalu v Česku a v jiných evropských zemích novela zákona o potravinách, kterou dnes schválila. Vláda by měla také posílit pravomoci státní Zemědělské A potravinářské inspekce a rozšířit možnost označit potravinu za Českou ladanový schválila novelu o ochraně spotřebitele najím, že základě zboží pod stejným obalem bude muset mít stejné složení jako v jiném členském státě Evropské unie.

**Microsoft:**

Pokud až 50 milionů korun by podle návrhu ministerstva zemědělství mohla hrozit za prodej potravin v různé kvalitě, ale stejném obalu v česku AV jiných evropských zemích. Novela zákona o potravinách, kterou dnes schválila vláda, by měla také posílit pravomoci státní zemědělské a potravinářské inspekce a rozšířit možnost označit potravinu za českou. Vláda navíc schválila novelu o ochraně spotřebitele, na jejímž základě zboží pod stejným obalem budou muset mít stejné složení jako v jiném členském státě evropské unie.

Oba texty jsou pochopitelné a vypadají rozumně. Hned na začátku se oba roboti nevypořádali s komentátorem říkajícím "pokuta až 50 milionů korun", ale ten Microsoftí to dal o kousek lépe. Z dalšího textu myslím, že Microsoft to trefuje přesněji a například Google je hladový a místo "na jejímž" říká "najím". Microsoft mi přijde také lépe chytl interpunkci a větnou stavbu. 

Ale jak říkám - tohle srovnání rozhodně není vypovídající, ale minimálně naznačuje, že vstup Microsoftu na české území co do speech-to-text je dost povedený. 

Syntéza řeči je rovněž dostupná u obou hráčů a nejsem odborník, tak posouzení nechám na vás. Microsoft model by měl být tradičnější a čeština není k dispozici v hlubším systému modelů (neural). Nicméně když poslouchám výsledek zdá se mi, že Microsoft je na moje ucho podstatně přirozenější v toku řeči, tedy intonaci a pauzách na konci vět a v souvětích, kde to Google mastí moc za sebou. Hlasově je ale Google řekl bych přirozenější a nevkrádá se mu tam nějaké to digitální zadrhnutí (podobné když vaše Bluetooth sluchátka na okamžik chytí horší signál). Google také lépe pochopil, že je v českém textu v závorce anglický výraz a stejným hlasem to přečetl s relativně anglickou výslovností, zatímco Microsoft s českou. Mimochodem když si oba pustím v angličtině, přijdou mi senzační a neuměl bych vybrat, který je lepší. Možná je to menší citlivostí na cizí jazyk (přecijen ten mateřský máme zadrátovaný podstatně hlouběji), složitostí češtiny nebo zkrátka její menší probádaností co do AI modelů, ale ta angličtina mi zní hodně věrně - kdybych neviděl obraz, například šlo o nějaké nahrané webové školení, myslím, že bych nevěděl, jestli je to namluvené člověkem nebo robotem. Na živém webináři i bez obrazu obličeje samozřejmě poznáte, že je ta osoba nějaká prkená a ani se neusměje, nepraští omylem do mikrofonu, nezafuní a nezakřičí jí tam dítě, takže je buď robot nebo přinejmenším nudná jak robot :)

Azure varianta: [https://azure.microsoft.com/cs-cz/services/cognitive-services/text-to-speech/#features](https://azure.microsoft.com/cs-cz/services/cognitive-services/text-to-speech/#features)

Google varianta: [https://cloud.google.com/text-to-speech](https://cloud.google.com/text-to-speech)

Mluvil jsem o přepisech, překladech a titulkování. Nutno říct, že pro ještě pokročilejší AI aplikace bude nutné ještě mít schopnost pochopit smysl textu, vytahovat hlavní záměr, klíčová slová nebo analyzovat sentiment. Tam ještě globální hráči moc nejsou - ani jeden. Tam nezbývá, než češtinu prohnat překladem, což nemusí být problém, ale přecijen se část informace může znepřesnit. Nicméně schopnost komunikace s uživatelem nejen přes klávesnici, ale slyšet ho a mluvit na něj je důležitá podmínka pro řadu aplikací.

Tak mnoho zdaru s roboty co umí česky!