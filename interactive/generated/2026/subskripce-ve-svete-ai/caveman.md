# Je předplatné vhodný obchodní model pro AI produkt?

META
- url: /new/2026/subskripce-ve-svete-ai/
- source: interactive\source\2026\subskripce-ve-svete-ai.article.md
- date: 2026-04-27
- audience: lidé řešící AI produkty, enterprise AI a agentické náklady
- thesis: flat subskripce pomáhá adopci, ale agenti rozbíjejí přirozené limity spotřeby; férovější model = licence jako vstupenka + poolovaná spotřeba + dokupy.

STRUCTURE
- 01 Klasické předplatné: dobré pro adopci, funguje díky průměru a přirozeným limitům.
- 02 AI problém: chat zvládne omezení, agenti mění spotřebu o řády.
- 03 Náklady: tokeny + compute jsou reálné měřitelné náklady.
- 04 Cloud model: subskripce odemyká produkt, obsahuje spotřebu, ideálně poolovanou, zbytek se dokupuje.
- 05 Mimo coding: podobný model čeká enterprise AI služby.
- 06 Verdikt: AI se nezdražilo; narazilo se na limit obchodního modelu.

KEY POINTS
- Flat subskripce = ideální pro adopci: uživatel nepočítá každé použití, učí se a šíří produkt.
- Provider vydělává na málo aktivních, méně na power users; model drží, pokud existuje přirozený limit spotřeby.
- Spotify příklad: průměr 50 h/měsíc, power user max cca 730 h/měsíc, prakticky ~10x.
- Kde přirozený limit není, provider používá „hvězdičku“: neomezené, ale neférové využívání se omezuje vágně.
- Chat: power user může spotřebovat spíše 100x tokenů; ještě lze řešit hodinovými limity, levnějším modelem, deprioritizací.
- Agent: hodiny práce, obrovský context, stovky tool callů, subagenti, paralelní okna; rozdíl může být 4 řády a bez zlé vůle.
- Závěr pro agenty: flat subscription to být nemůže; nutné placení podle férového využívání.

DETAILS
## Náklady
- Základní existence produktu: vývoj, bezpečnost, architektura, compliance, provoz.
- Přímé uživatelské náklady:
  - Tokeny: input, cached input, output; různé modely mají různé ceny; často přepočet na „AI jednotky“.
  - Anthropic token margin údajně 40–50 %; tokeny nejsou licence, ale inferencing/GPU/elektřina/IP modelu.
  - Multi-model služby (např. GitHub Copilot s OpenAI, Anthropic, Google) častěji používají virtuální měnu.
  - Compute: cloud agent potřebuje CPU/RAM a izolované prostředí; infra cloud marže cca 30–40 %, pořád reálný náklad.

## Model pro cloud
- Budoucí model: subskripce odemyká vlastnosti + obvykle obsahuje předplacenou spotřebu.
- Spotřeba může být:
  - nulová seat-only (Anthropic Claude Enterprise / Claude Code Enterprise: v ceně nic),
  - menší než licence (20 USD licence, 10 USD spotřeba),
  - 1:1 nebo víc (Cursor 20 USD = 20 USD, 60 USD = 70 USD; GitHub Copilot 19 USD = 19 USD).
- Pool je férový: licence dávají společný firemní pool; málo aktivní uživatel nepálí nevyužitou spotřebu, využije ji někdo jiný.
- Pool motivuje dát AI všem: nikdo není „neperspektivní“.
- Enterprise potřebuje per-user limity a politiku dokupů podle firmy/organizace; GitHub Copilot to má podle autora výborně.
- Éra vágních limitů (týden/hodina/neřekneme přesně/měníme/výjimky) podle autora skončí hlavně v enterprise; OpenAI Codex v tom zatím jede.

## Mimo coding
- Dnes hlavně kódovací agenti.
- M365 Copilot, Gemini, OpenAI, Claude většinou pořád klasická subskripce s podivnými limity.
- Claude Enterprise je výjimka: i běžné povídání seat-only bez spotřeby v ceně.
- Autor čeká podobný model pro enterprise: poplatek za hodinu propůjčeného počítače (např. Cowork) + tokeny.

VERDICT
- Autor preferuje model skutečné spotřeby, Azure-like, s oddělenou vstupenkou.
- Oblíbený model: GitHub Copilot — licence něco stojí, hodnota zpět v tokenech, pool pro firmu.
- AI se podle autora nezdražilo:
  - tokeny na trhu naceněny férově s rozumnou marží,
  - nezdražují se pro stejnou generaci/kvalitu,
  - nové mini modely dávají podobnou službu jako dřívější high-end za cca 5x méně,
  - cena za jednotku inteligence dramaticky klesá.
- Rozdíl: dnešní coding agent za hodinu napíše celou aplikaci; dřívější asistent navrhl třídu, která často nefungovala.
- Autor preferuje inteligenci a růst před úsporami.
- Problém není zdražení AI, ale neudržitelnost starého flat obchodního modelu.
- Potřeba: předvídatelné náklady, AI pro všechny, pool nevyužitých tokenů, rozumné limity dokupů podle organizací/uživatelů.
- Příští článek: otestované tipy jak šetřit tokeny.
