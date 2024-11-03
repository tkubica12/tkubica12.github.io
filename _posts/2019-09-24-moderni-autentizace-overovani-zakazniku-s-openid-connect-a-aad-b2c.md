---
layout: post
title: 'Moderní autentizace: ověřování zákazníků s OpenID Connect v AAD B2C'
tags:
- Security
- AAD
---
V minulém díle jsme použili OpenID Connect pro ověřování interních (nebo federovaných) uživatelů v AAD a dnes se zaměříme na koncové zákazníky. Ty typicky nechcete spravovat ve stejném tenantu, ale ve vyčleněném pro tyto účely. Přesně na to je Azure Active Directory B2C, která ale řeší dost dalších věcí, které určitě ve své aplikaci potřebujete. Tak například se umí integrovat na jiné identitní systémy jako je Google či Facebook a jednoduše vám zprostředkovat možnost logování zákazníků přes jejich účty na sociálních sítí (bez nutnosti psát pokáždé znovu kód, který by to dělal). Také umožňuje uživatelům vytvořit si samostatně účet, ověřit například platnost jejich emailu nebo jim umožnit resetovat zapomenuté heslo a tak podobně - vše jako součást služby, tedy bez práce a jednotně pro všechny vaše zákaznické aplikace.

# Založení Azure Active Directory B2C
Nejprve si tenant AAD B2C založím.

![](/images/2019/2019-09-17-06-40-36.png){:class="img-fluid"}

![](/images/2019/2019-09-17-06-42-02.png){:class="img-fluid"}

Pro jeho správu potřebuji na portále přepnout do tohoto nového tenantu.

![](/images/2019/2019-09-17-06-47-24.png){:class="img-fluid"}

Následně půjdu do All services a najdu si Azure AD B2C.

![](/images/2019/2019-09-17-07-14-24.png){:class="img-fluid"}

# Základní OpenID Connect řešení
To nejzákladnější ověření existujícího uživatele funguje úplně stejně jako u AAD interních uživatelů, které jsme rozebírali minule, takže to dnes ani zkoušet nebude (jak na to najdete v předchozím článku).

# Registrace a přihlášení uživatele
Na rozdíl od běžného AAD umí B2C vytvářet user flows, které umožňují například registraci nového uživatele. V rámci portálu máte celou řadu možných nastavení a flows můžete vytvořit hned několik třeba pro různé typy aplikací, customizovat grafickou podobu přihlášení a tak dále. Pokud vám tyto možnosti nestačí, můžete si vytvořit i svoje vlastní politiky přes import XML souborů, ale to my dělat nebudeme.

Přidáme si nové user flow.

![](/images/2019/2019-09-17-07-33-11.png){:class="img-fluid"}

Ze šablony si vybereme přihlašovací/registrační flow.

![](/images/2019/2019-09-17-07-33-50.png){:class="img-fluid"}

User flow bude mít nějaký název, který budeme AAD sdělovat v okamžiku přesměrování uživatele na registraci. Jaké flow se použije tedy můžeme řídit přímo v naší aplikaci.

![](/images/2019/2019-09-17-07-34-51.png){:class="img-fluid"}

Následně si zvolíme identity providera. Zatím tam vidíme jen registraci přes email, ale později si přidáme další.

![](/images/2019/2019-09-17-07-35-37.png){:class="img-fluid"}

AAD B2C podporuje více-faktorové ověření, takže pokud vaše aplikace pracuje s citlivými údaji, můžete uživatelům nabídnout tuto formu velmi vysokého zabezpečení.

![](/images/2019/2019-09-17-07-36-49.png){:class="img-fluid"}

Nakonec si řekneme, jaké údaje chceme u uživatele evidovat při registraci a co chceme vracet v claimu po přihlášení (tedy jaké atributy naše aplikace uvidí). Rád bych kolektoval a vracel country, při registraci uložil email a v claimu vracel všechny co o uživateli vím a do claimu bych rád ještě informaci o použitém identity providerovi (to se nám bude hodit později). 

![](/images/2019/2019-09-17-07-39-43.png){:class="img-fluid"}

Dole se mi líbí ještě jedna volba - v claimu se dozvím, zda se uživatel právě zaregistroval a je tu poprvé, na což bych chtěl aplikaci reagovat nějakým uvítáním či spuštěním průvodce ovládání aplikace.

![](/images/2019/2019-09-17-07-40-40.png){:class="img-fluid"}

Všimněme si, že po dokončení průvodce jsou možná další nastavení a úpravy. Například vlastní design stránek.

![](/images/2019/2019-09-17-07-50-46.png){:class="img-fluid"}

Můžeme si přidate podporu češtiny nebo dokonce nahrát vlastní slovníky s překlady.

Teď si zaregistrujeme aplikaci, podobně jako u klasického AAD.

![](/images/2019/2019-09-17-07-48-44.png){:class="img-fluid"}

