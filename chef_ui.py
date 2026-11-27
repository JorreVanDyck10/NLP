"""Lokale demo-interface: streamlit run chef_ui.py --server.address 127.0.0.1."""

import asyncio
import copy
import json
import os
from decimal import Decimal
from pathlib import Path
from time import perf_counter

import streamlit as st


ROOT = Path(__file__).resolve().parent
SEARCH_QUESTION = "Voor hoeveel porties is de kikkererwtencurry bedoeld?"
SCALE_QUESTION = "Schaal de curry van 4 naar 7 porties."
WATER_QUESTION = "Hoeveel water gaat er in totaal in de curry?"
MODES = ("Lokaal", "Groq", "Voorbeeld (gesimuleerd)")


def recipes():
    return json.loads((ROOT / "data" / "recipes.json").read_text(encoding="utf-8"))


def tool_input(state):
    """Gebruik de exacte agentinvoer; bouw alleen bij voorbeelddata de invoer op."""
    if not state.get("tool_result"):
        return None
    if state.get("tool_input"):
        return state["tool_input"]
    if state["route"] == "scale_recipe":
        recipe_id = state["hits"][0]["recipe_id"]
        recipe = next(recipe for recipe in recipes() if recipe["id"] == recipe_id)
        base, ingredients = recipe["servings"], recipe["ingredients"]
    else:
        base = state["base"]
        ingredients = [{"name": "ingrediënt", "quantity": state["quantity"], "unit": state["unit"]}]
    return {"from_servings": base, "to_servings": state["target"], "ingredients": ingredients}


def example_state(question):
    """Vaste schermvoorbeelden; geen model, zoekindex of MCP-server aangeroepen."""
    if question not in (SEARCH_QUESTION, SCALE_QUESTION):
        raise ValueError("Kies in voorbeeldmodus de knop Zoekvraag of Schaalvraag.")
    recipe = next(recipe for recipe in recipes() if recipe["id"] == "kikkererwten-groentecurry")
    text = f"Porties: {recipe['servings']}\n" + "\n".join(
        f"{item['quantity']} {item['unit']} {item['name']}"
        for item in recipe["ingredients"] if "quantity" in item
    )
    state = {
        "question": question,
        "route": "search",
        "answer": f"De kikkererwtencurry is bedoeld voor {recipe['servings']} porties.",
        "hits": [{"title": recipe["title"], "recipe_id": recipe["id"],
                  "section": "Ingrediënten", "text": text,
                  "source_url": recipe["source_url"], "score": 0.85}],
        "trace": ["router: search", "RAG: voorbeeldfragment"],
        "latency_ms": 1250.0,
        "llm_calls": [{"stage": "answer", "model": "gesimuleerd voorbeeld",
                       "prompt_tokens": 180, "completion_tokens": 24,
                       "latency_ms": 600.0, "ttft_ms": 180.0}],
    }
    if question == SCALE_QUESTION:
        state.update(route="scale_recipe", base=recipe["servings"], target=7)
        ingredients = copy.deepcopy(recipe["ingredients"])
        for item in ingredients:
            quantity = item.get("quantity")
            item["quantity"] = str(Decimal(str(quantity)) * 7 / recipe["servings"]) if quantity is not None else None
        state["tool_result"] = {"from_servings": recipe["servings"], "to_servings": 7,
                                "ingredients": ingredients}
        state["trace"] = ["router: scale_recipe", "RAG: voorbeeldfragment", "MCP: scale_ingredients (voorbeeld)"]
        state["llm_calls"] = [{"stage": "route", "model": "gesimuleerd voorbeeld",
                               "prompt_tokens": 95, "completion_tokens": 8,
                               "latency_ms": 220.0, "ttft_ms": None}]
        state["answer"] = "Curry van 4 naar 7 porties\n\n" + "\n".join(
            f"- {item['quantity']} {item.get('unit', '')} {item['name']}"
            if item["quantity"] is not None else f"- {item['name']} (naar behoefte)"
            for item in ingredients
        )
    state["tool_input"] = tool_input(state)
    return state


