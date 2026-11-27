# Persoon 4: lokale interface en demo

[Terug naar de README](../README.md)

Dit werkpakket toont de bestaande agent in een lokale Streamlit-interface. De code staat in `chef_ui.py`. De agent biedt daarnaast een optionele callback voor de volledige state na iedere stap en bewaart de exacte MCP-invoer. Routering, zoeken en rekenen blijven dezelfde agentfuncties gebruiken. Streamlit is gekozen omdat invoer, gespreksberichten en uitklapbare details vanuit Python kunnen worden getoond, zonder een aparte JavaScript-app.

De technische oplevering omvat een zoekdemo, een schaalvraag, echte Groq-metingen, zichtbare tussenstappen, foutmeldingen en een broncontrole als foutvoorbeeld. Het zelf oefenen en mondeling verdedigen blijft werk van persoon 4.

## Installeren en starten

Open PowerShell in de repository-root met Python 3.13:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ui.txt
.\.venv\Scripts\python.exe recipe_search.py build
.\.venv\Scripts\python.exe -m streamlit run chef_ui.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Open de lokale URL die Streamlit afdrukt, normaal `http://127.0.0.1:8501`. Sluit af met Ctrl+C in de terminal. De eerste indexbouw downloadt het embeddingmodel. Bouw de index opnieuw na receptwijzigingen. Voer indexbouw, benchmark en integratiecheck na elkaar uit en laat tijdens die controles geen andere aanvraag dezelfde lokale index gebruiken: Qdrant local laat één proces tegelijk toe.

Voor een volledige modeldemo kies je **Groq**. Vul je sleutel in het gemaskeerde veld in de zijbalk in, of stel `GROQ_API_KEY` vóór het starten in als omgevingsvariabele. Een ingevulde sleutel blijft alleen in die browsersessie, wordt niet in berichten of meetrapporten gezet en kan met **Ingevulde sleutel wissen** worden verwijderd. Een omgevingssleutel blijft beschikbaar totdat de server wordt gestopt. `.env` en `.env.*` zijn al uitgesloten van Git; de interface leest een `.env`-bestand niet automatisch.

De **voorbeeldmodus** heeft geen agent, modellen, index of API-sleutel nodig. Hiervoor volstaat een omgeving met `streamlit==1.45.0`; sla de indexbouw dan over. Gebruik de knoppen Zoekvraag en Schaalvraag. Antwoorden komen uit vaste voorbeelden en de tijden, scores en tokens zijn uitdrukkelijk **gesimuleerd**. Deze modus bewijst de schermwerking, niet de werking van RAG, Groq of MCP. Broncontrole is in deze modus uitgeschakeld.

## Wat het scherm toont

- **Gesprek:** de vraag en het antwoord blijven per browsersessie zichtbaar. Eerdere berichten worden niet aan de agent doorgegeven: iedere vraag is zelfstandig. Noem het recept dus opnieuw bij een vervolgvraag. Gesprek wissen verwijdert de zichtbare geschiedenis.
- **Gevolgde stappen:** de trace van de agent, bijvoorbeeld routering, opgehaalde fragmenten en MCP-tool. De interface krijgt na iedere afgeronde graph-stap de volledige state en werkt het scherm bij. Tijdens een langlopende stap blijft de status zichtbaar.
- **Bronfragmenten:** titel, receptonderdeel, tekst, overeenkomstscore en bronlink. De score is geen zekerheid dat een antwoord klopt.
- **MCP-aanroep:** toolnaam, exacte invoer en resultaat uit de agentstate. De schaaltabel rondt af tot maximaal zes decimalen. Een conversie toont het oorspronkelijke en het omgerekende gewicht. De ruwe gegevens zijn uitklapbaar. De live berekeningen gebeuren in `scale_server.py`.
- **Metingen:** verwerkingstijd, input- en outputtokens, TTFT en de afzonderlijke modelaanroepen. TTFT betekent de tijd tot het eerste zichtbare tekstfragment bij de antwoordaanroep. Die begint ná routering en zoeken, en is dus niet de tijd vanaf het indrukken van de knop. De verwerkingstijd omvat het agenttraject en de updates aan het scherm. Tokenmetingen verschijnen zodra de betreffende modelaanroep klaar is. Het modelantwoord wordt na de antwoordstap getoond; losse teksttokens worden nog niet op het scherm gestreamd.
- **Fouten:** verkeerde sleutel, gebruikslimiet, ontbrekende index en andere uitval krijgen hersteladvies. Al voltooide bronnen, trace en modelmetingen blijven zichtbaar. Een mislukte modelaanroep levert geen verzonnen tokens op. **Opnieuw proberen** herhaalt de vraag met de huidige modus en sleutel; het eerdere foutbericht blijft in het gesprek staan.

In **Lokaal** kiest bestaande Python-logica de route en geeft een zoekvraag de bronfragmenten terug. Er is geen genererend taalmodel: tokens en TTFT staan op **Niet gemeten**, niet op nul. Het embeddingmodel wordt wel gebruikt voor zoeken. In **Groq** worden de vraag en geselecteerde fragmenten naar Groq gestuurd. De interface gebruikt dezelfde modelinstellingen als de agent. Ontbrekende of gedeeltelijke modelmetingen worden zichtbaar gemeld. Bij een schaalvraag kan Groq alleen de route kiezen en geeft de rekentool het eindantwoord: dan zijn er routetokens, maar is een TTFT voor een modelantwoord niet van toepassing.

## Demo van begin tot eind

