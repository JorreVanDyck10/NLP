"""Groq-protocol en UI samen testen met gesimuleerde HTTP-responsen, zonder sleutel."""

import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import httpx
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import chef_agent
from recipe_search import RecipeSearch


class GroqInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        store = RecipeSearch()
        try:
            store.build("sections")
        finally:
            store.close()

    def app(self, handler):
        original = chef_agent.groq_client
        client_patch = patch("chef_agent.groq_client", lambda key: original(key, transport=httpx.MockTransport(handler)))
        client_patch.start()
        self.addCleanup(client_patch.stop)
        env_patch = patch.dict(os.environ, {"GROQ_API_KEY": "gesimuleerde-testkey"})
        env_patch.start()
        self.addCleanup(env_patch.stop)
        app = AppTest.from_file(str(ROOT / "chef_ui.py"), default_timeout=60).run()
        app.radio[0].set_value("Groq").run()
        return app

    def response(self, request, *, omit_usage=False):
        body = json.loads(request.content)
        if body.get("response_format"):
            route = "scale_recipe" if "Schaal" in body["messages"][-1]["content"] else "search"
            return httpx.Response(200, json={
                "choices": [{"message": {"content": json.dumps({"route": route})}}],
                "usage": {} if omit_usage else {"prompt_tokens": 120, "completion_tokens": 8},
            })
        events = [
            {"choices": [{"delta": {"content": "De kikkererwtencurry is bedoeld voor "}}]},
            {"choices": [{"delta": {"content": "4 porties."}}]},
            {"choices": [], "usage": {} if omit_usage else {"prompt_tokens": 180, "completion_tokens": 24}},
        ]
        data = "".join(f"data: {json.dumps(event)}\n\n" for event in events) + "data: [DONE]\n\n"
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, content=data)

    def test_search_uses_real_agent_and_displays_stream_measurements(self):
        app = self.app(self.response)
        app.button(key="search").click().run(timeout=60)
        self.assertEqual(len(app.exception), 0)
        state = app.session_state["messages"][-1]
        self.assertNotIn("error", state)
        self.assertTrue(state["hits"])
        self.assertEqual(len(state["llm_calls"]), 2)
        self.assertEqual(len(state["trace"]), 2)
        self.assertIn("4 porties", state["answer"])
        self.assertEqual(app.metric[1].value, "300")
        self.assertEqual(app.metric[2].value, "32")
        self.assertNotEqual(app.metric[3].value, "Niet gemeten")
        self.assertNotIn("gesimuleerde-testkey", str(app.session_state["messages"]))

    def test_scale_uses_real_mcp_and_does_not_invent_answer_ttft(self):
        app = self.app(self.response)
        app.button(key="scale").click().run(timeout=60)
        self.assertEqual(len(app.exception), 0)
        state = app.session_state["messages"][-1]
        self.assertNotIn("error", state)
        water = next(item for item in state["tool_result"]["ingredients"] if item["name"] == "water")
        self.assertEqual(water["quantity"], "735")
        original_water = next(item for item in state["tool_input"]["ingredients"] if item["name"] == "water")
        self.assertEqual(original_water["quantity"], 420)
        table = app.dataframe[0].value
        water_row = table[table["Ingrediënt"] == "water"].iloc[0]
        self.assertEqual(water_row["Van"], "420 ml")
        self.assertEqual(water_row["Naar"], "735 ml")
        self.assertEqual(app.metric[1].value, "120")
        self.assertEqual(app.metric[2].value, "8")
        self.assertEqual(app.metric[3].value, "Niet gemeten")

    def test_answer_failure_keeps_completed_sources_and_route_metrics(self):
        def handler(request):
            if json.loads(request.content).get("stream"):
                return httpx.Response(503, text="geheim testdetail")
            return self.response(request)

        app = self.app(handler)
        app.button(key="search").click().run(timeout=60)
        self.assertEqual(len(app.exception), 0)
        state = app.session_state["messages"][-1]
        self.assertTrue(state["hits"])
        self.assertIn("503", app.error[0].value)
        self.assertNotIn("geheim testdetail", str(app.session_state["messages"]))
        self.assertNotIn("answer", state)
        self.assertEqual(app.metric[1].value, "120")
        self.assertEqual(app.metric[3].value, "Niet gemeten")

    def test_missing_provider_usage_is_not_displayed_as_zero(self):
        app = self.app(lambda request: self.response(request, omit_usage=True))
        app.button(key="search").click().run(timeout=60)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.metric[1].value, "Niet gemeten")
        self.assertEqual(app.metric[2].value, "Niet gemeten")
        self.assertNotEqual(app.metric[3].value, "Niet gemeten")

    def test_known_recipe_overrides_incorrect_route_and_uses_sourced_total(self):
        def handler(request):
            self.assertTrue(json.loads(request.content).get("response_format"))
            return httpx.Response(200, json={
                "choices": [{"message": {"content": '{"route":"scale_quantity"}'}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 4},
            })

        app = self.app(handler)
        app.button(key="source_check").click().run(timeout=60)
        state = app.session_state["messages"][-1]
        self.assertNotIn("error", state)
        self.assertEqual(state["route"], "search")
        self.assertIn("routecontrole: scale_quantity → search", state["trace"])
        self.assertIn("420 ml water", state["answer"])
        self.assertEqual(len(state["llm_calls"]), 1)
        self.assertFalse(state.get("tool_result"))

    def test_mcp_failure_preserves_route_and_sources(self):
        app = self.app(self.response)
        with patch("chef_agent.call_mcp_tool", side_effect=chef_agent.McpToolError(chef_agent.MCP_ERROR)):
            app.button(key="scale").click().run(timeout=60)
        state = app.session_state["messages"][-1]
        self.assertEqual(state["route"], "scale_recipe")
        self.assertTrue(state["hits"])
        self.assertIn("Controleer de lokale MCP-server", state["error"])
        self.assertFalse(state.get("tool_result"))
        self.assertEqual(app.metric[-3].value, "120")

    def test_invalid_key_rate_limit_and_timeout_give_recovery_advice(self):
        app = self.app(self.response)
        for code, expected in ((401, "weigert de sleutel"), (429, "gebruikslimiet")):
            with self.subTest(status=code):
                def handler(request):
                    return httpx.Response(code, text="geheim testdetail")

                # Dit vervangt tijdelijk de al gemockte factory; geen echte HTTP-aanroep.
                with patch("chef_agent.groq_client", lambda key: httpx.AsyncClient(
                    base_url="https://api.groq.com/openai/v1/", transport=httpx.MockTransport(handler)
                )):
                    app.button(key="search").click().run(timeout=60)
                self.assertEqual(len(app.exception), 0)
                state = app.session_state["messages"][-1]
                self.assertIn(expected, state["error"])
                self.assertNotIn("geheim testdetail", str(state))
                self.assertFalse(state.get("tool_result"))

        def timeout(request):
            raise httpx.ReadTimeout("geheim testdetail")

        with patch("chef_agent.groq_client", lambda key: httpx.AsyncClient(
            base_url="https://api.groq.com/openai/v1/", transport=httpx.MockTransport(timeout)
        )):
            app.button(key="search").click().run(timeout=60)
        self.assertIn("kon de aanvraag niet afronden", app.session_state["messages"][-1]["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
