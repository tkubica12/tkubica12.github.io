

Agent HQ - řídí věž nejen pro GitHub Copilot agenty, ale i agenty od Anthropic, OpenAI, Google, Cognition (firma stojící za Windsurf editorem) nebo xAI. První s OpenAI Codex v preview s VS Code insiders. 

Mission control je přepracovaná řídící stránka na github.com, kde je vidět který agent na čem pracuje a umožňuje real-time streering, tedy zasáhnout do jeho práce! Tohle dělám když používám agent mode ve VS Code a vidím, že to jde špatným směrem, teď to lze pro na pozadí běžící agenty v cloudu. Kromě toho se zjednodušilo zadávání úkolů přímo z github.com/copilot/agents (tedy už ne jen z Issue nebo Delegate to agent tlačítka v IDE). Přímo z odsud je možné pokračovat v codespaces nebo VS Code.
https://github.blog/changelog/2025-10-28-a-mission-control-to-assign-steer-and-track-copilot-coding-agent-tasks/?utm_source=web-k2k-blog-cta&utm_medium=web&utm_campaign=universe25

Custom Agent - možnost v souboru definovat nového agenta. Proč něco takového chtít? AGENTS.md jsou instrukce pro všechny, to stále platí. Ale tohle je specializace na nějakou úlohu - něco co bych dřív řešil prompt souborem, ale to pak musí zadávat uživatel. Takhle vznikne přímo agent - no a potenciál to má v tom, že v multi-agent scénáři bude moci spolupracovat s ostatními. Lze definovat na úrovni enterprise a vstřikovat do organizací (a bránit úpravě)
https://github.blog/changelog/2025-11-27-custom-agents-for-github-copilot/?utm_campaign=universe25&utm_medium=web&utm_source=web-k2k-blog-cta
https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents

Plan Mode -

GitHub Code Quality - next gen code review, používá CodeQL engine (známé z code security), navrhuje úpravy, měří quality score. Pricing není zřejmý.
https://github.blog/changelog/2025-10-28-github-code-quality-in-public-preview/?utm_source=web-k2k-blog-cta&utm_medium=web&utm_campaign=universe25

Copilot Usage Metrics 
https://github.blog/changelog/2025-10-28-copilot-usage-metrics-dashboard-and-api-in-public-preview/?utm_source=web-k2k-blog-cta&utm_medium=web&utm_campaign=universe25

Context-isolated sub-agents -> dnes jsem dělal tak, že jsem otevřel jiné okno, ale teď to lze zadat přímo z hlavního chatu. Např. aktualizuj README s těmito novými envs a nechat to běžet někde na pozadí a pracovat dál na kódu.