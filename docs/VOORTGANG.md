# Flavor Chef

[Terug naar de README](../README.md). Voer alle commando's hieronder uit vanuit de repository-root.

## 19 november 2026

Flavor Chef is een kookassistent die recepten opzoekt en ingrediënthoeveelheden herschaalt. De huidige versie werkt lokaal via PowerShell.

**27 november 2026.** De broncode, proefrecepten, testvragen en lokale benchmark staan in deze repository. Bouw na het klonen de zoekindexen op met de onderstaande instructies.

### Eerste referentiemeting met drie proefrecepten

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
.\.venv\Scripts\python.exe evaluate_chef.py --output reports/local.json
```

`reports/local.json` blijft buiten Git. De bestaande `reports/baseline.json` is de bewaarde referentiemeting; vervang die alleen bewust volgens de [onderhoudsafspraken](../CONTRIBUTING.md).

### Uitgebreide receptendataset

De agent gebruikt nu 36 recepten. Bouw na een wijziging in de dataset beide indexen opnieuw met `recipe_search.py build`. Voer `python -m scripts.compare_chunking --output reports/chunking-local.json` uit in de virtuele omgeving om de lokale zoekvergelijking te herhalen. De [bronvermeldingen](../data/README.md#herkomst-van-de-agentrecepten) en de [resultaten](RAPPORT.md#receptendataset-en-chunking) staan bij de projectdocumentatie.

### Volgende stappen

1. **Voer de live Ragas-benchmark uit.** Installeer `requirements-eval.txt`, stel `GROQ_API_KEY` in als omgevingsvariabele en voer `python evaluate_chef.py --ragas --output reports/ragas.json` uit in de virtuele omgeving. Vergelijk Context Precision, Context Recall en Faithfulness per strategie. Controleer ook de token- en tijdmetingen.
2. **Bouw de lokale interface zodra het volledige opleverpunt aan bod komt.** De opdracht-pdf vraagt om een interface die gesprekken, opgehaalde fragmenten, MCP-aanroepen en telemetrie toont.
