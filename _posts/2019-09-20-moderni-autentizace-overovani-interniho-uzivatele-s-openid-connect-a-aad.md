---
layout: post
title: 'Moderní autentizace: ověřování interního uživatele s OpenID Connect v AAD'
tags:
- Security
- Entra
---
Dnes se podíváme na scénář jednoduchého přihlašování uživatele a nebudeme vyžadovat autorizaci, tedy neřešíme přístup k nějakým dalším zdrojům a API, chceme jen čistě zjistit, kdo s námi vlastně mluví. K tomu využijeme OpenID Connect, standardizovanou nadstavbu nad OAuth2. V dnešním díle si vyzkoušíme pro firemní aplikaci s AAD a příště se pustíme do řešení pro koncové uživatele s AAD B2C včetně integrací na jiné systémy jako jsou Google účty.

# Registrace pro OpenID Connect v AAD
Pro přihlašování interních uživatelů použiju svého AAD tenanta tomaskubica.in.

![](/images/2019/2019-09-16-05-50-38.png){:class="img-fluid"}

Přidejme si uživatele.

![](/images/2019/2019-09-16-05-51-31.png){:class="img-fluid"}

![](/images/2019/2019-09-16-05-52-17.png){:class="img-fluid"}

Iniciální heslo si poznamenám.

Každá aplikace, která má mít možnost využívat můj tenant, se musí registrovat.

![](/images/2019/2019-09-16-05-53-51.png){:class="img-fluid"}

Budeme u ní podporovat jen přihlášení z mého tenantu.

![](/images/2019/2019-09-16-05-54-32.png){:class="img-fluid"}

Přihlášení bude fungovat tak, že uživatel bude přesměrován na AAD, kde dojde k jeho přihlášení a AAD vystaví id_token. Ten potřebujeme doručit do aplikace a to buď přímo do prohlížeče nebo do backendu. V obou případech potřebujeme, aby AAD token doručilo na nějaké URL naší aplikace. Protože nic programovat nebudeme, necháme si poslat na http://localhost, kde odpověď jednoduše zachytíme a pohrajeme si s ní.

![](/images/2019/2019-09-16-06-00-10.png){:class="img-fluid"}

Jsme pouze u ověřování a výsledný id_token není nějaká extrémně citlivá záležitost, protože nezakládá možnost komunikovat s nějakým dalším systémem nebo api (na rozdíl od access tokenů, které prozkoumáme někdy příště). Pro OpenID Connect tak typycky nebudeme mít problém získat token rovnou v odpovědi z AAD, takže zapneme implicitní flow pro id_token.

![](/images/2019/2019-09-16-06-03-44.png){:class="img-fluid"}

# Přihlášení a získání základního id_token
Vaše aplikace by při připojení uživatele zjišťovala, jestli má nějakou cookie, která identifikuje jeho session. Žádnou takovou mít nebude a proto se rozhodne ho přesměrovat na AAD pro přihlášení. To si teď vyzkoušíme přímo v prohlížeči. 

Podívejme se na AAD endpointy.

![](/images/2019/2019-09-16-06-06-34.png){:class="img-fluid"}

Budeme využívat endpoint v2 - modernější verzi, která více odpovídá používání autentizačních a autorizačních protokolů jak je na trhu dnes běžné. v1 nic neporušuje, ale standard nechal některé otázky bez odpovědi a v1 měla trochu jinou strategii používání (například statické definování permissions nebo používání resource místo scope apod.). Mezitím se všechno na trhu ustálilo a různé identitní systémy doiterovaly k společnému způsobu a ten je otisknut ve v2. První naznačený endpoint je tedy pro autorizaci (nicméně běží na něm i autentizační OpenID Connect, protože ten je nadstavbou OAuth2) a druhý jsou metadata pro OpenID Connect (poznamenejte si, využijeme o chvilku později).

