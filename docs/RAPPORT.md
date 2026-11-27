# Flavor Chef | Projectrapport

[Terug naar de README](../README.md)

**Projectauteur** Raoul

**Doel:** een volledige MVP die Raoul zelf kan uitleggen. De rubric voorziet maximaal 85% voor een werkende MVP met goede analyse.

**Huidige fase.** De Ollama-demo en de agent staan samen in de repository. De agent gebruikt nu 36 recepten en beide chunkmethodes zijn op die set vergeleken. Zie de [voortgang](VOORTGANG.md) en de [MVP-checklist](MVP-CHECKLIST.md).

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