def execute(question, mode, api_key=None, on_update=None):
    if mode == MODES[2]:
        return example_state(question)
    api_key = ((api_key or "").strip() or os.environ.get("GROQ_API_KEY")) if mode == "Groq" else None
    if mode == "Groq" and not api_key:
        raise ValueError("GROQ_API_KEY ontbreekt. Vul de sleutel in de zijbalk in of stel de omgevingsvariabele in en herstart de interface.")
    # De voorbeeldmodus kan ook starten zonder de agentdependencies.
    from chef_agent import run

    state = asyncio.run(run(question, api_key, on_update=on_update))
    state["tool_input"] = tool_input(state)
    return state


def token_total(calls, field):
    values = [call.get(field) for call in calls]
    # Een ontbrekende meting is geen nul en ook geen volledig totaal.
    return sum(values) if values and all(value is not None for value in values) else None


def display_amount(item):
    if item.get("quantity") is None:
        return "naar behoefte"
    amount = f"{Decimal(str(item['quantity'])):.6f}".rstrip("0").rstrip(".").replace(".", ",")
    return f"{amount} {item.get('unit') or ''}".strip()


def render_result(state, *, in_progress=False):
    if state["mode"] == MODES[2]:
        st.warning("Gesimuleerd voorbeeld. Scores, tokens en tijden zijn ingevulde voorbeeldwaarden; er is geen live zoek- of MCP-aanroep gedaan.")
    st.caption(f"Modus: {state['mode']} · Route: {state.get('route', 'onbekend')}")
    if state.get("error"):
        st.error(state["error"])
        st.info("Deze aanvraag is niet afgerond. Hieronder staan alleen de stappen en metingen die al voltooid waren.")
    if state.get("answer"):
        st.markdown(state["answer"])
    if state.get("question") == WATER_QUESTION:
        st.info("Broncontrole: het recept bevat in totaal 420 ml water. De 375 ml in de bereidingsstap is een deel daarvan. Vergelijk het antwoord met de opgehaalde fragmenten; 420 + 375 zou een dubbeltelling zijn.")
    with st.expander("Gevolgde stappen", expanded=True):
        for step in state.get("trace", []):
            st.text(step)
    with st.expander(f"Bronfragmenten ({len(state.get('hits', []))})"):
        if not state.get("hits"):
            st.write("Voor deze vraag zijn geen bronfragmenten opgehaald.")
        for index, hit in enumerate(state.get("hits", []), 1):
            st.write(f"**{index}. {hit['title']} · {hit['section']}**")
            if hit.get("score") is not None:
                st.caption(f"Overeenkomstscore: {hit['score']:.3f} (geen kans op een correct antwoord)")
            st.text(hit["text"])
            url = hit.get("source_url", "")
            if url.startswith(("https://", "http://")):
                st.link_button("Open receptbron", url)
    with st.expander("MCP-aanroep"):
        if state.get("tool_result"):
            st.write("**Tool: scale_ingredients**")
            st.caption("Invoer en uitvoer uit de agentstate. In voorbeeldmodus zijn beide gesimuleerd.")
            result = state["tool_result"]
            st.write(f"Van **{result['from_servings']}** naar **{result['to_servings']}** porties")
            st.dataframe([
                {"Ingrediënt": original["name"], "Van": display_amount(original),
                 "Naar": display_amount(scaled), "Opmerking": scaled.get("note") or ""}
                for original, scaled in zip(state["tool_input"]["ingredients"], result["ingredients"], strict=True)
            ], use_container_width=True, hide_index=True)
            st.caption("Weergave afgerond tot maximaal zes decimalen. De ruwe toolgegevens hieronder bevatten de ontvangen waarden.")
            st.json({"input": state["tool_input"], "output": result}, expanded=False)
        else:
            st.write("Voor deze vraag is geen geslaagde MCP-aanroep geregistreerd.")
    with st.expander("Tokens en responstijden", expanded=True):
        calls = state.get("llm_calls", [])
        input_tokens = token_total(calls, "prompt_tokens")
        output_tokens = token_total(calls, "completion_tokens")
        columns = st.columns(4)
        latency = state.get("latency_ms")
        answer_calls = [call for call in calls if call.get("stage") == "answer"]
        ttft = answer_calls[0].get("ttft_ms") if answer_calls else None
        columns[0].metric("Verwerkingstijd", f"{latency:.0f} ms" if latency is not None else "Niet gemeten")
        columns[1].metric("Inputtokens", input_tokens if input_tokens is not None else "Niet gemeten")
        columns[2].metric("Outputtokens", output_tokens if output_tokens is not None else "Niet gemeten")
        columns[3].metric("TTFT antwoord", f"{ttft:.0f} ms" if ttft is not None else "Niet gemeten")
        st.caption("Verwerkingstijd omvat de agent en de updates aan het scherm. Tokens tellen de afgeronde modelaanroepen; TTFT begint bij de antwoordaanroep, na het zoeken.")
        if not calls and in_progress:
            st.info("De aanvraag loopt. Er zijn nog geen afgeronde modelmetingen beschikbaar.")
        elif not calls and state["mode"] == "Groq" and state.get("error"):
            st.info("Er zijn geen afgeronde modelmetingen ontvangen. Ontbrekende metingen worden niet als nul getoond.")
        elif not calls:
            st.info("Geen taalmodel aangeroepen. Tokenaantallen en tijd tot de eerste token (TTFT) zijn niet gemeten. De lokale zoekfunctie gebruikt wel embeddings.")
        elif input_tokens is None or output_tokens is None:
            st.info("Tokenmetingen ontbreken geheel of gedeeltelijk. Er wordt geen onvolledig totaal als volledig getoond.")
        for index, call in enumerate(calls, 1):
            st.write(f"**Modelaanroep {index}: {call.get('stage', 'onbekend')} · {call.get('model', 'onbekend')}**")
            st.json(call, expanded=False)
            if call.get("ttft_ms") is None:
                st.caption("TTFT niet gemeten voor deze aanroep. De router geeft JSON terug zonder tekststream." if call.get("stage") == "route" else "TTFT ontbreekt in de metingen van deze antwoordaanroep.")
        st.caption("Tokenaantallen komen uit de modelrespons; het zijn geen embeddingtokenmetingen.")


