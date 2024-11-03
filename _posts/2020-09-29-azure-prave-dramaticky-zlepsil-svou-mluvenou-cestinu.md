---
layout: post
published: true
title: Azure právě dramaticky zlepšil svou mluvenou češtinu aneb od Jakuba k Vlastičce
tags:
- AI
---
Je to měsíc co jsem vyzkoušel podporu češtiny pro převod mluveného slova na text (speech-to-text) a byl jsem příjemně překvapen přesností a kvalitou. Současně jsem otestoval obrácený směr, tedy syntézu řeči. Microsoft používal pouze standardní model, ale Jakub na rozdíl od paní z Google podle mě lépe pracoval s rytmem řeči a intonací ve větách. Ale Kuba neměl pod sebou hluboký neurální model, tak zněl dost jako robot. O měsíc později ale shodou okolností Microsoft rozšířil podporu jazyků pro text-to-speech s neurálním modelem a kromě Jakuba přišla Vlasta. Podle mého ucha zní naprosto úžasně, co myslíte vy?

Nejprve jsem si v Azure založil Speech objekt.

![](/images/2020/2020-09-25-08-16-26.png){:class="img-fluid"}

Následně na stránce speech.microsoft.com můžu použít GUI. To slouží primárně pro pokročilé metody, které pro češtinu k dispozici nejsou. Jedná se o možnost vytvářet vlastní hlasové tóny a spousta další pozoruhodných věcí, na které se podívám někdy příště. Já použiji sekci Audio Content Creation.

![](/images/2020/2020-09-25-08-15-58.png){:class="img-fluid"}

Takhle vypadá text pro Jakuba, standardní model.

![](/images/2020/2020-09-25-08-14-05.png){:class="img-fluid"}

A takhle Vlastička.

![](/images/2020/2020-09-25-08-14-26.png){:class="img-fluid"}

Totéž jsem udělal v Google.

![](/images/2020/2020-09-27-09-52-58.png){:class="img-fluid"}

Tady jsou odkazy na výsledné soubory se načteným textem, který jsem jim připravil. 

Jakub (Microsoft, starší model): [mp3](/images/2020/Jakub.mp3)

Vlasta (Microsoft, neurální model): [mp3](/images/2020/Vlasta.mp3)

Google (neurální model): [mp3](/images/2020/Google.mp3)

Mimochodem - neurální model má i Viktoria, Slovenská kolegyně, takže dnes už i tento jazyk funguje obousměrně! Více o podpoře jazyků najdete [tady](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support#text-to-speech).


Za mě tedy Vlasta jednoznačně nejlepší - co myslíte vy?