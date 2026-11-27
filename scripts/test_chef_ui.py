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
        self.assertIn("4 porties", app.session_state["messages"][0]["answer"])
        self.assertTrue(any("Gesimuleerd voorbeeld" in warning.value for warning in app.warning))
        self.assertEqual([metric.value for metric in app.metric], ["1250 ms", "180", "24", "180 ms"])
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
        self.assertTrue(all(metric.value == "Niet gemeten" for metric in app.metric[1:]))

    def test_missing_measurements_are_not_zero(self):
        app = self.app()
        state = example_state(SEARCH_QUESTION)
        state.update(mode="Lokaal", llm_calls=[])
        app.session_state["messages"] = [state]
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual([metric.value for metric in app.metric], ["1250 ms", "Niet gemeten", "Niet gemeten", "Niet gemeten"])
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
        async def failing_agent(question, api_key, on_update=None):
            if on_update:
                on_update({"question": question, "route": "search", "trace": ["router: search"],
                           "llm_calls": [], "latency_ms": 999999})
            raise RuntimeError("Interne verbinding: gevoelig-testdetail")

        with patch.dict(sys.modules, {"chef_agent": SimpleNamespace(run=failing_agent)}):
            app = self.app()
            app.chat_input[0].set_value(SEARCH_QUESTION).run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("kon de aanvraag niet afronden", app.error[0].value)
        self.assertNotIn("gevoelig-testdetail", app.error[0].value)
        self.assertEqual(app.session_state["messages"][0]["question"], SEARCH_QUESTION)
        self.assertEqual(app.session_state["messages"][0]["route"], "search")
        self.assertEqual(app.session_state["messages"][0]["trace"], ["router: search"])
        self.assertLess(app.session_state["messages"][0]["latency_ms"], 999999)
        self.assertTrue(all(metric.value == "Niet gemeten" for metric in app.metric[1:]))

    def test_session_key_is_not_saved_in_messages_and_can_be_cleared(self):
        received = []

        async def fake_agent(question, api_key, on_update=None):
            received.append(api_key)
            state = example_state(question)
            if on_update:
                on_update(state)
            return state

        with patch.dict(os.environ, {}, clear=True), patch.dict(sys.modules, {"chef_agent": SimpleNamespace(run=fake_agent)}):
            app = self.app()
            app.radio[0].set_value("Groq").run()
            app.text_input(key="groq_api_key").set_value("test-sleutel-geen-echte-key").run()
            app.button(key="search").click().run()
            self.assertEqual(received, ["test-sleutel-geen-echte-key"])
            self.assertNotIn("test-sleutel-geen-echte-key", str(app.session_state["messages"]))
            self.assertEqual(len(app.exception), 0)
            app.button(key="clear_key").click().run()
            self.assertEqual(app.text_input(key="groq_api_key").value, "")

    def test_retry_after_failure_keeps_history_and_can_succeed(self):
        attempts = []

        async def intermittent_agent(question, api_key, on_update=None):
            attempts.append(question)
            if len(attempts) == 1:
                raise RuntimeError("tijdelijk niet bereikbaar")
            return example_state(question)

        with patch.dict(sys.modules, {"chef_agent": SimpleNamespace(run=intermittent_agent)}):
            app = self.app()
            app.button(key="search").click().run()
            app.button(key="retry_0").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.session_state["messages"]), 2)
        self.assertTrue(app.session_state["messages"][0].get("error"))
        self.assertNotIn("error", app.session_state["messages"][1])
        self.assertIn("4 porties", app.session_state["messages"][1]["answer"])

    def test_source_control_preserves_model_answer_and_shows_reference(self):
        async def wrong_answer(question, api_key, on_update=None):
            state = example_state(SEARCH_QUESTION)
            state["answer"] = "Er gaat 795 ml water in de curry."
            return state

        with patch.dict(sys.modules, {"chef_agent": SimpleNamespace(run=wrong_answer)}):
            app = self.app()
            app.button(key="source_check").click().run()
        self.assertIn("795 ml", app.session_state["messages"][0]["answer"])
        self.assertTrue(any("420 ml" in info.value and "dubbeltelling" in info.value for info in app.info))

    def test_measured_zero_is_displayed_as_zero(self):
        app = self.app()
        state = example_state(SEARCH_QUESTION)
        state["mode"] = "Groq"
        state["llm_calls"][0].update(prompt_tokens=0, completion_tokens=0, ttft_ms=0)
        app.session_state["messages"] = [state]
        app.run()
        self.assertEqual([metric.value for metric in app.metric[1:]], ["0", "0", "0 ms"])

    def test_missing_answer_ttft_is_distinguished_from_router_ttft(self):
        app = self.app()
        state = example_state(SEARCH_QUESTION)
        state["mode"] = "Groq"
        state["llm_calls"][0]["ttft_ms"] = None
        app.session_state["messages"] = [state]
        app.run()
        self.assertEqual(app.metric[3].value, "Niet gemeten")
        self.assertTrue(any("TTFT ontbreekt" in caption.value and "antwoordaanroep" in caption.value for caption in app.caption))


if __name__ == "__main__":
    unittest.main(verbosity=2)