def friendly_error(exc):
    """Geef hersteladvies zonder HTTP-headers, API-sleutels of ruwe tracebacks."""
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status in (401, 403):
        return "Groq weigert de sleutel of toegang tot het model. Controleer je sleutel en modelinstelling."
    if status == 429:
        return "De Groq-gebruikslimiet is bereikt. Wacht even en probeer de vraag opnieuw."
    if status is not None:
        return f"Groq gaf HTTP-status {status}. Probeer later opnieuw of controleer de modelinstelling."
    if isinstance(exc, ModuleNotFoundError):
        return "Een benodigd pakket ontbreekt. Installeer requirements-ui.txt in de virtuele omgeving en start de interface opnieuw."
    if isinstance(exc, ValueError):
        message = str(exc)
        if message.startswith("GROQ_API_KEY ontbreekt"):
            return message
        if message.startswith("De index voor deze dataset ontbreekt"):
            return "De zoekindex ontbreekt of past niet bij de dataset. Voer python recipe_search.py build uit in de virtuele omgeving."
        if message.startswith("Groq gaf geen tekst terug"):
            return "Groq gaf een leeg antwoord terug. Probeer de vraag opnieuw of controleer het model en tokenbudget."
    return "De agent kon de aanvraag niet afronden. Controleer de index, modelverbinding en MCP-server. Probeer daarna opnieuw."


def clear_conversation():
    st.session_state["messages"] = []


def clear_key():
    st.session_state["groq_api_key"] = ""


