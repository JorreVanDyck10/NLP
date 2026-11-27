# Flavor Chef | MVP-checklist

[Terug naar de README](../README.md)

**Doel:** een werkende MVP die Raoul zelf kan uitleggen. Volgens de rubric kan een volledige MVP met goede analyse maximaal 85% halen.

Deze checklist volgt de oplevercriteria voor de Ollama-demo en de agent. De voortgang van de agent, MCP-tool en benchmark staat in [VOORTGANG.md](VOORTGANG.md).

De percentages hieronder zijn de gewichten van de beoordelingscriteria. De vereisten staan in de opdracht-pdf. Bewaar het lesmateriaal in een eigen lokale map buiten Git.

## 1. Recepten en chunking · 25%

- [x] Maak vijf voorbeeldrecepten en een lokale LlamaIndex-vectorindex.
- [x] Breid de agentdataset uit naar 30–50 gevarieerde recepten met ingrediënten, stappen, kooktijd, dieetlabels en herkomst. De agent gebruikt 36 recepten.
- [x] Vergelijk tokengebaseerde chunking met splitsen per receptsectie op dezelfde vragen. Zie de resultaten en foutanalyse in het [projectrapport](RAPPORT.md#receptendataset-en-chunking).

## 2. Agent en MCP · 35%

- [ ] Bouw een LangGraph-workflow die de vraag en tussenresultaten bijhoudt. Laat het model kiezen tussen recepten opzoeken, een tool gebruiken en gewoon antwoorden.
- [ ] Maak één lokale MCP-tool die hoeveelheden schaalt op basis van het aantal porties. Test de berekening en ongeldige invoer.
- [ ] Test alle routes. Combineer ook beide stappen in één vraag, bijvoorbeeld “Zoek de chili en schaal het recept naar zes porties.”

## 3. Evaluatie · 20%

- [ ] Maak 15–20 controlevragen met zelf nagekeken referentieantwoorden voor ingrediënten, vervangingen en conversies.
- [ ] Meet Context Precision, Context Recall en Faithfulness met Ragas. Noteer of fouten ontstaan bij het ophalen van de bron of bij het maken van het antwoord.

## 4. Inference, metingen en lokale interface · 10%

- [ ] Sluit Groq aan met een beschikbaar model op het gratis plan. De opdracht noemt Llama 3.1 8B als voorbeeld. Groq verwijst voor dat model nu naar `openai/gpt-oss-20b`. [Groq-modelwijzigingen](https://console.groq.com/docs/deprecations)
- [ ] Meet inputtokens, outputtokens, totale antwoordtijd en tijd tot de eerste token (TTFT).
- [ ] Maak een eenvoudige lokale interface met gesprekken, opgehaalde tekststukken, MCP-toolcalls en live metingen.

## 5. Proces en GenAI · 10%

- [ ] Vul het [projectrapport](RAPPORT.md) bij na elke fase en na feedback.
- [ ] Controleer het GenAI-beleid van de opleiding en maak de verantwoording af.
- [ ] Oefen de demo en code-uitleg zonder AI. Toon een foutgeval en leg uit hoe je vaststelde waar het misliep.
