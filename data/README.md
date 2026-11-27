# Projectdata

[Terug naar de README](../README.md)

| Bestand | Gebruikt door | Inhoud |
| --- | --- | --- |
| [recipes.json](recipes.json) | `recipe_search.py` en de agent | Drie proefrecepten van Health Canada met bronlinks |
| [evaluation.json](evaluation.json) | `evaluate_chef.py` | Evaluatievragen, verwachte routes en referentieantwoorden |
| [demo_recipes.json](demo_recipes.json) | `flavor_chef.py` | Vijf eigen voorbeeldrecepten voor de Ollama-demo |

De agent en de Ollama-demo gebruiken verschillende datastructuren. Voeg recepten toe aan het juiste bestand, behoud unieke ID's en vermeld de herkomst waar van toepassing. Controleer hoeveelheden en referentieantwoorden handmatig en bouw de bijbehorende zoekindex opnieuw na wijzigingen. De index zelf blijft buiten Git.
