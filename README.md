# Flavor Chef

Een kookassistent die recepten opzoekt en ingrediënthoeveelheden herschaalt. De repository bevat een agent met MCP-tool en benchmark, en een aparte lokale Ollama-demo.

**Ga je iets wijzigen? Lees eerst de [onderhoudsafspraken in CONTRIBUTING.md](CONTRIBUTING.md).** Dat geldt voor code, data, documentatie en AI-agenten. [AGENTS.md](AGENTS.md) legt deze leesstap ook vast voor coding agents.

## Kies je startpunt

| Onderdeel | Uitleg en installatie | Bestanden |
| --- | --- | --- |
| Agent, receptzoeker, MCP en benchmark | [Installatie en voortgang](docs/VOORTGANG.md) | `chef_agent.py`, `recipe_search.py`, `scale_server.py`, `evaluate_chef.py`, `requirements.txt` en optioneel `requirements-eval.txt` |
| Lokale RAG-demo met Ollama | [Demo starten](docs/OLLAMA-DEMO.md) | `flavor_chef.py`, `requirements-demo.txt` |

Voer alle installatie- en startcommando's uit vanuit de repository-root: de map met deze README. De twee onderdelen gebruiken verschillende datasets en virtuele omgevingen.

## Wegwijzer

| Locatie | Inhoud |
| --- | --- |
| [docs/](docs/README.md) | Installatie, voortgang, projectrapport en MVP-checklist |
| [data/](data/README.md) | Recepten en evaluatievragen met uitleg over hun gebruik |
| [reports/](reports/README.md) | Bewaarde referentiebenchmark; nieuwe lokale metingen worden genegeerd |
| [scripts/](scripts/check_repository.py) | Controle op structuur, lokale Markdown-links, Python-syntax en JSON |
| [.github/](.github/workflows/repository-check.yml) | GitHub Actions-controle en PR-checklist |

Lesmateriaal, modellen, sleutels, virtuele omgevingen en zoekindexen blijven buiten Git. Gebruik voor lesmateriaal een eigen lokale map; een pc-specifiek pad is geen installatievereiste.

## Controle voor een commit

```powershell
python scripts/check_repository.py
git diff --check
git status --short
git diff
git diff --cached
```

De repositorycontrole gebruikt alleen de Python-standaardbibliotheek en Git; er worden geen modellen of projectdependencies gedownload. Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor de volledige werkwijze en aanvullende functionele controles.
