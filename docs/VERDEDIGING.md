# Flavor Chef | Oefenen voor de verdediging

[Terug naar de documentatie](README.md) · [Interface starten](LOKALE-INTERFACE.md) · [Meetresultaten](RAPPORT.md) · [GenAI-verantwoording](RAPPORT.md#genai-disclosure)

## Demo in drie minuten

Oefen één keer in Groq-modus en één keer in lokale modus. Houd het [verslag van de eerdere fout](RAPPORT.md#wat-er-fout-ging) open, zodat je de diagnose ook kan uitleggen wanneer het huidige antwoord correct is.

| Stap | Wat ik toon | Wat ik zeg |
| --- | --- | --- |
| 1. **Zoekvraag** | `search`, het fragment met `Porties: 4`, het antwoord en de metingen. | “Mijn interface toont welke route de agent koos en uit welke bron het antwoord komt. Het antwoordmodel krijgt maximaal drie fragmenten.” |
| 2. **Schaalvraag** | De curry voor zeven porties, de invoer van `scale_ingredients` en 420 → 735 ml water. | “De agent vindt het recept en stuurt de volledige ingrediëntenlijst en beide aantallen naar de MCP-server. Die berekent 420 maal zeven gedeeld door vier.” |
| 3. **Typ een omrekening** | “Hoeveel kilogram is 250 gram?” geeft `convert_units` en 0,25 kg. | “De agent herkent de uitgeschreven eenheden en stuurt `250`, `g` en `kg` naar dezelfde server.” |
| 4. **Broncontrole** | De ingrediëntregel met 420 ml, de bereidingsstappen en het historische antwoord van 795 ml. | “Het model telde een deelhoeveelheid dubbel. De juiste bron was opgehaald. De agent gebruikt nu bij deze expliciete totaalvraag de bevestigde ingrediëntregel.” |
| 5. **Kies een extra vraag** | “Welke recepten bevatten geen zuivel?” toont het dieetfilter, drie receptsuggesties en de bronnen. | “Vrij zoeken kwam vroeger uit bij recepten mét zuivel. Voor deze vraag zoekt de agent nu in recepten met het label veganistisch. Het blijft een beperkte selectie op basis van de opgenomen recepten.” |

Bij uitval van Groq toon ik de werkende lokale index en MCP-server. De lokale modus toont de verwerkingstijd en gebruikt bij gewone zoekvragen de bronfragmenten als antwoord. De gesimuleerde voorbeeldmodus toont de schermbediening met vaste gegevens.

## Oefenvragen van makkelijk naar moeilijk

| Vraag | Kort antwoord om in mijn eigen woorden te oefenen |
| --- | --- |
| Wat is mijn bijdrage? | Ik heb de interface en demo uitgewerkt met hulp van Codex. Mijn scherm toont de trace, bronnen, exacte toolgegevens, metingen en foutmeldingen van dezelfde agent als de terminal. |
| Waarom Streamlit? | Het team gebruikt Python. Ik kon de bestaande agent rechtstreeks aanroepen en de tussenresultaten met standaardcomponenten tonen. |
| Wat is het verschil tussen de drie uitvoeringsmodi? | Lokaal doet echt zoeken en rekenen. Groq voegt de modelrouter en waar nodig een gegenereerd antwoord toe. Voorbeeld toont twee vaste scenario’s met gemarkeerde voorbeeldcijfers. |
| Welke data gebruiken we? | De agent gebruikt 36 recepten met ingrediënten, stappen, tijden, labels en bronlinks. Drie komen van Health Canada en 33 zijn Nederlandse bewerkingen uit het Open Recipe Corpus. |
| Hoe werkt een embedding? | We zetten vraag en tekstfragment om naar vectoren met hetzelfde meertalige MiniLM-model. Qdrant gebruikt cosinusovereenkomst om de best passende fragmenten te rangschikken. |
| Wat is het verschil tussen beide chunkmethodes? | De eerste splitst de doorlopende recepttekst op maximaal 96 tokens met 16 overlap. De tweede splitst eerst op onderdelen en gebruikt daarna dezelfde tokenlimiet. Daardoor blijven bijvoorbeeld ingrediënten vaker bij elkaar. |
| Waarom standaard drie fragmenten? | Extra fragmenten kosten modelcontext. In de vroege vergelijking met receptfilter leverde vijf tegenover drie evenveel volledig bewijs op. Herbekijk die afweging als de dataset of vragen veranderen. |
| Wat bewaart LangGraph in zijn state? | De oorspronkelijke vraag, gekozen route, herkend recept, opgehaalde fragmenten, toolgegevens, antwoord, trace en modelmetingen. De route bepaalt welke node daarna volgt. |
| Wie kiest de route? | In Groq-modus doet het model een JSON-voorstel. Expliciete aanwijzingen kunnen het voorstel corrigeren. Daarom slaat 20/20 routes op de hele agent inclusief routecontrole. |
| Wat maakt MCP hier meer dan een gewone Python-aanroep? | De agent start een lokale FastMCP-server als subprocess, opent een `ClientSession` over stdio, initialiseert de sessie en roept een tool aan met gestructureerde argumenten. |
| Wat valideren de tools? | Porties zijn positieve gehele getallen. Hoeveelheden zijn eindig en niet-negatief. De conversietool accepteert g en kg en rekent met `Decimal`. |
| Waar zit de berekening? | In `scale_server.py`. Het taalmodel kan een route voorstellen. De tool voert de berekening uit en de agent bewaart de exacte invoer en het resultaat. |
| Hoe komen de tussenstappen op het scherm? | `invoke_agent` gebruikt `astream` in `values`-modus als de interface een callback meegeeft. Na elke afgeronde graph-stap krijgt de interface de volledige tussenstand. |
| Waarom verschijnt bij schalen soms geen antwoord-TTFT? | Er kan een Groq-aanroep voor routering zijn, terwijl de tool zelf het eindantwoord levert. TTFT meet de start van de eerste tekst van een gestreamde antwoordaanroep. |
| Is TTFT de totale wachttijd? | TTFT start bij de antwoordaanroep, na routering en ophalen. De gemeten verwerkingstijd omvat de volledige aanvraag. |
| Wat meten Context Precision, Context Recall en Faithfulness? | Precision beoordeelt de rangschikking van relevante fragmenten. Recall bekijkt of de benodigde referentie-informatie in de fragmenten staat. Faithfulness laat een beoordelaar nagaan of de antwoordclaims steun vinden in die fragmenten. |
| Hoe kan een antwoord met Faithfulness 1,0 fout zijn? | De beoordelaar gaf de historische 795 ml die score hoewel het bronrecept in totaal 420 ml vereist. De aparte inhoudelijke vergelijking toonde de dubbeltelling. |
| Hoe onderscheid ik een zoekfout van een antwoordfout? | Ik kijk naar de route en het opgehaalde bewijs. Ontbreekt 475 g ricotta in de top 3, dan is het een zoekfout. Staat 420 ml wel in de bronnen maar is het antwoord 795 ml, dan ontstaat de fout bij het antwoorden. |
| Waarom week de vrije dieetvraag af? | De embedding zag gelijkenis rond het woord zuivel. Een expliciet dieetfilter selecteert nu geldige labels vóór Qdrant rangschikt. De zoekscore blijft een overeenkomstscore. |
| Waarom is 12/12 geen algemene betrouwbaarheid? | Het gaat om twaalf vaste bronvragen, grotendeels over drie recepten. We hebben een aanvullende zoekset en gerichte regressietests. De gewone agent verwerkt vragen zelfstandig en het dieetfilter ondersteunt een beperkt aantal expliciete categorieën. |
| Hoe hervatten we Ragas na een gebruikslimiet? | We bewaren de echte modelantwoorden en bronfragmenten. `--score-report` herneemt de ontbrekende metrieken met dezelfde beoordelaar op dezelfde gegevens. Dekking betekent hoeveel vragen per metriek werkelijk gescoord zijn. |
| Hoe heb ik AI gebruikt? | Ik benoem concreet de hulp bij de interface, tests en tekst en toon welke controles ik zelf kan reproduceren en uitleggen. Het team draagt de eindverantwoordelijkheid. |

## Zelf controleren

Loop zonder AI door [de interface](../chef_ui.py), [de agent](../chef_agent.py), [de index](../recipe_search.py), [de rekentool](../scale_server.py) en [de evaluatie](../evaluate_chef.py). Laat een teamgenoot tijdens de demo één extra vraag stellen. Noteer na afloop welk onderdeel je opnieuw moet oefenen en welke controles je zelf hebt gedaan.
