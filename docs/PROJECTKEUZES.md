# Flavor Chef | Projectkeuzes voor het eindrapport

[Documentatiewegwijzer](README.md) · [Projectrapport en resultaten](RAPPORT.md)

Vul dit document bij elke projectfase aan zodra een keuze verandert of erbij komt. Noteer wat we gebruiken, waarvoor het dient en waarom we het gekozen hebben. Voeg een versie, instelling, bron of beperking toe als die nodig is om de keuze uit te leggen of de proef te herhalen. Noteer meetresultaten in het [projectrapport](RAPPORT.md).

## 19 november 2026 | Eerste RAG-demo

| Wat gebruiken we? | Waarvoor en waarom? |
| --- | --- |
| PowerPoint 1 en de opdracht-pdf | De PowerPoint bepaalt de lesopbouw voor chunking, embeddings, RAG, tools en evaluatie. De pdf bepaalt de criteria voor de MVP. |
| Vijf eigen voorbeeldrecepten | Met een kleine set is tijdens de demo makkelijk te tonen welk fragment een antwoord ondersteunt. De chili dient als controlevraag met een bekende bereidingstijd. [Demorecepten](../data/demo_recipes.json) |
| Ollama met `qwen3-embedding:0.6b` en `qwen3.5:4b-q4_K_M` | Het embeddingmodel zet vraag en receptfragmenten om in vectoren. Het chatmodel formuleert een antwoord. Beide draaien voor deze demo op de eigen pc. [Demohandleiding](OLLAMA-DEMO.md) |
| LlamaIndex en drie receptsecties | De demo splitst elk recept in overzicht, ingrediënten en bereiding. LlamaIndex bewaart de vectorindex en geeft de drie best passende fragmenten terug. Zo kan de gebruiker zien waarop het antwoord steunt. [Democode](../flavor_chef.py) |

## 27 november 2026 | Agent en evaluatie

| Wat gebruiken we? | Waarvoor en waarom? |
| --- | --- |
| Drie proefrecepten van Health Canada | De oorspronkelijke recepten maken hoeveelheden, bereidingstijden en vervangingen controleerbaar. De dataset bewaart bronlinks en gebruikt vaste velden voor porties en ingrediënten. [Receptendata](../data/recipes.json) |
| LlamaIndex, FastEmbed en Qdrant | LlamaIndex splitst recepten op tokenlengte of per sectie. FastEmbed gebruikt `paraphrase-multilingual-MiniLM-L12-v2` voor de Nederlandstalige vragen en recepten. Qdrant bewaart beide lokale indexen. Hetzelfde model en top 3 houden de vergelijking tussen de chunkmethodes gelijk. [Zoekcode](../recipe_search.py) |
| Python, vastgelegde afhankelijkheden en LangGraph | De requirements leggen de belangrijkste pakketversies vast om dezelfde omgeving opnieuw op te bouwen. LangGraph maakt de routes voor zoeken, rechtstreeks schalen, een recept zoeken en schalen, en gewone conversatie expliciet. De route en tussenstappen zijn daardoor apart te controleren. [Afhankelijkheden](../requirements.txt) · [Agentcode](../chef_agent.py) |
| MCP via stdio en `Decimal` | De agent roept lokaal `scale_ingredients` aan. De tool berekent de hoeveelheden uit de opgegeven porties en behoudt de eenheden. `Decimal` houdt bijvoorbeeld `2,5 g` van vier naar zes porties controleerbaar als `3,75 g`. [Toolcode](../scale_server.py) |
| Groq met `openai/gpt-oss-20b` | Voor de live routekeuze en de formulering van antwoorden. Met streaming meten we de tijd tot de eerste zichtbare tekst. We gebruiken lage redeneerinspanning en maximaal 1024 uitvoertokens voor GPT-OSS. In de eerste live proef liep de oorspronkelijke limiet van 512 tokens vol voordat er zichtbare antwoordtekst kwam. [Agentcode](../chef_agent.py) · [Groq-documentatie](https://console.groq.com/docs/reasoning) |
| 18 referentievragen en een lokale benchmark | Dezelfde 11 zoekvragen, 6 schaalvragen en 1 begroeting draaien voor beide chunkmethodes. De benchmark bewaart route, bronfragmenten, tooluitkomst en antwoord. Dat maakt het mogelijk om de eerste foutstap te vinden. [Evaluatievragen](../data/evaluation.json) · [Benchmarkcode](../evaluate_chef.py) |
| Ragas 0.4.4 met `openai/gpt-oss-120b` als beoordelaar | Beide chunkmethodes krijgen dezelfde beoordelaar. Context Precision bekijkt de volgorde van relevante fragmenten. Context Recall controleert hoeveel van de referentie door de fragmenten wordt gedekt. Faithfulness controleert of de uitspraken in het antwoord door de fragmenten worden ondersteund. Bij elke metriek vermelden we hoeveel van de 11 zoekvragen een score kregen. Bij tijdelijke Groq-limieten wacht de benchmark tussen enkele nieuwe pogingen volgens `Retry-After`. [Afhankelijkheden](../requirements-eval.txt) · [Benchmarkcode](../evaluate_chef.py) · [Groq-limieten](https://console.groq.com/docs/rate-limits) |
| Codex | Ondersteunt implementatie, controles en documentatie. Het projectrapport vermeldt deze hulp per fase. Raoul gebruikt de repo, resultaten en lesbronnen om de keuzes zelf te kunnen uitleggen. [GenAI-vermelding](RAPPORT.md) |