Pojďme si to vyzkoušet. Pokud to chcete jednoduše, jděte do user flow a je tam "play" tlačítko. My ale, abychom měli stejný postup jako u dalších AAD článků, použijeme URI sami v browseru. Struktura přihlášení vypadá v mém případě takhle:

```
https://b2ctomaskubica.b2clogin.com/b2ctomaskubica.onmicrosoft.com/oauth2/v2.0/authorize?p=B2C_1_mojeprihlasovani&client_id=99a73bf2-ad78-4e81-ab35-0c5ae74c6737&nonce=defaultNonce&redirect_uri=http%3A%2F%2Flocalhost&scope=openid&response_type=id_token&prompt=login
```

Všimněte si jiného base URL, než jsme zvyklí, ale zbytek docela známe. Novinkou je atribut p, který identifikuje naše user flow. Pak je tu client_id (z registrace aplikace), nonce, redirect_uri, scope, response_type a ty už známe z minula. Prompt atribut napovídá AAD jaký dialog vlastně chceme vyvolat.

Objevila se mi přihlašovací stránka. Já ale login nemám, tak kliknu na sign up.

![](/images/2019/2019-09-17-07-57-20.png){:class="img-fluid"}

Zadám svůj email a kliknu na odeslání ověřovacího kódu. Přišel mi do emailu a já ho sem přeťukám.

![](/images/2019/2019-09-17-07-59-31.png){:class="img-fluid"}

Všimněme si, že jsem tázán na country. To souvisí s tím, že tento atribut jsme chtěli kolektovat, tak se na něj AAD ptá.

![](/images/2019/2019-09-17-08-00-22.png){:class="img-fluid"}

Všechno prošlo, dostávám id_token ve fragmentu. Dekóduji na jwt.ms a zjišťuji, že jsem dostal co potřebuji - email, country a informaci o tom, že to je nový uživatel.

![](/images/2019/2019-09-17-08-03-01.png){:class="img-fluid"}

Zavřu okno a zkusím to celé znovu, ale tentokrát už jako registrovaný uživatel.

![](/images/2019/2019-09-17-08-04-03.png){:class="img-fluid"}

Všechno prošlo a v tokenu vidím, že už to není nový uživatel.

![](/images/2019/2019-09-17-08-05-12.png){:class="img-fluid"}

# Úprava profilu či resetování hesla
Přidejme si teď user flow pro resetování hesla nebo editaci profilu.

![](/images/2019/2019-09-17-11-35-53.png){:class="img-fluid"}

![](/images/2019/2019-09-17-11-36-43.png){:class="img-fluid"}

Výsledná URL bude vypadat takhle:

```
https://b2ctomaskubica.b2clogin.com/b2c.tomaskubica.in/oauth2/v2.0/authorize?p=B2C_1_resetpassword&client_id=99a73bf2-ad78-4e81-ab35-0c5ae74c6737&nonce=defaultNonce&redirect_uri=http%3A%2F%2Flocalhost&scope=openid&response_type=id_token&prompt=login
```

![](/images/2019/2019-09-17-11-46-24.png){:class="img-fluid"}

Projdu procesem resetování hesla přes kód na email a následně se do aplikace dostane id_token. Tentokrát jsem nevybral email (což bychom normálně asi chtěli), nicméně jde mi o to ukázat, že v políčku tfp vidím user flow, které bylo použito. V aplikaci tedy vím, že bylo použito flow pro reset hesla.

![](/images/2019/2019-09-17-11-49-19.png){:class="img-fluid"}

Ještě si všimněme, že na normální přihlašovací obrazovce je Forget your password?

![](/images/2019/2019-09-17-11-50-31.png){:class="img-fluid"}

Nicméně to samo o sobě nevede na spuštění procesu pro reset hesla, protože můžete mít hned několik user flow, třeba pro každou aplikaci jiné. O tom jaké použít se tedy chceme rozhodnout v aplikaci. Proto mi do ní AAD vráti chybovou hlášku:

```
http://localhost/#error=access_denied&error_description=AADB2C90118%3a+The+user+has+forgotten+their+password.%0d%0aCorrelation+ID%3a+b89afdaf-03ef-4a39-b2b7-7f0899ef6566%0d%0aTimestamp%3a+2019-09-17+09%3a50%3a39Z%0d%0a
```

Je tedy na mě na ní reagovat a přesměrovat uživatele na flow s resetem hesla.

