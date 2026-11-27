# Flavor Chef | Projectrapport

[Terug naar de README](../README.md)

**Projectauteur** Raoul

**Doel:** een volledige MVP die Raoul zelf kan uitleggen. De rubric voorziet maximaal 85% voor een werkende MVP met goede analyse.

**Huidige fase.** De agent met MCP-tool, 36 recepten en de lokale interface zijn geïntegreerd en samen getest. Beide chunkmethodes zijn op die set vergeleken. De Ollama-demo blijft een apart onderdeel. Zie de [voortgang](VOORTGANG.md) en de [MVP-checklist](MVP-CHECKLIST.md).

## 19 november 2026 | Eerste RAG-demo

| Naam | Projectwerk |
| --- | --- |
| Raoul | Scope bepaald voor de MVP en de eerste demo op basis van PowerPoint 1. Lesmateriaal geordend, skill `nlpagent` aangemaakt, vijf voorbeeldrecepten opgesteld en de lokale RAG-demo gebouwd en getest. |

**Aanpak.** Elk recept krijgt drie chunks. LlamaIndex bewaart de embeddings lokaal en haalt bij een vraag de drie best passende chunks op. De aanwezige Ollama-modellen houden de demo lokaal. In de terminal zie je welke tekst bij het antwoord is meegestuurd.

**Lesbasis.** PowerPoint 1, slides 21–45 over embeddings, chunking en RAG en slides 84–90 over lokale modellen. De presentatie staat lokaal in `C:\NLPFull\lesmateriaal`.

**Gecontroleerd**

- De index bevat 15 chunks. Een nieuw proces haalt de juiste bereidingsstap voor de chili op.
- Het model antwoordt dat de chili 20 minuten moet sudderen. Bij een vraag over chocoladetaart meldt het dat de informatie ontbreekt.
- Een ontbrekende index en een onbereikbare Ollama-server geven elk een duidelijke foutmelding. De vier lesbestanden en de skill zijn gecontroleerd.

**GenAI-vermelding.** Voor de code, voorbeelddata, skill en documentatie is Codex gebruikt. Raouls eigen review, demo-oefening en controle van het GenAI-beleid staan nog open.

## 27 november 2026 | Integratie met main

De Ollama-demo en de agent staan samen in de repository. De demo gebruikt zijn vijf voorbeeldrecepten in `data/demo_recipes.json` en installeert via `requirements-demo.txt`. De agent gebruikt zijn eigen recepten en benchmark zoals beschreven in [VOORTGANG.md](VOORTGANG.md).

## 27 november 2026 | Repository onderhouden

De installatie-uitleg, voortgang, het rapport en de checklist staan gegroepeerd in `docs/`. De README is het gezamenlijke startpunt voor de agent en de Ollama-demo. De Python-entrypoints, datasets en bestaande referentiebenchmark zijn behouden.

De onderhoudsafspraken staan in [CONTRIBUTING.md](../CONTRIBUTING.md). [AGENTS.md](../AGENTS.md) verplicht coding agents die eerst te lezen; de PR-template vraagt dezelfde bevestiging aan bijdragers. De workflow `Repositorycontrole` controleert structuur, lokale Markdown-bestandslinks, Python-syntax, JSON en whitespace. Uitgebreide ignore-regels houden lokale omgevingen, indexen en proefmetingen buiten Git.

**Controle.** De repositorycontrole en whitespacecontrole zijn lokaal uitgevoerd. Ook de ignore-regels zijn nagegaan. Voor deze documentatie- en onderhoudswijziging is geen nieuwe modelbenchmark uitgevoerd. Voor de documentatie en controles is Codex gebruikt.

## 27 november 2026 | Persoon 4: lokale interface en demo

**Eigen bijdrage tot nu toe.** De gebruiker heeft bevestigd dat werkpakket 4 zijn verantwoordelijkheid is en de taakverdeling aangeleverd. Er is in deze sessie nog geen eigen code-review, mondelinge toelichting of door de gebruiker uitgevoerde demo vastgelegd.

