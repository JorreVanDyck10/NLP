# Flavor Chef

## 19 november 2026

Flavor Chef is een kookassistent die recepten opzoekt en ingrediënthoeveelheden herschaalt. De huidige versie werkt lokaal via PowerShell. De code, dataset en meetresultaten staan in de lokale projectmap. Deze eerste GitHub-update bevat het overdrachtsverslag. Voor een werkende checkout heeft een opvolger ook de hieronder genoemde projectbestanden nodig.

### Gebouwd en getest

- **Receptendataset.** `data/recipes.json` bevat drie proefrecepten van Health Canada met bronlinks, porties, tijden, ingrediënten, bereidingsstappen en dieettags. Het gaat om kikkererwten-groentecurry, lasagne uit de slowcooker en aardbeienpannenkoeken.
- **Recepten zoeken.** `recipe_search.py` maakt met LlamaIndex en een meertalig FastEmbed-model twee lokale Qdrant-indexen. Splitsen op tokenlengte levert 17 fragmenten op. Splitsen per receptonderdeel levert 20 fragmenten op. Beide indexen geven fragmenten met een bronlink en een overeenkomstscore terug.
- **Agent en MCP.** `chef_agent.py` gebruikt LangGraph voor de gespreksroute, receptzoekroute, directe rekentoolroute en de gecombineerde zoek- en rekentoolroute. `scale_server.py` biedt de MCP-tool `scale_ingredients` via stdio aan. De agent rekende onder meer 420 ml water voor vier porties om naar 735 ml voor zeven porties.
- **Evaluatie.** `data/evaluation.json` bevat 18 vragen met verwachte routes, referentieantwoorden en waar relevant controleerbare bronfragmenten of MCP-uitkomsten. `evaluate_chef.py` vergelijkt de twee chunkmethodes. De volledige lokale meetuitvoer staat in `reports/baseline.json`.
- **Telemetrie.** `--telemetry` toont de responstijd van de agent. Met `--groq` registreert de code ook prompttokens, antwoordtokens en de tijd tot het eerste zichtbare antwoordfragment. De Groq- en Ragas-koppelingen zijn met gesimuleerde API-antwoorden getest. Live Ragas-scores staan nog open omdat er tijdens de bouw geen `GROQ_API_KEY` beschikbaar was.

### Lokale benchmark

| Meting | Op tokenlengte | Per receptonderdeel |
| --- | ---: | ---: |
| Verwachte route | 18/18 | 18/18 |
| Correcte MCP-uitkomst | 6/6 | 6/6 |
| Al het benodigde bewijs in de top 3 | 9/11 | 10/11 |
| Al het benodigde bewijs op plek 1 | 5/11 | 8/11 |

De vervanging voor bloemkool was aanwezig in beide indexen. Het fragment kwam op plek 6 bij splitsen op tokenlengte en op plek 7 bij splitsen per receptonderdeel. Dat is een concreet voorbeeld van een rangschikkingsprobleem.

### Uitvoeren met de projectbestanden

Voer dit vanuit de projectmap uit met Python 3.13. De eerste indexbouw haalt het embeddingmodel op.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe recipe_search.py build
.\.venv\Scripts\python.exe chef_agent.py "Schaal de curry van 4 naar 7 porties" --trace --telemetry
.\.venv\Scripts\python.exe evaluate_chef.py --output reports/baseline.json
```

### Volgende stappen

1. **Breid de dataset uit naar 30–50 recepten.** Gebruik dezelfde structuur en unieke ID's, controleer de hoeveelheden en bewaar de bronlinks. Bouw beide indexen opnieuw en voeg representatieve testvragen over de nieuwe recepten toe.
2. **Voer de live Ragas-benchmark uit.** Installeer `requirements-eval.txt`, stel `GROQ_API_KEY` in als omgevingsvariabele en voer `python evaluate_chef.py --ragas --output reports/ragas.json` uit in de virtuele omgeving. Vergelijk Context Precision, Context Recall en Faithfulness per strategie. Controleer ook de token- en tijdmetingen.
3. **Onderzoek de zoekfouten opnieuw met de grotere dataset.** Gebruik de vraag over bloemkool als regressievoorbeeld. Vergelijk de positie van het juiste fragment en meet bij wijzigingen ook de invloed op het aantal contexttokens en de responstijd.
4. **Bouw de lokale interface zodra het volledige opleverpunt aan bod komt.** De opdracht-pdf vraagt om een interface die gesprekken, opgehaalde fragmenten, MCP-aanroepen en telemetrie toont.
