# Projectdata

[Terug naar de README](../README.md)

| Bestand | Gebruikt door | Inhoud |
| --- | --- | --- |
| [recipes.json](recipes.json) | `recipe_search.py` en de agent | 36 recepten met bronlinks, tijden, porties, ingrediënten, bereidingsstappen en dieettags |
| [evaluation.json](evaluation.json) | `evaluate_chef.py` | 20 agentvragen met verwachte routes en referentieantwoorden |
| [retrieval_checks.json](retrieval_checks.json) | `python -m scripts.compare_chunking` | Zeven extra zoekvragen over de uitgebreide receptenset |
| [demo_recipes.json](demo_recipes.json) | `flavor_chef.py` | Vijf eigen voorbeeldrecepten voor de Ollama-demo |

De agent en de Ollama-demo gebruiken verschillende datastructuren. Voeg recepten toe aan het juiste bestand, behoud unieke ID's en vermeld de herkomst waar van toepassing. Controleer hoeveelheden en referentieantwoorden handmatig en bouw de bijbehorende zoekindex opnieuw na wijzigingen. De index zelf blijft buiten Git.

De 20 agentvragen omvatten twaalf zoekvragen met positief bronbewijs, één zoekvraag over ontbrekende receptinformatie, zes schaalvragen en één begroeting. Bij `expected_missing_information` controleert de benchmark of de agent het juiste recept ophaalt. Lees het gegenereerde antwoord zelf om te zien of de agent terecht aangeeft dat de informatie ontbreekt. Ragas scoort de zoekvragen met positief bronbewijs.

## Herkomst van de agentrecepten

De drie bestaande Health Canada-recepten hebben elk een eigen bronlink. De 33 toegevoegde recepten zijn Nederlandstalige bewerkingen van een selectie uit het Open Recipe Corpus van Airon, gebaseerd op het Poolse Wikibooks-kookboek. Per recept staan de originele link, revisie, geschiedenis en naamsvermelding in de data. De bewerkingen van deze 33 records vallen onder CC BY-SA 4.0. [Vastgelegde bronversie](https://github.com/Rippy1911/open-recipe-corpus/tree/86102603bac07d79b94bc35cba5b50346798cc09) · [Licentie](https://creativecommons.org/licenses/by-sa/4.0/) · [Bronvermeldingen van het corpus](https://github.com/Rippy1911/open-recipe-corpus/blob/86102603bac07d79b94bc35cba5b50346798cc09/ATTRIBUTION.md)

De Nederlandse namen en bereidingsstappen zijn ingekort en vertaald. Hoeveelheden, porties en tijden komen uit de gestructureerde bron. Eenheden zijn aangepast aan de Nederlandse notatie. Waar de bron een hoeveelheid naar smaak opgeeft, bevat het ingrediënt alleen een naam. Dieettags beschrijven de opgenomen versie. Voor de aardappelpannenkoeken is bijvoorbeeld plantaardige olie gekozen uit de vetopties in de bron.
