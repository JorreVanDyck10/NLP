# Flavor Chef — projectrapport

## Wat we hebben gemaakt

Flavor Chef is een kookassistent die recepten opzoekt en hoeveelheden aanpast aan het aantal porties. Bij een receptvraag zoekt de agent eerst informatie in onze dataset. Het taalmodel maakt daarna een antwoord op basis van die fragmenten. Berekeningen gebeuren in een aparte Python-tool.

We hebben het werk verdeeld over recepten en zoeken, de agent en rekentool, evaluatie en de interface. Mijn deel is **persoon 4: de lokale interface en demo**. Daarin breng ik de andere onderdelen samen en laat ik zien hoe een antwoord tot stand komt.

De eerste demo van 19 november gebruikte Ollama en vijf voorbeeldrecepten. Die vond bij de controle de juiste bereidingstijd voor chili en meldde dat informatie over chocoladetaart ontbrak. Die demo staat apart van de agent met 36 recepten die hieronder wordt besproken. De resultaten hieronder zijn vastgelegd op 27 november 2026.

## Receptendataset en chunking

De agent gebruikt drie recepten van Health Canada en 33 Nederlandse bewerkingen uit het Open Recipe Corpus. Elk recept bevat ingrediënten, porties, bereidingsstappen, kooktijd, dieettags en een bronlink. De herkomst en licentie staan in de [datasetbeschrijving](../data/README.md#herkomst-van-de-agentrecepten). De recepten zijn niet door ons bereid om de kooktijden te controleren.

We vergelijken twee manieren om recepten in kleinere tekststukken, of chunks, te verdelen:

- Splitsen op maximaal 96 tokens, met 16 tokens overlap.
- Eerst splitsen per receptonderdeel, zoals ingrediënten en bereiding, en daarbinnen dezelfde tokenlimiet gebruiken.

Beide methodes gebruiken hetzelfde meertalige MiniLM-embeddingmodel. Dat zet tekst om in getallen waarmee we de vraag en receptfragmenten kunnen vergelijken. Qdrant bewaart de fragmenten en hun vectoren lokaal. De agent krijgt standaard de drie best passende fragmenten.

Bij de eerste vergelijking op 36 recepten zijn 18 zoekvragen gebruikt, zonder receptfilter of taalmodel. Een vraag telt als gevonden als de fragmenten samen alle afgesproken informatie uit het juiste recept bevatten.

| Meting | Tokenchunks | Receptsecties |
| --- | ---: | ---: |
| Aantal fragmenten | 106 | 133 |
| Volledig bewijs op plek 1 | 6/18 | 11/18 |
| Volledig bewijs in de top 3 | 13/18 | 14/18 |

Receptsecties zetten het volledige bewijs vaker bovenaan. Bij de watervraag stond bijvoorbeeld de ingrediëntenregel met **420 ml** meteen bovenaan. Bij tokenchunks stond eerst een bereidingsstap met **375 ml** en pas daarna het totaal.

Met vijf fragmenten in plaats van drie vonden receptsecties bewijs voor één extra vraag. Met het receptfilter van de agent bleef de score gelijk op 17/18, terwijl de hoeveelheid meegestuurde tekst toenam. Daarom bleef drie de standaard. Het fragment met de bloemkoolvervanging werd nog gemist.

Deze vergelijking is uitgevoerd met `python -m scripts.compare_chunking --output reports/chunking-local.json`. Ze meet de zoekfunctie. De agenttest verderop gebruikt een andere vraagset en ook receptnaamherkenning.

## Agent en rekentool

De agent gebruikt LangGraph om te kiezen tussen zoeken, een losse hoeveelheid schalen, een recept zoeken en schalen, of gewoon antwoorden. In de Groq-modus kiest `openai/gpt-oss-20b` de route en formuleert het model de zoekantwoorden. De lokale modus werkt zonder taalmodel.

Voor schalen roept de agent via MCP de Python-tool `scale_ingredients` aan. MCP is hier de verbinding tussen de agent en de rekentool. De tool rekent met de verhouding tussen de oude en nieuwe porties. Voor water in de curry is dat **420 × 7 / 4 = 735 ml**. Zo hoeft het taalmodel de hoeveelheden niet zelf uit te rekenen.

## Mijn bijdrage: lokale interface en demo

Ik heb met hulp van Codex de interface gebouwd in [chef_ui.py](../chef_ui.py). Ik gebruik Streamlit omdat ik daarmee vanuit Python het gesprek, de bronnen en de metingen kan tonen. De interface gebruikt dezelfde agent als de terminalversie en sluit aan op het werk van persoon 1 en 2.

Naast de vraag en het antwoord toon ik de gekozen route, de opgehaalde receptfragmenten en de invoer en uitvoer van de MCP-tool. Bij schalen staan de oude en nieuwe hoeveelheden naast elkaar. De tussenstappen verschijnen zodra ze klaar zijn. Daardoor kan ik bij een verkeerd antwoord nagaan of de fout bij het zoeken, rekenen of formuleren zit.

Er zijn drie modi: lokaal, Groq en een gesimuleerd voorbeeld. Bij dat voorbeeld staat duidelijk dat de cijfers geen echte metingen zijn. Als tokengegevens ontbreken, toon ik **Niet gemeten**. Bij een fout blijven de afgeronde stappen zichtbaar en kan de vraag opnieuw worden geprobeerd.

### Zoekvraag en schaalvraag

Voor de live controle zijn deze twee vragen via de interface uitgevoerd met Groq en de 36 recepten:

| Invoer | Tussenstappen | Uitvoer |
| --- | --- | --- |
| Voor hoeveel porties is de kikkererwtencurry bedoeld? | Zoekroute, drie curryfragmenten en een modelantwoord | 4 porties |
| Schaal de curry van 4 naar 7 porties. | Recept opzoeken en de ingrediënten met 4 en 7 porties naar MCP sturen | Onder andere water van 420 naar 735 ml en bloemkool van 500 naar 875 g |

| Live meting | Zoekvraag | Schaalvraag |
| --- | ---: | ---: |
| Inputtokens | 524 | 183 |
| Outputtokens | 68 | 32 |
| Verwerkingstijd | 3003 ms | 4493 ms |
| Tijd tot de eerste antwoordtoken (TTFT) | 348 ms | Niet van toepassing |

De tokenaantallen zijn opgeteld over de modelaanroepen. Bij de zoekvraag zijn er twee: de routekeuze en het antwoord. Bij de schaalvraag kiest het model alleen de route; de rekentool levert het resultaat. Daarom is daar geen TTFT voor een modelantwoord. De verwerkingstijd omvat de hele aanvraag en de schermupdates. Dit zijn twee afzonderlijke metingen; een volgende run kan andere tijden geven. De uitvoer staat lokaal in `reports/ui-live.json`.

Meer bronfragmenten meesturen kost meer inputtokens en kan de verwerking vertragen, maar kan ook ontbrekende informatie opleveren. Minder tokens betekent niet automatisch een sneller antwoord: de schaalvraag gebruikte minder modeltokens, maar duurde in deze proef langer. De rest van de keten en verschillen tussen API-aanroepen kunnen daarbij meespelen. Met deze twee vragen hebben we geen algemeen snelheidsverschil aangetoond.

### Controles en beperkingen

Voor mijn onderdeel slaagden twaalf schermtests, vijf tests met gesimuleerde Groq-responsen en vier lokale integratietests met samen 51 scenario's. Daarin zijn alle 36 recepten via de echte MCP-tool herschaald. De gesimuleerde tests controleerden onder andere een ongeldige sleutel, gebruikslimieten, een onbereikbare dienst en ontbrekende tokengegevens. De twee live vragen en de weergave in Chrome zijn apart gecontroleerd, met hulp van Codex.

De interface bewaart het gesprek op het scherm, maar verwerkt elke vraag zelfstandig. Vorige berichten worden dus niet als gesprekscontext gebruikt. Het antwoord verschijnt wanneer de antwoordstap klaar is; losse teksttokens verschijnen niet tijdens het genereren.

## Evaluatie met 36 recepten

De teamtest bevat 20 vragen: twaalf zoekvragen met een bekend antwoord, één vraag naar ontbrekende informatie, zes schaalvragen en één begroeting. Beide chunkmethodes gebruiken dezelfde recepten, vragen, hetzelfde embeddingmodel en maximaal drie fragmenten. De referenties staan in [data/evaluation.json](../data/evaluation.json).

### Lokale meting

Deze meting gebruikt geen taalmodel voor de route of het antwoord. Ze controleert de lokale routes, bronnen en berekeningen.

| Meting | Tokenchunks | Receptsecties |
| --- | ---: | ---: |
| Juiste route | 20/20 | 20/20 |
| Juiste gecontroleerde MCP-uitkomst | 6/6 | 6/6 |
| Volledig bewijs op plek 1 | 6/12 | 9/12 |
| Volledig bewijs in de top 3 | 10/12 | 11/12 |

### Live meting met Groq en Ragas

De agent gebruikte `openai/gpt-oss-20b`. Ragas gebruikte `qwen/qwen3.8-27b` als beoordelaar, nadat de eerste poging met GPT-OSS 120B tegen de dagelijkse tokenlimiet liep. Beide chunkmethodes zijn met dezelfde Qwen-beoordelaar getest.

| Meting | Tokenchunks | Receptsecties |
| --- | ---: | ---: |
| Juiste route | 18/20 | 18/20 |
| Juiste gecontroleerde MCP-uitkomst | 6/6 | 6/6 |
| Volledig bewijs op plek 1 | 6/12 | 8/12 |
| Volledig bewijs in de top 3 | 9/12 | 9/12 |
| Context Precision | 0,6833 | 0,8000 |
| Context Recall | 0,9000 | 0,8000 |
| Faithfulness | 1,0000 | 0,9000 |

Context Precision beoordeelt of relevante fragmenten hoog staan. Context Recall kijkt of de benodigde informatie is opgehaald. Faithfulness kijkt of het antwoord door de opgehaalde tekst wordt ondersteund. Ragas kon bij beide methodes dezelfde tien van de twaalf zoekvragen scoren. Twee vragen kregen door een verkeerde route geen broncontext.

Bij vergelijking met de referenties waren acht van de twaalf zoekantwoorden volledig juist, bij beide methodes. Bij de yoghurtcakevraag gaf de agent terecht aan dat de bakvormmaat niet in de opgehaalde informatie stond. De schaalvraag over Quiche Lorraine leverde onder andere 200 g deeg en twee eieren op voor vier porties.

De uitvoer staat lokaal in `reports/evaluation-expanded.json` en `reports/ragas-expanded.json`, met datasetversies en instellingen. De commando's om de meting te herhalen staan in [VOORTGANG.md](VOORTGANG.md#live-benchmark-met-groq-en-ragas).

### Wat er fout ging

Bij een fout is eerst gecontroleerd of de juiste receptinformatie was opgehaald.

- **Verkeerde route:** de ricottavraag ging naar schalen. De vraag naar de oventemperatuur ging naar chat en kreeg 90 °C als antwoord, terwijl het recept 120 °C vermeldt.
- **Gemist fragment:** de vervanging voor bloemkool stond wel in de index, maar buiten de top 3. De agent kreeg die informatie dus niet mee.
- **Verkeerd antwoord met de juiste bron:** bij de watervraag waren de juiste 420 ml opgehaald. Het model telde daar de 375 ml uit een bereidingsstap opnieuw bij en antwoordde 795 ml. Die 375 ml maken al deel uit van het totaal. Ragas gaf dit antwoord bij beide methodes toch Faithfulness 1,0.

Ik heb de watervraag daarom als **Broncontrole** in mijn interface opgenomen. Het echte modelantwoord blijft zichtbaar naast de referentie van 420 ml. Daarmee kan ik tonen waarom bronnen bekijken en het antwoord narekenen nodig blijven. De gewone zoekdemo gebruikt de portievraag.

Op deze testset geven receptsecties vaker het bewijs op de eerste plek. In de live top 3 is er geen verschil. De rekentool geeft alle zes gecontroleerde uitkomsten juist terug.

De volgende stap is gericht op de fouten: duidelijkere routevoorbeelden voor ingrediënt- en temperatuurvragen, een zoekvergelijking die vervangingen beter herkent en een antwoordregel die het ingrediëntentotaal scheidt van hoeveelheden per bereidingsstap. Of die aanpassingen helpen, moet met dezelfde vragen opnieuw worden gemeten.

### Eerste proef met drie recepten

Vóór de uitbreiding is getest met drie recepten en 18 vragen. Lokaal waren beide methodes correct voor 18/18 routes en 6/6 schaaluitkomsten. De [bewaarde baseline](../reports/baseline.json) hoort bij die versie.

De live proef gebruikte GPT-OSS 20B voor de agent en GPT-OSS 120B voor Ragas. Beide methodes haalden 16/18 routes en 6/6 schaaluitkomsten. Ragas scoorde negen van de elf zoekvragen:

| Metriek | Tokenchunks | Receptsecties |
| --- | ---: | ---: |
| Context Precision | 0,7593 | 0,7778 |
| Context Recall | 0,8889 | 0,7778 |
| Faithfulness | 0,8889 | 1,0000 |

De uitvoer stond in `reports/ragas.json`, met tokengegevens en tijden voor 58 agentaanroepen en TTFT voor 22 antwoordaanroepen. Deze eerdere proef heeft een andere dataset, vraagset en beoordelaar dan de meting met 36 recepten. De cijfers zijn daarom geen rechtstreekse voor-en-na-vergelijking.

## Gebruikt en waarom

De gebruikte technieken, redenen en lesbronnen staan in [PROJECTKEUZES.md](PROJECTKEUZES.md). Voor mijn onderdeel is alleen PowerPoint 1 gebruikt. De opdrachtbron is *NLP & LLM Challenge: Agentic Culinary Assistant / Flavor Chef*, pagina's 1–3.

## Gebruik van AI en wat ik nog moet doen

Voor mijn deel heb ik Codex gebruikt bij de implementatie, de testcode, de technische controles en het herschrijven van dit rapport. Bij de andere werkpakketten is Codex ook gebruikt voor code, data, metingen en foutanalyse. De genoemde controles zijn met AI-hulp uitgevoerd.

Mijn interface is technisch afgerond. Ik moet de code nog zelf nalopen en de demo en uitleg oefenen. Het precieze GenAI-beleid van de opleiding moet nog gecontroleerd worden; de opdracht verwijst daarvoor naar een apart beleid. De huidige evaluatie test porties herschalen. Een aparte test voor eenhedenconversie, die de opdracht ook noemt, is in deze gerapporteerde versie nog niet aangetoond.
