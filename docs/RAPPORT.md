# Flavor Chef | Projectrapport

[Terug naar de README](../README.md)

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

## 27 november 2026 | Persoon 4: lokale interface en demo

**Eigen bijdrage tot nu toe.** De gebruiker heeft bevestigd dat werkpakket 4 zijn verantwoordelijkheid is en de taakverdeling aangeleverd. Er is in deze sessie nog geen eigen code-review, mondelinge toelichting of door de gebruiker uitgevoerde demo vastgelegd.

**AI-hulp en keuze.** Codex heeft `chef_ui.py`, `requirements-ui.txt`, zes interfacechecks en de [demo-uitleg](LOKALE-INTERFACE.md) toegevoegd. De interface gebruikt Streamlit en roept de bestaande agent aan; de routering, dataset, evaluatie en MCP-rekentool zijn niet aangepast. Per vraag zijn antwoord, trace, bronfragmenten, toolinvoer/-uitvoer en metingen zichtbaar. De toolinvoer is afgeleid uit dezelfde state en brondata, geen onderschept protocol-log. De geschiedenis blijft in de browsersessie; iedere vraag wordt zelfstandig verwerkt. Metingen verschijnen na afloop. De aparte voorbeeldmodus markeert ingevulde tokens, tijden en scores als gesimuleerd.

**Uitgevoerde controles.** Installatie in `.venv` met Python 3.13 en `pip check` slagen. Beide bestaande indexen zijn lokaal opgebouwd (17 tokenchunks en 20 sectiechunks). Zes AppTest-checks slagen, inclusief ontbrekende sleutel, ontbrekende/gedeeltelijke metingen, foutafhandeling, geschiedenis en moduswissels. De Streamlit-server gaf HTTP 200 op de healthcheck. De repositorycontrole en whitespacecontrole slagen.

**Echte lokale keten via de interface.** Bij “Hoeveel water gaat er in totaal in de curry?” was de route `search` en bevatten de drie opgehaalde fragmenten de juiste **420 ml water**. De gemeten agenttijd was ongeveer **1902 ms**. Bij “Schaal de curry van 4 naar 7 porties” was de trace `scale_recipe`, drie RAG-fragmenten, `MCP: scale_ingredients`; de echte tool gaf **735 ml water** terug bij een agenttijd van ongeveer **2909 ms**. Een losse schaalvraag gaf via MCP ook **300 g** terug voor 200 g van vier naar zes porties. Dit zijn afzonderlijke controles op deze pc, geen nieuwe benchmark. Er is geen taalmodel gebruikt: tokenvelden tonen terecht **Niet gemeten**.

**Lesbasis en open controle.** PowerPoint 1, slides 69, 72–73 en 82–83 zijn visueel bekeken. PowerPoint 2 en 3 zijn niet gebruikt. De opdracht-pdf en het opleidingsbeleid voor GenAI ontbreken nog; de scope komt uit de aangeleverde taakverdeling. Live Groq-tokens en TTFT zijn niet geverifieerd omdat `GROQ_API_KEY` ontbreekt. Visuele browsercontrole was niet beschikbaar in deze chat; AppTest controleerde wel de interacties en getoonde velden. Persoon 4 moet de demo nog zelf oefenen, de code nakijken en de GenAI-verantwoording aan het opleidingsbeleid toetsen.

## Volgende fasen

Noteer per fase de datum, het projectwerk onder de naam van de projectauteur, de gemaakte keuze en het testresultaat. Vermeld eventueel GenAI-gebruik apart en werk de MVP-checklist bij.
