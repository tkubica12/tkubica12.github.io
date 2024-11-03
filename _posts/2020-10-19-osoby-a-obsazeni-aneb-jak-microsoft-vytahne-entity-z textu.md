---
layout: post
published: true
title: Osoby a obsazení aneb jak Microsoft AI vytáhne entity z textu včetně češtiny
tags:
- AI
---
Cognitivní služby v Azure jsou velmi mocné a je to hodně zajímavá oblast. Bohužel čeština není zrovna světový jazyk a tak podpora pro ni není nikdy na úrovni hlavních jazyků planety, ale přesto se do služeb postupně dostává. Dnes si vyzkoušíme Named Entity Recognizer, který češtinu podporuje a řekneme si i co navíc umí v jiných jazycích (a na co se tak snad můžeme těšit v češtině později).

# Analýza textu
Tato funkce je součástí rodiny služeb pro analýzu textu. Tam patří rozpoznání sentimentu (například pokud potřebujete identifikovat pochvalné nebo naštvané příspěvky), vytažení klíčových slov (v podstatě zjištění o čem text je, co je hlavním sdělením ať už pro účely generování metadat a následného vyhledávání, vytažení hlavních myšlenek a akčních bodů z emailu apod.) nebo právě detekce entit. Zatím pouze poslední zmíněná funkce podporuje češtinu, proto si ji vyzkouším jako první.

# Named Entity Recognizer
Představte si, že vezmete Dostojevského román a chcete zjistit hlavní používané entity. Tím mám na mysli osoby, místa, instituce a tak podobně. NER vám vrátí nalezené entity a jejich přesné místo v knize. Následně si můžeme tato data vzít a zjistit nejčastěji zmiňované osoby nebo místa a naplnit tím metadata patřící ke knize a tak podobně. Představme si třeba, že vezmete všechny novinové texty u nás a tyto informace z nich začnete těžit. Jste tak schopni vědět o kom se píše, o jakých místech nebo institucích články jsou. Na základě analýzy těchto dat v čase můžete identifikovat klíčové osoby politiky v jednotlivých obdobích nebo přes detekci anomálií zjistit, že se o někom píše neobvykle často (takže má asi průšvih nebo úspěch).

Řešení vyhledá i osobní údaje, ale pro angličtinu jde služba ještě dál díky speciální variantě pro zdravotnictví. Systém dokáže vytáhnout dignózu, orgány, nemoce, léčiva, dávkování, rodinnou příslušnost, symptomy a mnoho dalších entit. Následně vám vrátí i klíčové vztahy mezi entitami, tedy například datum vyšetření nebo dávka medikace. Určitě si dokážete představit kolik záznamů ve zdravotnictví existuje, kde se tohle všechno vyskytuje a jak zajímavé by mohlo být tato data analyzovat za účelem zhodnocení kvality léčiv, postupů a tak podobně. Prvním krokem k analýze ale je získat strukturovaná data a ta často v takové podobě připravena nejsou - NER z běžných lékařských záznamů vytáhne strukturovaná data.

