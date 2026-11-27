# Flavor Chef | MVP-checklist

[Terug naar de README](../README.md)

**Doel:** een werkende MVP die Raoul zelf kan uitleggen. Volgens de rubric kan een volledige MVP met goede analyse maximaal 85% halen.

Deze checklist volgt de oplevercriteria voor de Ollama-demo en de agent. De voortgang van de agent, MCP-tool en benchmark staat in [VOORTGANG.md](VOORTGANG.md).

De percentages hieronder zijn de gewichten van de beoordelingscriteria. De vereisten staan in de opdracht-pdf. Bewaar het lesmateriaal in een eigen lokale map buiten Git.

## 1. Recepten en chunking · 25%

- [x] Maak vijf voorbeeldrecepten en een lokale LlamaIndex-vectorindex.
- [x] Breid de agentdataset uit naar 30–50 gevarieerde recepten met ingrediënten, stappen, kooktijd, dieetlabels en herkomst. De agent gebruikt 36 recepten.
- [x] Vergelijk tokengebaseerde chunking met splitsen per receptsectie op dezelfde vragen. Zie de resultaten en foutanalyse in het [projectrapport](RAPPORT.md#receptendataset-en-chunking).

## 2. Agent en MCP · 35%

- [ ] Bouw een LangGraph-workflow die de vraag en tussenresultaten bijhoudt. Laat het model kiezen tussen recepten opzoeken, een tool gebruiken en gewoon antwoorden.
  - [x] De vier lokale routes werken samen met de interface, brondata en MCP-tool. De live Groq-proef op drie proefrecepten toont twee routeringsfouten. Zie het [projectrapport](RAPPORT.md#27-november-2026--live-groq--en-ragas-meting).
- [ ] Maak één lokale MCP-tool die hoeveelheden schaalt op basis van het aantal porties. Test de berekening en ongeldige invoer.
- [ ] Test alle routes. Combineer ook beide stappen in één vraag, bijvoorbeeld “Zoek de chili en schaal het recept naar zes porties.”
  - [x] Herhaalbare integratiecheck voor persoon 1 + 2 + 4: tien zoekvragen, alle 36 recepten herschalen, een losse schaalvraag, chat en drie ongeldige/onvolledige vragen.

## 3. Evaluatie · 20%

- [x] Leg 20 controlevragen vast en controleer de referenties tegen de recepten en de portieberekeningen.
- [x] Meet beide chunkmethodes lokaal en controleer per vraag de route, opgehaalde bronnen, tooluitkomst en het antwoord.
- [x] Meet Context Precision, Context Recall en Faithfulness live met Ragas en vergelijk de antwoorden met de referenties. Ragas scoorde negen van de elf zoekvragen per methode op de drie proefrecepten. De [foutanalyse](RAPPORT.md#27-november-2026--live-groq--en-ragas-meting) behandelt de overige vragen.
- [x] Breid de agent-evaluatie uit met vragen over de nieuwe recepten. Controleer ook of de agent het juiste recept ophaalt als het gevraagde detail ontbreekt.
- [x] Herhaal de live meting op de 36 recepten. Ragas scoorde tien van twaalf beantwoordbare zoekvragen per methode. Beide antwoorden meldden terecht dat de yoghurtcakebron geen bakvormmaat vermeldt. [Uitgebreide evaluatie](RAPPORT.md#27-november-2026--evaluatie-met-36-recepten)

## 4. Inference, metingen en lokale interface · 10%

- [x] Sluit Groq aan met een beschikbaar model op het gratis plan. De live evaluatie gebruikte `openai/gpt-oss-20b`. [Projectkeuzes](PROJECTKEUZES.md)
- [x] Meet inputtokens, outputtokens, totale antwoordtijd en tijd tot de eerste token (TTFT) in de live agentbenchmark. TTFT is gemeten voor de 22 gestreamde antwoorden. [Live meetverslag](RAPPORT.md#27-november-2026--live-groq--en-ragas-meting)
- [x] Maak een eenvoudige lokale interface met gesprekken, opgehaalde tekststukken, MCP-toolcalls en beschikbare live metingen.
  - [x] Bouw het scherm in `chef_ui.py` met vraag/antwoord, bronfragmenten, toolinvoer/-uitvoer en beschikbare metingen na afloop; zie [persoon 4](LOKALE-INTERFACE.md).
  - [x] Voeg expliciete meldingen voor ontbrekende metingen en een gemarkeerde gesimuleerde voorbeeldmodus toe; controleer die met AppTest.
  - [x] Controleer de echte lokale zoek- en schaalvraag via AppTest: curryfragment met 420 ml water, daarna MCP-resultaat 735 ml voor 7 porties.
  - [x] Controleer ook de 33 nieuwe recepten; de voorbeeldmodus kiest de curry op ID en blijft werken bij een andere datasetvolgorde.
  - [x] Controleer echte Groq-metingen en TTFT bij de zoekdemo (4 porties) en modeltokens bij de schaalvraag (735 ml water voor 7 porties).
  - [x] Toon afgeronde tussenstappen tijdens de aanvraag en bewaar voltooide bronnen/metingen bij fouten; voeg hersteladvies en opnieuw proberen toe.
  - [x] Controleer de interface visueel in Chrome; toon exacte toolinvoer/-uitvoer en maak een broncontrole voor de bekende dubbeltelling bij de watervraag.
  - [x] Leg de demostappen en uitleg voor de verdediging vast in [de handleiding](LOKALE-INTERFACE.md).
  - [ ] Oefen de demo en code-uitleg zelf en rond de eigen review/GenAI-verantwoording af. Het modelantwoord verschijnt na de antwoordstap; losse teksttokens worden niet op het scherm gestreamd.

## 5. Proces en GenAI · 10%

- [ ] Vul het [projectrapport](RAPPORT.md) bij na elke fase en na feedback.
- [ ] Controleer het GenAI-beleid van de opleiding en maak de verantwoording af.
- [ ] Oefen de demo en code-uitleg zonder AI. Toon een foutgeval en leg uit hoe je vaststelde waar het misliep.