def main():
    st.set_page_config(page_title="Flavor Chef", page_icon="🍲", layout="wide")
    st.title("Flavor Chef")
    st.write("Zoek een recept op of schaal de ingrediënten naar jouw aantal porties.")
    api_key = None
    with st.sidebar:
        st.header("Demo instellen")
        mode = st.radio("Uitvoering", MODES)
        if mode == "Lokaal":
            st.info("Zoeken en rekenen op je eigen pc. Zoekvragen tonen bronfragmenten; er wordt geen antwoord door een taalmodel geschreven.")
        elif mode == "Groq":
            st.info("Vragen en geselecteerde receptfragmenten worden naar Groq gestuurd.")
            api_key = st.text_input("Groq API-sleutel (optioneel)", type="password", key="groq_api_key",
                                    help="Alleen voor deze browsersessie. Laat leeg om GROQ_API_KEY uit de omgeving te gebruiken.")
            st.caption("Omgevingssleutel beschikbaar." if os.environ.get("GROQ_API_KEY") else "Geen omgevingssleutel gevonden. Je kunt hierboven een sleutel invullen.")
            st.button("Ingevulde sleutel wissen", key="clear_key", on_click=clear_key)
        else:
            st.warning("Alleen twee vaste voorbeelden. De metingen zijn gesimuleerd.")
        st.caption("Berichten blijven tijdens deze sessie zichtbaar. Iedere vraag wordt apart verwerkt: herhaal de receptnaam bij een vervolgvraag.")
        st.button("Gesprek wissen", key="clear", on_click=clear_conversation)

    st.session_state.setdefault("messages", [])
    question = None
    left, middle, right = st.columns(3)
    if left.button("Zoekvraag", key="search", use_container_width=True):
        question = SEARCH_QUESTION
    if middle.button("Schaalvraag", key="scale", use_container_width=True):
        question = SCALE_QUESTION
    if right.button("Broncontrole", key="source_check", use_container_width=True, disabled=mode == MODES[2]):
        question = WATER_QUESTION
    st.caption("Democontrole: curry voor 4 porties; 420 ml water wordt 735 ml voor 7 porties. Broncontrole toont de vraag met een bekende kans op dubbeltelling.")
    for index, message in enumerate(st.session_state["messages"]):
        with st.chat_message("user"):
            st.write(message["question"])
        with st.chat_message("assistant"):
            render_result(message)
            if message.get("error") and st.button("Opnieuw proberen", key=f"retry_{index}"):
                question = message["question"]

    typed = st.chat_input("Bijvoorbeeld: hoeveel water gaat er in de curry?", disabled=mode == MODES[2])
    question = (typed or question or "").strip()
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            status_box = st.status("Vraag ontvangen", expanded=False)
            live_result = st.empty()
            partial = {}

            def update(snapshot):
                partial.update(snapshot, mode=mode)
                if snapshot.get("answer"):
                    label = "Antwoord gereed"
                elif snapshot.get("tool_result"):
                    label = "Rekentool gereed"
                elif snapshot.get("hits"):
                    label = "Bronnen gevonden"
                elif snapshot.get("route"):
                    label = "Route gekozen: " + snapshot["route"]
                else:
                    label = "Vraag ontvangen"
                status_box.update(label=label)
                with live_result.container():
                    render_result(partial, in_progress=True)

            started = perf_counter()
            try:
                state = execute(question, mode, api_key=api_key, on_update=update)
                status_box.update(label="Aanvraag afgerond", state="complete")
            except Exception as exc:
                state = {**partial, "error": friendly_error(exc),
                         "latency_ms": round((perf_counter() - started) * 1000, 2)}
                status_box.update(label="Aanvraag niet afgerond", state="error")
            state["latency_ms"] = state.get("latency_ms", round((perf_counter() - started) * 1000, 2))
        state.update(question=question, mode=mode)
        st.session_state["messages"].append(state)
        st.rerun()


if __name__ == "__main__":
    main()
