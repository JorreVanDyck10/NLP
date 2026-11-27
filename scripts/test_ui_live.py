"""Vier live demovragen via AppTest. Sleutel via omgeving of verborgen stdin."""

import argparse
import getpass
import json
import os
import re
from pathlib import Path
import sys
from decimal import Decimal

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "ui-live.json")
    args = parser.parse_args()
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        if sys.stdin.isatty():
            key = getpass.getpass("Groq-sleutel (wordt niet getoond): ")
        else:
            print("Wacht op Groq-sleutel via stdin; de waarde wordt niet getoond.", flush=True)
            key = sys.stdin.readline().strip()
    if not key:
        parser.error("Een sleutel is nodig voor deze live controle.")

    os.environ["GROQ_API_KEY"] = key
    report = {"mode": "live_groq_ui", "recipe_count": len(json.loads((ROOT / "data" / "recipes.json").read_text(encoding="utf-8"))), "cases": []}
    try:
        app = AppTest.from_file(str(ROOT / "chef_ui.py"), default_timeout=90).run()
        app.radio[0].set_value("Groq").run()
        typed_questions = {"convert": "Hoeveel kilogram is 250 gram?", "diet": "Welke recepten bevatten geen zuivel?"}
        for demo in ("search", "scale", *typed_questions):
            if demo in typed_questions:
                app.chat_input[0].set_value(typed_questions[demo]).run(timeout=90)
            else:
                app.button(key=demo).click().run(timeout=90)
            if app.exception:
                raise RuntimeError("De interface gaf een niet-afgevangen fout.")
            state = app.session_state["messages"][-1]
            calls = state.get("llm_calls", [])
            row = {
                "question": state["question"], "route": state.get("route"),
                "answer": state.get("answer"), "error": state.get("error"),
                "trace": state.get("trace", []), "source_count": len(state.get("hits", [])),
                "latency_ms": state.get("latency_ms"), "llm_calls": calls,
                "displayed_metrics": [metric.value for metric in app.metric[-4:]],
            }
            if demo == "search":
                row["checks"] = {
                    "search_route": state.get("route") == "search",
                    "source_has_4_servings": any("Porties: 4" in hit["text"] for hit in state.get("hits", [])),
                    "answer_has_correct_quantity": re.search(r"(?<!\d)4\s+(?:porties|personen)", state.get("answer", "")) is not None,
                    "answer_ttft_measured": any(call.get("stage") == "answer" and call.get("ttft_ms") is not None for call in calls),
                }
            elif demo == "scale":
                water = next((item for item in state.get("tool_result", {}).get("ingredients", []) if item["name"] == "water"), {})
                row["checks"] = {"scale_route": state.get("route") == "scale_recipe", "water_is_735_ml": water.get("quantity") == "735"}
            elif demo == "convert":
                result = state.get("tool_result", {})
                row["checks"] = {
                    "convert_route": state.get("route") == "convert_quantity",
                    "conversion_is_0_25_kg": result.get("unit") == "kg" and Decimal(result["amount"]) == Decimal("0.25"),
                    "tool_is_convert_units": state.get("tool_name") == "convert_units",
                }
            else:
                hits = state.get("hits", [])
                row["checks"] = {
                    "diet_search_route": state.get("route") == "search" and state.get("diet") == "zuivelvrij",
                    "three_distinct_vegan_recipes": len({hit["recipe_id"] for hit in hits}) == 3
                    and all("veganistisch" in hit["dietary_tags"] for hit in hits),
                    "source_titles_in_answer": all(hit["title"] in state.get("answer", "") for hit in hits),
                    "only_router_called": [call.get("stage") for call in calls] == ["route"],
                }
            row["checks"]["tokens_measured"] = bool(calls) and all(call.get("prompt_tokens") is not None and call.get("completion_tokens") is not None for call in calls)
            row["checks"]["no_ui_error"] = not state.get("error")
            report["cases"].append(row)
            print(f"Live {demo}: {json.dumps(row['checks'])}", flush=True)

        report["passed"] = all(all(row["checks"].values()) for row in report["cases"])
        # De sleutel is nooit onderdeel van de te bewaren meetuitvoer.
        output = json.dumps(report, ensure_ascii=False, indent=2)
        if key in output:
            raise RuntimeError("Uitvoer is niet opgeslagen: onverwachte sleutel in de resultaten.")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
        print("Live controle geslaagd." if report["passed"] else "Live controle bevat open punten; zie het lokale meetrapport.")
        return 0 if report["passed"] else 1
    finally:
        os.environ.pop("GROQ_API_KEY", None)


if __name__ == "__main__":
    sys.exit(main())