**AI-hulp en keuze.** Codex heeft `chef_ui.py`, `requirements-ui.txt`, zes interfacechecks en de [demo-uitleg](LOKALE-INTERFACE.md) toegevoegd. De interface gebruikt Streamlit en roept de bestaande agent aan; de routering, dataset, evaluatie en MCP-rekentool zijn niet aangepast. Per vraag zijn antwoord, trace, bronfragmenten, toolinvoer/-uitvoer en metingen zichtbaar. De toolinvoer is afgeleid uit dezelfde state en brondata, geen onderschept protocol-log. De geschiedenis blijft in de browsersessie; iedere vraag wordt zelfstandig verwerkt. Metingen verschijnen na afloop. De aparte voorbeeldmodus markeert ingevulde tokens, tijden en scores als gesimuleerd.

**Uitgevoerde controles.** Installatie in `.venv` met Python 3.13 en `pip check` slagen. Beide bestaande indexen zijn lokaal opgebouwd (17 tokenchunks en 20 sectiechunks). Zes AppTest-checks slagen, inclusief ontbrekende sleutel, ontbrekende/gedeeltelijke metingen, foutafhandeling, geschiedenis en moduswissels. De Streamlit-server gaf HTTP 200 op de healthcheck. De repositorycontrole en whitespacecontrole slagen.

**Echte lokale keten via de interface.** Bij “Hoeveel water gaat er in totaal in de curry?” was de route `search` en bevatten de drie opgehaalde fragmenten de juiste **420 ml water**. De gemeten agenttijd was ongeveer **1902 ms**. Bij “Schaal de curry van 4 naar 7 porties” was de trace `scale_recipe`, drie RAG-fragmenten, `MCP: scale_ingredients`; de echte tool gaf **735 ml water** terug bij een agenttijd van ongeveer **2909 ms**. Een losse schaalvraag gaf via MCP ook **300 g** terug voor 200 g van vier naar zes porties. Dit zijn afzonderlijke controles op deze pc, geen nieuwe benchmark. Er is geen taalmodel gebruikt: tokenvelden tonen terecht **Niet gemeten**.

**Lesbasis en open controle.** PowerPoint 1, slides 69, 72–73 en 82–83 zijn visueel bekeken. PowerPoint 2 en 3 zijn niet gebruikt. De opdracht-pdf en het opleidingsbeleid voor GenAI ontbreken nog; de scope komt uit de aangeleverde taakverdeling. Live Groq-tokens en TTFT zijn niet geverifieerd omdat `GROQ_API_KEY` ontbreekt. Visuele browsercontrole was niet beschikbaar in deze chat; AppTest controleerde wel de interacties en getoonde velden. Persoon 4 moet de demo nog zelf oefenen, de code nakijken en de GenAI-verantwoording aan het opleidingsbeleid toetsen.

## 27 november 2026 | Integratie persoon 1, 2 en 4

**Vraag en eigen bijdrage.** De gebruiker vroeg de nieuwste repository op te halen en recepten/zoeken, agent/MCP en interface samen te controleren. De eigen review en demo-oefening door de gebruiker blijven open.

**Uitgevoerd met AI-hulp.** De nieuwste wijzigingen zijn opgehaald. De branch `feat/recepten-en-chunking` van persoon 1 is samengevoegd met de lokale interface van persoon 4 en de bestaande agent/MCP-code van persoon 2. De dataset bevat nu 36 recepten. Conflicten in het rapport en de voortgang zijn opgelost met behoud van beide bijdragen. De aparte evaluatiebranch van persoon 3 is nog niet in deze integratie opgenomen. Codex voegde `scripts/test_integration.py` toe en repareerde de voorbeeldmodus: die kiest het curryrecept op ID in plaats van het eerste recept in de lijst. Dit voorkomt een verkeerd voorbeeld als de dataset anders wordt gesorteerd.

