---
layout: post
published: true
title: "Velké jazykové modely v AI: Blábolení, které začalo být zatraceně užitečné"
tags:
- AI
---
Jak všechny ty velké jazykové modely, které teď mají takovou pozornost těch Internetů (přestože jsou tady už pár let, jenže najednou je jejich kvalita tak vysoko, že už to nelze přehlédnout), vlastně intuitivně fungují? Nemyslím teď zkoumání technologie transformerů, topologie těchto modelů, proč jsou některé encoder-decoder zatímco GPT je jen decoder a přitom třeba BERT je jen encoder. Základní jednoduchá představa, která mi pomáhá pobrat základní limity toho všeho, je následující: Model toho hodně naposlouchal a pak blábolí na zadané téma. Jen toho ale už naposlouchal tolik, že to blábolení začalo dávat smysl. A to natolik, že to "zadané téma" může být kus textu, který chcete sumarizovat, parsovat, přeložit nebo doplnit. Jak už jsem na tomto blogu ukazoval, model umí blábolit i v JSON. Nicméně, a to je důležité mít na paměti, o struktuře JSON a jeho pravidlech nic neví.

Ale vraťme se ke srovnání jaké dává starší nebo menší model výsledky v porovnání s tím moderním a obrovským s tím, že princip všech je pro účely dnešního článku velmi podobný - všechny blábolí, jen některé toho načetly víc, jsou tedy sečtělejší. Pro příklad - nejmenší model Ada má problém doplnit správně i věci typu 1+5=. To je přece něco, co dokázaly i mechanické počítací stroje co nepotřebovaly elektřinu. To tak sofistikovaný model nezvládne? Tím chci ukázat, že jde opravdu o jazykový model - ne matematický. Když se herec opije a blábolí na zadané téma, málokdy z něj vypadne funkční výpočet integrálu i když mu o něj řeknete. Model nepočítá, ale blábolí - tedy generuje jazykový výstup na základě své obrovské sečtělosti.

# Vyzkoušejme na příběhu
S čím budeme pracovat? Nahodím následující začátek historky a myslím, že tam určitě je potenciál na nějaké zajímavé pokračování:

**Finish this funny story.**

**Green frog walks into a bar and orders a beer. Bartender, robot running on Windows, freeze for a moment and say:**

Začněme příkladem staršího modelu **GPT-2** (rok 2019, ono to zas tak staré není), který byl velikánský a obsahoval 1,5 miliardy parametrů. Dá se tedy očekávat, že bude schopen generovat dostatečně dlouhé texty.

---

*Finish this funny story.*

*Green frog walks into a bar and orders a beer. Bartender, robot running on Windows, freeze for a moment and say: a burger on that.*

*Small pink elephant walked into a bar and orders a beer. Bartender, robot running on Windows, freeze for a moment and say: a dollar sign on that.*

*Shanghai-shoe salesman, in the most competitive market in the world, walks into a bar and orders a beer. Robot bartender freezes.*

*Silence.*

*Groans.*

*"What can I get you to drink" says barkeep.*

*Groans.*

*"We have a special on Jim Beam Whiskey" says robot bartender.*

*"Bartender, give me*

---

Hmm, jako textu je to dost, ale úplné blábolení. Doslova opakuje myšlenky, které jsem mu nahodil. Není to vtipné, nemá to žádný konec, příběh se nikam neposunul. 

## Ada

Pojďme do modernějších vod GPT-3 (cirka 2020, 175 miliard parametrů). Tam máme v Azure OpenAI službě k dispozici modely různých velikostí - čím menší model, tím méně schopností, ale větší rychlost a nižší cena. Očekávám, že všechny modely tady už budou k věci, ale ty malé nebudou schopné vyprodukovat delší koherentní příběh. Zkusme si to.

Nejdřív tedy nejmenší model **Ada**.

---

*Finish this funny story.*

*Green frog walks into a bar and orders a beer. Bartender, robot running on Windows, freeze for a moment and say:*

*"I'm sorry, your beer is empty."*

---

Neurazí, ale to je tak všechno.

## Babbage

Co model **Babbage**?

---

*Finish this funny story.*

*Green frog walks into a bar and orders a beer. Bartender, robot running on Windows, freeze for a moment and say:*

*"Sorry, we don't serve beer to frogs."*

---

Vtipné to není, ale za mě to dává už hodně smysl. Tohle už vyžadovalo blábolit opravdu na zadané téma, ne jen tak.

## DaVinci 001

Model Curie přeskočím, nic zajímavého z něj nevypadlo. Pojďme na velký model v původní podobě - **DaVinci 001**.

---

*Finish this funny story.*

*Green frog walks into a bar and orders a beer. Bartender, robot running on Windows, freeze for a moment and say:*

*"Hey, you can't order beer, you're a frog!"*

*"I'm not just a frog, I'm a green frog," the frog replies.*

*"Even worse," the bartender says. "Green frogs are underage."*

*The frog hops off to find another bar.*

---

