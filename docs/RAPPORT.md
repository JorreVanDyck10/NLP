# Flavor Chef | Projectrapport

[Terug naar de README](../README.md) · [Onderbouwing van de projectkeuzes](PROJECTKEUZES.md)

**Projectauteur** Raoul

**Doel:** een volledige MVP die Raoul zelf kan uitleggen. De rubric voorziet maximaal 85% voor een werkende MVP met goede analyse.

**Huidige fase.** De agent gebruikt 36 recepten en ondersteunt zoeken, porties herschalen en g ↔ kg omrekenen via de lokale interface. De MVP-evaluatie gebruikt 20 vragen op 36 recepten. De Ollama-demo is een apart onderdeel. Zie de [projectoverdracht](PROJECTKEUZES.md), de [voortgang](VOORTGANG.md) en de [MVP-checklist](MVP-CHECKLIST.md).

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

**Mijn werkpakket.** Ik ben verantwoordelijk voor werkpakket 4: de lokale interface en de demo van Flavor Chef. Mijn doel is om naast het antwoord ook de bronnen, de MCP-aanroep en de metingen zichtbaar te maken. Hieronder beschrijf ik de eerste versie; de afgeronde technische oplevering staat [verderop in dit rapport](#27-november-2026--persoon-4-technisch-opgeleverd).

**Aanpak en AI-hulp.** Ik heb met ondersteuning van Codex de eerste interface uitgewerkt in `chef_ui.py`, met `requirements-ui.txt`, zes interfacechecks en een [demo-handleiding](LOKALE-INTERFACE.md). Ik heb hiervoor Streamlit gebruikt, omdat ik zo vanuit Python het gesprek en de tussenresultaten kan tonen. De interface gebruikt de bestaande agent. In deze eerste versie werd de toolinvoer nog uit de vraag en brondata afgeleid en verschenen de metingen na afloop. De geschiedenis bleef in de browsersessie, terwijl iedere vraag zelfstandig werd verwerkt. Ik heb ook een voorbeeldmodus voorzien die ingevulde tokens, tijden en scores duidelijk als gesimuleerd markeert.

**Controles van de eerste versie.** Voor deze versie zijn met hulp van Codex de installatie, dependencies, zes AppTest-checks, repositorystructuur en whitespace gecontroleerd. Beide indexen zijn opgebouwd met de toenmalige drie recepten: 17 tokenchunks en 20 sectiechunks. De schermchecks behandelden onder meer een ontbrekende sleutel, ontbrekende metingen, fouten, geschiedenis en moduswissels. De Streamlit-server gaf HTTP 200 op de healthcheck.

**Echte lokale keten via de interface.** Bij “Hoeveel water gaat er in totaal in de curry?” was de route `search` en bevatten de drie opgehaalde fragmenten de juiste **420 ml water**. De gemeten agenttijd was ongeveer **1902 ms**. Bij “Schaal de curry van 4 naar 7 porties” was de trace `scale_recipe`, drie RAG-fragmenten, `MCP: scale_ingredients`; de echte tool gaf **735 ml water** terug bij een agenttijd van ongeveer **2909 ms**. Een losse schaalvraag gaf via MCP ook **300 g** terug voor 200 g van vier naar zes porties. Dit zijn afzonderlijke controles op deze pc, geen nieuwe benchmark. Er is geen taalmodel gebruikt: tokenvelden tonen terecht **Niet gemeten**.

**Lesbasis en afbakening.** Voor deze fase heb ik PowerPoint 1 als lesbasis gebruikt, met slides 69, 72–73 en 82–83. De inhoud is visueel geraadpleegd. PowerPoint 2 en 3 zijn niet gebruikt. Bij deze eerste controle waren echte Groq-metingen en visuele browsercontrole nog niet beschikbaar; die zijn bij de technische oplevering hieronder wel uitgevoerd. Mijn eigen demo-oefening, code-review en controle van het opleidingsbeleid voor GenAI blijven afzonderlijke vervolgstappen.

## 27 november 2026 | Integratie persoon 1, 2 en 4

**Vraag en eigen bijdrage.** De gebruiker vroeg de nieuwste repository op te halen en recepten/zoeken, agent/MCP en interface samen te controleren. De eigen review en demo-oefening door de gebruiker blijven open.

**Uitgevoerd met AI-hulp.** De nieuwste wijzigingen zijn opgehaald. De branch `feat/recepten-en-chunking` van persoon 1 is samengevoegd met de lokale interface van persoon 4 en de bestaande agent/MCP-code van persoon 2. De dataset bevat nu 36 recepten. Conflicten in het rapport en de voortgang zijn opgelost met behoud van beide bijdragen. De aparte evaluatiebranch van persoon 3 is nog niet in deze integratie opgenomen. Codex voegde `scripts/test_integration.py` toe en repareerde de voorbeeldmodus: die kiest het curryrecept op ID in plaats van het eerste recept in de lijst. Dit voorkomt een verkeerd voorbeeld als de dataset anders wordt gesorteerd.

**Controles.** Vier integratietests met **51 scenario's** slagen via de echte interface en backend: tien zoekvragen, inclusief de zeven nieuwe vragen van persoon 1; het herschalen van **alle 36 recepten** met behoud van eenheden, notities en onbepaalde hoeveelheden; een losse schaalvraag; begroeting; en drie ongeldige/onvolledige schaalvragen zonder tooluitvoering. Alle 36 recepten passen ook in het Pydantic-invoerformaat van de MCP-tool. Daarnaast slagen zeven interfacechecks, dependencycontrole, repositorycontrole en whitespacecontrole.

De lokale benchmark is opnieuw uitgevoerd naar het genegeerde `reports/integration.json`. Beide chunkmethodes halen opnieuw **18/18 routes** en **6/6 MCP-uitkomsten**. Het benodigde bewijs staat in de top 3 bij **9/11** vragen voor tokenchunks en **10/11** voor sectiechunks. De referentiebaseline is behouden. Deze cijfers bewijzen de gecontroleerde routes en berekeningen, niet de inhoudelijke juistheid van toekomstige modelantwoorden.

Ook de zoekvergelijking zonder receptfilter is op de geïntegreerde versie herhaald (`reports/chunking-integration.json`, buiten Git): **106 tokenchunks** en **133 sectiechunks**, met top-3-bewijs voor **13/18** en **14/18** vragen. Dit bevestigt de vergelijking van persoon 1. Deze ongerichte zoekvergelijking en de agentbenchmark met receptnaamherkenning meten verschillende stappen en mogen niet als dezelfde score worden gelezen.

**Open na deze fase.** De live proef van persoon 3 volgde afzonderlijk op de drie proefrecepten en staat verderop in dit rapport. De volledige agenttestset moet ook de nieuwe recepten gaan omvatten. De bloemkoolvraag blijft een bekend rangschikkingsprobleem en vraagt verdere analyse. Voor de interface blijven live Groq-tokens, TTFT, visuele browsercontrole, persoonlijke demo-oefening en GenAI-beleid te controleren. PowerPoint 2 en 3 zijn niet gebruikt.

## Gebruikt en waarom

De [projectkeuzes](PROJECTKEUZES.md) leggen vast wat we gebruiken, waarvoor en waarom. Fasedetails en meetresultaten staan bij de betrokken projectfase.

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

Splitsen per onderdeel gaf op deze vragen vaker het bewijs op plek 1. Bij enkele vragen gaf tokenlengte een beter resultaat. De vergelijking is klein en meet toegang tot broninformatie. Een live Ragas-meting met deze uitgebreide dataset en het GenAI-beleid van de opleiding vragen nog verificatie. De recepttijden zijn bronwaarden en de bereidingen zijn niet fysiek uitgeprobeerd.

### Drie of vijf zoekfragmenten

In een aanvullende test op dezelfde 18 vragen vond splitsen per receptonderdeel zonder receptfilter al het bewijs bij 14 vragen met drie fragmenten en bij 15 met vijf. Met de bestaande receptnaamherkenning van de agent vond de zoeker het bewijs bij 17 van de 18 vragen, zowel met drie als met vijf fragmenten. De gemiddelde hoeveelheid fragmenttekst steeg daarbij van 616 naar 915 tekens. Het voorstel is daarom om drie fragmenten als standaard te behouden. De bloemkoolvervanging bleef de enige misser met receptnaamherkenning. Het juiste fragment stond op plek 7 bij de sectiemethode.

### Gecontroleerd

- 36 unieke recept-ID's en de vereiste velden. De oorspronkelijke drie records zijn inhoudelijk ongewijzigd.
- Hoeveelheden, porties en tijden van de 33 aanvullingen vergeleken met de vastgelegde corpusversie. De 33 bronrevisies zijn bevestigd via Wikibooks. Dieettags zijn gekozen op basis van de opgenomen ingrediënten.
- Beide Qdrant-indexen opnieuw opgebouwd. De repositorycontrole en `git diff --check` zijn uitgevoerd.
- De bestaande lokale agentbenchmark opnieuw uitgevoerd. Beide methodes behouden 18/18 juiste routes en 6/6 correcte MCP-uitkomsten.
- Nieuw recept via de bestaande agent getest. Bij *Schaal Quiche Lorraine van 6 naar 4 porties* vond RAG drie fragmenten en rekende de MCP-tool onder meer 300 g kruimeldeeg om naar 200 g.

## 27 november 2026 | Werkpakket 3: evaluatie en foutanalyse

**Raoul.** Deze lokale en de volgende live meting gebruikten de oorspronkelijke corpusversie met drie proefrecepten. Werkpakket 3 omvat de controle van 18 referenties en de vergelijking van beide chunkmethodes. De set bevat 11 zoekvragen, 6 schaalvragen en 1 begroeting. De zoekreferenties zijn vergeleken met de drie receptbronnen en de schaalaantallen zijn nagerekend. De mozzarellavraag beoordeelt het moment van toevoegen, zoals gevraagd. De kookstand is aanvullende informatie. [Curry](https://www.canada.ca/en/health-canada/services/food-guide/eating-support/kitchen/recipes/chickpea-vegetable-curry.html), [lasagne](https://www.canada.ca/en/health-canada/services/food-guide/eating-support/kitchen/recipes/slow-cooked-lasagna.html), [pannenkoeken](https://www.canada.ca/en/health-canada/services/food-guide/eating-support/kitchen/recipes/strawberry-pancakes.html).

**Meting.** Beide indexen zijn opgebouwd met `recipe_search.py build`. `evaluate_chef.py --output reports/local.json` mat dezelfde drie recepten en 18 vragen met top 3 en het embeddingmodel `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. De run gebruikte Python 3.13.15 en de afhankelijkheden uit [requirements-eval.txt](../requirements-eval.txt). De SHA-256-hashes beginnen voor de recepten met `454c5734c1ee` en voor de vragen met `a1c698e33919`. De volledige hashes staan in de lokale uitvoer. De meetmethode volgt PowerPoint 1, slides 73–83.

| Meting | Op tokenlengte | Per receptsectie |
| --- | ---: | ---: |
| Verwachte route | 18/18 | 18/18 |
| Gecontroleerde MCP-uitkomsten | 6/6 | 6/6 |
| Alle benodigde broninformatie in het eerste fragment | 5/11 | 8/11 |
| Alle benodigde broninformatie in de top 3 | 9/11 | 10/11 |
| Gemiddelde reciproke rang van het volledige bewijs in de top 3 | 0,6212 | 0,7879 |

De route, MCP-controle en bewijsrang kwamen per vraag overeen met de [bewaarde referentiemeting](../reports/baseline.json). Per receptsectie werd het volledige bewijs bij één extra zoekvraag opgehaald. Dat verschil geldt voor deze kleine testset met drie recepten.

**Foutanalyse.** Voor de gemiste zoekvragen is dezelfde zoekvraag met hetzelfde receptfilter opnieuw uitgevoerd over alle fragmenten van het recept.

- `curry-substitution` koos op beide methodes de zoekroute. De top 3 bevatte ingrediënten- en bereidingsinformatie. Het fragment met de vervangingen stond op plek 6 van 6 bij tokenchunks en op plek 7 van 7 bij receptsecties. De broninformatie zat in beide indexen en viel buiten de drie fragmenten die de agent kreeg.
- `lasagne-ricotta` miste bij tokenchunks de `475 g magere ricotta`. Het fragment stond op plek 5 van 6. Bij receptsecties stond het ingrediëntenfragment op plek 3 van 7. Een te toetsen hypothese is dat bij vragen naar hoeveelheden een extra gewicht voor het ingrediënt en de vermelde eenheid het juiste fragment hoger zet.
- `curry-water-stages` laat zien waarom de benchmark alle benodigde feiten controleert. De twee hoeveelheden moeten samen aanwezig zijn. Het volledige bewijs was beschikbaar na twee resultaten bij tokenchunks en na drie bij receptsecties.
- De zes gecontroleerde schaaluitkomsten kwamen ook overeen met de getoonde hoeveelheden. Zo werd `2,5 g` van vier naar zes porties `3,75 g`. De begroeting haalde geen fragmenten op en startte geen MCP-tool.

**Voorbereiding Ragas.** Met gesimuleerde scores is gecontroleerd welke referenties, context en antwoorden de drie metrieken ontvangen en hoe de benchmark ontbrekende scores telt. Lokaal toont de agent bij zoekvragen de bronfragmenten. De live proef hieronder beoordeelt ook de gegenereerde antwoorden.

**GenAI-vermelding.** Codex hielp bij de referentiecontrole, benchmarkcode, uitvoering en foutanalyse. Raouls eigen review en demo-oefening staan open.

## 27 november 2026 | Live Groq- en Ragas-meting

**Raoul.** Deze live meting gebruikt de oorspronkelijke drie proefrecepten. Beide chunkmethodes draaiden via `evaluate_chef.py --ragas --output reports/ragas.json`, met top 3 en dezelfde recept- en vraagversies als bij de lokale benchmark. De agent gebruikte `openai/gpt-oss-20b` en de Ragas-beoordelaar gebruikte `openai/gpt-oss-120b`. De eerste proef leverde een leeg antwoord op omdat GPT-OSS het tokenbudget gebruikte voor redeneren. Met lage redeneerinspanning en een budget van 1024 tokens leverde de agent zichtbaar antwoord. De benchmark wachtte bij tijdelijke Groq-gebruikslimieten en rondde beide runs af. [Instellingen en keuzes](PROJECTKEUZES.md)

| Meting | Op tokenlengte | Per receptsectie |
| --- | ---: | ---: |
| Verwachte route | 16/18 | 16/18 |
| Gecontroleerde MCP-uitkomsten | 6/6 | 6/6 |
| Alle benodigde broninformatie in het eerste fragment | 5/11 | 7/11 |
| Alle benodigde broninformatie in de top 3 | 8/11 | 8/11 |
| Context Precision | 0,7593 (9/11) | 0,7778 (9/11) |
| Context Recall | 0,8889 (9/11) | 0,7778 (9/11) |
| Faithfulness | 0,8889 (9/11) | 1,0000 (9/11) |

Ragas scoorde bij beide methodes dezelfde negen zoekvragen. De twee verkeerd gerouteerde zoekvragen leverden geen receptcontext op. Per receptsectie lag de gemiddelde Context Precision iets hoger en lag de gemiddelde Context Recall lager. De vergelijking geldt voor deze proef met drie recepten.

**Telemetrie.** De ruwe live-uitvoer bevat inputtokens, outputtokens en duur voor alle 58 Groq-aanroepen van de agent. De 22 gestreamde antwoordaanroepen bevatten ook TTFT. De 36 routeaanroepen geven in één keer JSON terug. De aparte weergavecontrole staat bij de [oplevering van de Streamlit-interface](#27-november-2026--persoon-4-technisch-opgeleverd).

**Inhoudelijke controle.** Per methode zijn zeven van de elf zoekvragen volledig juist beantwoord. Bij één vraag gaf de agent terecht aan dat de opgehaalde fragmenten onvoldoende informatie bevatten. De overige drie antwoorden hadden een routerings- of antwoordfout.

- `lasagne-ricotta` ging bij beide methodes naar `scale_quantity`. De agent vroeg het aantal porties in plaats van de 475 g ricotta uit het recept op te halen.
- `pancakes-temperature` ging bij beide methodes naar `chat`. De agent gaf 90 °C zonder receptcontext. Het recept vermeldt 120 °C.
- `curry-substitution` ging naar de zoekroute. Het bewijs viel bij beide methodes buiten de top 3. De agent meldde terecht dat de opgehaalde fragmenten de vervanging niet vermeldden.
- `curry-water` haalde bij beide methodes de totale hoeveelheid van 420 ml op. De agent telde daar de 375 ml uit een bereidingsstap opnieuw bij en antwoordde 795 ml. Ragas gaf voor Faithfulness bij dit antwoord 0,0 met tokenchunks en 1,0 met receptsecties. De handmatige vergelijking met het recept blijft nodig om dit soort fout te vinden.

**GenAI-vermelding.** Codex hielp bij het oplossen van de lege antwoorden, het uitvoeren van de benchmark en de vergelijking met de referenties.

## 27 november 2026 | Integratie van werkpakket 3

De evaluatiecode, de foutanalyse en het keuzeoverzicht zijn samengevoegd met de versie met 36 recepten en de lokale interface. Codex hielp bij het samenvoegen en testen. De zeven schermtests en de vier integratietests, inclusief herschalen van alle 36 recepten, slaagden lokaal. De lokale benchmark met het uitgebreide corpus haalde per methode 18/18 routes en 6/6 MCP-uitkomsten. De top 3 bevatte het volledige bewijs bij 9/11 zoekvragen met tokenchunks en 10/11 met receptsecties. Deze herhaling gebruikte de bestaande 18 agentvragen. De live Ragas-meting hierboven blijft de referentie op drie proefrecepten.

## 27 november 2026 | Persoon 4 technisch opgeleverd

**Mijn bijdrage.** Ik heb het technische deel van werkpakket 4 afgerond: de lokale interface en demo van Flavor Chef. Ik heb met hulp van Codex het gesprek, de bronfragmenten, de MCP-aanroepen en de token- en tijdmetingen samengebracht in één Streamlit-interface. De oplevering is via [PR #6](https://github.com/JorreVanDyck10/NLP/pull/6) opgenomen in `main`. De interface sluit aan op de recepten en zoekfunctie van persoon 1 en de agent en rekentool van persoon 2.

**Uitvoering en keuzes.** Ik heb de interface zo opgezet dat ze na iedere afgeronde LangGraph-stap de volledige tussenstand ontvangt. Daardoor worden de route, opgehaalde bronnen en beschikbare metingen tijdens de aanvraag zichtbaar. Voor de MCP-tool toon ik de exacte invoer en uitvoer. Een tabel vergelijkt de hoeveelheden vóór en na het schalen; de ruwe gegevens blijven uitklapbaar. Ik heb ook hersteladvies en Opnieuw proberen voorzien, met behoud van reeds afgeronde stappen. Voor de Groq-sleutel is er een gemaskeerd veld per browsersessie dat gewist kan worden. De sleutel is bij de controles niet in broncode, interfaceberichten, Git of meetuitvoer opgeslagen.

Ik toon tokens, verwerkingstijd en TTFT afzonderlijk, omdat ze verschillende dingen meten. Bij een gewone zoekvraag formuleert het model een antwoord en kan TTFT gemeten worden. Bij routering gevolgd door alleen de rekentool is er geen gestreamd modelantwoord. In dat geval toont de interface terecht geen antwoord-TTFT. De callback voor de schermupdates is optioneel, zodat de terminalversie en benchmark hun bestaande uitvoerpad behouden.

**Gerichte live controle op 36 recepten.** Voor mijn oplevering zijn met `scripts/test_ui_live.py` twee echte demovragen uitgevoerd via Streamlits AppTest en `openai/gpt-oss-20b`. Codex hielp bij de uitvoering en het vastleggen van de resultaten. De meetuitvoer staat lokaal in het genegeerde `reports/ui-live.json` en bevat geen sleutel. Ik gebruik deze controle om de werking van mijn interface aan te tonen; de volledige Ragas-benchmark hoort bij werkpakket 3.

| Vraag | Antwoord/route | Inputtokens | Outputtokens | Verwerkingstijd | TTFT antwoord |
| --- | --- | ---: | ---: | ---: | ---: |
| Voor hoeveel porties is de kikkererwtencurry bedoeld? | 4 porties; `search`, drie bronfragmenten en modelantwoord | 524 | 68 | 3003 ms | 348 ms |
| Schaal de curry van 4 naar 7 porties. | `scale_recipe`, RAG en echte MCP; 420 ml water wordt 735 ml | 183 | 32 | 4493 ms | Niet van toepassing: alleen modelroutering, daarna toolantwoord |

De zoekvraag gebruikte twee modelaanroepen en de schaalvraag één. Tokens zijn opgeteld over afgeronde modelaanroepen. TTFT begint bij de antwoordaanroep, na zoeken. Verwerkingstijd omvat het agenttraject en de updates aan het scherm. Dit zijn afzonderlijke metingen op deze pc; timings kunnen per run verschillen.

**Visuele controle.** Bij de technische controle met Codex is de interface ook in Chrome nagekeken: de echte zoek- en schaalvraag, routes, bronfragmenten, meetvelden en de tabel met 420 ml en 735 ml naast elkaar. De voorbeeldmodus was herkenbaar als gesimuleerd. Met een bewust ongeldige testsleutel verscheen hersteladvies zonder verzonnen tokens. Na het wissen van die testsleutel werkte Opnieuw proberen met de geldige omgevingssleutel. Het eerdere foutbericht bleef zichtbaar in de geschiedenis. Het controletabblad en de tijdelijke previewserver zijn daarna gesloten.

**Foutvoorbeeld voor mijn verdediging.** Ik heb de watervraag opgenomen onder Broncontrole. Tijdens de live controle antwoordde Groq **795 ml** door 420 en 375 ml op te tellen, terwijl de juiste totale hoeveelheid van 420 ml wel in de bronnen stond. Hiermee kan ik uitleggen dat een fout antwoord niet altijd door de zoekfunctie ontstaat. Mijn interface bewaart het echte modelantwoord en toont de referentie, zodat de dubbeltelling zichtbaar wordt. Voor de gewone zoekdemo gebruik ik de portievraag. De fout is vastgelegd in `reports/ui-water-control.json`; de correctie van het modelgedrag hoort bij persoon 2.

**Testresultaat en beperkingen.** Voor mijn werkpakket zijn twaalf schermtests, vijf protocoltests met gesimuleerde Groq-responsen en vier echte lokale integratietests met 51 scenario's geslaagd. Daarbij zijn alle 36 recepten via MCP herschaald. Ook dependencies, repositorystructuur en whitespace zijn gecontroleerd. De protocoltests omvatten onder meer HTTP 401/429/503, time-outs, ontbrekende tokengegevens en behoud van bronnen bij een mislukte antwoordaanroep. Deze gesimuleerde fouten staan los van de echte live demometingen hierboven. Een volledige nieuwe Ragas-meting is voor mijn werkpakket niet uitgevoerd.

De gesprekshistoriek is zichtbaar in de interface, maar iedere vraag wordt zelfstandig verwerkt. Het modelantwoord verschijnt na de antwoordstap en wordt niet token voor token getoond. Voor dit werk heb ik alleen PowerPoint 1 als lesbasis gebruikt; de opdracht-pdf en het GenAI-beleid waren hier nog niet beschikbaar.

**GenAI-vermelding en vervolg.** Ik heb Codex gebruikt als ondersteuning bij de implementatie, testcode, technische controles en documentatie. Mijn technische bijdrage voor persoon 4 is afgerond. Ik moet de code nog zelf nalopen, de demo en mondelinge uitleg oefenen en mijn AI-verantwoording toetsen aan het beleid van de opleiding.

## 27 november 2026 | Evaluatie met 36 recepten

**Raoul.** De agenttestset bevat nu 20 vragen, binnen de 15–20 uit de opdracht. Er zijn twaalf zoekvragen met beantwoordbare referenties, één vraag over ontbrekende receptinformatie, zes schaalvragen en één begroeting. De schaalvraag waarbij het aantal porties gelijk bleef, maakte plaats voor het herschalen van Quiche Lorraine van zes naar vier porties. De extra zoekvragen gaan over de 75 ml olijfolie voor marmitako en de ontbrekende bakvormmaat bij yoghurtcake. De nieuwe referenties zijn tegen de vastgelegde bron gecontroleerd. [Evaluatievragen](../data/evaluation.json) · [Corpusversie](https://github.com/Rippy1911/open-recipe-corpus/tree/86102603bac07d79b94bc35cba5b50346798cc09)

**Methode.** Beide chunkmethodes gebruikten dezelfde 36 recepten, 20 vragen, top 3 en het meertalige MiniLM-embeddingmodel. `recipe_search.py build` controleerde of de actuele indexen klaarstonden. De receptenhash begint met `cfe4adba054de` en de vragenhash met `70c673ccf1d1`. De volledige hashes staan in de lokale JSON-uitvoer. De toets op ontbrekende informatie controleert of de agent het juiste recept ophaalt. De inhoud van het gegenereerde antwoord wordt handmatig gecontroleerd. De drie Ragas-metrieken zijn bestemd voor de twaalf zoekvragen met positief bronbewijs. [Meetinstructies](VOORTGANG.md#live-benchmark-met-groq-en-ragas)

### Lokale agentbenchmark met 20 vragen

Uitgevoerd met `evaluate_chef.py --output reports/evaluation-expanded.json` in Python 3.13.15.

| Meting | Op tokenlengte | Per receptsectie |
| --- | ---: | ---: |
| Fragmenten in de index | 106 | 133 |
| Verwachte route | 20/20 | 20/20 |
| Gecontroleerde MCP-uitkomsten | 6/6 | 6/6 |
| Alle benodigde broninformatie in het eerste fragment | 6/12 | 9/12 |
| Alle benodigde broninformatie in de top 3 | 10/12 | 11/12 |

De route, bewijsrang en toolcontrole voor de zeventien gedeelde vragen kwamen overeen met de vorige lokale run op 36 recepten. De 75 ml olijfolie stond bij beide methodes in het eerste fragment. Voor Quiche Lorraine leverde MCP bij beide methodes 200 g hartig kruimeldeeg, vier plakken gerookt spek en twee eieren. Bij de vraag naar een bakvormmaat haalden beide methodes alleen fragmenten uit het juiste yoghurtcakerecept op. De lokale agent geeft deze fragmenten terug.

De zoekcontrole met hetzelfde receptfilter over alle fragmenten van het recept plaatste de bloemkoolvervanging op plek 6 bij tokenchunks en plek 7 bij receptsecties. De ricotta stond op plek 5 met tokens en plek 3 met secties. De broninformatie staat in beide indexen. Bij de missers valt het benodigde fragment buiten de top 3 die de agent ontvangt.

### Live evaluatie met Groq en Ragas op 36 recepten

De eerste poging met `openai/gpt-oss-120b` als beoordelaar stopte door de dagelijkse tokenlimiet. Voor de herhaling staat `RAGAS_JUDGE_MODEL` op `qwen/qwen3.8-27b`. Beide chunkmethodes gebruiken diezelfde beoordelaar. De agent gebruikt opnieuw `openai/gpt-oss-20b`. De eerdere live proef verschilt zowel in testset als in beoordelaar. Vergelijk de chunkmethodes binnen dezelfde meetrun. [Herhalen](VOORTGANG.md#live-benchmark-met-groq-en-ragas) · [Groq-limieten](https://console.groq.com/docs/rate-limits)

| Meting | Op tokenlengte | Per receptsectie |
| --- | ---: | ---: |
| Verwachte route | 18/20 | 18/20 |
| Gecontroleerde MCP-uitkomsten | 6/6 | 6/6 |
| Alle benodigde broninformatie in het eerste fragment | 6/12 | 8/12 |
| Alle benodigde broninformatie in de top 3 | 9/12 | 9/12 |
| Context Precision | 0,6833 (10/12) | 0,8000 (10/12) |
| Context Recall | 0,9000 (10/12) | 0,8000 (10/12) |
| Faithfulness | 1,0000 (10/12) | 0,9000 (10/12) |

Ragas scoorde dezelfde tien zoekvragen per methode. Twee zoekvragen kregen door een routeringsfout geen broncontext. Met receptsecties stond het volledige bewijs vaker in het eerste fragment. De methodes haalden evenveel volledig bewijs in de top 3. Context Precision was hoger bij receptsecties en Context Recall hoger bij tokenchunks.

**Inhoudelijke controle.** Met beide methodes was het antwoord op acht van de twaalf beantwoordbare zoekvragen volledig juist. Bij de ontbrekende bakvormmaat meldde de agent bij beide methodes dat de opgehaalde yoghurtcakefragmenten die informatie missen. De nieuwe marmitakovraag gaf 75 ml olijfolie en de schaalvraag over Quiche Lorraine gaf alle gecontroleerde hoeveelheden correct terug.

- **Routering.** `lasagne-ricotta` ging naar `scale_quantity`. `pancakes-temperature` ging naar `chat` en kreeg 90 °C als antwoord, terwijl het recept 120 °C vermeldt. Beide fouten kwamen voor bij beide chunkmethodes.
- **Zoeken.** Bij `curry-substitution` stond het bewijs buiten de top 3. De agent meldde terecht dat de opgehaalde fragmenten onvoldoende informatie gaven. Ragas gaf die melding bij receptsecties Faithfulness 0,0.
- **Antwoord.** Bij `curry-water` haalde de agent 420 ml uit het recept en telde de 375 ml uit een bereidingsstap opnieuw mee. Beide antwoorden van 795 ml kregen van Ragas Faithfulness 1,0. De vergelijking met de referentie bracht de rekenfout aan het licht.

De aantallen tonen wat op deze 20 vragen is gemeten. De zes gecontroleerde MCP-uitkomsten waren bij beide methodes correct. De live JSON-uitvoer staat lokaal in `reports/ragas-expanded.json`.

Na de integratie met persoon 4 is de volledige lokale benchmark herhaald. Alle routerings-, schaal- en zoekuitkomsten kwamen overeen. De drie nieuwe vragen zijn voor beide chunkmethodes opnieuw live via Groq gecontroleerd, inclusief de exacte MCP-invoer bij het herschalen. De twaalf schermtests slaagden ook.

**GenAI-vermelding.** Codex hielp met het uitbreiden en controleren van de testset, het uitvoeren van de metingen en de foutanalyse.

## 27 november 2026 | MVP-oplevering

**Uitgangspunt.** PR #6 leverde de live interface op. PR #7 leverde de live nulmeting op de uitgebreide dataset. De huidige testset bewaart negentien van de twintig vragen van PR #7, inclusief alle twaalf bronvragen, de vraag naar de bakvormmaat en de Quiche Lorraine-schaalvraag. De losse schaalvraag over 200 g maakte plaats voor **250 g → 0,25 kg**. De omgekeerde conversie en een expliciet onbekende recepttitel zitten in de integratietests. [Gebruikt en waarom](PROJECTKEUZES.md#27-november-2026--keuzes-voor-de-mvp-oplevering)

**Gerichte live vergelijking.** Op de versie vóór de fixes koos Groq bij receptsecties twee maal de goede route. Het antwoord op de watervraag was **795 ml** ondanks het opgehaalde ingrediëntentotaal. Met de wijzigingen geeft dezelfde methode de juiste receptenroute en levert ze **475 g ricotta** en **120 °C**. De curryvervanging staat voortaan als derde fragment in beide strategieën. Het antwoord noemt wortel, aubergine, pompoen en broccoli. Bij de watervraag kwam de ingrediëntregel met **420 ml water** op plek 1 bij secties en plek 2 bij tokens. De agent gebruikt die regel rechtstreeks als totaal. Voor ricotta mist de tokenmethode nog het fragment en meldt het model dat de hoeveelheid ontbreekt. De sectiemethode haalt het bewijs op plek 3 op.

**Lokale benchmark.** Beide methodes haalden 20/20 routes en 6/6 MCP-uitkomsten. In de top 3 kwam volledig bronbewijs bij 11/12 vragen met tokenchunks en bij 12/12 met receptsecties. De afzonderlijke zoekvergelijking zonder receptfilter mat 19 unieke vragen. Die haalde 14/19 met tokenchunks en 15/19 met receptsecties. Vergelijk de aantallen per methode binnen elke test, aangezien de vraagsets verschillen.

**Reproduceerbaarheid.** De [meetcommando’s](VOORTGANG.md#live-benchmark-met-groq-en-ragas) bouwen beide Qdrant-indexen en gebruiken top 3. De beoordelaar voor vergelijking met PR #7 is `qwen/qwen3.8-27b`, met `openai/gpt-oss-20b` voor de agent. Een tussentijdse poging met de oude GPT-OSS 120B-beoordelaar liep tegen de gebruikslimiet aan. De JSON-rapporten zijn lokaal. Ze bevatten corpus- en testsethashes, bronfragmenten, gekozen route, tool- en antwoorduitvoer en de beschikbare metingen.

**Demoketen.** Streamlits live controle testte het antwoord **4 porties**, de schaaluitkomst **735 ml** en `convert_units` met **0,25 kg**. De zoekvraag gebruikte 606 inputtokens en 108 outputtokens, met een antwoord-TTFT van 401 ms. De schaalvraag gebruikte 224 inputtokens en 38 outputtokens. De conversie gebruikte 219 inputtokens en 29 outputtokens. Bij die twee vragen komen de routetokens van Groq en de berekening van MCP. De conversie is ook via de browser uitgevoerd. Gebruik het vroegere antwoord van **795 ml** voor de diagnose tijdens de verdediging.

**GenAI-vermelding.** Het team stelde de scope vast en maakte Groq-toegang beschikbaar. Codex hielp met de implementatie, regressietests, meting en rapportering. De eigen teamreview en demo-oefening blijven open. Het exacte GenAI-beleid van de opleiding is nog te controleren.

## Volgende fasen

Noteer per fase de datum, het projectwerk onder de naam van de projectauteur, de gemaakte keuze en het testresultaat. Vermeld eventueel GenAI-gebruik apart en werk de MVP-checklist bij.
