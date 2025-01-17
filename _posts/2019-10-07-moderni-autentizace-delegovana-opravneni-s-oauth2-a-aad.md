---
layout: post
title: 'Moderní autentizace: delegovaná oprávnění s OAuth2 a AAD'
tags:
- Security
- Entra
---
Představme si, že budujeme aplikaci, ve které si uživatel může prohlédnout a změnit svoje údaje - číslo účtu pro posílání výplaty, svoje telefonního číslo apod. Například ten telefon bude uložen v AAD profilu a tak budeme chtít zavolat Microsoft Graph API. To se dá použít na spoustu věcí v rámci Office365 - číst a psát emaily, projíždět kontakty, psát zprávy do Teams, pracovat s kalendářem, vytvářet Excel či Word soubory, ukládat věci do OneDrive a mnoho dalšího. Mohli bychom použít dvě varianty, ale obě nejsou moc dobré:
- uživatel dá aplikaci svoje heslo do Office365 a ta pak může dělat všechno (úžasný nápad)
- administrátor dá aplikaci univerzální právo na práci s profily uživatelů v AAD (pak se vystavuji riziku, že někdo aplikace hackne a odejde se všemi údaji a navíc v AAD logu uvidím jen přístupy aplikace, ne který uživatel vlastně změnu chtěl provádět)

Přesně tohle, tedy schopnost udělit delegované granulární oprávnění, vznikl protokol OAuth2. Nejdřív si vyzkoušíme popsaný scénář, kdy budeme přistupovat do Microsoft Graph a v druhé části si ukážeme, jak i naše jiná aplikace může publikovat sadu oprávnění, na které si může první aplikace zajistit souhlas u uživatele.

# OAuth2 a autorizace do Microsoft Graph
Nejprve stručně jak to funguje. Aplikace se musí zaregistrovat do AAD a následně pokud potřebuje přístup ke čtení celého profilu uživatele, zahájí autorizační kolečko. Uživatel se domluví s AAD (přihlásí se tam), AAD mu řekne, že aplikace chce taková a taková oprávnění a uživatel to odsouhlasí (nebo může oprávnění za celou organizaci udělit i administrátor jako jsme to viděli ve scénáři s OpenID Connect). Výsledkem je access_token, který AAD do aplikace doručí a to buď přímo (implicit flow - méně bezpečná varianta, ale zatím jediná rozumná pro single-page aplikace běžící jen v browseru) nebo si ho aplikace vyzvedne sama přes svůj backend (bezpečnější - to dnes použijeme). Token má nějaké náležitost a ty si probereme, ale tento token je zajímavý ne pro naší aplikaci, ale pro resource, ke kterému přistupuje (v našem případě AAD profil), protože ten si tak ověří, že aplikace tohle může jménem uživatele udělat.

Nejprve tedy opět zaregistrujeme aplikaci a poznamenáme si client (application) id.

![](/images/2019/2019-09-20-08-07-18.png){:class="img-fluid"}

Redirect si necháme posílat na localhost, protože chceme všechno zkoušet bez nutnosti aplikaci opravdu mít.

![](/images/2019/2019-09-20-08-08-12.png){:class="img-fluid"}

Protože bude používat v2 AAD endpoint, nepotřebujeme staticky definovat scope (tedy informaci k čemu chceme získat delegované oprávnění), to proběhne dynamicky na základně requestu (o tom později). Nicméně uděláme jeden krok navíc - vygenerujeme si client secret. Ten použijeme později v procesu k vyzvedávání tokenu na backendu, ale k tomu se dostaneme.

![](/images/2019/2019-09-20-08-10-52.png){:class="img-fluid"}

![](/images/2019/2019-09-20-08-11-15.png){:class="img-fluid"}

Nezapomeňte si poznamenat secret, pak už vidět nebude.

![](/images/2019/2019-09-20-08-11-54.png){:class="img-fluid"}

