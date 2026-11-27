# Flavor Chef | Projectrapport

[Terug naar de README](../README.md) · [Onderbouwing van de projectkeuzes](PROJECTKEUZES.md)

**Projectauteur** Raoul

**Doel:** een volledige MVP die Raoul zelf kan uitleggen. De rubric voorziet maximaal 85% voor een werkende MVP met goede analyse.

**Huidige fase:** de eerste Ollama-demo en de agent met MCP-tool en lokale benchmark zijn samengebracht. De [voortgang](VOORTGANG.md) beschrijft de actuele agentstatus; de [MVP-checklist](MVP-CHECKLIST.md) volgt de eerste demo.

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

## 27 november 2026 | Werkpakket 3: evaluatie en foutanalyse

**Raoul.** Werkpakket 3 omvat de controle van 18 referenties en de vergelijking van beide chunkmethodes. De set bevat 11 zoekvragen, 6 schaalvragen en 1 begroeting. De zoekreferenties zijn vergeleken met de drie receptbronnen en de schaalaantallen zijn nagerekend. De mozzarellavraag beoordeelt het moment van toevoegen, zoals gevraagd. De kookstand is aanvullende informatie. [Curry](https://www.canada.ca/en/health-canada/services/food-guide/eating-support/kitchen/recipes/chickpea-vegetable-curry.html), [lasagne](https://www.canada.ca/en/health-canada/services/food-guide/eating-support/kitchen/recipes/slow-cooked-lasagna.html), [pannenkoeken](https://www.canada.ca/en/health-canada/services/food-guide/eating-support/kitchen/recipes/strawberry-pancakes.html).

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

**Raoul.** Beide chunkmethodes draaiden via `evaluate_chef.py --ragas --output reports/ragas.json`, met top 3 en dezelfde recept- en vraagversies als bij de lokale benchmark. De agent gebruikte `openai/gpt-oss-20b` en de Ragas-beoordelaar gebruikte `openai/gpt-oss-120b`. De eerste proef leverde een leeg antwoord op omdat GPT-OSS het tokenbudget gebruikte voor redeneren. Met lage redeneerinspanning en een budget van 1024 tokens leverde de agent zichtbaar antwoord. De benchmark wachtte bij tijdelijke Groq-gebruikslimieten en rondde beide runs af. [Instellingen en keuzes](PROJECTKEUZES.md)

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

**Inhoudelijke controle.** Per methode zijn zeven van de elf zoekvragen volledig juist beantwoord. Bij één vraag gaf de agent terecht aan dat de opgehaalde fragmenten onvoldoende informatie bevatten. De overige drie antwoorden hadden een routerings- of antwoordfout.

- `lasagne-ricotta` ging bij beide methodes naar `scale_quantity`. De agent vroeg het aantal porties in plaats van de 475 g ricotta uit het recept op te halen.
- `pancakes-temperature` ging bij beide methodes naar `chat`. De agent gaf 90 °C zonder receptcontext. Het recept vermeldt 120 °C.
- `curry-substitution` ging naar de zoekroute. Het bewijs viel bij beide methodes buiten de top 3. De agent meldde terecht dat de opgehaalde fragmenten de vervanging niet vermeldden.
- `curry-water` haalde bij beide methodes de totale hoeveelheid van 420 ml op. De agent telde daar de 375 ml uit een bereidingsstap opnieuw bij en antwoordde 795 ml. Ragas gaf voor Faithfulness bij dit antwoord 0,0 met tokenchunks en 1,0 met receptsecties. De handmatige vergelijking met het recept blijft nodig om dit soort fout te vinden.

**GenAI-vermelding.** Codex hielp bij het oplossen van de lege antwoorden, het uitvoeren van de benchmark en de vergelijking met de referenties.

## Volgende fasen

Noteer per fase de datum, het projectwerk onder de naam van de projectauteur, de gemaakte keuze en het testresultaat. Vermeld eventueel GenAI-gebruik apart en werk de MVP-checklist bij.
