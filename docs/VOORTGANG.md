# Flavor Chef

[Terug naar de README](../README.md). Voer alle commando's hieronder uit vanuit de repository-root.

## 19 november 2026

Flavor Chef is een kookassistent die recepten opzoekt en ingrediënthoeveelheden herschaalt. De huidige versie werkt lokaal via PowerShell.

**27 november 2026.** De broncode, proefrecepten, testvragen en lokale benchmark staan in deze repository. Bouw na het klonen de zoekindexen op met de onderstaande instructies.

### Eerste referentiemeting met drie proefrecepten

- **Receptendataset.** Deze referentiemeting gebruikte de eerste drie proefrecepten van Health Canada. Het gaat om kikkererwten-groentecurry, lasagne uit de slowcooker en aardbeienpannenkoeken.
- **Recepten zoeken.** `recipe_search.py` maakt met LlamaIndex en een meertalig FastEmbed-model twee lokale Qdrant-indexen. Splitsen op tokenlengte levert 17 fragmenten op. Splitsen per receptonderdeel levert 20 fragmenten op. Beide indexen geven fragmenten met een bronlink en een overeenkomstscore terug.
- **Agent en MCP.** `chef_agent.py` gebruikt LangGraph voor de gespreksroute, receptzoekroute, directe rekentoolroute en de gecombineerde zoek- en rekentoolroute. `scale_server.py` biedt de MCP-tool `scale_ingredients` via stdio aan. De agent rekende onder meer 420 ml water voor vier porties om naar 735 ml voor zeven porties.
- **Evaluatie.** Deze referentiemeting bevat 18 vragen met verwachte routes, referentieantwoorden en waar relevant controleerbare bronfragmenten of MCP-uitkomsten. `evaluate_chef.py` vergelijkt de twee chunkmethodes. De volledige lokale referentiemeting staat in `reports/baseline.json`.
- **Telemetrie.** `--telemetry` toont de responstijd van de agent. Met `--groq` registreert de code ook prompttokens, antwoordtokens en de tijd tot het eerste zichtbare antwoordfragment. De latere live Groq- en Ragas-proef op de drie proefrecepten staat in het [projectrapport](RAPPORT.md#eerste-proef-met-drie-recepten).

### Lokale referentiemeting

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
.\.venv\Scripts\python.exe chef_agent.py "Reken 250 g om naar kg" --trace
.\.venv\Scripts\python.exe evaluate_chef.py --output reports/local.json
```

`reports/local.json` blijft buiten Git. De bestaande `reports/baseline.json` is de bewaarde referentiemeting; vervang die alleen bewust volgens de [onderhoudsafspraken](../CONTRIBUTING.md).

De meetuitvoer bevat per vraag de referentie, gekozen route, geordende bronfragmenten, MCP-uitkomst en het antwoord. `failure_stage` markeert de eerste vastgestelde foutstap. Voor de bekende regressies controleert de live benchmark ook enkele antwoordfeiten. Lees gegenereerde antwoorden naast de referentie en bronfragmenten om andere inhoudelijke afwijkingen te vinden.

### Live benchmark met Groq en Ragas

Stel `GROQ_API_KEY` lokaal in als omgevingsvariabele. Bij deze benchmark ontvangen de Groq-modellen de testvragen, opgehaalde receptfragmenten, referenties en gegenereerde antwoorden die nodig zijn voor de metrieken.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-eval.txt
.\.venv\Scripts\python.exe recipe_search.py build
.\.venv\Scripts\python.exe evaluate_chef.py --groq --output reports/mvp-afwerking-groq.json
$env:RAGAS_JUDGE_MODEL = 'qwen/qwen3.8-27b'
.\.venv\Scripts\python.exe evaluate_chef.py --score-report reports/mvp-afwerking-groq.json --output reports/mvp-afwerking-ragas.json
```

Het ingestelde beoordelaarsmodel is hetzelfde als bij de [nulmeting op 36 recepten](RAPPORT.md#evaluatie-met-36-recepten). `scored` en `total` geven het aantal gescoorde en verwachte bronvragen per metriek aan. De eerste stap bewaart de live antwoorden, bronnen en agentmetingen. De tweede beoordeelt de bewaarde vragen voor beide strategieën om beurten en schrijft na elke beoordeling de voortgang. Bij onvolledige dekking eindigt ze met code 2. Herneem met hetzelfde beoordelaarsmodel en geef het Ragas-bestand als invoer én uitvoer mee. De opgeslagen scores, antwoorden en bronfragmenten blijven behouden. Gebruik `--groq --case curry-water --case lasagne-ricotta` voor een korte live agentcontrole. De meetuitvoer blijft lokaal. [Groq-limieten](https://console.groq.com/docs/rate-limits)

Bij een Groq-limiet kan dezelfde agentuitvoer lokaal worden beoordeeld met Ragas. Start Ollama en zorg dat `qwen3.5:4b-q4_K_M` beschikbaar is. Gebruik een eigen scorebestand per beoordelaar. Voor de lokale beoordelingsstap volstaat de eerder opgeslagen Groq-uitvoer. [Ollama-compatibiliteit](https://docs.ollama.com/api/openai-compatibility)

```powershell
$env:RAGAS_JUDGE_MODEL = 'qwen3.5:4b-q4_K_M'
.\.venv\Scripts\python.exe evaluate_chef.py --score-report reports/mvp-afwerking-groq.json --ollama-judge --output reports/mvp-afwerking-ragas-ollama.json
```

### Uitgebreide receptendataset

De agent gebruikt 36 recepten. Bouw de zoekindexen opnieuw met `recipe_search.py build` wanneer de recepten of de indexindeling wijzigen. De [vaste agentbenchmark](../data/evaluation.json) bevat 20 vragen. `python -m scripts.compare_chunking --output reports/chunking-local.json` vergelijkt de 12 zoekvragen met positief bronbewijs en 11 aanvullende zoekvragen, zonder recept- of dieetfilter. De [bronvermeldingen](../data/README.md#herkomst-van-de-agentrecepten) en de [eerdere zoekvergelijking](RAPPORT.md#receptendataset-en-chunking) staan bij de projectdocumentatie.

### Volgende stappen

Oefen de portievraag, het herschalen van de curry, een uitgeschreven eenheidsconversie en de Broncontrole. Neem de eigen code-review en de [GenAI-verantwoording](RAPPORT.md#genai-disclosure) mee. [Draaiboek en oefenvragen](VERDEDIGING.md)
