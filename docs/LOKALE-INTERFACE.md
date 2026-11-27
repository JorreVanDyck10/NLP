# Persoon 4: lokale interface en demo

[Terug naar de README](../README.md)

Dit werkpakket toont de bestaande agent in een lokale Streamlit-interface. De code staat in `chef_ui.py`; routering, zoeken en de MCP-rekentool blijven in hun bestaande bestanden. Streamlit is gekozen omdat invoer, gespreksberichten en uitklapbare details vanuit Python kunnen worden getoond, zonder een aparte JavaScript-app.

## Installeren en starten

Open PowerShell in de repository-root met Python 3.13:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ui.txt
.\.venv\Scripts\python.exe recipe_search.py build
.\.venv\Scripts\python.exe -m streamlit run chef_ui.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Open de lokale URL die Streamlit afdrukt, normaal `http://127.0.0.1:8501`. Sluit af met Ctrl+C in de terminal. De eerste indexbouw downloadt het embeddingmodel. Bouw de index opnieuw na receptwijzigingen. Verwijder of vervang geen actieve index terwijl een andere gebruiker die gebruikt.

De **voorbeeldmodus** heeft geen agent, modellen, index of API-sleutel nodig. Hiervoor volstaat een omgeving met `streamlit==1.45.0`; sla de indexbouw dan over. Gebruik de knoppen Zoekvraag en Schaalvraag. Antwoorden komen uit vaste voorbeelden en de tijden, scores en tokens zijn uitdrukkelijk **gesimuleerd**. Deze modus bewijst de schermwerking, niet de werking van RAG, Groq of MCP.

## Wat het scherm toont

- **Gesprek:** de vraag en het antwoord blijven per browsersessie zichtbaar. Eerdere berichten worden niet aan de agent doorgegeven: iedere vraag is zelfstandig. Noem het recept dus opnieuw bij een vervolgvraag. Gesprek wissen verwijdert de zichtbare geschiedenis.
- **Gevolgde stappen:** de trace van de agent, bijvoorbeeld routering, opgehaalde fragmenten en MCP-tool.
- **Bronfragmenten:** titel, receptonderdeel, tekst, overeenkomstscore en bronlink. De score is geen zekerheid dat een antwoord klopt.
- **MCP-aanroep:** toolnaam en resultaat. De getoonde invoer wordt afgeleid uit dezelfde vraag/state en brondata als de agent; er wordt geen netwerk- of protocol-log onderschept. De live berekening gebeurt in `scale_server.py`.
- **Metingen:** agenttijd, input- en outputtokens en de afzonderlijke modelaanroepen. TTFT betekent de tijd tot het eerste zichtbare tekstfragment van het model. De router streamt geen tekst en heeft daarom geen TTFT-meting. De interface toont de metingen na afloop, en streamt de tussenstappen nog niet tijdens het uitvoeren.

In **Lokaal** kiest bestaande Python-logica de route en geeft een zoekvraag de bronfragmenten terug. Er is geen genererend taalmodel: tokens en TTFT staan op **Niet gemeten**, niet op nul. Het embeddingmodel wordt wel gebruikt voor zoeken. In **Groq** worden de vraag en geselecteerde fragmenten naar Groq gestuurd. Stel `GROQ_API_KEY` buiten Git in als omgevingsvariabele vóór het starten. De interface leest dezelfde instellingen als de agent; ze slaat de sleutel niet op in de chat. Ontbrekende of gedeeltelijke modelmetingen worden zichtbaar gemeld.

## Demo van begin tot eind

