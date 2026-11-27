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
- **Telemetrie.** `--telemetry` toont de responstijd van de agent. Met `--groq` registreert de code ook prompttokens, antwoordtokens en de tijd tot het eerste zichtbare antwoordfragment. De latere live Groq- en Ragas-proef op de drie proefrecepten staat in het [projectrapport](RAPPORT.md#27-november-2026--live-groq--en-ragas-meting).

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
.\.venv\Scripts\python.exe evaluate_chef.py --output reports/local.json
```

`reports/local.json` blijft buiten Git. De bestaande `reports/baseline.json` is de bewaarde referentiemeting; vervang die alleen bewust volgens de [onderhoudsafspraken](../CONTRIBUTING.md).

De meetuitvoer bevat per vraag de referentie, gekozen route, geordende bronfragmenten, MCP-uitkomst en het antwoord. `failure_stage` markeert de eerste vastgestelde foutstap. De automatische controle op `answer` signaleert ontbrekende tekst. Voor inhoudelijke beoordeling vergelijk je het antwoord met de referentie en de opgehaalde fragmenten.

### Live benchmark met Groq en Ragas

Stel `GROQ_API_KEY` lokaal in als omgevingsvariabele. Bij deze benchmark ontvangen de Groq-modellen de testvragen, opgehaalde receptfragmenten, referenties en gegenereerde antwoorden die nodig zijn voor de metrieken.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-eval.txt
.\.venv\Scripts\python.exe recipe_search.py build
$env:RAGAS_JUDGE_MODEL = 'qwen/qwen3.8-27b'
.\.venv\Scripts\python.exe evaluate_chef.py --ragas --output reports/ragas-expanded.json
```

Het ingestelde beoordelaarsmodel hoort bij de actuele evaluatie op 36 recepten. `scored` en `total` geven het aantal gescoorde en verwachte zoekvragen per metriek aan. De meetuitvoer blijft lokaal. Bij tijdelijke Groq-gebruikslimieten wacht de benchmark voor een nieuwe poging, waardoor de meting langer kan duren. [Resultaten](RAPPORT.md#27-november-2026--evaluatie-met-36-recepten) · [Groq-limieten](https://console.groq.com/docs/rate-limits)

### Uitgebreide receptendataset

De agent gebruikt nu 36 recepten. Bouw na een wijziging in de dataset beide indexen opnieuw met `recipe_search.py build`. De [actuele agentbenchmark](../data/evaluation.json) bevat 20 vragen. `python -m scripts.compare_chunking --output reports/chunking-local.json` meet met de huidige testset alleen de 12 zoekvragen met positief bronbewijs en de 7 aanvullende zoekvragen. De [bronvermeldingen](../data/README.md#herkomst-van-de-agentrecepten) en de resultaten van de [eerdere zoekvergelijking](RAPPORT.md#receptendataset-en-chunking) staan bij de projectdocumentatie.

### Volgende stappen

**Integratie persoon 1 + 2 + 4 (27 november).** De uitgebreide dataset is samengevoegd met de bestaande agent, MCP-tool en interface. `python scripts/test_integration.py` controleert echte lokale scenario's; `python scripts/test_chef_ui.py` controleert zeven schermscenario's zonder modellen. Gebruikte technieken, redenen en verificatiestatus staan in [het rapport](RAPPORT.md#gebruikt-en-waarom).

1. **Controleer de foutgevallen opnieuw bij agentwijzigingen.** Gebruik de 20 vragen om te zien of de routerings-, zoek- en antwoordfouten zich nog voordoen. [Evaluatie met 36 recepten](RAPPORT.md#27-november-2026--evaluatie-met-36-recepten)
2. **Controleer de bestaande interface met live Groq en oefen de demo.** Gesprekken, bronfragmenten, MCP en beschikbare metingen zijn zichtbaar. Tokenmetingen en TTFT via de interface blijven te controleren. De interface toont metingen na afloop. Zie [de handleiding](LOKALE-INTERFACE.md).