Výborně. Pojďme si teď připravit URL, na kterou uživatele přesměrujeme pro autorizaci a vyplňme správné parametry. Většinu jsme rozebírali v minulých článcích, ale zaměříme se na rozdíly.

```
https://login.microsoftonline.com/cdc3cb25-000b-429b-ab96-d7ef178575e5/oauth2/v2.0/authorize?client_id=462daa70-e21e-4136-a2f5-5d1ba2011736&response_type=code&redirect_url=http%3A%2F%2Flocalhost&response_mode=query&scope=User.ReadWrite&state=12345
```

* client_id je identifikátor registrované aplikace (client/application id)
* response_type použijeme code, tedy nechceme přímo token, ale jen kód na jeho vyzvednutí (o tom později)
* redirect_url je http://localhost pro naše demo účely a musí se shodovat s tou nastavenou při registraci
* reponse_mode použijeme query, protože to se nám bude nejlépe chytat. Fragment se hodí spíše pro doručování tokenů přímo (SPA) a nejlepší by bylo použít form_post.
* scope definuje k čemu chceme získat přístup. Microsoft Graph je pro AAD primární věc, takže jednotlivé řetězce jsou krátké a bez dlouhého odkazu na resource (později uvidíme, že s vlastním resourcem to bude vypadat trochu jinak). Seznam oprávnění najdu na [https://docs.microsoft.com/en-us/graph/permissions-reference#user-permissions](https://docs.microsoft.com/en-us/graph/permissions-reference#user-permissions) a pro účely načtení telefonního čísla zvolíme User.ReadWrite
* state jsme rozebírali minule - měli bychom je náhodně vygenerovat pro každý request a kontrolovat, že jsou i v odpovědi a chránit se tak před některými útoky

Pojďme do anonymního okna a dáme tam námi smontované url.

![](/images/2019/2019-09-20-08-21-36.png){:class="img-fluid"}

![](/images/2019/2019-09-20-08-21-52.png){:class="img-fluid"}

Uživatel je vyzván k udělení souhlasu.

![](/images/2019/2019-09-20-08-31-36.png){:class="img-fluid"}

V této souvislosti jedna poznámka. Souhlas pro User.ReadWrite může uživatel udělit (nebo to za něj udělá administrátor), ale třeba pro plný profil (User.ReadWrite.All) to možné není, protože AAD pro takové operace vyžaduje administrátorského oprávnění. Tedy to, že se můžu uživatele zeptat na oprávnění ještě neznamená, že on má v organizaci možnost ho udělit. Tak třeba nechceme, aby si běžný uživatel mohl nastavit jiného nadřízeného.

Všechno proběhlo a v adress bar vidím kód na vyzvednutí access_token.

```
http://localhost/?code=OAQABAAIAAAAP0wLlqdLVToOpA4kwzSnxboGwRLCo1xphSuUPvFeolQA1OWeP7XEFty6mCR0zvDk6QNxuiIMj3ZsQFuT3hXeYG55ZKsnqWfysLLfLiLLJ0Kb3YgRR7atKp5mcXLYrg_08GH0SNDW1BOgGPjwuKM21Jbj9-s54NkWhq74qYBNGUsaoyqD-AweucSjIEHBXb3H_j2PKGvAfLIMnbKg3Z6iY8qaRQykOSZs4mOd50MsiFfQGRo64SkwaUhfKqE3pzwScm4tTKwec0_uMJLCMDqiHIKi_dLw4ZgZuJAl_RG9cR9joby6qcz-Y6IaSoqT38H0i9FOo-vbfAfV5512m858WzyxvXsWMF5tT4lsc14zCSIsndQGJ5wQTgYCZPyYWBpii-KSiYxWooh6OcREqsgF0LjcAnmu-1SOR1R_lHlygOiYxJt2GnKkCnHjYTe1Q3ATMsG0YUz8gGHSjBWqAUjBoW5zg2I-RoNSK52dprmCodcRUFFzV8ccKaWckE-vQiJT0uJt0vmcBE8BcuRa65ul8Qt3tOMAuYRCqOQRZO1XLc5yf1ft8rsPaXPEVh9gK56Gfan5f5RaWpUsENtEUuvqCc6YDgl0oZ9iPb-mlmqe7oyAA&state=12345&session_state=380c2800-a7ee-4ed0-9336-4bf582823bc2
```

Teď tedy k vysvětlení, proč to není rovnou access_token. Jde o bezpečnost. AAD svou odpověď musí vrátit do prohlížeče a součástí odpovědi je kromě dalších informací především vynucení redirect kam potřebujeme. Jinak řečeno code nebo token protoče prohlížečem a v tom je ten zádrhel. Browser není něco, co máte plně pod kontrolou a přestože bezpečnost už je tam dobrá, nikdy nevíte. Co když má v browseru nějakou extension, která je schopná koukat do address bar (tzn. vidí query) nebo i do stránky samotné (takže vidí i form_post) například s vidinou "zabezpečení", blokování reklam nebo něco podobného. Pokud pošlem rovnou token, je šance, že bude vyzrazen. Nicméně pokud máte aplikaci, která nemá žádný backend a běží jen v browseru, je možné doručit token rovnou ve fragmentu (tomu se pak říká implicit flow a prováděli jsme ho v předchozích článcích s OpenID Connect, protože id_token je méně citlivý).

Přes browser tedy proteče jen code a ten přes redirect doputuje do našeho backendu. To už je plně kontrolované prostředí a navíc je tam možné bezpečně uložit client_secret. Backend tedy teď zavolá AAD, prokáže se heslem (client_secret) a vymění si code za access_token a ten tedy nikdy prohlížečem neprobublá a client_secret taky ne.

Co tedy backend udělá? Vezme code, client_id, client_secret a nechá si poslat token z AAD (má na to omezený čas, myslím asi 10 minut od vydání code). Je to POST request a v body jsou tyto údaje, tak použijeme Postman.

![](/images/2019/2019-09-20-08-48-37.png){:class="img-fluid"}

Token je tady.

![](/images/2019/2019-09-20-08-49-21.png){:class="img-fluid"}

Možná teď máte touhu, se do něj podívat. Udělat to můžeme, ale není důvod. V aplikaci si netvořme žádnou návaznost na vnitřek tokenu - není to náš byznys. Token není pro nás, ale pro resource, na který budeme chtít přistoupit, tedy v tomto případě Microsoft Graph. To co je důležuté pro nás, tedy jaký má scope a za jak dlouho mu vyprší platnost, jsme dostali v metadatech a token nemusíme otvírat.

Token vypadá takhle, ale nečtěte si ho v aplikaci. Pokud vás třeba napadá, že takhle zjistíte co je to za uživatele, tak to není vhodné použití OAuth2 - na to je dělaný OpenID Connect, o kterém už jsem psal.

![](/images/2019/2019-09-20-08-53-30.png){:class="img-fluid"}

Token tedy máme a můžeme zavolat Microsoft Graph API a přidat telefon uživatele. Použijeme Postman. URL bude https://graph.microsoft.com/v1.0/me a metoda PATCH.

![](/images/2019/2019-09-20-09-06-47.png){:class="img-fluid"}

Autorizace Bearer token a vložíme řetězec, co jsme dostali v odpovědi od AAD.

![](/images/2019/2019-09-20-09-07-57.png){:class="img-fluid"}

Přidáme header Content-type: application/json

![](/images/2019/2019-09-20-09-08-27.png){:class="img-fluid"}

Do body vložíme tento JSON.

![](/images/2019/2019-09-20-09-17-07.png){:class="img-fluid"}

Pošleme a dostaneme odpověď 204 - přijato.

![](/images/2019/2019-09-20-09-17-29.png){:class="img-fluid"}

Po chvilce uvidíme nový telefon v AAD.

![](/images/2019/2019-09-20-09-18-12.png){:class="img-fluid"}

# OAuth2 a autorizace do mého vlastního API
Aplikaci máme zaregistrovanou a umíme si říct o access_token a získat delegované oprávnění na přístup do Microsoft Graph API na změnu telefonu uživatele. Další typ údaje, který aplikace chce zpracovávat je číslo účtu na posílání výplaty. To je vedeno v Payroll aplikaci, která vznikla například vlastním vývojem. Ukažme si, jak něco takového zajistit.

Aplikaci máme z předchozího kroku zaregistrovanou a tohle je připraveno. Jak ale do AAD přidat Payroll řešení tak, aby AAD vědělo jaké typy oprávnění Payroll nabízí a také aby Payroll vystaveným tokenům věřil?

Payroll aplikaci musíme také zaregistrovat do AAD. Následně v AAD řekneme, jaké typy oprávnění (scope) bude payroll mít.

![](/images/2019/2019-09-20-13-24-37.png){:class="img-fluid"}

Nejprve si zvolíme identifikátor.

![](/images/2019/2019-09-20-13-25-36.png){:class="img-fluid"}

Přidejme například oprávnění Account.Read, které opravňuje k načtení bankovního účtu.

![](/images/2019/2019-09-20-13-37-31.png){:class="img-fluid"}

Uděláme ještě Account.ReadWrite.

![](/images/2019/2019-09-20-13-38-52.png){:class="img-fluid"}

Oba tyto scope umožňují consent uživatele, ale můžeme mít i takové, které vyžadují schválení administrátorem. například možnost změnit výši platu nechceme dát běžnému uživateli.

Výborně. Vrátíme se do naší přehledové aplikace a řekneme si o access_token k payroll službě. scope bude api://mypayroll/Account.Read.

```
https://login.microsoftonline.com/cdc3cb25-000b-429b-ab96-d7ef178575e5/oauth2/v2.0/authorize?client_id=462daa70-e21e-4136-a2f5-5d1ba2011736&response_type=code&redirect_url=http%3A%2F%2Flocalhost&response_mode=query&scope=api%3A%2F%2Fmypayroll%2FAccount.Read&state=12345
```

Dostáváme obrazovku pro udělení souhlasu pro přístup k payrollu.

![](/images/2019/2019-09-20-13-43-37.png){:class="img-fluid"}

Dostanu code a na backendu si vyměníme code za access-token.

Jak jsme říkali, jako aplikaci mě u něj nezajímá obsah. Jen si při vrácení kódu zkontroluji state parametr a v metadatech uvidím kdy token vyprší a jaký má scope. Víc jako aplikace nepotřebuji. Teď bych se mohl připojit na payroll API (to ale nemáme, hrajeme si bez programování) a jako autorizaci mu poslat header Bearer: TADYJETOKEN.

![](/images/2019/2019-09-20-13-50-48.png){:class="img-fluid"}

Payroll si musí kolem tokenu pár věci zkontrolovat:
- Sedí tokenu signatura (tedy nehrál si někdo s obsahem a je to vůbec od AAD)?
- Je token určen pro mě (aud)?
- Je časově platný (iat, nbf, exp)?
- Jaké oprávnění (scp)?
- Další identifikátory typu jaký je to user, z jaké aplikace, v jakém tenantu apod.

A co když chci token zrušit, můžu ho revokovat? Nemůžu, protože celé řešení je bezestavové. Nicméně z toho důvodu má token krátkou platnost, v případě AAD je to 1 hodina. Pak si musíte sehnat nový a to má AAD příležitost říct, že už ne. Ale co když už uživatel stránku opustil a vy potřebujete na backendu přistupovat na resource dál? O tom je refresh token. A co když máte nějaké batch zpracování a není možné nebo vhodné přistupovat jménem jednotlivých uživatelů, ale dostat přístup ke všemu? O tom bude client flow. Oboje příště.