**Controles.** Vier integratietests met **51 scenario's** slagen via de echte interface en backend: tien zoekvragen, inclusief de zeven nieuwe vragen van persoon 1; het herschalen van **alle 36 recepten** met behoud van eenheden, notities en onbepaalde hoeveelheden; een losse schaalvraag; begroeting; en drie ongeldige/onvolledige schaalvragen zonder tooluitvoering. Alle 36 recepten passen ook in het Pydantic-invoerformaat van de MCP-tool. Daarnaast slagen zeven interfacechecks, dependencycontrole, repositorycontrole en whitespacecontrole.

De lokale benchmark is opnieuw uitgevoerd naar het genegeerde `reports/integration.json`. Beide chunkmethodes halen opnieuw **18/18 routes** en **6/6 MCP-uitkomsten**. Het benodigde bewijs staat in de top 3 bij **9/11** vragen voor tokenchunks en **10/11** voor sectiechunks. De referentiebaseline is behouden. Deze cijfers bewijzen de gecontroleerde routes en berekeningen, niet de inhoudelijke juistheid van toekomstige modelantwoorden.

Ook de zoekvergelijking zonder receptfilter is op de geïntegreerde versie herhaald (`reports/chunking-integration.json`, buiten Git): **106 tokenchunks** en **133 sectiechunks**, met top-3-bewijs voor **13/18** en **14/18** vragen. Dit bevestigt de vergelijking van persoon 1. Deze ongerichte zoekvergelijking en de agentbenchmark met receptnaamherkenning meten verschillende stappen en mogen niet als dezelfde score worden gelezen.

**Open.** Groq-routering, gegenereerde antwoorden, tokens en TTFT en live Ragas-evaluatie zijn niet gecontroleerd bij gebrek aan een sleutel. De evaluatiebranch van persoon 3 moet apart worden gereviewd en geïntegreerd; de volledige agenttestset moet ook de nieuwe recepten gaan omvatten. De bloemkoolvraag blijft een bekend rangschikkingsprobleem en vraagt verdere analyse. Visuele browsercontrole, persoonlijke demo-oefening, opdracht-pdf en GenAI-beleid blijven open. PowerPoint 2 en 3 zijn niet gebruikt.

## Gebruikt en waarom

Deze tabel is het gezamenlijke keuzeoverzicht en wordt bijgewerkt bij gewijzigde projectkeuzes. Fasedetails en meetresultaten blijven bij de gedateerde fase staan. AGENTS.md verplicht het bijhouden van deze sectie bij toekomstige werkzaamheden.

