---
layout: post
title: 'Moderní autentizace: oprávnění pro procesy běžící v pozadí s AAD'
tags:
- Security
- AAD
---
V minulém díle jsme se pustili do autorizace aplikace, která přistupovala na Payroll API. Dnes budeme chtít vyřešit dva problémy. Co když potřebujeme, aby naše aplikace fungovala v pozadí i po té, co uživatel opustil stránku a v pozadí s Payroll API komunikovala jménem uživatele? Token po hodině vyprší a co dál. Navíc můžeme mít ještě jinou aplikaci, která odesílá peníze v dávkách a autorizace jménem uživatele tam nedává smysl - potřebovali bychom se přihlásit ke všem účtům a dávkově zpracovávat.

# Udržení přístupu s refresh tokenem
Pokračujme kde jsme minule skončili, tedy máme zaregistrovanou aplikaci, zaregistrované Payroll API a umíme si jménem uživatele říci o access_token. Teď potřebujeme, aby aplikace v pravidelných intervalech na Payroll API přistupovala i po té, co uživatel opustil stránku. Když token vyprší, nemáme uživatele a nemůžeme tedy projet kolečko pro získání nového tokenu.

OAuth2 tohle řeší vydáváním refresh tokenu. Díky němu můžeme na pozadí v aplikaci požádat o nový token aniž bychom museli mít uživatele v okně. Podstatné ale je, že AAD má minimálně každou hodinu možnost se k tomu vyjádřit. Token tedy nelze revokovat (OAuth2 je stateless), ale pokud oprávnění odeberu, prodloužení už se nepovede. Vyzkoušejme si to.

Refresh token od AAD získáme tak, že do scope přidáme offline_access. Výsledné URI z minula tedy upravíme takto:

```
https://login.microsoftonline.com/cdc3cb25-000b-429b-ab96-d7ef178575e5/oauth2/v2.0/authorize?client_id=462daa70-e21e-4136-a2f5-5d1ba2011736&response_type=code&redirect_url=http%3A%2F%2Flocalhost&response_mode=query&scope=api%3A%2F%2Fmypayroll%2FAccount.Read+offline_access&state=12345
```

Použijeme opět Postman k vyzvednutí tokenu a tentokrát získáváme i refresh_token.

![](/images/2019/2019-09-23-06-19-34.png){:class="img-fluid"}

Token mi končí v tento čas:

![](/images/2019/2019-09-23-06-21-17.png){:class="img-fluid"}

Požádejme si teď o nový token z backendu. Použijeme atribut refresh_token, grant_type bude refresh_token a potřebujeme také client_id a client_secret.

![](/images/2019/2019-09-23-06-27-30.png){:class="img-fluid"}

Dostáváme nový access_token a také nový refresh_token.

![](/images/2019/2019-09-23-06-28-09.png){:class="img-fluid"}

Srovnejme konec platnosti access_token s předchozím.

![](/images/2019/2019-09-23-06-28-59.png){:class="img-fluid"}

Pojďme teď aplikaci odebrat z myapps nebo změnit heslo uživatele.

![](/images/2019/2019-09-23-06-31-47.png){:class="img-fluid"}

Minutku počkáme a zkusíme, jestli refresh_token funguje. Nechodí. Odebrání souhlasu nebo změna hesla uživatele refresh_token zneplatnilo a musíme jít interaktivním přihlášením.

![](/images/2019/2019-09-23-06-33-47.png){:class="img-fluid"}

# Autentizace aplikace vůči aplikaci
Pojďme probrat druhý scénář. Tentokrát budeme mít aplikaci robutek, která ma za úkol pravidelně načítat čísla bankovních účtu všech uživatelů a například z důvodu zjednodušení nebude používat komunikaci na Payroll API autorizovanou jménem uživatele (například takových uživatelů je 10 000 a token pro každého zvlášť se nám dělat nechce). Budeme tedy potřebovat aplikaci robutek autorizovat vůči Payroll napřímo, tedy identitou robutek. Něčemu takovému se v AAD typicky říká service principal a samozřejmě na to budeme potřebovat provést správnou registraci aplikace, ale také schválení administrátora. Aplikace pro získání token použije buď "jméno a heslo", tedy client_id a client_secret nebo certifikát.

Zaregistrujeme aplikaci robutek a nemusíme zadávat redirect URL (nepřihlašujeme se interaktivně).

![](/images/2019/2019-09-23-11-12-09.png){:class="img-fluid"}

Oprávnění se v tomto případě (tzv. client credentials flow neboli grant) v AAD musí definovat staticky. Přidejme robutkovi práva na Payroll.

![](/images/2019/2019-09-23-11-13-33.png){:class="img-fluid"}

![](/images/2019/2019-09-23-11-14-01.png){:class="img-fluid"}

![](/images/2019/2019-09-23-11-14-31.png){:class="img-fluid"}

Jako administrátor AAD udělím robůtkovi souhlas.

![](/images/2019/2019-09-23-11-15-13.png){:class="img-fluid"}

Výborně. Teď potřebujeme nějaké heslo, které robůtek použije pro získání access_token.

![](/images/2019/2019-09-23-11-17-04.png){:class="img-fluid"}

![](/images/2019/2019-09-23-11-17-34.png){:class="img-fluid"}

Heslo si zkopírujeme.

![](/images/2019/2019-09-23-11-18-01.png){:class="img-fluid"}

Použijeme Postman a namíříme na endpoint pro vyzvedávání tokenů. Jako parametry budeme potřebovat client_id, client_secret, grant_type, který bude client_credentials a také scope. Tady je situace trochu jiná, než jsme zvyklí. Client credentials flow využívá staticky definovaná oprávnění a dává přístup k resource, tedy Payroll v našem případě. Místo vylistování konkrétních oprávnění, tak bude scope .default. Výsledek vypadá nějak takhle:

![](/images/2019/2019-09-23-11-22-09.png){:class="img-fluid"}

Výborně, máme token.

![](/images/2019/2019-09-23-11-22-32.png){:class="img-fluid"}

Je určen pro Payroll.

![](/images/2019/2019-09-23-11-23-07.png){:class="img-fluid"}

Také v něm nacházím identifikátor aplikace robutek a informaci, že se prokázala přes client_secret.

![](/images/2019/2019-09-23-11-23-42.png){:class="img-fluid"}

Místo client_secret bychom mohli použít certifikát. To v rámci mého neprogramátorského koutku dělat nebudu, protože bychom se museli zamotat do různých nástrojů a postupů, které pro nás dobře udělá nějaké hezké SDK. V zásadě jde o to, že robutek bude mít certifikát a jeho pulic verze se nahraje do AAD v jeho registraci. Následně robutek použije client assertion, tedy vygeneruje si JWT a to podepíše právě tím svým certifikátem. Díky tomu ho AAD pozná a nahrazuje jednodušší client_secret.

Dnes jsme si ukázali, jak si aplikace může přes refresh token říci o další access_token i v případě, že uživatel už na obrazovce není a může jeho jménem operovat na pozadí. Také jsme si prošli případ, kdy nějaké zpracování probíhá přes veškerá data a ověřování přes uživatele tam není vhodné. Tam jsme použili service principal a client credential flow (grant). 