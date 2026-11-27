"""Echte lokale keten 1 + 2 + 4; vereist requirements-ui.txt en embeddingmodel."""

from decimal import Decimal
import json
from pathlib import Path
import sys
import unittest

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from recipe_search import RecipeSearch, STRATEGIES, load_recipes


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipes = {recipe["id"]: recipe for recipe in load_recipes()}
        store = RecipeSearch()
        try:
            for strategy in STRATEGIES:
                store.build(strategy)
        finally:
            store.close()

    def app(self):
        app = AppTest.from_file(str(ROOT / "chef_ui.py"), default_timeout=60).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def ask(self, app, question):
        app.chat_input[0].set_value(question).run(timeout=60)
        self.assertEqual(len(app.exception), 0)
        state = app.session_state["messages"][-1]
        self.assertNotIn("error", state, state.get("error"))
        self.assertEqual(state["mode"], "Lokaal")
        self.assertGreaterEqual(state["latency_ms"], 0)
        self.assertEqual(state["llm_calls"], [])
        return state

    def test_search_from_interface_returns_correct_source_and_amount(self):
        app = self.app()
        cases = [
            {"question": "Hoeveel water gaat er in totaal in de curry?", "recipe_id": "kikkererwten-groentecurry", "evidence": [["420 ml water"]]},
            {"question": "Hoeveel ricotta heb ik nodig voor de lasagne?", "recipe_id": "slowcooker-lasagne", "evidence": [["475 g magere ricotta"]]},
            {"question": "Hoeveel melk gaat er in de pannenkoeken?", "recipe_id": "aardbeienpannenkoeken", "evidence": [["375 ml magere melk"]]},
        ]
        cases += json.loads((ROOT / "data" / "retrieval_checks.json").read_text(encoding="utf-8"))
        for case in cases:
            recipe_id = case["recipe_id"]
            with self.subTest(recipe=recipe_id):
                state = self.ask(app, case["question"])
                self.assertEqual(state["route"], "search")
                self.assertTrue(state["hits"])
                correct = [hit for hit in state["hits"] if hit["recipe_id"] == recipe_id]
                for group in case["evidence"]:
                    self.assertTrue(any(phrase in hit["text"] for phrase in group for hit in correct), case)
                self.assertTrue(all(hit["source_url"] == self.recipes[hit["recipe_id"]]["source_url"] for hit in state["hits"]))
                self.assertFalse(state.get("tool_result"))
        self.assertEqual(len(app.chat_message), 2 * len(cases))

    def test_search_then_real_mcp_scales_all_ingredients(self):
        app = self.app()
        for recipe_id, recipe in self.recipes.items():
            target = recipe["servings"] + 1
            with self.subTest(recipe=recipe_id):
                state = self.ask(app, f"Schaal {recipe['title']} naar {target} porties.")
                self.assertEqual(state["route"], "scale_recipe")
                self.assertTrue(state["hits"])
                self.assertEqual(state["hits"][0]["recipe_id"], recipe_id)
                self.assertIn("MCP: scale_ingredients", state["trace"])
                self.assertEqual(state["tool_input"]["ingredients"], recipe["ingredients"])
                self.assertEqual(state["tool_result"]["from_servings"], recipe["servings"])
                self.assertEqual(state["tool_result"]["to_servings"], target)
                scaled = state["tool_result"]["ingredients"]
                self.assertEqual(len(scaled), len(recipe["ingredients"]))
                for original, actual in zip(recipe["ingredients"], scaled, strict=True):
                    self.assertEqual(actual["name"], original["name"])
                    self.assertEqual(actual["unit"], original.get("unit"))
                    self.assertEqual(actual["note"], original.get("note"))
                    if "quantity" in original:
                        expected = Decimal(str(original["quantity"])) * target / recipe["servings"]
                        self.assertEqual(Decimal(actual["quantity"]), expected)
                    else:
                        self.assertIsNone(actual["quantity"])

    def test_direct_tool_and_chat_routes(self):
        app = self.app()
        state = self.ask(app, "Schaal 2,5 g van 4 naar 6 porties.")
        self.assertEqual(state["route"], "scale_quantity")
        self.assertEqual(Decimal(state["tool_result"]["ingredients"][0]["quantity"]), Decimal("3.75"))
        self.assertFalse(state.get("hits"))
        state = self.ask(app, "Hallo!")
        self.assertEqual(state["route"], "chat")
        self.assertFalse(state.get("hits"))
        self.assertFalse(state.get("tool_result"))

    def test_invalid_servings_and_unknown_recipe_do_not_run_tool(self):
        app = self.app()
        for question in ("Schaal 200 g van 0 naar 6 porties.", "Schaal de curry naar 0 porties.", "Schaal de pizza naar 6 porties."):
            with self.subTest(question=question):
                state = self.ask(app, question)
                self.assertFalse(state.get("tool_result"))
                self.assertFalse(state.get("tool_input"))
                self.assertTrue(state["answer"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
