# Flavor Chef

[Terug naar de README](../README.md). Voer alle commando's hieronder uit vanuit de repository-root.

## 19 november 2026

Flavor Chef is een kookassistent die recepten opzoekt en ingrediënthoeveelheden herschaalt. De huidige versie werkt lokaal via PowerShell.

**27 november 2026.** De broncode, proefrecepten, testvragen en lokale benchmark staan in deze repository. Bouw na het klonen de zoekindexen op met de onderstaande instructies.

### Gebouwd en getest

- **Receptendataset.** `data/recipes.json` bevat drie proefrecepten van Health Canada met bronlinks, porties, tijden, ingrediënten, bereidingsstappen en dieettags. Het gaat om kikkererwten-groentecurry, lasagne uit de slowcooker en aardbeienpannenkoeken.
- **Recepten zoeken.** `recipe_search.py` maakt met LlamaIndex en een meertalig FastEmbed-model twee lokale Qdrant-indexen. Splitsen op tokenlengte levert 17 fragmenten op. Splitsen per receptonderdeel levert 20 fragmenten op. Beide indexen geven fragmenten met een bronlink en een overeenkomstscore terug.
- **Agent en MCP.** `chef_agent.py` gebruikt LangGraph voor de gespreksroute, receptzoekroute, directe rekentoolroute en de gecombineerde zoek- en rekentoolroute. `scale_server.py` biedt de MCP-tool `scale_ingredients` via stdio aan. De agent rekende onder meer 420 ml water voor vier porties om naar 735 ml voor zeven porties.
- **Evaluatie.** `data/evaluation.json` bevat 18 vragen met verwachte routes, referentieantwoorden en waar relevant controleerbare bronfragmenten of MCP-uitkomsten. `evaluate_chef.py` vergelijkt de twee chunkmethodes. De volledige lokale meetuitvoer staat in `reports/baseline.json`.
- **Telemetrie.** `--telemetry` toont de responstijd van de agent. Met `--groq` registreert de code ook prompttokens, antwoordtokens en de tijd tot het eerste zichtbare antwoordfragment. De live Groq- en Ragas-resultaten staan in het [projectrapport](RAPPORT.md#27-november-2026--live-groq--en-ragas-meting).

### Lokale referentiemeting

| Meting | Op tokenlengte | Per receptonderdeel |
| --- | ---: | ---: |
| Verwachte route | 18/18 | 18/18 |
| Correcte MCP-uitkomst | 6/6 | 6/6 |
| Al het benodigde bewijs in de top 3 | 9/11 | 10/11 |
| Al het benodigde bewijs op plek 1 | 5/11 | 8/11 |

De vervanging voor bloemkool was aanwezig in beide indexen. Het fragment kwam op plek 6 bij splitsen op tokenlengte en op plek 7 bij splitsen per receptonderdeel. Dat is een concreet voorbeeld van een rangschikkingsprobleem.

De resultaten van de herhaling, inclusief de controle van de 18 referenties en de foutanalyse per methode, staan in het [projectrapport](RAPPORT.md#27-november-2026--werkpakket-3-evaluatie-en-foutanalyse).

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

De lokale uitvoer bevat per vraag de referentie, de gekozen route, de geordende bronfragmenten, de MCP-uitkomst en het antwoord. `failure_stage` markeert de eerste vastgestelde foutstap. De controle op `answer` signaleert een ontbrekend antwoord. Voor inhoudelijke beoordeling vergelijk je het gegenereerde antwoord met de referentie en de opgehaalde fragmenten.

### Live benchmark met Groq en Ragas

Stel `GROQ_API_KEY` lokaal in als omgevingsvariabele. Bij deze benchmark ontvangen de Groq-modellen de testvragen, opgehaalde receptfragmenten, referenties en gegenereerde antwoorden die nodig zijn voor de metrieken.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-eval.txt
.\.venv\Scripts\python.exe recipe_search.py build
.\.venv\Scripts\python.exe evaluate_chef.py --ragas --output reports/ragas.json
```

`scored` en `total` geven het aantal gescoorde en verwachte zoekvragen per metriek aan. De meetuitvoer blijft lokaal. Bij tijdelijke Groq-gebruikslimieten wacht de benchmark voor een nieuwe poging, waardoor de meting langer kan duren. [Groq-limieten](https://console.groq.com/docs/rate-limits)

### Volgende stappen

1. **Breid de dataset uit naar 30–50 recepten.** Gebruik dezelfde structuur en unieke ID's, controleer de hoeveelheden en bewaar de bronlinks. Bouw beide indexen opnieuw en voeg representatieve testvragen over de nieuwe recepten toe.
2. **Onderzoek de zoekfouten opnieuw met de grotere dataset.** Gebruik de vraag over bloemkool als regressievoorbeeld. Vergelijk de positie van het juiste fragment en meet bij wijzigingen ook de invloed op het aantal contexttokens en de responstijd.
3. **Bouw de lokale interface zodra het volledige opleverpunt aan bod komt.** De opdracht-pdf vraagt om een interface die gesprekken, opgehaalde fragmenten, MCP-aanroepen en telemetrie toont.
