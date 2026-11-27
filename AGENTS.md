# Verplichte instructies voor coding agents

Deze instructies gelden voor de volledige repository.

1. Lees vóór elke taak [CONTRIBUTING.md](CONTRIBUTING.md) volledig. Voer pas daarna wijzigingen uit. Dit geldt ook voor een kleine documentatie- of datawijziging.
2. Lees [README.md](README.md) en de documentatie van het betrokken onderdeel in [docs/](docs/README.md).
3. Controleer `git status --short` en behoud bestaand werk van anderen. Lees eventuele aanvullende `AGENTS.md`-bestanden in de betrokken submap.
4. Volg de mapindeling en onderhoudsafspraken. Werk bij verplaatsingen alle verwijzingen bij. Voeg geen gegenereerde indexen, omgevingen, modellen, lokale meetuitvoer of geheimen toe.
5. Voer vóór oplevering `python scripts/check_repository.py` en `git diff --check` uit, plus de functionele controles die bij de wijziging horen. Rapporteer wat is gecontroleerd en wat niet kon worden uitgevoerd.
6. Werk documentatie bij als gebruik, installatie, voortgang of structuur verandert. Controleer de volledige diff en de te committen bestanden.

Gebruik de checklist uit CONTRIBUTING.md bij iedere wijziging. Houd commits en pull requests beperkt tot één samenhangende taak.