1. Kies **Groq**, controleer dat een sleutel beschikbaar is en klik **Zoekvraag**: “Voor hoeveel porties is de kikkererwtencurry bedoeld?” Toon de route `search`, het overzichtsfragment met **Porties: 4**, het modelantwoord **4 porties** en de modelmetingen. Leg uit dat de bron het antwoord moet ondersteunen.
2. Klik **Schaalvraag**: “Schaal de curry van 4 naar 7 porties.” Controleer `scale_recipe`, de curryfragmenten en `scale_ingredients`. Open MCP-aanroep: de waterregel moet van **420 ml** naar **735 ml** gaan. Berekening: `420 × 7 / 4 = 735`. Controleer ook bloemkool: `500 × 7 / 4 = 875 ml`. TTFT antwoord staat hier terecht op Niet gemeten: de tool geeft het antwoord, zonder gestreamde modelantwoordaanroep.
3. Typ “Reken 250 g om naar kg.” Controleer `convert_units` en het resultaat **0,25 kg**. Open MCP-aanroep om de invoer en uitvoer te tonen.
4. Klik **Broncontrole** voor “Hoeveel water gaat er in totaal in de curry?” De referentie is **420 ml**. Daarvan gaat 45 ml in de pasta en blijft 375 ml over voor later. Gebruik de oude **795 ml** uit het [meetverslag](RAPPORT.md#evaluatie-met-36-recepten) voor de diagnose. De agent gebruikt nu de opgehaalde ingrediëntregel rechtstreeks bij deze expliciete totaalvraag. Open de fragmenten en wijs aan welke regel het totaal bevat.
5. Gebruik **Lokaal** als terugvaloptie. Zoekvragen tonen opgehaalde bronfragmenten en de verwerkingstijd. Porties schalen en g ↔ kg omrekenen gebruiken dezelfde MCP-server.
6. Toon de foutafhandeling met een ontbrekende of ongeldige sleutel en gebruik daarna Opnieuw proberen met een werkende sleutel. Test dit alleen als je de gewenste fout bewust wilt demonstreren; een gesimuleerde fout bewijst geen actuele storing bij Groq.
7. Wis het gesprek en een eventueel ingevulde sessiesleutel na de demo.

Bij een verkeerd antwoord kijk je eerst naar Bronfragmenten. Ontbreekt de juiste informatie daar, dan ligt het probleem vóór het formuleren van het antwoord. De interface repareert die zoekfout niet; geef het voorbeeld door aan persoon 1 of 3. Problemen in routering, Groq of de rekentool horen bij persoon 2.

## Zelf kunnen uitleggen

“Mijn interface gebruikt dezelfde agent als de terminal en krijgt na iedere afgeronde stap de tussenstand. Daardoor kan ik zien of een fout bij zoeken, rekenen of antwoorden ontstaat. De rekentool vermenigvuldigt hoeveelheden met het nieuwe aantal porties gedeeld door het oude aantal. De tokens komen uit de modelrespons. TTFT meet alleen hoe lang het antwoordmodel op zijn eerste tekstfragment liet wachten. Zonder zo'n modelaanroep toon ik ‘Niet gemeten’. Met het watervoorbeeld kan ik aantonen dat juiste bronnen toch een fout modelantwoord kunnen opleveren.”

Lesbasis: PowerPoint 1, slide 69 over de gedeelde workflow-state, slides 72–73 over MCP en de rekentool, en slides 82–83 over het verschil tussen een demo en evaluatie en het controleren van de hele keten. Deze slides zijn visueel bekeken omdat de tekstextractie vooral afbeeldingen opleverde. PowerPoint 2 en 3 zijn niet gebruikt.

## Controles

```powershell
.\.venv\Scripts\python.exe scripts/test_chef_ui.py
.\.venv\Scripts\python.exe scripts/test_ui_groq.py
python scripts/check_repository.py
git diff --check
```

De twaalf schermchecks gebruiken Streamlits AppTest en draaien ook in GitHub Actions zonder modellen. De zeven Groq-protocoltests gebruiken gesimuleerde HTTP-responsen met de echte agent en lokale zoekfunctie. Ze controleren tokens, TTFT, foutstatussen, routecorrectie en het behouden van bronnen bij Groq- of MCP-uitval. Deze tests vereisen de agentdependencies en de index. [AppTest-documentatie](https://docs.streamlit.io/develop/concepts/app-testing/get-started)

Controleer de echte lokale keten van persoon 1, 2 en 4 met:

```powershell
.\.venv\Scripts\python.exe scripts/test_integration.py
```

Deze integratiecheck bouwt beide indexen indien nodig. Zes tests behandelen 58 scenario's, waaronder elf zoekvragen, het herschalen van alle 36 recepten, conversie in beide richtingen, ongeldige invoer en een onbekend recept. Ze gebruiken de lokale zoekfunctie en MCP-server. Bij schalen controleren ze alle hoeveelheden, eenheden, notities en ingrediënten naar smaak.

Een echte live controle van de drie demovragen kun je herhalen met:

```powershell
.\.venv\Scripts\python.exe scripts/test_ui_live.py
```

De sleutel wordt uit `GROQ_API_KEY` gelezen of verborgen gevraagd. De controle verwacht **4 porties**, **735 ml water** en **0,25 kg**. Ze schrijft de metingen zonder sleutel naar het genegeerde `reports/ui-live.json`.

Zie [het projectrapport](RAPPORT.md) voor de uitgevoerde controles. De opdracht-pdf bepaalt de scope. De eigen code-review, demonstratie en controle van het opleidingsbeleid voor GenAI staan nog open.
