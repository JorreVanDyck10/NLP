"""Echte lokale keten 1 + 2 + 4; vereist requirements-ui.txt en embeddingmodel."""

from decimal import Decimal
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
        for question, recipe_id, evidence in (
            ("Hoeveel water gaat er in totaal in de curry?", "kikkererwten-groentecurry", "420 ml water"),
            ("Hoeveel ricotta heb ik nodig voor de lasagne?", "slowcooker-lasagne", "475 g magere ricotta"),
            ("Hoeveel melk gaat er in de pannenkoeken?", "aardbeienpannenkoeken", "375 ml magere melk"),
        ):
            with self.subTest(recipe=recipe_id):
                state = self.ask(app, question)
                self.assertEqual(state["route"], "search")
                self.assertTrue(state["hits"])
                self.assertTrue(all(hit["recipe_id"] == recipe_id for hit in state["hits"]))
                self.assertTrue(any(evidence in hit["text"] for hit in state["hits"]))
                self.assertTrue(all(hit["source_url"] == self.recipes[recipe_id]["source_url"] for hit in state["hits"]))
                self.assertFalse(state.get("tool_result"))
        self.assertEqual(len(app.chat_message), 6)

    def test_search_then_real_mcp_scales_all_ingredients(self):
        app = self.app()
        for recipe_id, alias, target in (
            ("kikkererwten-groentecurry", "curry", 7),
            ("slowcooker-lasagne", "lasagne", 4),
            ("aardbeienpannenkoeken", "pannenkoeken", 2),
        ):
            with self.subTest(recipe=recipe_id):
                state = self.ask(app, f"Schaal de {alias} naar {target} porties.")
                recipe = self.recipes[recipe_id]
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
