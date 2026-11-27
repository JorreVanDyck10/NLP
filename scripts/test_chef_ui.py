"""Interfacechecks zonder model of API: python scripts/test_chef_ui.py."""

import copy
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chef_ui import MODES, SEARCH_QUESTION, example_state, recipes


class InterfaceTests(unittest.TestCase):
    def test_example_keeps_curry_when_dataset_order_changes(self):
        reordered = list(reversed(recipes()))
        with patch("chef_ui.recipes", return_value=reordered):
            state = example_state(SEARCH_QUESTION)
        self.assertEqual(state["hits"][0]["recipe_id"], "kikkererwten-groentecurry")
        self.assertIn("420 ml water", state["hits"][0]["text"])

    def app(self):
        app = AppTest.from_file(str(ROOT / "chef_ui.py"), default_timeout=15).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_examples_show_search_scale_history_and_clear(self):
        app = self.app()
        app.radio[0].set_value(MODES[2]).run()
        app.button(key="search").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("420 ml", app.session_state["messages"][0]["answer"])
        self.assertTrue(any("Gesimuleerd voorbeeld" in warning.value for warning in app.warning))
        self.assertEqual([metric.value for metric in app.metric], ["1250 ms", "180", "24"])
        app.button(key="scale").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.chat_message), 4)
        result = app.session_state["messages"][1]
        water = next(item for item in result["tool_result"]["ingredients"] if item["name"] == "water")
        self.assertEqual(water["quantity"], "735")
        self.assertEqual(result["tool_input"]["from_servings"], 4)
        self.assertEqual(result["tool_input"]["to_servings"], 7)
        app.button(key="clear").click().run()
        self.assertEqual(len(app.session_state["messages"]), 0)
        self.assertEqual(len(app.chat_message), 0)

    def test_missing_groq_key_is_visible_without_losing_question(self):
        with patch.dict(os.environ, {}, clear=True):
            app = self.app()
            app.radio[0].set_value("Groq").run()
            app.chat_input[0].set_value(SEARCH_QUESTION).run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("GROQ_API_KEY ontbreekt", app.error[0].value)
        self.assertEqual(app.session_state["messages"][0]["question"], SEARCH_QUESTION)
        self.assertEqual(len(app.metric), 0)

    def test_missing_measurements_are_not_zero(self):
        app = self.app()
        state = example_state(SEARCH_QUESTION)
        state.update(mode="Lokaal", llm_calls=[])
        app.session_state["messages"] = [state]
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual([metric.value for metric in app.metric], ["1250 ms", "Niet gemeten", "Niet gemeten"])
        self.assertTrue(any("Geen taalmodel aangeroepen" in info.value for info in app.info))

    def test_partial_measurements_are_not_a_complete_total(self):
        app = self.app()
        state = example_state(SEARCH_QUESTION)
        state["mode"] = "Groq"
        second = copy.deepcopy(state["llm_calls"][0])
        second.update(prompt_tokens=None, ttft_ms=None)
        state["llm_calls"].append(second)
        app.session_state["messages"] = [state]
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[1].value, "Niet gemeten")
        self.assertEqual(app.metric[2].value, "48")
        self.assertTrue(any("gedeeltelijk" in info.value for info in app.info))

    def test_mode_switch_keeps_original_provenance(self):
        app = self.app()
        app.radio[0].set_value(MODES[2]).run()
        app.button(key="scale").click().run()
        app.radio[0].set_value("Lokaal").run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("Gesimuleerd voorbeeld" in warning.value for warning in app.warning))
        self.assertEqual(app.session_state["messages"][0]["mode"], MODES[2])

    def test_agent_failure_keeps_question_and_hides_raw_error(self):
        async def failing_agent(question, api_key):
            raise RuntimeError("Interne verbinding: gevoelig-testdetail")

        with patch.dict(sys.modules, {"chef_agent": SimpleNamespace(run=failing_agent)}):
            app = self.app()
            app.chat_input[0].set_value(SEARCH_QUESTION).run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("kon de aanvraag niet afronden", app.error[0].value)
        self.assertNotIn("gevoelig-testdetail", app.error[0].value)
        self.assertEqual(app.session_state["messages"][0]["question"], SEARCH_QUESTION)
        self.assertEqual(len(app.metric), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