# Povídka Šimka a Grossmana
Vyzkoušel jsem vzít text povídky Šimka a Grossmana - Jak jsem cestoval ([https://www.youtube.com/watch?v=vKoRJiZeZ40](https://www.youtube.com/watch?v=vKoRJiZeZ40)). Sekce může mít jen 5000 bytů, tak jsem ji rozdělil do částí a smotnoval JSON, který jsem poslal do Speech API. V textu bylo hodně uvozovek, tak jsem použil escapovací online program. Výsledný dotaz vypadal takhle:

```bash
curl -X POST "https://mujtext.cognitiveservices.azure.com/text/analytics/v3.0/entities/recognition/general?model-version=latest&showStats=true" \
-H "Content-Type: application/json" \
-H "Ocp-Apim-Subscription-Key: mujklicek" \
--data-ascii '
{
  "documents": [
    {
      "language": "cs",
      "id": "1",
      "text": "Kdy\u017E jsem  se takhle jednoho  p\u011Bkn\u00E9ho dne probudil  vedle sv\u00E9\r\n              \u017Eeny Marcely, dob\u0159e  jsem si ji prohl\u00E9dl a  rozhodl se, \u017Ee tento\r\n              rok budu muset  v\u00EDce cestovat. Proto jsem uv\u00EDtal,  kdy\u017E jsem byl\r\n              za  sv\u00E9  pracovn\u00ED  \u00FAsp\u011Bchy   vybr\u00E1n  je\u0161t\u011B  spole\u010Dn\u011B  s  kolegou\r\n              Ing.Mach\u00E1\u010Dkem a  vedouc\u00EDm odbytu Karlem J\u00EDlkem,  kter\u00FD sice nem\u00E1\r\n              titul, ale m\u00E1 \u00FAsp\u011Bch u  \u017Een, na tematick\u00FD z\u00E1jezd POZNEJTE EVROP-\r\n              SK\u00C9 P\u0158\u00CDSTAVY do Hamburku.\r\n                 Radostn\u011B jsem ten den ve  vr\u00E1tnici odp\u00EDchl a ut\u00EDkal dom\u016F sd\u011B-\r\n              lit  \u017Een\u011B tu  radostnou novinu.  Pohled na  Marcelu, kter\u00E1  m\u011Bla\r\n              pr\u00E1v\u011B ve vlasech nat\u00E1\u010Dky a  na obli\u010Deji ple\u0165ovou masku z dro\u017Ed\u00ED,\r\n              m\u011B p\u0159esv\u011Bd\u010Dil,  \u017Ee Hamburk u\u017E pot\u0159ebuji  jako soli. Marcela v\u0161ak\r\n              byla  jin\u00E9ho  n\u00E1zoru  :  \"Tv\u016Fj  p\u0159\u00EDstav  je domov, K\u00E1jo,\" \u0159ekla.\r\n              Nam\u00EDtl jsem,  \u017Ee m\u011B p\u0159itahuj\u00ED lod\u011B.  \"Tak jsme mohli jet  k moj\u00ED\r\n              mamince do  D\u011B\u010D\u00EDna !\"\r\n                 \"Jen\u017Ee to by  pak byl z\u00E1jezd za trest a  j\u00E1 ho m\u00E1m za odm\u011Bnu,\r\n              Marcelko.\"\r\n                 Letmo  jsem pol\u00EDbil  \u017Eenu na  dro\u017Ed\u00ED a  ode\u0161el do  restaurace\r\n              U kotvy na p\u0159edcestovn\u00ED  poradu. Mach\u00E1\u010Dek s J\u00EDlkem tam  u\u017E na m\u011B\r\n              \u010Dekali.\r\n                 \"Tak kluci,  co si vezmeme s  sebou ?\" zeptal jsem  se, sotva\r\n              jsem dosedl.  \"Tady jsem to  sepsal,\" pochlubil se  J\u00EDlek a hned\r\n              tak\u00E9 \u010Detl : \"Desetkr\u00E1t d\u017Euve\u010D, \u0161i\u0161ku turisty, ten vydr\u017E\u00ED nejd\u00FDl,\r\n              litr tuzemsk\u00FDho, \u0161est sv\u00ED\u010Dek.\"\r\n                 \"Na co sv\u00ED\u010Dky  ?\" podivil jsem se. \"No,  kdyby v hotelu vypli\r\n              proud.  M\u00E1me sv\u00FD  zku\u0161enosti ze  slu\u017Eebn\u00EDch cest.  Vzpome\u0148 si na\r\n              N\u00E1chod,\" usadil  m\u011B J\u00EDlek a  hned pokra\u010Doval :  \"T\u0159ikr\u00E1t kafe za\r\n              dvan\u00E1ct a ponornej va\u0159i\u010D, podnikov\u00FD  suven\u00FDry na v\u00FDm\u011Bnu a pytl\u00EDk\r\n              dvoukorun do  automat\u016F.\" Vyj\u00E1d\u0159il jsem  se seznamem spokojenost,\r\n              ale  Mach\u00E1\u010Dek byl  jin\u00E9ho n\u00E1zoru  : \"P\u00E1nov\u00E9,  nejedeme na tramp,\r\n              jedeme  reprezentovat  podnik.  Uv\u011Bdomte  si,  \u017Ee  m\u00E1te  v\u0161echno\r\n              hrazen\u00FD  od  ROH.  D\u017Euve\u010D  si  schovejte,  a\u017E  pojedete  v  l\u00E9t\u011B\r\n              s rodinou na Zlat\u00FD p\u00EDsky do  Bratislavy. "
    },
    {
      "language": "cs",
      "id": "2",
      "text": "My mus\u00EDme sehnat akor\u00E1t\r\n              marky a spolehlivou p\u00E1nskou ochranu.\"\r\n                 \"Pro\u010D ?\" zeptal jsem se, \"ty se chce\u0161 pr\u00E1t ?\"\r\n                 \"Nech si  ty kecy na koledu.  Hamburk je m\u011Bsto h\u0159\u00EDchu  a na\u0161\u00ED\r\n              povinnost\u00ED je  sice dob\u0159e reprezentovat,  ale neriskovat zdrav\u00ED.\r\n              Nerad bych, a\u017E se vr\u00E1t\u00EDme, zamotal na\u0161emu zdravotnictv\u00ED hlavu.\"\r\n                 Banka i gum\u00E1rensk\u00FD pr\u016Fmysl n\u00E1s  vybavily perfektn\u011B. A\u017E na to,\r\n              \u017Ee bance jsme museli je\u0161t\u011B  trochu pomoci v \u010Dern\u00E9 pobo\u010Dce hotelu\r\n              ALCRON. Kurs  jedna ku t\u0159iceti  byl ten den  sice trochu nep\u0159\u00EDz-\r\n              niv\u00FD, ale nakonec do Hamburku  nejezd\u00EDme ka\u017Ed\u00FD t\u00FDden, a tak jsem\r\n              to vydr\u017Eel. Den p\u0159ed odjezdem jsme je\u0161t\u011B zvolili vedouc\u00EDm na\u0161eho\r\n              kolektivu Ing.L\u00E1\u010Fu Mach\u00E1\u010Dka,kter\u00FD z n\u00E1s m\u011Bl s cetov\u00E1n\u00EDm nejv\u011Bt\u0161\u00ED\r\n              zku\u0161enosti, nebo\u0165 byl u\u017E t\u0159ikr\u00E1t v Bulharsku jako kapit\u00E1n podni-\r\n              kov\u00E9ho  mu\u017Estva  nohejbalu  a  jedenkr\u00E1t  v  Rumunsku  s Balneou\r\n              a s  pohmo\u017Ed\u011Bn\u00FDm  kolenem,  do  kter\u00E9ho  ho  v  Bulharsku kopli.\r\n              Proto\u017Ee  si z  EFFORIE SUD   s Balneou  p\u0159ivezl \u00FAplavici  a tak\u00E9\r\n              proto, \u017Ee  m\u00E1 p\u0159\u00EDli\u0161 \u010Dasto  prsty v nose,  p\u0159ezd\u00EDv\u00E1me mu dr.Emil\r\n              Holub.\r\n\r\n\r\n                 V pond\u011Bl\u00ED r\u00E1no v 7.00  hodin byl sraz v\u0161ech \u00FA\u010Dastn\u00EDk\u016F z\u00E1jezdu\r\n              u Rudolfina.  Odjezd napl\u00E1novan\u00FD  na  osmou  se v\u0161ak  v\u0161ak jemn\u011B\r\n              zdr\u017Eel.  \u0158idi\u010D  autobusu,nositel  odznaku  MILI\u00D3N  KILOMETR\u016E BEZ\r\n              NEHODY,   V\u00E1clav   Dvo\u0159\u00E1k,   le\u017Eel   pod   autobusem,  opravoval\r\n              p\u0159evodovku,ze  kter\u00E9 cr\u010Del  olej  a  prozp\u011Bvoval si  p\u00EDse\u0148 Svoji\r\n              \u0161kodov\u011Bnku  m\u00E1m tak  r\u00E1d. Po  dvou hodin\u00E1ch  le\u017Een\u00ED byla olejov\u00E1\r\n              n\u00E1dr\u017E pr\u00E1zdn\u00E1 a ochrapt\u011Bl\u00FD  milion\u00E1\u0159 V\u00E1clav n\u00E1s po\u017E\u00E1dal, abychom\r\n              si v\u0161ichni  vystoupili, proto\u017Ee tuhle z\u00E1vadu  by nedal dohromady\r\n              ani  Ferda  Mravenec,  \u017Ee  mus\u00ED  zajet  do depa autobus vym\u011Bnit.\r\n              Nastal chaos. Mnoz\u00ED \u00FA\u010Dastn\u00EDci z\u00E1jezdu vyt\u00E1hli \u0161roubov\u00E1ky, za\u010Dali\r\n              jimi obratn\u011B to\u010Dit a vytahovat  z r\u016Fzn\u00FDch \u010D\u00E1st\u00ED autobusu roli\u010Dky\r\n              sto\u010Den\u00FDch  bankovek r\u016Fzn\u00FDch  m\u011Bn. Laborant  Tu\u010Dek, jemu\u017E  dolary\r\n              zapadly  do  podlahy,  kle\u010Del  p\u0159ed  vousatou \u00FA\u010Detn\u00ED Mar\u0161\u00E1lkovou\r\n              a pla\u010D\u00EDc \u017Eadonil o pinzetu. Kdy\u017E  mu nab\u00EDdla, \u017Ee mu vytrh\u00E1 vousy\r\n              sama,  nebo\u0165  m\u00E1  na  to  grif,  m\u00E1vl  odevzdan\u011B  rukou  a za\u010Dal\r\n              v podlaze dloubat no\u017E\u00EDkem.\r\n                 Nov\u00FD autobus byl p\u0159istaven v 16.00 odpoledne. Nastoupili jsme\r\n              a \u010Dekali  je\u0161t\u011B chv\u00EDli  na Tu\u010Dka,  kter\u00FD p\u0159ijel  z depa tax\u00EDkem.\r\n              V lev\u00E9  ruce  dr\u017Eel  v\u00EDt\u011Bzoslavn\u011B  potrhan\u00E9  dolary  a \u00FAp\u011Bnliv\u00FDm\r\n              hlasem prohl\u00E1sil: \"Mus\u00EDte mi zastavit  u pap\u00EDrnictv\u00ED ! Je\u0161t\u011B ne\u017E\r\n              opust\u00EDme na\u0161i  drahou, milovanou vlast,  mus\u00EDm sehnat pr\u016Fhlednou\r\n              lepenku !\"\r\n "
    },
    {
      "language": "cs",
      "id": "3",
      "text": "Dal\u0161\u00ED v\u011Bt\u0161\u00ED zdr\u017Een\u00ED bylo kupodivu  a\u017E na celnici. Na ob\u010Dansk\u00E9\r\n              upozorn\u011Bn\u00ED z m\u00EDsta bydli\u0161t\u011B  byl podnikov\u00E9mu l\u00E9ka\u0159i MUDr. Maz\u00E1n-\r\n              kovi celn\u00EDmi  org\u00E1ny bolestiv\u011B vyta\u017Een  z ned\u016Fstojn\u00E9ho m\u00EDsta  na\r\n              t\u011Ble l\u00E9ka\u0159sk\u00FD  diplom. Marn\u011B se  vymlouval, \u017Ee cht\u011Bl  v Hamburku\r\n              l\u00E9\u010Dit chud\u00E9.  Tematick\u00FD z\u00E1jezd POZNEJ EVROPSK\u00C9  P\u0158\u00CDSTAVY byl pro\r\n              n\u011Bj ukon\u010Den v \u0161ir\u00FDch \u0161umavsk\u00FDch hvozdech.\r\n                 Kone\u010Dn\u011B se dal autobus znovu do pohybu. \u0158idi\u010D milion\u00E1\u0159 V\u00E1clav\r\n              \u0161l\u00E1pnul po\u0159\u00E1dn\u011B  na plyn a v\u011Bdom  si toho, \u017Ee zde  nen\u00ED omezov\u00E1n\r\n              vyhl\u00E1\u0161kou  100, vyvinul  \u0161edes\u00E1tikilometrovou rychlost.  N\u011Bkte\u0159\u00ED\r\n              \u00FA\u010Dastn\u00EDci z\u00E1jezdu  si prohl\u00ED\u017Eeli krajinu,  ale my \u010Dty\u0159i  jsme se\r\n              z\u00E1jmem sledovali mzdovou \u00FA\u010Detn\u00ED V\u011Bru \u00DAlisnou, kter\u00E9 padala hlava\r\n              na v\u0161echny strany,nej\u010Dast\u011Bji pak dozadu. Zrovna kdy\u017E jsme za\u010Dali\r\n              uzav\u00EDrat s\u00E1zky, pro\u010D tomu tak je,  V\u011Bra \u00DAlisn\u00E1 se s v\u00FDk\u0159ikem \"U\u017E\r\n              to  nevydr\u017E\u00EDm   !\"  chytla  za  hlavu   a  s  chatrnou  v\u00FDmluvou\r\n              :\"Proboha,co mi to tam ta  kade\u0159nice zase dala...?\" za\u010Dala vyta-\r\n              hovat z drdolu brou\u0161en\u00FD servis Moser pro \u0161est osob.\r\n                 Milan V\u00E1gner  z osobn\u00EDho odd\u011Blen\u00ED,  vedouc\u00ED podnikov\u00E9ho foto-\r\n              grafick\u00E9ho krou\u017Eku,  vyndal fotoapar\u00E1t a za\u010Dal  \u00DAlisnou i servis\r\n              fotit bleskem. \"A\u0165 na tebe,  V\u011Bru\u0161ko,m\u00E1me n\u011Bjakou pam\u00E1tku v pod-\r\n              nikov\u00E9m albu  !\" \u0159ekl, a  t\u00EDm nazna\u010Dil, \u017Ee  mu na tomto  z\u00E1jezdu\r\n              nep\u016Fjde ani tak o evropsk\u00E9 p\u0159\u00EDstavy jako sp\u00ED\u0161 o kolektiv.\r\n                 \"Ta \u00DAlisn\u00E1 se ale m\u00E1, m\u00E1  tak n\u011Bkdo kliku !\" \u0161eptal z\u00E1vistiv\u011B\r\n              J\u00EDlek. \"Servis Moser  ! Mn\u011B by se na  hlav\u011B neudr\u017Eelo ani rajsk\u00E9\r\n              jabl\u00ED\u010Dko...\" a s beznad\u011Bj\u00ED v o\u010D\u00EDch si p\u0159ejel hlavu, kter\u00E1 nejv\u00EDc\r\n              p\u0159ipom\u00EDnala koleno  a kde p\u00E1r  osam\u011Bl\u00FDch vl\u00E1sk\u016F nem\u011Blo  probl\u00E9my\r\n              s nedostatkem m\u00EDsta.\r\n                 P\u0159i prvn\u00ED zast\u00E1vce na ciz\u00EDm \u00FAzem\u00ED, u benz\u00EDnov\u00E9 pumpy, nevydr-\r\n              \u017Eel Mach\u00E1\u010Dek nap\u011Bt\u00ED okam\u017Eiku,  vystoupil a z automatu NECKERMANN\r\n              se  za rachotu  dvoukorun  za\u010Daly  sypat \u017Ev\u00FDka\u010Dky  a pun\u010Doch\u00E1\u010De.\r\n              Mach\u00E1\u010Dek, rozru\u0161en\u00FD t\u00EDm, \u017Ee  to opravdu fubguje,si spletl sorti-\r\n              ment a za\u010Dal jedny pun\u010Doch\u00E1\u010De \u017Ev\u00FDkat. Brzy v\u0161ak seznal sv\u016Fj omyl\r\n              a s vrozenou  \u010Deskou skromnost\u00ED po\u017E\u00E1dal  majitele pumpy, aby  mu\r\n              pun\u010Doch\u00E1\u010De vym\u011Bnil za jin\u00E9, kdy\u017E mu ud\u011Blal takovou tr\u017Ebu.\r\n\r\n\r\n                 Pach mo\u0159e a nafty n\u00E1s  p\u0159iv\u00EDtal. Byli jsme v Hamburku. Ubyto-\r\n              vali n\u00E1s v  hotelu kategorie C s honosn\u00FDm  n\u00E1zvem SANTA F\u00C9. Na\u0161e\r\n              trojice protekc\u00ED  z\u00EDskala jednol\u016F\u017Ekov\u00FD pokoj  se \u0161ikm\u00FDm stropem,\r\n              kter\u00FD siln\u011B  p\u0159ipom\u00EDnal chudou lodn\u00ED  kajutu. \"P\u0159\u00EDstav se  neza-\r\n              p\u0159e,\" prohl\u00E1sil  Mach\u00E1\u010Dek a za\u010Dal  zkoumat dv\u011B p\u0159ist\u00FDlky,  kter\u00E9\r\n              byly k  nerozezn\u00E1n\u00ED podobn\u00E9 na\u0161im  spartaki\u00E1dn\u00EDm leh\u00E1tk\u016Fm. Loso-\r\n              vali jsme. Gau\u010D vyhr\u00E1l Mach\u00E1\u010Dek, hned se na n\u011Bm \u0161\u0165astn\u011B rozvalil\r\n              a d\u011Blal n\u00E1m chut\u011B.  Ozvalo se zaklep\u00E1n\u00ED a ve  dve\u0159\u00EDch se objevil\r\n              vedouc\u00ED z\u00E1jezdu.  \"Ml\u00E1denci, vedu v\u00E1m  je\u0161t\u011B jednoho nocle\u017En\u00EDka,\r\n              pr\u00FD tady m\u00E1te gau\u010D dvoj\u00E1k !\"\r\n                 \"Jdi  kousek  d\u00E1l,\"  \u0159ekl  fotograf  V\u00E1gner  a  lehl si vedle\r\n              Mach\u00E1\u010Dka. \"Ml\u00E1denci, mysl\u00EDm, \u017Ee by bylo spr\u00E1vn\u00E9 a \u010Destn\u00E9 \u0159\u00EDci si\r\n              o sob\u011B pravdu, a\u0165 je jak\u00E1koliv. CHR\u00C1PU !!!\"\r\n                 "
    },
    {
      "language": "cs",
      "id": "4",
      "text": "Fotograf  V\u00E1gner bohu\u017Eel  nelhal. A\u010Dkoliv  jsme byli  z cesty\r\n              smrteln\u011B vy\u010Derp\u00E1ni, nikdo  z n\u00E1s tu noc nezamhou\u0159il  oka. To, \u017Ee\r\n              \u00FAderem des\u00E1t\u00E9 hodiny ve\u010Dern\u00ED za\u010Dal hr\u00E1t orchestr t\u011Bsn\u011B za gau\u010Dem\r\n              (pozd\u011Bji jsme zjistili, \u017Ee od  p\u00F3dia jsme odd\u011Bleni pouze umakar-\r\n              to- vou st\u011Bnou) n\u00E1m tolik nevadilo. N\u00E1hle se ale ozvalo cosi, co\r\n              siln\u011B  p\u0159ipom\u00EDnalo  zvuky  st\u00E1da  zd\u011B\u0161en\u00FDch  hroch\u016F  p\u0159i  po\u017E\u00E1ru\r\n              v d\u017Eungli.  To  fotograf  V\u00E1gner  usnul sp\u00E1nkem nespravedliv\u00FDch.\r\n              Mach\u00E1\u010Dek vysko\u010Dil z gau\u010De jako bodnut\u00FD v\u010Delou. \"Kur\u0148a chlapi, to\r\n              je p\u0159\u00ED\u0161ern\u00FD, to  snad ani nen\u00ED pravda ! S  n\u00EDm sp\u00E1t nem\u016F\u017Eu, sra-\r\n              z\u00EDme spartaki\u00E1dn\u00ED l\u016F\u017Eka !\" \"Ani n\u00E1pad,\" br\u00E1nil se J\u00EDlek, \"vyhr\u00E1l\r\n              jsi gau\u010D, tak si u\u017E\u00EDvej !\"\r\n              \"Tak  mu ucpu  v\u00FDfuk !\"  vyk\u0159ikl Mach\u00E1\u010Dek  pomstychtiv\u011B a nacpal\r\n              V\u00E1gnerovi  do nosu  dv\u011B fazole.  Chv\u00EDli bylo  ticho,pak se ozval\r\n              n\u00E1dech, fazole  nevydr\u017Eely - a V\u00E1gner  sest\u0159elil lampi\u010Dku. Chr\u00E1-\r\n              p\u00E1n\u00ED potm\u011B  bylo je\u0161t\u011B d\u011Bsiv\u011Bj\u0161\u00ED.  Na dve\u0159e se  ozvalozabouch\u00E1n\u00ED\r\n              a ve\u0161el \u010D\u00ED\u0161n\u00EDk. \"Meine  liebe Herren, was ist das  ? Das ist un-\r\n              m\u00F6glich !\"\r\n                 Pochopili jsme,  \u017Ee V\u00E1gnerova produkce ru\u0161\u00ED  hosty v baru p\u0159i\r\n              tanci a \u017Ee  \u0161patn\u011B sly\u0161\u00ED hudbu. Spole\u010Dn\u00FDmi silami  jsme se vrhli\r\n              na  V\u00E1gnera, ale  p\u0159es ve\u0161ker\u00E9  \u00FAsil\u00ED se  n\u00E1m ho nepoda\u0159ilo pro-\r\n              budit. Vedouc\u00ED orchestru k n\u00E1m ve\u0161el u\u017E bez klep\u00E1n\u00ED. \"Meine Her-\r\n              ren, das ist  Skandal !\" Posv\u00EDtil si na  chr\u00E1pala baterkou a bez\r\n              okolk\u016F mu vrazil do \u00FAst dus\u00EDtko z jazztrubky.\r\n                 V  6.30  r\u00E1no  se  ozvalo  \u0159in\u010Den\u00ED  bud\u00EDku PRIM na\u0159\u00EDzen\u00E9ho na\r\n              sedmou. V\u00E1gner  se prot\u00E1hl, posadil se  a jak zaz\u00EDval, zatroubil\r\n              T\u0159e\u0161\u0148ov\u00E9 kv\u011Bty.  Vyndal si dus\u00EDtko  a \u0159ekl :  \"To jsou ale  blb\u00FD\r\n              f\u00F3ry!\" na\u010De\u017E  si dus\u00EDtko vyfotografoval.Pak  ode\u0161el,pr\u00FD fotogra-\r\n              fovat p\u0159\u00EDstav.\r\n                 Usnuli jsme vys\u00EDlen\u00EDm. Probudil n\u00E1s a\u017E orchestr v deset hodin\r\n              ve\u010Der. J\u00EDlek u\u017E byl vzh\u016Fru a jeho oko bylo p\u0159ipl\u00E1cnut\u00E9 k umakar-\r\n              tov\u00E9 st\u011Bn\u011B. \"Co se to sakra d\u011Bje ?\" zeptal jsem se, ale J\u00EDlek mi\r\n              dal prst  na \u00FAsta: \"Psst  ! Navrtal jsem  to, ty vole  ! Poj\u010F se\r\n              pod\u00EDvat !\"  Nasadil jsem oko k  umakartu. Vid\u011Bl jsem v\u0161echno,na\u010D\r\n              jsem vlastn\u011B tou\u017Eil  do Hamburku p\u0159ijet. Program byl  u\u017E v pln\u00E9m\r\n              proudu. Na  p\u00F3diu p\u0159\u00EDmo p\u0159ed  n\u00E1mi se promenovalo  \u0161est kr\u00E1sn\u00FDch\r\n              d\u00EDvek, kter\u00E9 se zjevn\u011B chystaly ke stript\u00FDzu. Rychle jsem probu-\r\n              dil Mach\u00E1\u010Dka. Bleskem jsem mu  vysv\u011Btlil na\u0161\u00ED situaci. Byl \u0161t\u011Bs-\r\n              t\u00EDm bez sebe. J\u00EDlek u\u017E mezit\u00EDm  vrtal dal\u0161\u00ED dv\u011B d\u00EDry, abychom se\r\n              nemuseli tla\u010Dit.\r\n                 \"To je vono,\" mnul si ruce Mach\u00E1\u010Dek, \"ka\u017Edej svoj\u00ED hv\u011Bzd\u00E1rnu.\r\n              Kluc\u00ED, my jsme  se ale um\u011Bli narodit !  Celej tejden odtud nevy-\r\n              t\u00E1hnu paty. P\u0159\u00EDstav i s lod\u011Bma n\u00E1m ml\u017Eou pol\u00EDbit prdel !\"\r\n\r\n\r\n                 Uva\u0159ili jsme si rychle jednotliv\u011B grog a zasedli ka\u017Ed\u00FD ke sv\u00E9\r\n              d\u00ED\u0159e.  Krasavice  na  p\u00F3diu  za\u010Daly  odhazovat  jednotliv\u00E9 \u010D\u00E1sti\r\n              od\u011Bvu. M\u011Bli jsme o\u010Di navrch hlavy, schylovalo se k fin\u00E1le. \"A to\r\n              v\u0161echno m\u00E1me zadarmo ! V\u00EDte,  kolik tam stoj\u00ED vstupn\u00FD ?\" liboval\r\n              si Mach\u00E1\u010Dek. Gong. Tu\u0161 - a spodn\u00ED pr\u00E1dlo z krasavic spadlo. P\u0159ed\r\n              na\u0161ima d\u00EDrama  se kroutilo \u0161est nah\u00FDch  chlap\u016F. No prost\u011B, v\u00FDlet\r\n              do Hamburku  se zase jednou  pln\u011B vyda\u0159il !!!  U\u017E se zase  t\u011B\u0161\u00EDm\r\n              dom\u016F na Marcelu. Zlat\u00FD dro\u017Ed\u00ED !!!"
    }
  ]
}
' 
```

Tady je k dispozici výsledek:

```json
{
    "statistics": {
        "documentsCount": 4,
        "validDocumentsCount": 4,
        "erroneousDocumentsCount": 0,
        "transactionsCount": 4
    },
    "documents": [
        {
            "id": "1",
            "statistics": {
                "charactersCount": 2291,
                "transactionsCount": 3
            },
            "entities": [
                {
                    "text": "Marcely",
                    "category": "Person",
                    "offset": 82,
                    "length": 7,
                    "confidenceScore": 0.97
                },
                {
                    "text": "Macháčkem",
                    "category": "Person",
                    "offset": 321,
                    "length": 9,
                    "confidenceScore": 0.98
                },
                {
                    "text": "Karlem Jílkem",
                    "category": "Person",
                    "offset": 350,
                    "length": 13,
                    "confidenceScore": 0.95
                },
                {
                    "text": "Pohled",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 631,
                    "length": 6,
                    "confidenceScore": 0.97
                },
                {
                    "text": "Marcela",
                    "category": "Person",
                    "offset": 810,
                    "length": 7,
                    "confidenceScore": 0.97
                },
                {
                    "text": "Děčína",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 1010,
                    "length": 6,
                    "confidenceScore": 0.86
                },
                {
                    "text": "Macháček",
                    "category": "Person",
                    "offset": 1254,
                    "length": 8,
                    "confidenceScore": 0.98
                },
                {
                    "text": "Jílkem",
                    "category": "Person",
                    "offset": 1265,
                    "length": 6,
                    "confidenceScore": 0.96
                },
                {
                    "text": "Jílek",
                    "category": "Person",
                    "offset": 1456,
                    "length": 5,
                    "confidenceScore": 0.99
                },
                {
                    "text": "Náchod",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 1770,
                    "length": 6,
                    "confidenceScore": 0.98
                },
                {
                    "text": "Jílek",
                    "category": "Person",
                    "offset": 1790,
                    "length": 5,
                    "confidenceScore": 0.99
                },
                {
                    "text": "Macháček",
                    "category": "Person",
                    "offset": 2015,
                    "length": 8,
                    "confidenceScore": 0.98
                },
                {
                    "text": "Bratislavy",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 2279,
                    "length": 10,
                    "confidenceScore": 0.91
                }
            ],
            "warnings": []
        },
        {
            "id": "2",
            "statistics": {
                "charactersCount": 2956,
                "transactionsCount": 3
            },
            "entities": [
                {
                    "text": "Hamburk",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 189,
                    "length": 7,
                    "confidenceScore": 0.96
                },
                {
                    "text": "Banka",
                    "category": "Organization",
                    "offset": 398,
                    "length": 5,
                    "confidenceScore": 0.37
                },
                {
                    "text": "Láďu Macháčka",
                    "category": "Person",
                    "offset": 809,
                    "length": 13,
                    "confidenceScore": 0.87
                },
                {
                    "text": "Bulharsku",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 910,
                    "length": 9,
                    "confidenceScore": 0.99
                },
                {
                    "text": "Rumunsku",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 1000,
                    "length": 8,
                    "confidenceScore": 0.99
                },
                {
                    "text": "Bulharsku",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 1083,
                    "length": 9,
                    "confidenceScore": 0.99
                },
                {
                    "text": "Emil",
                    "category": "Person",
                    "offset": 1255,
                    "length": 4,
                    "confidenceScore": 0.86
                },
                {
                    "text": "Holub",
                    "category": "Person",
                    "offset": 1275,
                    "length": 5,
                    "confidenceScore": 0.95
                },
                {
                    "text": "Rudolfina",
                    "category": "Organization",
                    "offset": 1383,
                    "length": 9,
                    "confidenceScore": 0.35
                },
                {
                    "text": "Václav   Dvořák",
                    "category": "Person",
                    "offset": 1551,
                    "length": 15,
                    "confidenceScore": 0.97
                },
                {
                    "text": "Václav",
                    "category": "Person",
                    "offset": 1818,
                    "length": 6,
                    "confidenceScore": 1.0
                },
                {
                    "text": "Ferda  Mravenec",
                    "category": "Person",
                    "offset": 1946,
                    "length": 15,
                    "confidenceScore": 0.95
                },
                {
                    "text": "Laborant  Tuček",
                    "category": "Person",
                    "offset": 2215,
                    "length": 15,
                    "confidenceScore": 0.82
                },
                {
                    "text": "Nový autobus",
                    "category": "Person",
                    "offset": 2546,
                    "length": 12,
                    "confidenceScore": 0.48
                },
                {
                    "text": "Tučka",
                    "category": "Person",
                    "offset": 2650,
                    "length": 5,
                    "confidenceScore": 0.74
                }
            ],
            "warnings": []
        },
        {
            "id": "3",
            "statistics": {
                "charactersCount": 3533,
                "transactionsCount": 4
            },
            "entities": [
                {
                    "text": "Václav",
                    "category": "Person",
                    "offset": 512,
                    "length": 6,
                    "confidenceScore": 0.98
                },
                {
                    "text": "Věru Úlisnou",
                    "category": "Person",
                    "offset": 806,
                    "length": 12,
                    "confidenceScore": 0.23
                },
                {
                    "text": "Věra Úlisná",
                    "category": "Person",
                    "offset": 969,
                    "length": 11,
                    "confidenceScore": 0.12
                },
                {
                    "text": "Moser",
                    "category": "Person",
                    "offset": 1205,
                    "length": 5,
                    "confidenceScore": 0.27
                },
                {
                    "text": "Milan",
                    "category": "Person",
                    "offset": 1244,
                    "length": 5,
                    "confidenceScore": 1.0
                },
                {
                    "text": "Jílek",
                    "category": "Person",
                    "offset": 1714,
                    "length": 5,
                    "confidenceScore": 0.96
                },
                {
                    "text": "Servis Moser",
                    "category": "Person",
                    "offset": 1722,
                    "length": 12,
                    "confidenceScore": 0.27
                },
                {
                    "text": "Macháček",
                    "category": "Person",
                    "offset": 2074,
                    "length": 8,
                    "confidenceScore": 0.96
                },
                {
                    "text": "Macháček",
                    "category": "Person",
                    "offset": 2230,
                    "length": 8,
                    "confidenceScore": 0.96
                },
                {
                    "text": "Přístav",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 2834,
                    "length": 7,
                    "confidenceScore": 0.36
                },
                {
                    "text": "Macháček",
                    "category": "Person",
                    "offset": 2884,
                    "length": 8,
                    "confidenceScore": 0.96
                },
                {
                    "text": "Macháček",
                    "category": "Person",
                    "offset": 3050,
                    "length": 8,
                    "confidenceScore": 0.96
                },
                {
                    "text": "fotograf",
                    "category": "Person",
                    "offset": 3341,
                    "length": 8,
                    "confidenceScore": 0.39
                },
                {
                    "text": "Macháčka",
                    "category": "Person",
                    "offset": 3391,
                    "length": 8,
                    "confidenceScore": 0.87
                }
            ],
            "warnings": []
        },
        {
            "id": "4",
            "statistics": {
                "charactersCount": 3738,
                "transactionsCount": 4
            },
            "entities": [
                {
                    "text": "Fotograf",
                    "category": "Person",
                    "offset": 0,
                    "length": 8,
                    "confidenceScore": 0.96
                },
                {
                    "text": "fotograf",
                    "category": "Person",
                    "offset": 493,
                    "length": 8,
                    "confidenceScore": 0.48
                },
                {
                    "text": "Macháček",
                    "category": "Person",
                    "offset": 557,
                    "length": 8,
                    "confidenceScore": 0.99
                },
                {
                    "text": "Jílek",
                    "category": "Person",
                    "offset": 767,
                    "length": 5,
                    "confidenceScore": 0.91
                },
                {
                    "text": "Macháček",
                    "category": "Person",
                    "offset": 872,
                    "length": 8,
                    "confidenceScore": 0.99
                },
                {
                    "text": "přístav",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 2052,
                    "length": 7,
                    "confidenceScore": 0.18
                },
                {
                    "text": "Jílek",
                    "category": "Person",
                    "offset": 2163,
                    "length": 5,
                    "confidenceScore": 0.91
                },
                {
                    "text": "Jílek",
                    "category": "Person",
                    "offset": 2292,
                    "length": 5,
                    "confidenceScore": 0.91
                },
                {
                    "text": "Macháčka",
                    "category": "Person",
                    "offset": 2720,
                    "length": 8,
                    "confidenceScore": 0.86
                },
                {
                    "text": "Jílek",
                    "category": "Person",
                    "offset": 2810,
                    "length": 5,
                    "confidenceScore": 0.91
                },
                {
                    "text": "Macháček",
                    "category": "Person",
                    "offset": 2938,
                    "length": 8,
                    "confidenceScore": 0.99
                },
                {
                    "text": "Přístav",
                    "category": "Location",
                    "subcategory": "GPE",
                    "offset": 3080,
                    "length": 7,
                    "confidenceScore": 0.2
                },
                {
                    "text": "Macháček",
                    "category": "Person",
                    "offset": 3468,
                    "length": 8,
                    "confidenceScore": 0.99
                }
            ],
            "warnings": []
        }
    ],
    "errors": [],
    "modelVersion": "2020-04-01"
}
```

Hlavní osoby příběhu myslím máme.

# Osobní údaje
Zajímavý je také režim zachycení osobních údajů. To může být zajímavé zejména v situaci, kdy ukládáte vstup uživatele a osobní údaje tam nepředpokládáte. Nicméně v rámci GDPR se potřebujete ujistit, že tam nejsou, protože jinak k nim chcete přistupovat jinak. Může to být třeba situace inzerentního serveru, kdy z právních, praktických či obchodních důvodů nechcete, aby v textu inzerátu byl telefon, email nebo něco podobného a kontakt má být jen prostřednictvím platformy.

Zkusíme pár hodnot:

```bash
curl -X POST "https://mujtext.cognitiveservices.azure.com/text/analytics/v3.1-preview.1/entities/recognition/pii?model-version=latest&showStats=false" \
-H "Content-Type: application/json" \
-H "Ocp-Apim-Subscription-Key: mujklic" \
--data-ascii '
{
  "documents": [
    {
      "language": "en",
      "id": "1",
      "text": "Hoďmě sem třeba mejlík borec@seznam.cz a co třeba číslo 970917/3859 nebo +420 720 123456. Tohle rodné číslo v ČR platné není: 970917/3857"
    }
  ]
}
' 
```

Koukněme na výsledek.

```json
{
    "documents": [
        {
            "id": "1",
            "entities": [
                {
                    "text": "borec@seznam.cz",
                    "category": "Email",
                    "offset": 23,
                    "length": 15,
                    "confidenceScore": 0.8
                },
                {
                    "text": "970917/3859",
                    "category": "Czech Personal Identity Number",
                    "offset": 56,
                    "length": 11,
                    "confidenceScore": 0.85
                },
                {
                    "text": "970917/3859",
                    "category": "EU National Identification Number",
                    "offset": 56,
                    "length": 11,
                    "confidenceScore": 0.97
                },
                {
                    "text": "970917/3859",
                    "category": "EU Social Security Number (SSN) or Equivalent ID",
                    "offset": 56,
                    "length": 11,
                    "confidenceScore": 0.85
                },
                {
                    "text": "970917/3859",
                    "category": "EU Tax Identification Number (TIN)",
                    "offset": 56,
                    "length": 11,
                    "confidenceScore": 0.75
                },
                {
                    "text": "970917/3859",
                    "category": "Slovakia Personal Number",
                    "offset": 56,
                    "length": 11,
                    "confidenceScore": 0.85
                },
                {
                    "text": "420 720 123456",
                    "category": "Phone Number",
                    "offset": 74,
                    "length": 14,
                    "confidenceScore": 0.8
                },
                {
                    "text": "970917/3857",
                    "category": "EU Tax Identification Number (TIN)",
                    "offset": 126,
                    "length": 11,
                    "confidenceScore": 0.75
                }
            ],
            "warnings": []
        }
    ],
    "errors": [],
    "modelVersion": "2020-07-01"
}
```

Umělá inteligence pro analýzu textu je velmi zajímavá oblast pro mnoho vašich aplikací a datových zdrojů. Přestože v angličtině a jiných velkých jazycích je o hodně dál, přímá podpora češtiny pro řadu služeb existuje (a tam kde není lze v prvním kroku použít překlad - ale tím se samozřejmě do procesu dostane nějaká ta nepřesnost). Dnes jsme si vyzkoušeli vytáhnout entity a osobní údaje z českého textu. Příště si vyzkoušíme další hrátky s textem a ť už s češtinou nebo bez.