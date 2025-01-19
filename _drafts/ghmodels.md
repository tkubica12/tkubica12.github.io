---
layout: post
published: true
title: Zkoušejte a vyvíjejte AI aplikace zadarmo s GitHub Models - OpenAI, Llama, Mistral i Phi
tags:
- AI
- GitHub
---
# AI modely pro vývojáře zdarma na GitHub Models
Chcete přidat jazykové modely do svých aplikací? Používat jednotné API pro hned několik modelů přes ty nejlepší na planetě od OpenAI (včetně o1) až větší i menší open source modely jako je Llama nebo Phi? Rychle model vyzkoušet na hřišti (playgroundu) a rovnou si zkopírovat ukázku kódu třeba v Pythonu, Javascriptu, C# nebo Javě? A co třeba srovnat výstupy dvou modelů mezi sebou? Nebo použít AI pro vylepšení vašeho systémového promptu? Tak tohle všechno nabízí GitHub Models jako vždy jednoduchým a intuitivním způsobem.

[![](/images/2025/2025-01-19-17-22-05.png){:class="img-fluid"}](/images/2025/2025-01-19-17-22-05.png)

# Kolik můžu zadarmo a jak později s produkcí
Tato funkce je určena skutečně jen pro hraní si s modely, první aplikace nebo rychle prozkoumání nových modelů. Limity se liší podle náročnosti modelu (Phi nabízí víc jak GPT-4o a to zas víc jak o1) a také podle vašeho tieru (Free a Individual Copilot mají nejmenší, Copilot Enterprise největší). Konkrétní seznam najdete v [dokumentaci](https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits). Jak vidíte je to jednoznačně zaměřené na vývojáře, na vyzkoušení, co který model dělá, jak funguje API a jak ho začlenit a otestovat do vaší aplikace, což je poznat především na omezení počtu vstupních a výstupních tokenů (určitě to například nestačí na nějaký dlouhý kontext nebo Retrieval Augmented Generation). Kromě o1 se i na Free Copilot dostanete na poměrně štědré hodnoty pro zkoušení jako je 15 zpráv za minutu a 150 za den u modelu typu GPT-4o.

# Vyzkoušejme
Můžeme se podívat na [marketplace modelů](https://github.com/marketplace?type=models) a vidíme, že aktuálně jsou v nabídce z komerční modely OpenAI a Cohere, komerční o open source varianty Mistral a oblíbené open source modely Llama, Microsoft Phi a AI21.

[![](/images/2025/2025-01-19-17-33-16.png){:class="img-fluid"}](/images/2025/2025-01-19-17-33-16.png)

Jakmile si vyberu, mám hned přístup na jednoduché hřiště, kde mohu nastavit některé parametry, system message a rovnou se ptát.

[![](/images/2025/2025-01-19-17-41-18.png){:class="img-fluid"}](/images/2025/2025-01-19-17-41-18.png)

Můžeme i porovnat dva modely mezi sebou, tak například Phi 4 o velikosti 14B vs. o dost větší Llama 3.3 o velikosti 70B. 

[![](/images/2025/2025-01-19-17-52-26.png){:class="img-fluid"}](/images/2025/2025-01-19-17-52-26.png)

Zkusím ještě jednu.

[![](/images/2025/2025-01-19-17-54-47.png){:class="img-fluid"}](/images/2025/2025-01-19-17-54-47.png)

Hmm, nějak to dávají, zkusme menší modely kolem 4B.

[![](/images/2025/2025-01-19-17-57-09.png){:class="img-fluid"}](/images/2025/2025-01-19-17-57-09.png)

Ale to není pointa - tou je, že můžeme zahrnuté modely snadnou vyzkoušet.

Zadám teď nějakou systémovou zprávu a nechám si ji vylepšit od AI.

[![](/images/2025/2025-01-19-18-01-26.png){:class="img-fluid"}](/images/2025/2025-01-19-18-01-26.png)

[![](/images/2025/2025-01-19-18-02-22.png){:class="img-fluid"}](/images/2025/2025-01-19-18-02-22.png)

[![](/images/2025/2025-01-19-18-02-41.png){:class="img-fluid"}](/images/2025/2025-01-19-18-02-41.png)

Systémový prompt funguje hezky.

[![](/images/2025/2025-01-19-18-04-06.png){:class="img-fluid"}](/images/2025/2025-01-19-18-04-06.png)

Líbí se mi to, zkusím si dát do aplikace. Můžeme se podívat na kód z těchto jazyků:

[![](/images/2025/2025-01-19-18-05-17.png){:class="img-fluid"}](/images/2025/2025-01-19-18-05-17.png)

V případě OpenAI si mohu zvolit buď OpenAI SDK nebo Azure AI Inference SDK - já využiji tuto možnost, protože kód pak bude stejný pro úplně všechny modely v katalogu.

[![](/images/2025/2025-01-19-18-06-04.png){:class="img-fluid"}](/images/2025/2025-01-19-18-06-04.png)

[![](/images/2025/2025-01-19-18-06-18.png){:class="img-fluid"}](/images/2025/2025-01-19-18-06-18.png)

Kde seženu klíč? Kliknutím na tlačítko dostávám návod a v případě GitHub Models je to můj GitHub Personal Access Token. Nicméně protože je řešení postaveno na Azure AI službě, tak pro produkční účely si mohu endpoint a klíč vygenerovat tam - začínám platit a dostávám produkční řešení bez limitů.

[![](/images/2025/2025-01-19-18-07-57.png){:class="img-fluid"}](/images/2025/2025-01-19-18-07-57.png)

Dokonce si ani nemusím nic připravovat na vlastním počítači, využiji GitHub Codespaces - vzdálenou pracovní stanici ať už plně přes web nebo ze svého Visual Studio Code.

[![](/images/2025/2025-01-19-18-08-49.png){:class="img-fluid"}](/images/2025/2025-01-19-18-08-49.png)

[![](/images/2025/2025-01-19-18-09-26.png){:class="img-fluid"}](/images/2025/2025-01-19-18-09-26.png)

Naběhne mi připravené prostředí se všemi knihovnami a v něm příklady. Najdu příklad v Pythonu a kliknu na "play" - funguje, můžu ladit, zkoušet, učit se.

[![](/images/2025/2025-01-19-18-12-31.png){:class="img-fluid"}](/images/2025/2025-01-19-18-12-31.png)

Stejně tak příklady obsahují Jupyter notebooky, které jsou tak= hned z první pěkně nastavené a můžu je rovnou spouštět a hrát si.

[![](/images/2025/2025-01-19-18-14-50.png){:class="img-fluid"}](/images/2025/2025-01-19-18-14-50.png)

Nebo chcete použít framework jako je LangChain nebo LlamaIndex?

[![](/images/2025/2025-01-19-18-16-52.png){:class="img-fluid"}](/images/2025/2025-01-19-18-16-52.png)

Samozřejmě v CodeSpaces i přes web funguje Copilot, takže s kódováním pomůže.