Přesměrování tedy povede na https://login.microsoftonline.com/cdc3cb25-000b-429b-ab96-d7ef178575e5/oauth2/v2.0/authorize, nicméně potřebujeme do volání přidat pár parametrů:
* client_id: identifikátor naší aplikace, který vznikl při její registraci v AAD (označuje se tam jako Application ID)
* response_type: jakou odpověď očekáváme, pro začátek s implicitním flow (doručení rovnou tokenu) tady dáme id_token
* redirect_url: to bude kopírovat nastavení při registraci, tedy v našem případě http://localhost (v URL encode, protože znaky :// by prohlížeč zmátly)
* response_mode: říkáme, jakým způsobem chceme token v redirectu doručit. Genericky vzato jsou tu varianty from_post (výsledek vypadá jako při odeslání HTML formuláře, tedy je to POST na nějaký endpoint), query (odpověď přijde jako běžné parametry GETu za otazníkem) nebo fragment (informace přijdou za symbolem #, což se dostane do browseru, ale ne dál - typické pro single-page aplikace). Ne všechny možnosti jsou z různých (primárně bezpečnostních) důvodů k dispozici u všech typů přihlášení/autorizace. U implicitního flow v dnešním článku použijeme fragment.
* scope: tady říkáme u OAuth2 k čemu chceme získat práva, v našem případě jde o právo na přihlášení a dává se sem openid
* state: nějaké náhodné číslo, které se nám vrátí i v odpovědi a my zkontrolujeme, že je stejné (brání před některými útoky)
* nonce: opět nějaké náhodné číslo, které AAD vloží přímo do id_tokenu (a podepíše) a my si zkontrlujeme, že je stejné (bráníme se před replay útoky)

Celé URL bude vypadat takhle:

```
https://login.microsoftonline.com/cdc3cb25-000b-429b-ab96-d7ef178575e5/oauth2/v2.0/authorize?client_id=45d4844f-9df4-4381-a7b4-bbf9957e565e&response_type=id_token&redirect_url=http%3A%2F%2Flocalhost&response_mode=fragment&scope=openid&state=12345&nonce=54321
```

V prohlížeči zmáčkneme F12 a jdeme na záložku Network (resp. pro doručení přes fragment to uvidíme i v address baru, ale pro form_post to bude potřeba) a pošleme výše uvedené URL. Vyplníme našeho uživatele.

![](/images/2019/2019-09-16-06-28-04.png){:class="img-fluid"}

Zadáme iniciální heslo vzniklé při založení uživatele (v enterprise praxi bychom pravděpodoboně nezakládali cloud-only uživatele, ale tento by vznikl synchronizací s Active Directory v on-premises).

![](/images/2019/2019-09-16-06-29-36.png){:class="img-fluid"}

Je to první přihlášení, takže si musíme změnit heslo.

![](/images/2019/2019-09-16-06-30-32.png){:class="img-fluid"}

Naše aplikace chce uživatele přihlásit a chce tedy od něj souhlas s načtením základního profilu.

![](/images/2019/2019-09-16-06-31-42.png){:class="img-fluid"}

Localhost, na kterého se odpověď vrátila, v našem případě samozřejmě nikam nevede (nemáme aplikaci), nicméně vidíme, že nám přišel fragment (to za #):

![](/images/2019/2019-09-16-06-33-50.png){:class="img-fluid"}

Celé to vypadá takhle:

```
http://localhost/#id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6ImllX3FXQ1hoWHh0MXpJRXN1NGM3YWNRVkduNCJ9.eyJhdWQiOiI0NWQ0ODQ0Zi05ZGY0LTQzODEtYTdiNC1iYmY5OTU3ZTU2NWUiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vY2RjM2NiMjUtMDAwYi00MjliLWFiOTYtZDdlZjE3ODU3NWU1L3YyLjAiLCJpYXQiOjE1Njg2MDgwNDQsIm5iZiI6MTU2ODYwODA0NCwiZXhwIjoxNTY4NjExOTQ0LCJhaW8iOiJBVFFBeS84TUFBQUFkcitqUU9BTERoRDFqcUdSQ2ZvWFBsUU5uaWhITlVHb0NiU0ZjaFQxMFhEd1hQUXM5TGw5enhtNkpnbEFYVmhTIiwibm9uY2UiOiI1NDMyMSIsInN1YiI6InNRWTl0UnV1OE9xMnBWZDN0b3owSnRMMDdhRDdGRDVLRHBGWGdfbXlMekUiLCJ0aWQiOiJjZGMzY2IyNS0wMDBiLTQyOWItYWI5Ni1kN2VmMTc4NTc1ZTUiLCJ1dGkiOiJnRHVVNUZaRXprV0lZUVhYVkt5VUFBIiwidmVyIjoiMi4wIn0.WJTk9rwkBw8gCceJ5KUHX_xYQNf0-samcqMaVZ0_RJeUojAV6HhwHaNnGHp3uqomOoUHD8n4v6NoYU_lO27QiVEfdVd_PKKuZHSRFEfEEs8FCFKPxwJv_8_9pmfl4fMGpEhg-IiEt2H-6AT4XXI3WAGPKNY5V-Q0AlJEoMxj9FcEU5hhHFsIN0MRkRqSiN6XwKOR1CAituwX6SxlqVJE_NhKyQnypYZ51RiM0Xlr2tuMQ18varbKFBNFsSTsXHahPb4bqTw9jD5kD39ZnJw5MtW8Lmw696Dk6WETyuTw5oBJMYxRV2CU-eB-rauLIBCYzAwpGkJYLIPV0ut4zancKQ&state=12345&session_state=315ae2ea-6ef1-4b17-b2fd-58bd6b208c7d
```

Dostali jsme id_token. Měli bychom si ale pár věcí ověřit. State je stejný, jako jsme poslali, takže to je dobré. id_token je JWT v base64 kódování a protože nemáme žádný vlastní kód, necháme si ho rozbalit v jwt.ms (id_token není nijak zvlášť citlivý, ale až budeme řešit autorizaci s access_token, zvažte, zda chcete token parsovat takhle online - tato stránka to dělá přímo v browseru a bude bezpečná, ale nikdy nevíte a kromě pokusných uživatelů bych parsing raději udělal lokálně ručně nebo nějakým skriptem):

![](/images/2019/2019-09-16-06-36-15.png){:class="img-fluid"}

![](/images/2019/2019-09-16-06-36-42.png){:class="img-fluid"}

Záložka Claims moc pěkně vysvětluje co jednotlivé atributy znamenají:

![](/images/2019/2019-09-16-06-37-19.png){:class="img-fluid"}

Ověřme si, že token je časově platný (iat, nbf a ext) - údaje jsou v Epoch time (počet vteřin od 1.1.1970) a nonce sedí. Dále bychom se měli podívat na audience a ujistit se, že token je opravdu vystaven pro naší aplikaci. Určitě se podíváme, že state a nonce sedí.

Ještě bychom měli (a je to důležité!) udělat jednu věc - ověřit podpis. V alg je zapsáno, jaký algoritmus byl pro podepsání použit a podepisovací klíč najdeme na https://login.microsoftonline.com/cdc3cb25-000b-429b-ab96-d7ef178575e5/v2.0/.well-known/openid-configuration. Ručně to teď dělat nebudeme, v praxi to pro vás zařídí autentizační knihovna v aplikaci. Zjednodušeně řečeno AAD vezme první dvě části tokenu (header a payload), udělá nad nimi hash a tu podepíše svým privátním klíčem. Vaše aplikace pak použije public klíč a ověří, že výsledek sedí, tedy že s tokenem nebylo nijak manipulováno a protože pouze AAD vlastní privátní klíč, je prokázáno, že skutečně token vystavilo.

Všechny tyto kontroly znamenají, že token nemohl nikdo modifikovat, je platný, je opravdu určený pro nás a vznikl na základě našeho aktuálního požadavku a nejde o znovupřehrání. Všecno dost podstatné.

Ještě zmiňme, že AAD jde v tomto směru ještě o kus dál nad rámec standardu. Kromě univerzálního podepisovacího klíče můžete vygenerovat zvláštní klíč pro každou aplikaci s funkcí claims-mapping (aktuálně v preview).

# Načtení dalších podrobností uživatele
Token sice máme, ale moc informací v něm není. Hodil by se nám třeba email uživatele nebo rovnou jeho profil včetně hezkého jména (zadal jsem při vytváření uživatele jako Tomas User1). Abychom je dostali, musíme si o ně říct - tedy do scope kromě openid přidáme ještě email nebo rovnou celý profile. Zopakujme přihlášení s tím, že do scope dáme openid+profile (to + je URL encoded mezera).

```
https://login.microsoftonline.com/cdc3cb25-000b-429b-ab96-d7ef178575e5/oauth2/v2.0/authorize?client_id=45d4844f-9df4-4381-a7b4-bbf9957e565e&response_type=id_token&redirect_url=http%3A%2F%2Flocalhost&response_mode=fragment&scope=openid+profile&state=12345&nonce=54321
```

Všimněte si, že souhlas znovu dávat nemusíte - už byl zaznamenán a AAD si to pamatuje.

Výsledný id_token opět rozbalíme v jwt.ms a už toho vidíme víc.

![](/images/2019/2019-09-16-06-41-44.png){:class="img-fluid"}

# Správa souhlasů uživatele
Jako uživatel se můžu podívat na https://myapps.microsoft.com/, kde najdu aplikace, ke kterým jsem se přihlásil.

![](/images/2019/2019-09-16-07-00-40.png){:class="img-fluid"}

Pojďme teď tuto aplikaci odstranit.

![](/images/2019/2019-09-16-07-01-07.png){:class="img-fluid"}

Po odstranení doporučuji třeba minutu počkat. Následně se pokuste znovu přihlásit do "aplikace". Protože jsme souhlas odstranili, budeme o něj znovu požádání:

![](/images/2019/2019-09-16-07-04-33.png){:class="img-fluid"}

# Souhlas udělený administrátorem za celou organizaci
U interní aplikace, která chce jen přihlášení a žádná další složitá práva možná nepotřebujete, nemusí dávat smysl, aby každý uživatel individuálně uděloval souhlas. Mohlo by je to mást a třeba vám to připadá zbytečné. V takovém případě může udělit souhlas administrátor pro celou vaší organizaci a uživatelů už se AAD ptát nebude. To se dá udělat buď staticky v GUI aplikační registrace, nebo dynamickým způsobem. To má tu výhodu, že udělení administrátorského souhlasu můžete dát přímo do vaší aplikace.

Nejprve jděte do myapps jako user1 a aplikaci znova odstraníme, čímž revokujeme svůj souhlas.

Následně v jiném anonymním okně jiného prohlížeče (nebo to předchozí zavřete) otevřete přihlašovací URL, ale tentokrát se přihlásíme účtem administrátora

![](/images/2019/2019-09-16-07-12-47.png){:class="img-fluid"}

Jako administrátor mohu udělit souhlas jménem celé organizace.

![](/images/2019/2019-09-16-07-13-50.png){:class="img-fluid"}

Teď se přihlašte znova jako user1 a všimněte si, že přestože jsme svůj konsent revokovali vymazáním aplikace z myapps, nemusíme ho znovu udělit. Administrátor to udělal jménem celé organizace.

Dnes jsme si prošli základní scénář ověření interního uživatele AAD přes OpenID Connect protokol. Nějaké detaily jsem vynechal, ale pyramida se také nejlépe staví postupně. Přístě zkusíme to samé, ale pro vaše zákazníky, tedy AAD B2C. Navíc přibude možnost registračních flow uživatelů, resetování zapomenutého hesla nebo integrace přihlašování ze sociálních sítí typu LinkedIn, Google či Facebook.

