"""Lokale demo-interface: streamlit run chef_ui.py --server.address 127.0.0.1."""

import asyncio
import copy
import json
import os
from decimal import Decimal
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent
SEARCH_QUESTION = "Hoeveel water gaat er in totaal in de curry?"
SCALE_QUESTION = "Schaal de curry van 4 naar 7 porties."
MODES = ("Lokaal", "Groq", "Voorbeeld (gesimuleerd)")


def recipes():
    return json.loads((ROOT / "data" / "recipes.json").read_text(encoding="utf-8"))


def tool_input(state):
    """Leid de invoer af uit dezelfde state en brondata als de bestaande agent."""
    if not state.get("tool_result"):
        return None
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
    text = "\n".join(
        f"{item['quantity']} {item['unit']} {item['name']}"
        for item in recipe["ingredients"] if "quantity" in item
    )
    state = {
        "question": question,
        "route": "search",
        "answer": "Voor de curry is in totaal 420 ml water nodig.",
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


def execute(question, mode):
    if mode == MODES[2]:
        return example_state(question)
    api_key = os.environ.get("GROQ_API_KEY") if mode == "Groq" else None
    if mode == "Groq" and not api_key:
        raise ValueError("GROQ_API_KEY ontbreekt. Stel de omgevingsvariabele in en herstart de interface.")
    # De voorbeeldmodus kan ook starten zonder de agentdependencies.
    from chef_agent import run

    state = asyncio.run(run(question, api_key))
    state["tool_input"] = tool_input(state)
    return state


def token_total(calls, field):
    values = [call.get(field) for call in calls]
    # Een ontbrekende meting is geen nul en ook geen volledig totaal.
    return sum(values) if values and all(value is not None for value in values) else None


def render_result(state):
    if state["mode"] == MODES[2]:
        st.warning("Gesimuleerd voorbeeld. Scores, tokens en tijden zijn ingevulde voorbeeldwaarden; er is geen live zoek- of MCP-aanroep gedaan.")
    st.caption(f"Modus: {state['mode']} · Route: {state.get('route', 'onbekend')}")
    if state.get("error"):
        st.error(state["error"])
        st.info("Deze aanvraag is mislukt. Er worden geen bronfragmenten, toolresultaten of metingen als geslaagd getoond.")
        return
    st.markdown(state["answer"])
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
            st.caption("Invoer, afgeleid uit de vraag en dezelfde brondata als de agent; dit is geen apart protocol-log.")
            st.json(state["tool_input"])
            st.write("**Uitvoer van de tool**")
            st.json(state["tool_result"])
        else:
            st.write("Voor deze vraag is geen geslaagde MCP-aanroep geregistreerd.")
    with st.expander("Tokens en responstijden", expanded=True):
        calls = state.get("llm_calls", [])
        input_tokens = token_total(calls, "prompt_tokens")
        output_tokens = token_total(calls, "completion_tokens")
        columns = st.columns(3)
        latency = state.get("latency_ms")
        columns[0].metric("Agenttijd", f"{latency:.0f} ms" if latency is not None else "Niet gemeten")
        columns[1].metric("Inputtokens", input_tokens if input_tokens is not None else "Niet gemeten")
        columns[2].metric("Outputtokens", output_tokens if output_tokens is not None else "Niet gemeten")
        st.caption("Agenttijd omvat de agentuitvoering, zonder het tekenen van deze interface. Metingen verschijnen na afloop van de aanvraag.")
        if not calls:
            st.info("Geen taalmodel aangeroepen. Tokenaantallen en tijd tot de eerste token (TTFT) zijn niet gemeten. De lokale zoekfunctie gebruikt wel embeddings.")
        elif input_tokens is None or output_tokens is None:
            st.info("Tokenmetingen ontbreken geheel of gedeeltelijk. Er wordt geen onvolledig totaal als volledig getoond.")
        for index, call in enumerate(calls, 1):
            st.write(f"**Modelaanroep {index}: {call.get('stage', 'onbekend')} · {call.get('model', 'onbekend')}**")
            st.json(call)
            if call.get("ttft_ms") is None:
                st.caption("TTFT niet gemeten voor deze aanroep. De router gebruikt geen tekststream.")
        st.caption("Tokenaantallen komen uit de modelrespons; het zijn geen embeddingtokenmetingen.")


def main():
    st.set_page_config(page_title="Flavor Chef", page_icon="🍲", layout="wide")
    st.title("Flavor Chef")
    st.write("Zoek een recept op of schaal de ingrediënten naar jouw aantal porties.")
    with st.sidebar:
        st.header("Demo instellen")
        mode = st.radio("Uitvoering", MODES)
        if mode == "Lokaal":
            st.info("Zoeken en rekenen op je eigen pc. Zoekvragen tonen bronfragmenten; er wordt geen antwoord door een taalmodel geschreven.")
        elif mode == "Groq":
            st.info("Vragen en geselecteerde receptfragmenten worden naar Groq gestuurd. De sleutel wordt uit de omgevingsvariabele gelezen.")
        else:
            st.warning("Alleen twee vaste voorbeelden. De metingen zijn gesimuleerd.")
        st.caption("Berichten blijven tijdens deze sessie zichtbaar. Iedere vraag wordt apart verwerkt: herhaal de receptnaam bij een vervolgvraag.")
        if st.button("Gesprek wissen", key="clear"):
            st.session_state["messages"] = []

    st.session_state.setdefault("messages", [])
    question = None
    left, right = st.columns(2)
    if left.button("Zoekvraag", key="search", use_container_width=True):
        question = SEARCH_QUESTION
    if right.button("Schaalvraag", key="scale", use_container_width=True):
        question = SCALE_QUESTION
    st.caption(f"Zoekvraag: {SEARCH_QUESTION} · Schaalvraag: {SCALE_QUESTION}")
    for message in st.session_state["messages"]:
        with st.chat_message("user"):
            st.write(message["question"])
        with st.chat_message("assistant"):
            render_result(message)

    typed = st.chat_input("Bijvoorbeeld: hoeveel water gaat er in de curry?", disabled=mode == MODES[2])
    question = (typed or question or "").strip()
    if question:
        with st.spinner("Flavor Chef verwerkt je vraag…"):
            try:
                state = execute(question, mode)
            except Exception as exc:
                # Bewaar fouten als bericht, zonder traceback of mogelijke API-headers.
                if isinstance(exc, (ValueError, ModuleNotFoundError)):
                    error = str(exc)
                else:
                    error = "De agent kon de aanvraag niet afronden. Controleer de index, modelverbinding en MCP-server. Probeer daarna opnieuw."
                state = {"error": error}
        state.update(question=question, mode=mode)
        st.session_state["messages"].append(state)
        st.rerun()


if __name__ == "__main__":
    main()
