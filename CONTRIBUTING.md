# GitHub overzichtelijk houden

**Verplicht lezen vóór iedere wijziging.** Iedereen die aan deze repository werkt, ook met een AI-agent, leest dit bestand eerst. De README verwijst hiernaar en AGENTS.md maakt deze stap verplicht voor coding agents. Pas deze afspraken ook toe bij kleine wijzigingen.

## Vaste indeling

```text
NLP/
├── README.md                   # Startpunt voor het hele project
├── AGENTS.md                   # Instructies voor coding agents
├── CONTRIBUTING.md             # Deze onderhoudsafspraken
├── .gitignore
├── *.py                        # Bestaande uitvoerbare projectmodules
├── requirements*.txt           # Dependencies per onderdeel
├── docs/                       # Installatie, voortgang, rapport en checklist
├── data/                       # Kleine brondata en evaluatievragen
├── reports/                    # Bewust bewaarde referentiemetingen
├── scripts/                    # Onderhoudscontroles
└── .github/                    # Workflow en PR-template
```

- Houd de root beperkt tot bovenstaande bestanden en mappen. Nieuwe uitleg hoort in `docs/`, met een link vanuit de documentatiewegwijzer. Geef een nieuw onderdeel een duidelijke plek; pas bij een bewuste structuurwijziging ook deze afspraken en de repositorycontrole aan.
- Behoud de huidige Python-entrypoints en requirements-bestanden zolang de startcommando's daarvan afhangen. Een verhuizing vereist aanpassing en controle van imports, datapaden en alle commando's.
- Geef nieuwe bestanden duidelijke namen. Maak geen varianten zoals `final`, `final2`, `nieuw` of `backup`; Git bewaart versies. Volg de bestaande taal en naamgeving van het onderdeel.
- Houd iedere uitleg op één hoofdplek. De README verwijst naar installatiehandleidingen; het rapport bevat projectkeuzes en resultaten; de checklist bevat open opleverpunten. Historische resultaten blijven herkenbaar als historisch.

## Wat wel en niet in Git hoort

- **Wel:** broncode, requirements, kleine receptendatasets met herkomst, evaluatievragen, onderhoudsscripts en actuele documentatie.
- **Alleen bewust:** `reports/baseline.json` is een bewaarde referentiemeting. Vervang die alleen bij een bedoelde nieuwe baseline, met uitleg over commando, dataset, instellingen en resultaten in het projectrapport. Andere metingen blijven standaard lokaal. Een extra referentiemeting vereist een gerichte uitzondering in `.gitignore` en uitleg in `reports/README.md`.
- **Lokaal houden:** virtuele omgevingen, Python-caches, vectorindexen, modellen, logs, tijdelijke bestanden, editorinstellingen, lespresentaties en opdrachtbestanden. Verwijs naar extern lesmateriaal zonder één pc-pad als vereiste op te leggen.
- **Geen geheimen:** commit geen `.env`, API-sleutels of credentials. Gebruik omgevingsvariabelen; een `.env.example` mag alleen lege waarden of herkenbare placeholders bevatten. `.gitignore` verwijdert geen bestanden die al gevolgd worden: controleer ook de diff.

## Werkwijze per taak

1. Lees deze afspraken en de relevante documentatie. Controleer met `git status --short` of er bestaand werk is. Maak of hergebruik een passende taakbranch vanaf een actuele `main`, bijvoorbeeld `feat/recepten`, `fix/zoekresultaten` of `docs/installatie`. Verplaats bestaand werk niet ongemerkt en herschrijf geen gedeelde geschiedenis.
2. Houd de wijziging gericht. Meng een nieuwe feature niet met een grote herstructurering. Verplaats bestaande bestanden in plaats van kopieën achter te laten en werk alle links bij.
3. Werk de relevante documentatie mee bij. Leg een nieuwe projectfase of meetresultaat vast in `docs/RAPPORT.md`; werk de voortgang en checklist bij waar de wijziging daar aanleiding toe geeft. Maak geen nieuwe losse voortgangsbestanden.
4. Controleer vanuit de repository-root:

   ```powershell
   python scripts/check_repository.py
   git diff --check
   git status --short
   git diff
   git diff --cached
   ```

   De repositorycontrole bekijkt gevolgde én niet-genegeerde nieuwe bestanden. Ze controleert de afgesproken indeling, uitgesloten lokale bestanden, lokale Markdown-bestandslinks, Python-syntax en JSON. Externe URLs, Markdown-ankers, geheimen in bestandsinhoud en de werking van de modellen vallen buiten deze controle.

5. Controleer gedrag als code of data verandert. Gebruik de start- en evaluatiecommando's uit de betrokken handleiding. Bouw indexen opnieuw na receptwijzigingen. Vermeld wanneer Ollama, modellen of een API-sleutel ontbreken; claim dan geen geslaagde functionele test. Een documentatieverplaatsing vereist vooral controle van links en commando's, geen nieuwe modelbenchmark.
6. Voeg alleen de bedoelde bestanden toe met `git add <pad>`. Controleer daarna `git diff --cached` en maak een commit met een korte, concrete omschrijving.
7. Open een pull request naar `main`, vul de PR-checklist in en beschrijf wijziging en controle. Houd één samenhangende taak per PR. Merge pas na geslaagde repositorycontrole en review volgens de teamafspraken.
8. Verwijder een gemergede taakbranch zodra is nagegaan dat er geen uniek werk of open PR meer van afhangt. Verwijder geen branches van anderen zonder afstemming.

## Wat GitHub automatisch controleert

De workflow `Repositorycontrole` voert dezelfde controle uit op pushes en pull requests naar `main`. De PR-template vraagt expliciet te bevestigen dat dit bestand gelezen en toegepast is. Een script kan niet vaststellen of iemand de tekst daadwerkelijk heeft gelezen.

Als een beheerder merges technisch wil blokkeren bij een mislukte controle, moet die in de GitHub-regels voor `main` de statuscheck `Repositorycontrole` verplicht maken en pull requests vereisen. Deze repositorybestanden stellen zelf geen branchbeveiliging in.

## Checklist vóór commit en PR

- [ ] Ik heb CONTRIBUTING.md gelezen en toegepast.
- [ ] De wijziging heeft één duidelijk doel en past in de vaste indeling.
- [ ] Documentatie en lokale links kloppen; er zijn geen overbodige kopieën.
- [ ] Ik voeg geen geheimen, caches, indexen, modellen of onbedoelde meetuitvoer toe.
- [ ] De repositorycontrole en `git diff --check` slagen.
- [ ] Relevante functionele controles zijn uitgevoerd, of de beperking is beschreven.
- [ ] Ik heb de volledige diff en de te committen bestanden nagekeken.
