---
layout: post
published: true
title: "Jiskra naděje pro ty, co mají skvělé nápady na aplikace, ale neumí ani trochu programovat: GitHub Spark"
tags:
- AI
- GitHub
---
Začněme výsledkem - tady je aplikace, kterou si dnes vytvoříme bez napsání jediného řádku kódu i bez klikání v nějakém designeru low-code platformy. Je pro studenty, kde zaznamenávají v rámci výuky místa, která navštívili, s pomocí AI k nim dávají popis, svoje hodnocení a fotografie z místa. Aplikace umožňuje přidávat, editovat, vyhledávat, vygenerovat PDF report, zobrazovat v mapě a přichází s AI asistentem, s kterým lze diskutovat nad navštívenými místy a ptát se na další inspiraci.

[![](/images/2025/GitHubSparkDemo.gif){:class="img-fluid"}](/images/2025/GitHubSparkDemo.gif)

# GitHub Spark
Jde o technologické preview (tedy zatím ne nějaký hotový produkt) od GitHubu, na který je aktuálně [waitlist](https://github.com/github_spark_waitlist_signup). Přináší možnost člověku, který neumí programovat, ale má nápady a chce je zhmotnit, ukázat kolegům, šéfům, uživatelům - prototypovat, hledat podporu, získat feedback. Už jsem takové jednoduché generátory z jiných stránek zkoušel a problém byl, že první iterace dobrá, ale pak to začne být horší a horší. GitHub Spark ale tenhle problém neměl, zdálo se mi spíše naopak. Nejen, že držel projekt pohromadě, nerozbíjel moc často co už má, ale je hlavně připraven na iterativní způsob práce. 

Další co je jiné je to, že má nástroj pod kapotou sběr chybových hlášek, datovou perzistentní vrstvu a přístup k AI modelům. Osobně myslím, že tohle je budoucnost low-code platforem. Ne pseudojazyk, přesouvání nějakých ovládacích prvků myší a tak podobně, ale prostě přirozená řeč a diskuse nad výsledky.

# Povídání s AI a jak appka postupně vznikala
Na začátku je úvodní obrazovka a výběr z několika AI modelů. Mně se jednoznačně nejvíc osvědčilo o1-preview. Je sice pomalejší, ale ten model je opravdu chytrý a dává nejlepší výsledky. Jak uvidíte později v jeden okamžik jsem použil běžnější modely (ja byl zvědavý na Claude - v porovnání s GPT-4o byly výsledky o chlup lepší, než klasický GPT-4o) a to z toho důvodu, že GitHub Spark pak umí vygenerovat několik pokusů, z kterých si lze vybrat (super když jsem řešil UI požadavky).

[![](/images/2025/2025-01-17-09-36-24.png){:class="img-fluid"}](/images/2025/2025-01-17-09-36-24.png)

Tohle je tedy můj iniciální prompt - popsal jsem co ta aplikace má v základu dělat.

> Create application for my students to track their visits to historical places Prague as their home assignment. Make sure they can create item they visited (location, PoI), add description to it, links to official sources, their review and rating. They should be able to see their progress in the app and see their visits visualized in map. Make sure data is persistent.

[![](/images/2025/2025-01-17-09-44-11.png){:class="img-fluid"}](/images/2025/2025-01-17-09-44-11.png)

V tomto místě se mi stalo, že appka nenaběhla, v kódu byla hnedle chyba. Kliknul jsem na palec dolu a GitHub Spark to zkusil znova a vyšlo to. S jinými generátory jsem měl podobnou zkušenost a v tento moment jsem si říkal, že to prostě bude podobné.

[![](/images/2025/2025-01-17-09-56-31.png){:class="img-fluid"}](/images/2025/2025-01-17-09-56-31.png)

Tady je už funkční verze.

[![](/images/2025/2025-01-17-10-00-23.png){:class="img-fluid"}](/images/2025/2025-01-17-10-00-23.png)

Při kliknutí na tlačítko přidat se graficky moc nepovedla mapa - vyčnívá z dialogu, zakrývá ovládací prvky.

[![](/images/2025/2025-01-17-10-14-35.png){:class="img-fluid"}](/images/2025/2025-01-17-10-14-35.png)

Tak jsem mu to řekl, ať to opraví.

> When clicking on Add New Visit button dialog there is popup with map that os not aligned with it. It get over dialog, over fields and so on. Fix it, please.

[![](/images/2025/2025-01-17-10-52-20.png){:class="img-fluid"}](/images/2025/2025-01-17-10-52-20.png)

Tady už začalo být jasné, že na rozdíl od jednoduchých generátorů, GitHub Spark se bude dobře držet nějaké myšlenkové linky, kterou budeme společně rozvíjet. Verzuje si, umí se vracet, opravovat a nechá si do toho mluvit. V tomhle je ten hlavní rozdíl - s každou iterací jsem měl pocit, že nám to jde lépe a lépe, ne že je to křehčí a křehčí.

Dobrá - zadávat souřadnice z hlavy je nepraktické, ať tam přidá mapku.

> Add New Visit dialog contains Latitude and Longitude fields. It is not user friendly. Make sure user can click on map and get coordinates from there or preferably can do some search for POI in map.

[![](/images/2025/2025-01-17-10-56-42.png){:class="img-fluid"}](/images/2025/2025-01-17-10-56-42.png)

Skvělé! Vyhledávání tam sice nedal, ale vybírání na mapce mi teď stačí. Vidím, že GitHub Spark přemýšlí se mnou a také má nějaké nápady, co by se dalo dělat dál. Možnost měnit a mazat záznamy je dobrý nápad, to určitě chci taky!

[![](/images/2025/2025-01-17-10-59-13.png){:class="img-fluid"}](/images/2025/2025-01-17-10-59-13.png)

Výsledek zafungoval, jsem spokojen.

[![](/images/2025/2025-01-17-11-00-57.png){:class="img-fluid"}](/images/2025/2025-01-17-11-00-57.png)

Další jeho nápad - export do PDF. Dává mi taky smysl, pojďme na to.

[![](/images/2025/2025-01-17-11-03-13.png){:class="img-fluid"}](/images/2025/2025-01-17-11-03-13.png)

[![](/images/2025/2025-01-17-11-05-12.png){:class="img-fluid"}](/images/2025/2025-01-17-11-05-12.png)

[![](/images/2025/2025-01-17-11-05-33.png){:class="img-fluid"}](/images/2025/2025-01-17-11-05-33.png)

Teď bych chtěl studentům trochu pomoci. Co kdyby si mohli subscription nechat vygenerovat na základě nějakých svých stručných poznámek a klíčových bodů, klidně v jiném jazyce.

> I would like to use AI to help students generate Description in English by providing ability to type in any other language, provide just list of hights or unstructured insights or notes and AI would help them generate short polished description in English.

Dal to na první pokus - tohle mě dostalo. Vlevo vidím, že GitHub Spark je na to vyloženě dělaný a vygenerované prompty nejsou jen pohřbené někde v kódu, ale můžu si je prohlédnout i měnit vlevo dole.

[![](/images/2025/2025-01-17-11-17-02.png){:class="img-fluid"}](/images/2025/2025-01-17-11-17-02.png)

Themes

[![](/images/2025/2025-01-17-11-18-29.png){:class="img-fluid"}](/images/2025/2025-01-17-11-18-29.png)

> Application work well, but since it is for young students, make it more fresh and cool. Don't be afraid to use colors, animations, unusual UI and so on. Make it more playful.

[![](/images/2025/2025-01-17-12-42-26.png){:class="img-fluid"}](/images/2025/2025-01-17-12-42-26.png)

[![](/images/2025/2025-01-17-12-45-51.png){:class="img-fluid"}](/images/2025/2025-01-17-12-45-51.png)

> Title should fit one line, it looks better. Also rating should be visualized as starts and Edit button shout not have ? icon, but something like pencil button.

[![](/images/2025/2025-01-17-12-49-21.png){:class="img-fluid"}](/images/2025/2025-01-17-12-49-21.png)

> Allow students to upload optional images and implement image galery for each item showing few thumbnails on main screen.

[![](/images/2025/2025-01-17-13-13-55.png){:class="img-fluid"}](/images/2025/2025-01-17-13-13-55.png)

[![](/images/2025/2025-01-17-13-14-23.png){:class="img-fluid"}](/images/2025/2025-01-17-13-14-23.png)

> Picture upload button is not very nice and not aligned with UI elements, can you make it more consistent with overall app look?

[![](/images/2025/2025-01-17-13-18-37.png){:class="img-fluid"}](/images/2025/2025-01-17-13-18-37.png)

> Enable search and filter functionality on list of visits

[![](/images/2025/2025-01-17-13-24-47.png){:class="img-fluid"}](/images/2025/2025-01-17-13-24-47.png)

> Add "visits chat" which will be AI powered engine to find the best visits based on user interests and its conversation with agent. Make sure chat fits into existing UI style nicely. I want it to be just button and new dialog might open, similar in style to Add New Visit, but this time with simple chat interface do talk about visits with AI.

> Chat works and AI answers questions, but it does not have context of my visits. Make sure it only recommends places in Prague. Also it must know about recorded visits and reviews from this app and get context from it, eg. be able to tell rating or recommend based on description in app.

> Review the code. AI Visits Chat works and give responses, but it seems to ignore my system message. In system message I state he is expert tour guide for Prague, provide visits context and so on. But model does seem to get it. Eg. When I ask: What you can do? Model answer with: I can help with a variety of tasks such as providing information, answering questions, generating text, creating summaries, offering recipes, and more. Just let me know what you need assistance with! That indicates it have not got system prompt correctly.

> In Visits Chat model sometimes responds with Markdown, but it is not displayed as such. Make sure markdown such as **boldstuff** are interpreted. Careful not to break anything - last time you tried you broke Edit dialog and deleted prompt for description generation, which is not related to Visits Chat.

[![](/images/2025/2025-01-17-15-57-43.png){:class="img-fluid"}](/images/2025/2025-01-17-15-57-43.png)

[![](/images/2025/2025-01-17-16-05-09.png){:class="img-fluid"}](/images/2025/2025-01-17-16-05-09.png)
