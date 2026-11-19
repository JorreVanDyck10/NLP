# Flavor Chef

Een lokale demo die vragen beantwoordt op basis van vijf voorbeeldrecepten.

- [Projectrapport](RAPPORT.md)
- [MVP-checklist](MVP-CHECKLIST.md)

De PowerPoints en de opdracht-pdf staan in de lokale map `C:\NLPFull\lesmateriaal`. [VOORTGANG.md](VOORTGANG.md) beschrijft een afzonderlijke uitwerking van Flavor Chef.

## Starten op Windows

Start Ollama. De demo gebruikt `qwen3-embedding:0.6b` en `qwen3.5:4b-q4_K_M`. Op de werk-pc staan beide modellen al klaar. Op een andere pc kun je elk ontbrekend model ophalen met `ollama pull <modelnaam>`.

Open PowerShell in de projectmap.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe flavor_chef.py index
```

Gebruik `index` opnieuw na wijzigingen aan `data/recipes.json`. De index komt in `storage/`.

## Demo

```powershell
.\.venv\Scripts\python.exe flavor_chef.py search "Hoe lang moet de chili pruttelen?"
.\.venv\Scripts\python.exe flavor_chef.py ask "Hoe lang moet de chili pruttelen?"
.\.venv\Scripts\python.exe flavor_chef.py ask "Hoe lang moet de chocoladetaart bakken?"
```

1. `index` splitst elk recept in overzicht, ingrediënten en bereiding. Ollama zet elk stuk om in een vector. LlamaIndex bewaart de index op schijf.
2. `search` zet de vraag met hetzelfde model om in een vector. LlamaIndex haalt de drie best passende tekststukken op.
3. `ask` toont die stukken en geeft ze mee aan het taalmodel als context. Het antwoord over de chili hoort **20 minuten** te zijn. Voor chocoladetaart ontbreekt de informatie in de recepten.

De demo stuurt vragen en recepttekst naar Ollama op de eigen pc. De uitleg volgt PowerPoint 1, slides 21–45 en 84–90.
