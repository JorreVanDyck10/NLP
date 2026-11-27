# Verplichte instructies voor coding agents

Deze instructies gelden voor de volledige repository.

1. Lees vóór elke taak [CONTRIBUTING.md](CONTRIBUTING.md) volledig. Voer pas daarna wijzigingen uit. Dit geldt ook voor een kleine documentatie- of datawijziging.
2. Lees [README.md](README.md) en de documentatie van het betrokken onderdeel in [docs/](docs/README.md).
3. Controleer `git status --short` en behoud bestaand werk van anderen. Lees eventuele aanvullende `AGENTS.md`-bestanden in de betrokken submap.
4. Volg de mapindeling en onderhoudsafspraken. Werk bij verplaatsingen alle verwijzingen bij. Voeg geen gegenereerde indexen, omgevingen, modellen, lokale meetuitvoer of geheimen toe.
5. Voer vóór oplevering `python scripts/check_repository.py` en `git diff --check` uit, plus de functionele controles die bij de wijziging horen. Rapporteer wat is gecontroleerd en wat niet kon worden uitgevoerd.
6. Werk documentatie bij als gebruik, installatie, voortgang of structuur verandert. Controleer de volledige diff en de te committen bestanden.
7. Houd [docs/PROJECTKEUZES.md](docs/PROJECTKEUZES.md) actueel als gezamenlijk keuzeoverzicht. Noteer per nieuwe of gewijzigde keuze de techniek, toepassing, reden, relevante lesbasis en werkelijk uitgevoerde controle of beperking. Verwijs vanuit **Gebruikt en waarom** in het [projectrapport](docs/RAPPORT.md) naar dat overzicht. Leg meetresultaten en controles vast bij de betrokken fase en onderscheid eigen werk, AI-hulp, echte metingen en simulaties.

Gebruik de checklist uit CONTRIBUTING.md bij iedere wijziging. Houd commits en pull requests beperkt tot één samenhangende taak.