Tak to ale není vůbec špatné! Příběh má délku, má konec a celý dává smysl. Vtipné to sice nějak moc není, ale ta práce s textem je za mě obdivuhodná - všimněte si hrátky typu já nejsem jen žába, já jsem zelená žába a pointa, že u zelených žab je to ještě horší, protože jsou nezletilé.

## DaVinci 003

Na závěr si dejme nejnovější model GPT 3.5 z roku 2022 tedy **DaVinci 003**. Zkusil jsem tři běhy s temperature 1 (ať máme nějaké diverzifikované výsledky) a vybral pro vás ten za mě nejlepší.

---

*Finish this funny story.*

*Green frog walks into a bar and orders a beer. Bartender, robot running on Windows, freeze for a moment and say:*

*"I'm sorry, sir, but I can't serve you. You don't have a valid ID."*

*The frog looks at the robot and says, "What do you mean? I'm a frog!"*

*The robot looks back and says, "I'm sorry, sir, but my software doesn't recognize amphibians as valid customers."*

*The frog sighs and hops away, muttering to himself, "That's the last time I try to get a drink at a Windows bar."*

---

Tak tohle už je opravdu dobré! Vtipné, využilo nahozených míčů (žába v baru, robot s Windows), má to vývoj a konec příběhu.

# Použitelnost, limity a kudy odtud dál
Na příkladu technologií typu GitHub Copilot, masivního úspěchu ChatGPT a odstartování nové fáze válek vyhledávačů tentokrát využívající AI místo jen klasické vyhledávací (i když skvělé) technologie (Bing propojil vyhledávání s ChatGPT, Google se dostal do záklonu a rychle rychle musel ukázat těžce nedodělaný Bard zatímco startup You.com už nějakou dobu AI pro vyhledávání používá o to včetně YouChat a YouCode), je zřejmé, že užitečné je to nesmírně. I v dnešním článku je myslím dobře vidět rozdíl mezi rokem 2019 a 2022. Většina technologie se vyvíjí v S-křivkách - neustále se pozvolna zlepšují a zlepšují až najednou dojde k fázovému přechodu a z hračky nebo experimentu je rázem něco zásadního a velkého (a tam se vývoj zase na nějakou dobu zastaví, než se objeví nová technologie se svojí S-křivkou). Řekl bych, že velké jazykové modely jsou v tomto bodě - tohle už není hračka.

Nicméně - pořád si připomínejme, že tenhle model je o blábolení, které začalo být úžasné díky nesmírné sečtělosti. To bude pokračovat - GPT-4 je za dveřmi a bude určitě zas o hodně dál. Ale jazykový model není myslící stroj, ani matematický nástroj, ani indexační vyhledávač. Přímo se dá krásně použít tam, kde potřebujete pracovat s textem - doplnit, vymyslet název, sumarizovat, parsovat, překládat. Na hodně aplikací to ale bude jen nástroj - API v Azure, které použijete a budete stavět nad tím. To co dělá nový Bing je, že spojuje tradiční vyhledávání s velkým jazykovým modelem. Jste tak například schopni lépe pochopit dotaz uživatele (vytáhnout to podstatné, parsovat apod.), vygenerovat z něj vyhledávací kód (tak jak Copilot generuje kód můžete třeba vygenerovat search do klasického vyhledávače), výsledky z hledání vzít a stránky prohnat jazykovým modelem. Vytáhnout z nich podstatu, nejdůležitější informace a ty zkompilovat do formy odpovědi na dotaz uživatele. Takhle myslím budeme napříště vyhledávat informace na webu. Výsledkem nebudou odkazy, ale odpověď - a pořádně ozdrojovaná, takže budete vědět z čeho robot tak usuzuje a můžete jít do dalších detailů nebo si to ověřit. Podobným způsobem se dá očekávat velké množství dalších aplikací - Azure OpenAI je API, které odemyká nové možnosti, ne finální produkt.

A ještě jedna poznámka k inovativnosti. Častou kritikou jistě bude, že model nic nového nevymyslí a jen opakuje co mu lidstvo podstrčilo. To myslím je jen otázka poměrně krátkého času - jazykový model může být vstupenkou generické umělé inteligence do světa lidí, takže ta se může skutečně naučit z našich učebnic (opravdu naučit, ne být jen jazykovým modelem). Ale druhá věc - lidé v naprosté většině případů zas tak inovativní nejsou. Například v knížce Relationships 5.0 je celkem hezky popsáno jak v oblasti výběru partnera jsou lidé inovativní nesmírně málo a často se točí ve spirále stále stejných rozhodnutí i přestože pro ně nemusí být optimální. Klasický problém explore vs. exploit. Zvyk je železná košile a možná právě AI je něco, co nám dokáže probourat myšlenkové krabičky, do kterých jsme se zavřeli. Model tedy bude často inovativnější než lidé. To ale samozřejmě neznamená, že v extrémech typu Albert Einstein nebo Leonardo da Vinci tomu není naopak - jasně že je (teda alespoň zatím).