1. Kies **Lokaal** en klik **Zoekvraag**: “Hoeveel water gaat er in totaal in de curry?” Controleer de route `search` en open Bronfragmenten. Zoek naar **420 ml water** in het juiste curryrecept. De lokale agent toont fragmenten; voor een geformuleerd modelantwoord kies je Groq zodra een sleutel beschikbaar is.
2. Klik **Schaalvraag**: “Schaal de curry van 4 naar 7 porties.” Controleer `scale_recipe`, de curryfragmenten en `scale_ingredients`. De invoer bevat 4 en 7 porties en 420 ml water; de tooluitvoer hoort **735 ml water** te bevatten. Berekening: `420 × 7 / 4 = 735`. Controleer ook bloemkool: `500 × 7 / 4 = 875 ml`.
3. Controleer bij beide antwoorden de agenttijd en de uitleg over ontbrekende tokens. Een echt uitgevoerde lokale aanvraag heeft een gemeten tijd, maar geen modeltokenmetingen.
4. Gebruik **Voorbeeld (gesimuleerd)** om dezelfde schermonderdelen met ingevulde modelmetingen te laten zien. Benoem tijdens je verdediging dat dit voorbeeldwaarden zijn.
5. Kies Groq zonder sleutel om de foutmelding te controleren. Test een echte Groq-aanvraag pas met een beschikbare sleutel. Controleer dan tokenvelden en de afzonderlijke modelaanroepen; verzin geen ontbrekende metingen.

Bij een verkeerd antwoord kijk je eerst naar Bronfragmenten. Ontbreekt de juiste informatie daar, dan ligt het probleem vóór het formuleren van het antwoord. De interface repareert die zoekfout niet; geef het voorbeeld door aan persoon 1 of 3. Problemen in routering, Groq of de rekentool horen bij persoon 2.

## Zelf kunnen uitleggen

“Mijn interface roept dezelfde agent aan als de terminal. Ik bewaar per vraag het antwoord en de tussenresultaten. Daardoor kan ik zien of een fout bij zoeken, rekenen of antwoorden ontstaat. De rekentool vermenigvuldigt hoeveelheden met het nieuwe aantal porties gedeeld door het oude aantal. Zonder modelaanroep zijn er geen gemeten modeltokens. Ik toon daarom ‘Niet gemeten’. De gesimuleerde modus dient om de schermen te demonstreren en is geen bewijs van een werkende modelkoppeling.”

Lesbasis: PowerPoint 1, slide 69 over de gedeelde workflow-state, slides 72–73 over MCP en de rekentool, en slides 82–83 over het verschil tussen een demo en evaluatie en het controleren van de hele keten. Deze slides zijn visueel bekeken omdat de tekstextractie vooral afbeeldingen opleverde. PowerPoint 2 en 3 zijn niet gebruikt.

## Controles

```powershell
.\.venv\Scripts\python.exe scripts/test_chef_ui.py
python scripts/check_repository.py
git diff --check
```

De zeven interfacechecks gebruiken Streamlits AppTest en controleren voorbeelden, geschiedenis wissen, herkomst bij moduswissels, een ontbrekende sleutel, ontbrekende/gedeeltelijke tokenmetingen, een mislukte agentaanroep en een andere volgorde van de recepten. Ze downloaden geen modellen en draaien ook in GitHub Actions. De installatie en basis van AppTest volgen de [officiële Streamlit-documentatie](https://docs.streamlit.io/develop/concepts/app-testing/get-started).

Controleer de echte lokale keten van persoon 1, 2 en 4 met:

```powershell
.\.venv\Scripts\python.exe scripts/test_integration.py
```

Deze integratiecheck bouwt beide indexen indien nodig en kan het embeddingmodel downloaden. Vier tests controleren elf scenario's: zoeken en herschalen voor elk van de drie huidige recepten, een losse schaalvraag, een begroeting en drie ongeldige/onvolledige schaalvragen. De controles gebruiken de echte lokale zoekfunctie en MCP-server, zonder Groq. Nieuwe recepten vragen ook om representatieve nieuwe scenario's; deze check bewijst niet de juistheid van een toekomstige uitgebreide dataset.

Zie [het projectrapport](RAPPORT.md) voor de werkelijk uitgevoerde controles en beperkingen. De opdracht-pdf en het GenAI-beleid zijn hier nog niet beschikbaar; de eisen voor dit werkpakket komen uit de aangeleverde taakverdeling. Persoon 4 moet de code, demonstratie en AI-verantwoording nog zelf nalopen.