# Integrace sociálních sítí
Mohu mít různé důvody pro používání svých vlastních loginů a hesel, ale jako uživatel mám rád, když mi aplikace umožní pro přihlášení použít svůj login na sociální síti, třeba Google nebo LinkedIn. Nemusím si tak pamatovat zase další heslo a také mohu mít jistotu, že je přihlášení dobře zabezpečeno například více-faktorovým ověřením, aniž bych se musel spoléhat na aplikaci, že takovou možnost má (ale jak jsme psali s AAD B2C není žádný problém takové zabezpečení nabídnout). Zda chcete či nechcete tohle umožnit je na vás. Pravdou je, že pak Google ví kdy se kdo k vaší aplikaci přihlašuje a těžko říct, co se těmi daty dělá (resp. lehko říct, ale nechci spekulovat - je to zdarma, tak to něco asi znamená). Na druhou stranu je to pro uživatele pohodlné. Zkrátka záleží na povaze vaší aplikace - pro přístup ke zdravotní dokumentaci bych Google login nepreferoval, pro přístup k aplikacím, které mohou být pro Google konkurenční (multimediální obsah například) asi taky ne (za AAD platím a vím, že Microsoft si na službu tímto vydělal aniž by prodával moje data). Ale pro e-shop bych asi problém neměl ... tam bych zas nechtěl svůj obchod integrovat na identitu Amazonu.

Pojďme si napojit identity providera. Příjemné je, že řada konektorů už je připravena na jednoduché zprovoznění, nicméně můžete se napojit i na generického OpenID Connect providera, pokud ten váš v nabídce není.

![](/images/2019/2019-09-17-13-46-02.png){:class="img-fluid"}

Pro konfiguraci potřebujeme zaregistrovat AAD B2C u Googlu a na oplátku od nich získáme client id a secret.

![](/images/2019/2019-09-17-13-46-56.png){:class="img-fluid"}

Půjdu do Google Developers konzole a provedu registraci. Nejprve vytvořím nový projekt.

![](/images/2019/2019-09-17-13-48-35.png){:class="img-fluid"}

Jdu do Credentials a přidám nové.

![](/images/2019/2019-09-17-13-50-01.png){:class="img-fluid"}

Bude to po mně chtít nastavit si obrazovku se souhlasem.

![](/images/2019/2019-09-17-13-51-38.png){:class="img-fluid"}

![](/images/2019/2019-09-17-13-53-31.png){:class="img-fluid"}

Registrovaná aplikace je webová a musím povolit doménu přiřazenou k mému AAD B2C.

![](/images/2019/2019-09-17-14-04-41.png){:class="img-fluid"}

Získám client id a client secret.

![](/images/2019/2019-09-17-13-57-56.png){:class="img-fluid"}

Tyto údaje zadáme do AAD B2C.

![](/images/2019/2019-09-17-13-59-04.png){:class="img-fluid"}

Pojďme teď do našeho existujícího user flow přidat možnost přihlášení přes Google.

![](/images/2019/2019-09-17-14-00-08.png){:class="img-fluid"}

Vyzkoušíme si to. V novém okně spustím přihlašovací mechanismus stejně, jako před tím.

```
https://b2ctomaskubica.b2clogin.com/b2ctomaskubica.onmicrosoft.com/oauth2/v2.0/authorize?p=B2C_1_mojeprihlasovani&client_id=99a73bf2-ad78-4e81-ab35-0c5ae74c6737&nonce=defaultNonce&redirect_uri=http%3A%2F%2Flocalhost&scope=openid&response_type=id_token&prompt=login
```

Mám tady novou možnost přihlášení přes Google.

![](/images/2019/2019-09-17-14-02-09.png){:class="img-fluid"}

![](/images/2019/2019-09-17-14-05-09.png){:class="img-fluid"}

Funguje i druhý faktor.

![](/images/2019/2019-09-17-14-07-29.png){:class="img-fluid"}

Následuje obrazovka se souhlasem.

![](/images/2019/2019-09-17-14-08-05.png){:class="img-fluid"}

V rámci vytváření účtu jsem žádal o další informace od uživatele, v mém případě country.

![](/images/2019/2019-09-17-14-08-41.png){:class="img-fluid"}

Výborně. To je celé a už tu mám id_token z AAD B2C.

![](/images/2019/2019-09-17-14-10-13.png){:class="img-fluid"}

Můžu se podívat do AAD B2C a vidím v něm jak uživatele, co se registroval na email, tak toho druhého, který využil přihlášení přes Google.

![](/images/2019/2019-09-17-14-11-59.png){:class="img-fluid"}


AAD B2C je výborný způsob jak řešit identity vašich zákazníků. Je to jednotný systém pro všechny vaše aplikace a neobjevujete znovu a znovu kolo. Navíc AAD B2C jede podle posledních bezpečnostních best practice a určitě nechcete být nuceni reportovat úřadům únik přístupových dat uživatelů a nechat se propírat v novinách, což se často u podomácku řešených identitních systémů stává. AAD B2C ušetří spoustu práce s registrací a evidencí uživatelů, úpravy údajů (třeba změna adresy) či zapomenutá hesla a z jednoho místa vyřešíte napojení dalších identitních providerů aniž byste to museli řešit pro každou aplikaci zvlášť (pokud to neudělám přes AAD B2C, tak musím u všech providerů registrovat všechny aplikace jednu po druhé). AAD B2C toho umí ještě víc, ale na to se podíváme zase někdy jindy. Příště už se totiž pustíme do toho, proč OAuth2 vlastně vznikl - autorizace a delegace oprávnění.

