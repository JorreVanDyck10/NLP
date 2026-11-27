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

- [x] Bouw een LangGraph-workflow die de tussenresultaten bijhoudt. Laat Groq een route voorstellen voor zoeken, herschalen, omrekenen of conversatie. Controleer het voorstel tegen expliciete vraaggegevens.
- [x] Test `scale_ingredients` en `convert_units` op de lokale MCP-server, inclusief ongeldige invoer en afhandeling van MCP-uitval.
- [x] Test alle routes, inclusief zoeken en schalen in één vraag. De integratiecheck herschaalt alle 36 recepten en test beide conversierichtingen en een onbekend recept.

## 3. Evaluatie · 20%

- [x] Leg 20 controlevragen vast en controleer de referenties tegen de recepten, de portieberekeningen en de g ↔ kg-conversie.
- [x] Meet beide chunkmethodes lokaal en controleer per vraag de route, opgehaalde bronnen, tooluitkomst en het antwoord.
- [x] Meet Context Precision, Context Recall en Faithfulness live met Ragas en vergelijk de antwoorden met de referenties. Ragas scoorde negen van de elf zoekvragen per methode op de drie proefrecepten. De [foutanalyse](RAPPORT.md#27-november-2026--live-groq--en-ragas-meting) behandelt de overige vragen.
- [x] Breid de agent-evaluatie uit met vragen over de nieuwe recepten. Controleer ook of de agent het juiste recept ophaalt als het gevraagde detail ontbreekt.
- [x] Herhaal de live meting op de 36 recepten. Ragas scoorde tien van twaalf beantwoordbare zoekvragen per methode. Beide antwoorden meldden terecht dat de yoghurtcakebron geen bakvormmaat vermeldt. [Uitgebreide evaluatie](RAPPORT.md#27-november-2026--evaluatie-met-36-recepten)
- [x] Controleer de vier bekende fouten op de standaardmethode na de agentwijzigingen. [MVP-meting](RAPPORT.md#27-november-2026--mvp-oplevering)

## 4. Inference, metingen en lokale interface · 10%

- [x] Sluit Groq aan met een beschikbaar model op het gratis plan. De live evaluatie gebruikte `openai/gpt-oss-20b`. [Projectkeuzes](PROJECTKEUZES.md)
- [x] Meet inputtokens, outputtokens, totale antwoordtijd en tijd tot de eerste token (TTFT) in de live agentbenchmark. TTFT is gemeten voor de 22 gestreamde antwoorden. [Live meetverslag](RAPPORT.md#27-november-2026--live-groq--en-ragas-meting)
- [x] Maak een eenvoudige lokale interface met gesprekken, opgehaalde tekststukken, MCP-toolcalls en beschikbare live metingen.
  - [x] Bouw het scherm in `chef_ui.py` met vraag/antwoord, bronfragmenten, toolinvoer/-uitvoer en beschikbare metingen na afloop; zie [persoon 4](LOKALE-INTERFACE.md).
  - [x] Voeg expliciete meldingen voor ontbrekende metingen en een gemarkeerde gesimuleerde voorbeeldmodus toe; controleer die met AppTest.
  - [x] Controleer de echte lokale zoek- en schaalvraag via AppTest: curryfragment met 420 ml water, daarna MCP-resultaat 735 ml voor 7 porties.
  - [x] Controleer ook de 33 nieuwe recepten; de voorbeeldmodus kiest de curry op ID en blijft werken bij een andere datasetvolgorde.
  - [x] Controleer echte Groq-metingen en TTFT bij de zoekdemo (4 porties) en modeltokens bij de schaalvraag (735 ml water voor 7 porties).
  - [x] Controleer g ↔ kg via MCP in de live interface, met exacte invoer, uitvoer en de beschikbare Groq-metingen.
  - [x] Toon afgeronde tussenstappen tijdens de aanvraag en bewaar voltooide bronnen/metingen bij fouten; voeg hersteladvies en opnieuw proberen toe.
  - [x] Controleer de interface visueel in Chrome; toon exacte toolinvoer/-uitvoer en maak een broncontrole voor de bekende dubbeltelling bij de watervraag.
  - [x] Leg de demostappen en uitleg voor de verdediging vast in [de handleiding](LOKALE-INTERFACE.md).
  - [ ] Oefen de demo en code-uitleg zelf en rond de eigen review/GenAI-verantwoording af. Het modelantwoord verschijnt na de antwoordstap; losse teksttokens worden niet op het scherm gestreamd.

## 5. Proces en GenAI · 10%

- [ ] Vul het [projectrapport](RAPPORT.md) bij na elke fase en na feedback.
- [ ] Controleer het GenAI-beleid van de opleiding en maak de verantwoording af.
- [ ] Oefen de demo en code-uitleg zonder AI. Toon een foutgeval en leg uit hoe je vaststelde waar het misliep.
