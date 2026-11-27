# Flavor Chef | Projectoverdracht en projectkeuzes

[Documentatiewegwijzer](README.md) · [Projectrapport en resultaten](RAPPORT.md)

Gebruik dit document om een werkpakket over te nemen of de keuzes voor het eindrapport terug te vinden. Begin met de stand van je werkpakket en volg de link naar de code, controlevragen of handleiding.

## Stand per werkpakket

Bijgewerkt op **27 november 2026**. `main` bevat de agent, MCP-tool, 36 recepten, lokale interface en evaluatiecode. De aparte Ollama-demo gebruikt vijf eigen voorbeeldrecepten.

| Werkpakket | Gedaan en gecontroleerd | Hier kun je verder |
| --- | --- | --- |
| **1. Recepten en zoeken** | Breidde de dataset uit naar 36 recepten met bronvermeldingen. Beide indexen zijn gebouwd en vergeleken op 18 zoekvragen. Receptsecties gaven in die vergelijking vaker volledig bewijs op plek 1. | Onderzoek waarom de bloemkoolvervanging buiten de top 3 valt. Meet bij een wijziging opnieuw op dezelfde vragen. [Zoekcode](../recipe_search.py) · [Zoekvergelijking](RAPPORT.md#receptendataset-en-chunking) |
| **2. Agent, Groq en MCP** | De vier lokale routes werken en alle 36 recepten zijn via MCP herschaald. De live Groq-proef haalde 16/18 routes per methode en registreerde tokens en TTFT. De benchmark herstelde van tijdelijke Groq-limieten, HTTP 429. | Onderzoek de twee verkeerd gerouteerde receptvragen en test de afhandeling bij Groq- of MCP-uitval. [Agentcode](../chef_agent.py) · [MCP-tool](../scale_server.py) · [Live foutanalyse](RAPPORT.md#27-november-2026--live-groq--en-ragas-meting) |
| **3. Evaluatie en foutanalyse** | De 18 referentievragen zijn nagekeken. De lokale benchmark draaide op beide chunkmethodes. Ragas scoorde op de oorspronkelijke drie proefrecepten dezelfde 9 van de 11 zoekvragen per methode. | Voeg agentvragen toe over de nieuwe recepten. Herhaal daarna de live meting met beide indexen op de uitgebreide dataset. [Evaluatievragen](../data/evaluation.json) · [Benchmarkcode](../evaluate_chef.py) · [Uitvoeren](VOORTGANG.md#live-benchmark-met-groq-en-ragas) |
| **4. Lokale interface en demo** | Streamlit toont antwoord, route, bronnen, MCP en metingen. Zeven schermtests en vier lokale integratietests zijn geslaagd. De voorbeeldmodus markeert gesimuleerde waarden. | Controleer tokens en TTFT in de interface met een echte Groq-aanvraag en oefen de demo. [Interfacehandleiding](LOKALE-INTERFACE.md) · [Schermtests](../scripts/test_chef_ui.py) |

## Overnemen en bijhouden

1. Haal `main` op, lees de installatie voor jouw onderdeel en maak je taakbranch volgens de onderhoudsafspraken. [Startpunt](../README.md) · [Onderhoudsafspraken](../CONTRIBUTING.md)
2. Gebruik de controle uit je werkpakket om je wijziging te verifiëren. Gebruik bij het vergelijken dezelfde vragen en noteer het corpus en de instellingen. De gedeelde meetresultaten staan in het rapport. [Projectrapport](RAPPORT.md)
3. Werk dit document bij in dezelfde wijziging als de stand, een keuze of een volgende stap verandert. Noteer bij een nieuwe keuze wat we gebruiken en waarom, met een verwijzing naar de code, bron of les. Bewaar meetdetails bij de betrokken fase in het rapport en wijzig de checklist als een opleverpunt van status verandert. [MVP-checklist](MVP-CHECKLIST.md)

Deze lees- en bijwerkafspraak geldt ook voor de begeleider `nlpagent`. Die bewaart hier de actuele keuzes en werkpakketstatus en zet uitvoerings- en testbewijs in het bestaande rapport. De lokale skill bevat alleen de werkwijze, zodat de inhoud niet tussen de skill en deze documenten uit elkaar gaat lopen.

## 19 november 2026 | Eerste RAG-demo

| Wat gebruiken we? | Waarvoor en waarom? |
| --- | --- |
| PowerPoint 1 en de opdracht-pdf | De PowerPoint bepaalt de lesopbouw voor chunking, embeddings, RAG, tools en evaluatie. De pdf bepaalt de criteria voor de MVP. |
| Vijf eigen voorbeeldrecepten | Met een kleine set is tijdens de demo makkelijk te tonen welk fragment een antwoord ondersteunt. De chili dient als controlevraag met een bekende bereidingstijd. [Demorecepten](../data/demo_recipes.json) |
| Ollama met `qwen3-embedding:0.6b` en `qwen3.5:4b-q4_K_M` | Het embeddingmodel zet vraag en receptfragmenten om in vectoren. Het chatmodel formuleert een antwoord. Beide draaien voor deze demo op de eigen pc. [Demohandleiding](OLLAMA-DEMO.md) |
| LlamaIndex en drie receptsecties | De demo splitst elk recept in overzicht, ingrediënten en bereiding. LlamaIndex bewaart de vectorindex en geeft de drie best passende fragmenten terug. Zo kan de gebruiker zien waarop het antwoord steunt. [Democode](../flavor_chef.py) |

## 27 november 2026 | Agent en evaluatie op drie proefrecepten

| Wat gebruiken we? | Waarvoor en waarom? |
| --- | --- |
| Drie proefrecepten van Health Canada | De oorspronkelijke recepten maken hoeveelheden, bereidingstijden en vervangingen controleerbaar. De dataset bewaart bronlinks en gebruikt vaste velden voor porties en ingrediënten. [Receptendata](../data/recipes.json) |
| LlamaIndex, FastEmbed en Qdrant | LlamaIndex splitst recepten op tokenlengte of per sectie. FastEmbed gebruikt `paraphrase-multilingual-MiniLM-L12-v2` voor de Nederlandstalige vragen en recepten. Qdrant bewaart beide lokale indexen. Hetzelfde model en top 3 houden de vergelijking tussen de chunkmethodes gelijk. [Zoekcode](../recipe_search.py) |
| Python, vastgelegde afhankelijkheden en LangGraph | De requirements leggen de belangrijkste pakketversies vast om dezelfde omgeving opnieuw op te bouwen. LangGraph maakt de routes voor zoeken, rechtstreeks schalen, een recept zoeken en schalen, en gewone conversatie expliciet. De route en tussenstappen zijn daardoor apart te controleren. Lesbasis voor de agentroutes is PowerPoint 1, slide 69. [Afhankelijkheden](../requirements.txt) · [Agentcode](../chef_agent.py) |
| MCP via stdio en `Decimal` | De agent roept lokaal `scale_ingredients` aan. De tool berekent de hoeveelheden uit de opgegeven porties en behoudt de eenheden. `Decimal` houdt bijvoorbeeld `2,5 g` van vier naar zes porties controleerbaar als `3,75 g`. Lesbasis voor de tool is PowerPoint 1, slides 72–73. [Toolcode](../scale_server.py) |
| Groq met `openai/gpt-oss-20b` | Voor de live routekeuze en de formulering van antwoorden. Met streaming meten we de tijd tot de eerste zichtbare tekst. We gebruiken lage redeneerinspanning en maximaal 1024 uitvoertokens voor GPT-OSS. In de eerste live proef liep de oorspronkelijke limiet van 512 tokens vol voordat er zichtbare antwoordtekst kwam. [Agentcode](../chef_agent.py) · [Groq-documentatie](https://console.groq.com/docs/reasoning) |
| 18 referentievragen en een lokale benchmark | Dezelfde 11 zoekvragen, 6 schaalvragen en 1 begroeting draaien voor beide chunkmethodes. De benchmark bewaart route, bronfragmenten, tooluitkomst en antwoord. Dat maakt het mogelijk om de eerste foutstap te vinden. [Evaluatievragen](../data/evaluation.json) · [Benchmarkcode](../evaluate_chef.py) |
| Ragas 0.4.4 met `openai/gpt-oss-120b` als beoordelaar | Beide chunkmethodes krijgen dezelfde beoordelaar. Context Precision bekijkt de volgorde van relevante fragmenten. Context Recall controleert hoeveel van de referentie door de fragmenten wordt gedekt. Faithfulness controleert of de uitspraken in het antwoord door de fragmenten worden ondersteund. Bij elke metriek vermelden we hoeveel van de 11 zoekvragen een score kregen. Bij tijdelijke Groq-limieten wacht de benchmark tussen enkele nieuwe pogingen volgens `Retry-After`. [Afhankelijkheden](../requirements-eval.txt) · [Benchmarkcode](../evaluate_chef.py) · [Groq-limieten](https://console.groq.com/docs/rate-limits) |
| Codex | Ondersteunt implementatie, controles en documentatie. Het projectrapport vermeldt deze hulp per fase. Raoul gebruikt de repo, resultaten en lesbronnen om de keuzes zelf te kunnen uitleggen. [GenAI-vermelding](RAPPORT.md) |

## 27 november 2026 | Uitgebreide dataset en lokale interface

| Wat gebruiken we? | Waarvoor en waarom? |
| --- | --- |
| JSON met 36 agentrecepten | De 33 aanvullingen verbreden het aanbod over acht categorieën. De bronvermelding maakt de herkomst controleerbaar. De integratiecheck valideert de data als MCP-invoer en controleert het herschalen van alle 36 recepten. [Bronvermeldingen](../data/README.md#herkomst-van-de-agentrecepten) · [Integratiecheck](../scripts/test_integration.py) |
| Cosinusovereenkomst in Qdrant en zoekvergelijking | De zoeker rangschikt fragmenten op gelijkenis tussen de vectoren. We vergelijken drie en vijf fragmenten om te meten hoeveel extra bewijs en broncontext de agent krijgt. De score geeft de overeenkomst van vectoren weer. [Zoekcode](../recipe_search.py) · [Zoekvergelijking](RAPPORT.md#receptendataset-en-chunking) |
| Pydantic | Beschrijft en valideert de invoer en uitvoer van de MCP-tool, zodat gegevens zoals porties en eenheden een vaste vorm hebben. De integratiecheck controleert dat ongeldige portievragen geen rekentool uitvoeren. [Toolcode](../scale_server.py) |
| Streamlit | Toont het gesprek, de trace, bronfragmenten, de MCP-tool en beschikbare metingen vanuit Python. De interface gebruikt dezelfde agent als de CLI. Metingen verschijnen na afloop en iedere vraag wordt zelfstandig verwerkt. PowerPoint 1, slides 82–83, is de lesbasis voor het zichtbaar maken van tussenstappen. [Interface-uitleg](LOKALE-INTERFACE.md) |
| AppTest en `unittest` | Controleren interfacegedrag en de lokale keten herhaalbaar, met onder meer moduswissels, ontbrekende metingen, bronvragen en ongeldige invoer. De schermtests draaien in CI. De modelafhankelijke integratietests draaien lokaal. [Schermtests](../scripts/test_chef_ui.py) · [Integratiecheck](../scripts/test_integration.py) |
| Git en GitHub Actions | Versiebeheer bewaart de bijdragen per werkpakket. GitHub Actions controleert de repository, links, Python, JSON, whitespace en de schermtests. [Workflow](../.github/workflows/repository-check.yml) |

Voor de live Ragas-cijfers geldt de oorspronkelijke dataset met drie proefrecepten. De uitgebreidere zoekvergelijking en integratietests gebruiken 36 recepten. [Meetresultaten](RAPPORT.md)