| Techniek of hulpmiddel | Waarvoor gebruikt en waarom | Controle of beperking |
| --- | --- | --- |
| Python en JSON | Uitvoerbare logica en kleine leesbare datasets die we zelf kunnen nakijken. | 36 agentrecepten en vijf aparte Ollama-demorecepten; syntax, JSON en MCP-invoerformaat gecontroleerd. |
| LlamaIndex-chunking | Vergelijkt knippen op tokens met knippen per receptonderdeel; zo kunnen we nagaan of betekenisvolle stukken beter worden gevonden. | Twee indexen op 36 recepten; vergelijking op dezelfde 18 zoekvragen. Zie de resultaten onder Receptendataset en chunking. |
| FastEmbed met `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Zet vragen en tekst om in vergelijkbare getalvectoren voor zoeken op betekenis, lokaal en met ondersteuning voor meerdere talen. | Echte zoekvragen vanuit de interface, inclusief de nieuwe zoekvragen van persoon 1. |
| Lokale Qdrant-vectorstore | Bewaart en doorzoekt die vectoren met cosinusovereenkomst; geen aparte gehoste database nodig. | Indexen blijven buiten Git. Een zoekscore is geen kans op een correct antwoord. |
| LangGraph | Laat de gedeelde vraag/state door expliciete zoek-, reken- en antwoordstappen lopen; maakt de gekozen route zichtbaar. | Vier lokale routes getest. Groq-modelroutering nog niet live geverifieerd. Lesbasis: PowerPoint 1, slide 69. |
| MCP via stdio en `scale_ingredients` | Laat de agent een aparte lokale Python-rekentool aanroepen via een vast protocol. Vaste berekeningen worden door code uitgevoerd. | Integratiecheck voor alle 36 recepten en losse hoeveelheden. Lesbasis: PowerPoint 1, slides 72–73. |
| `Decimal` en Pydantic | Nauwkeurig met decimale hoeveelheden rekenen en invoer/uitvoer beschrijven en valideren. | Alle herschaalde ingrediënten vergeleken met de brondata; ongeldige portievragen voeren geen rekentool uit. |
| Groq en HTTPX | Bestaande optionele koppeling voor modelroutering, geformuleerde antwoorden en modelmetingen; interface hergebruikt dezelfde agent. | Geen sleutel beschikbaar. Echte tokens, TTFT en modelantwoorden zijn nog niet geverifieerd. |
| Streamlit | Bouwt gesprek, bronfragmenten, MCP-details en meetvelden direct vanuit Python, zodat de interface beperkt en uitlegbaar blijft. | Zeven schermchecks en een echte integratiecheck met 51 scenario's op de huidige dataset. Metingen verschijnen na afloop; elke vraag is zelfstandig. |
| AppTest en unittest | Controleren de interface en de volledige lokale keten herhaalbaar, inclusief foutgevallen. | Snelle schermchecks draaien in CI; de modelafhankelijke integratiecheck draait lokaal. Visuele browsercontrole blijft open. |
| Ragas | Voorziene evaluatie van bronkwaliteit en antwoordtrouw, naast controle van routes en berekeningen. | Bestaande optionele koppeling; live scores ontbreken. Werkpakket 3 blijft apart te integreren. |
| Ollama | Aparte bestaande lokale RAG-demo met vijf voorbeeldrecepten; bruikbaar om lokaal embeddings en antwoorden te demonstreren. | Niet de backend van `chef_ui.py` en niet opnieuw functioneel getest bij deze integratie. |
| Git, GitHub Actions en Codex | Versiebeheer en automatische controles houden de samenwerking herhaalbaar; Codex hielp bij implementatie, tests en documentatie. | Repositoryafspraken gelezen; AI-bijdragen staan per fase. Eigen review en opleidingsbeleid moeten nog worden nagegaan. |

Lesbasis voor het zichtbaar controleren van tussenstappen: PowerPoint 1, slides 82–83. De keuze voor Streamlit/AppTest is een implementatiekeuze; deze tools worden hier niet als eis uit de slides of de ontbrekende opdracht-pdf voorgesteld.
## Receptendataset en chunking

**27 november 2026.** De gebruiker koos taak 1 voor het team en gaf PowerPoint 1 als lesbasis. Codex hielp met de bronselectie, de Nederlandse bewerking, het vergelijkingsscript, de uitvoering en de documentatie. De drie bestaande recepten zijn behouden. De [33 nieuwe recepten](../data/README.md#herkomst-van-de-agentrecepten) zijn verspreid over acht categorieën, waaronder ontbijt, lunch, avondeten en dessert.

Dia's 29–36 behandelen hoe chunkgrenzen bepalen welk deel van een recept je kunt terugvinden. De eerste methode splitst de volledige recepttekst op maximaal 96 tokens met maximaal 16 tokens overlap. De tweede methode houdt overzicht, ingrediënten, bereiding en eventuele vervangingen apart en hanteert binnen elk onderdeel dezelfde limiet. De 96 tokens slaan op de tekst vóór het toevoegen van de kop. Beide methodes gebruiken hetzelfde meertalige embeddingmodel en dezelfde lokale Qdrant-vectorstore, zoals besproken op dia's 37–45.

### Lokale zoekvergelijking

`python -m scripts.compare_chunking --output reports/chunking-local.json` vergelijkt de elf bestaande zoekvragen en zeven nieuwe vragen. De zoeker doorzoekt alle 36 recepten zonder receptfilter, router of taalmodel. Een vraag telt als gevonden zodra de fragmenten samen alle afgesproken tekstbewijzen uit het juiste recept bevatten. De top 10 maakt de diagnose mogelijk. De tabel telt de eerste één en drie plaatsen.

| Meting | Op tokenlengte | Per receptonderdeel |
| --- | ---: | ---: |
| Fragmenten in de index | 106 | 133 |
| Al het benodigde bewijs op plek 1 | 6/18 | 11/18 |
| Al het benodigde bewijs in de top 3 | 13/18 | 14/18 |

Bij de vraag *Hoeveel water gaat er in totaal in de curry?* kwam bij splitsen per onderdeel eerst het ingrediëntenfragment met **420 ml water**. Bij splitsen op tokenlengte kwam eerst een bereidingsstap met **375 ml**, de hoeveelheid voor één stap. Het volledige antwoord stond daar op plek 2. Bij de bloemkoolvervanging kwam het juiste fragment bij beide methodes buiten de top 10. De sectiemethode zette bijvoorbeeld de kalkoenvervanging van de lasagne op plek 1. De vervanging stond wel in het curryrecept, dus de fout ontstond bij het rangschikken van de zoekresultaten.

Splitsen per onderdeel gaf op deze vragen vaker het bewijs op plek 1. Bij enkele vragen gaf tokenlengte een beter resultaat. De vergelijking is klein en meet toegang tot broninformatie. De live Ragas-beoordeling en het GenAI-beleid van de opleiding vragen nog verificatie. De recepttijden zijn bronwaarden en de bereidingen zijn niet fysiek uitgeprobeerd.

### Drie of vijf zoekfragmenten

In een aanvullende test op dezelfde 18 vragen vond splitsen per receptonderdeel zonder receptfilter al het bewijs bij 14 vragen met drie fragmenten en bij 15 met vijf. Met de bestaande receptnaamherkenning van de agent vond de zoeker het bewijs bij 17 van de 18 vragen, zowel met drie als met vijf fragmenten. De gemiddelde hoeveelheid fragmenttekst steeg daarbij van 616 naar 915 tekens. Het voorstel is daarom om drie fragmenten als standaard te behouden. De bloemkoolvervanging bleef de enige misser met receptnaamherkenning. Het juiste fragment stond op plek 7 bij de sectiemethode.

### Gecontroleerd

- 36 unieke recept-ID's en de vereiste velden. De oorspronkelijke drie records zijn inhoudelijk ongewijzigd.
- Hoeveelheden, porties en tijden van de 33 aanvullingen vergeleken met de vastgelegde corpusversie. De 33 bronrevisies zijn bevestigd via Wikibooks. Dieettags zijn gekozen op basis van de opgenomen ingrediënten.
- Beide Qdrant-indexen opnieuw opgebouwd. De repositorycontrole en `git diff --check` zijn uitgevoerd.
- De bestaande lokale agentbenchmark opnieuw uitgevoerd. Beide methodes behouden 18/18 juiste routes en 6/6 correcte MCP-uitkomsten.
- Nieuw recept via de bestaande agent getest. Bij *Schaal Quiche Lorraine van 6 naar 4 porties* vond RAG drie fragmenten en rekende de MCP-tool onder meer 300 g kruimeldeeg om naar 200 g.

## Volgende fasen

Noteer per fase de datum, het projectwerk onder de naam van de projectauteur, de gemaakte keuze en het testresultaat. Vermeld eventueel GenAI-gebruik apart en werk de MVP-checklist bij.
