# Flavor Chef | Projectoverdracht en projectkeuzes

[Documentatiewegwijzer](README.md) · [Projectrapport en resultaten](RAPPORT.md)

Gebruik dit document om een werkpakket over te nemen of de keuzes voor het eindrapport terug te vinden. Begin met de stand van je werkpakket en volg de link naar de code, controlevragen of handleiding.

## Stand per werkpakket

Bijgewerkt op **27 november 2026**. `main` bevat de agent, MCP-tool, 36 recepten, lokale interface en evaluatiecode. De aparte Ollama-demo gebruikt vijf eigen voorbeeldrecepten.

| Werkpakket | Gedaan en gecontroleerd | Hier kun je verder |
| --- | --- | --- |
| **1. Recepten en zoeken** | De dataset telt 36 recepten. De bloemkoolvervanging komt nu bij beide methodes in de top 3 wanneer de vraag en het recept expliciet zijn. | Receptsecties zijn de standaard. Bij tokenchunks valt de ricottahoeveelheid buiten de top 3. [Zoekcode](../recipe_search.py) · [MVP-meting](RAPPORT.md#27-november-2026--mvp-oplevering) |
| **2. Agent, Groq en MCP** | LangGraph controleert het routevoorstel. De vier bekende fouten zijn gericht live gecontroleerd op receptsecties. De MCP-server schaalt porties en rekent g ↔ kg om. | Oefen de uitleg van routevoorstel, bronregel en MCP-aanroep. [Agentcode](../chef_agent.py) · [MCP-server](../scale_server.py) |
| **3. Evaluatie en foutanalyse** | PR #7 leverde de live nulmeting. De MVP-set behoudt alle twaalf beantwoordbare bronvragen en de ontbrekende bakvormmaat. De nieuwe live agentrun haalde 20/20 routes per methode. | Vul bij nieuw Groq-quotum de ontbrekende Qwen-beoordelingen aan. [Nulmeting](RAPPORT.md#27-november-2026--evaluatie-met-36-recepten) · [Nameting](RAPPORT.md#live-nameting-op-de-mvp) |
| **4. Lokale interface en demo** | PR #6 leverde de live Streamlit-demo op. De MVP-interface toont ook de exacte conversie, gecontroleerd met echte Groq-aanroepen en in de browser. Broncontrole toont de waterregel voor de diagnose. | Persoon 4 oefent de demo en doet de eigen code-review en GenAI-verantwoording. [Handleiding](LOKALE-INTERFACE.md) · [Live controle](../scripts/test_ui_live.py) |

## Overnemen en bijhouden

**Mijn afgeronde bijdrage is werkpakket 4: de lokale interface en demo.** Ik heb dit technische onderdeel met ondersteuning van Codex opgeleverd. De uitvoering, keuzes en testresultaten staan in mijn [ik-verslag in het projectrapport](RAPPORT.md#27-november-2026--persoon-4-technisch-opgeleverd). Mijn eigen code-review, demo-oefening en GenAI-verantwoording blijven open. Gebruik dit onderscheid bij een volgende overdracht: de technische implementatie is afgerond.

1. Haal `main` op, lees de installatie voor jouw onderdeel en maak je taakbranch volgens de onderhoudsafspraken. [Startpunt](../README.md) · [Onderhoudsafspraken](../CONTRIBUTING.md)
2. Gebruik de controle uit je werkpakket om je wijziging te verifiëren. Gebruik bij het vergelijken dezelfde vragen en noteer het corpus en de instellingen. De gedeelde meetresultaten staan in het rapport. [Projectrapport](RAPPORT.md)
3. Werk dit document bij in dezelfde wijziging als de stand, een keuze of een volgende stap verandert. Noteer bij een nieuwe keuze wat we gebruiken en waarom, met een verwijzing naar de code, bron of les. Bewaar meetdetails bij de betrokken fase in het rapport en wijzig de checklist als een opleverpunt van status verandert. [MVP-checklist](MVP-CHECKLIST.md)

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
| 20 agentvragen op de uitgebreide dataset | We behouden 17 vragen uit de vorige run als vergelijking. Een nieuwe ingrediëntvraag, een gecombineerde zoek- en schaalvraag en een vraag over ontbrekende receptinformatie vergroten de dekking binnen de opdrachtgrens. Bij ontbrekende informatie controleren we de gekozen bron en lezen we het antwoord handmatig. [Evaluatievragen](../data/evaluation.json) · [Methode en resultaten](RAPPORT.md#27-november-2026--evaluatie-met-36-recepten) |
| Qwen 3.8 27B als Ragas-beoordelaar | GPT-OSS 120B bereikte tijdens de eerste poging de dagelijkse tokenlimiet. Beide chunkmethodes zijn voor de uitgebreide evaluatie uitgevoerd met Qwen als dezelfde beoordelaar. GPT-OSS 20B bleef het antwoordmodel. [Model bij Groq](https://console.groq.com/docs/model/qwen/qwen3.8-27b) · [Uitgebreide evaluatie](RAPPORT.md#27-november-2026--evaluatie-met-36-recepten) |

## 27 november 2026 | Oplevering lokale interface (persoon 4)

| Wat gebruiken we? | Waarvoor en waarom? |
| --- | --- |
| LangGraph `astream` met volledige state na iedere stap | De interface toont de voortgang en bronfragmenten zodra een graph-stap klaar is. De bestaande routes en reducers blijven het werk uitvoeren. De callback is optioneel; CLI en benchmark gebruiken hun bestaande uitvoerpad. [Agentcode](../chef_agent.py) |
| Exacte `tool_input` in de agentstate | De UI hoeft de invoer niet meer achteraf uit de receptendata af te leiden. Een tabel zet de ontvangen hoeveelheden vóór en na schalen naast elkaar; de ruwe gegevens blijven uitklapbaar. [Interface](../chef_ui.py) |
| Gemaskeerd sessieveld of `GROQ_API_KEY` | Een gebruiker kan de volledige demo starten met een sleutel in de eigen browsersessie. De sleutel komt niet in berichten, meetuitvoer of Git. Een omgevingssleutel blijft alleen in het serverproces beschikbaar. [Gebruik en opruimen](LOKALE-INTERFACE.md) |
| Afzonderlijke velden voor verwerkingstijd, tokens en TTFT | Verwerkingstijd omvat de agent en schermupdates. Tokens zijn de som van afgeronde modelaanroepen. TTFT hoort bij de gestreamde antwoordaanroep, dus niet bij een alleen door de tool geformuleerd eindantwoord. Ontbrekende metingen worden expliciet getoond. |
| Portievraag als gewone zoekdemo en watervraag als broncontrole | De gewone zoekdemo laat een gecontroleerd antwoord (4 porties) zien. De watervraag laat zien dat juiste fragmenten toch tot een onjuist antwoord kunnen leiden: 795 ml door het dubbel tellen van 420 en 375. De UI toont de referentie en bewaart het echte antwoord, zodat de fout verdedigbaar kan worden geanalyseerd. |
| AppTest met gesimuleerd Groq-protocol én echte live modelaanroepen | Gesimuleerde 401/429/503-responsen, time-out en ontbrekende usage maken de foutweergave herhaalbaar zonder een echte storing uit te lokken. Een afzonderlijke live controle bewijst dat de echte interface de providergegevens ontvangt. Beide soorten bewijs blijven in het rapport apart benoemd. [Protocoltests](../scripts/test_ui_groq.py) · [Live controle](../scripts/test_ui_live.py) |

## 27 november 2026 | Keuzes voor de MVP-oplevering

| Wat gebruiken we? | Waarvoor en waarom? |
| --- | --- |
| Groq `openai/gpt-oss-20b` met een LangGraph-routecontrole | Het model stelt een route voor. Bij herkenbare recepten en expliciete toolinvoer heeft de code voldoende informatie om een voorstel te corrigeren. De trace toont beide routes als ze verschillen. PowerPoint 1, dia’s 68, 71–72. [Agentcode](../chef_agent.py) |
| Eén plaats voor een vervangingsfragment in Qdrant | Bij een expliciete vervangingsvraag over één bekend recept controleren beide strategieën hun top 3. Zo kan de bronregel over bloemkool mee als die buiten de eerste drie valt. De overige plaatsen volgen gelijkenis. PowerPoint 1, dia’s 79 en 83. [Zoekcode](../recipe_search.py) |
| Rechtstreeks antwoord op een opgehaalde ingrediëntregel | Voor een expliciete totaalvraag met één herkenbaar ingrediënt leest de agent de hoeveelheid uit de bevestigde bronregel. Zo wordt een deelhoeveelheid uit de bereiding niet opnieuw opgeteld. Bij andere zoekvragen formuleert Groq het antwoord. PowerPoint 1, dia’s 40, 72 en 79. [Agentcode](../chef_agent.py) |
| `convert_units` in dezelfde FastMCP-server | De server valideert g en kg en rekent met `Decimal`. Dezelfde state bewaart de toolnaam, argumenten en uitkomst voor de trace en het scherm. PowerPoint 1, dia’s 67–68 en 72. [MCP-server](../scale_server.py) |
| Ragas 0.4.4 met `qwen/qwen3.8-27b` en handmatige controle | PR #7 en de MVP-meting gebruiken dezelfde twaalf beantwoordbare zoekvragen en dezelfde beoordelaar. Daarom kunnen we de dekking en de gemeten scores naast elkaar zetten. Een ontbrekende score blijft zichtbaar. Lees het antwoord zelf om reken- en bronfouten te herkennen. PowerPoint 1, dia’s 79 en 82–83. [Meetresultaten](RAPPORT.md#27-november-2026--mvp-oplevering) |
