"""Echte lokale keten 1 + 2 + 4; vereist requirements-ui.txt en embeddingmodel."""

import asyncio
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chef_agent import build_agent, invoke_agent
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
            {"question": "Waarmee kan ik de bloemkool in de curry vervangen?", "recipe_id": "kikkererwten-groentecurry", "evidence": [["wortel, aubergine, pompoen of broccoli"]]},
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

    def test_mass_conversion_and_invalid_input(self):
        app = self.app()
        for question, to_unit, expected in (
            ("Reken 250 g om naar kg.", "kg", Decimal("0.25")),
            ("Hoeveel g is 0,25 kg?", "g", Decimal(250)),
            ("Hoeveel kilogram is 250 gram?", "kg", Decimal("0.25")),
            ("Hoeveel gram zijn 1,5 kilogram?", "g", Decimal(1500)),
        ):
            with self.subTest(question=question):
                state = self.ask(app, question)
                self.assertEqual(state["route"], "convert_quantity")
                self.assertEqual(state["tool_name"], "convert_units")
                self.assertEqual(state["tool_input"]["to_unit"], to_unit)
                self.assertEqual(state["tool_result"]["unit"], to_unit)
                self.assertEqual(Decimal(state["tool_result"]["amount"]), expected)
                self.assertEqual(len(app.dataframe), 0)
        for question in ("Reken 1 l om naar kg.", "Reken -2 kg om naar g.", "Converteer naar kg."):
            with self.subTest(question=question):
                state = self.ask(app, question)
                self.assertEqual(state["route"], "convert_quantity")
                self.assertFalse(state.get("tool_input"))
                self.assertFalse(state.get("tool_result"))
                self.assertIn("Geef een niet-negatieve hoeveelheid", state["answer"])

    def test_dietary_questions_use_three_distinct_recipes_with_matching_tags(self):
        cases = (
            ("Welke recepten bevatten geen zuivel?", "zuivelvrij", {"veganistisch"}),
            ("Welke gerechten zijn veganistisch?", "veganistisch", {"veganistisch"}),
            ("Welke vegetarische recepten hebben jullie?", "vegetarisch", {"vegetarisch", "veganistisch"}),
        )
        for strategy in STRATEGIES:
            agent = build_agent(strategy=strategy)
            for question, diet, tags in cases:
                with self.subTest(strategy=strategy, diet=diet):
                    state = asyncio.run(invoke_agent(agent, question))
                    self.assertEqual(state["route"], "search")
                    self.assertIn(f"Dieetfilter: {diet}", state["trace"])
                    self.assertEqual(len({hit["recipe_id"] for hit in state["hits"]}), 3)
                    for hit in state["hits"]:
                        recipe = self.recipes[hit["recipe_id"]]
                        self.assertTrue(tags.intersection(recipe["dietary_tags"]))
                        self.assertIn(hit["title"], state["answer"])
                        self.assertIn(recipe["source_url"], state["answer"])
            with self.subTest(strategy=strategy, diet="recipe-specific"):
                state = asyncio.run(invoke_agent(agent, "Is het recept voor yoghurtcake veganistisch?"))
                self.assertNotIn("diet", state)
                self.assertEqual({hit["recipe_id"] for hit in state["hits"]}, {"yoghurtcake"})

    def test_quoted_unknown_recipe_rejects_unrelated_sources(self):
        app = self.app()
        state = self.ask(app, 'Staat het recept “Saffraan-venkelterrine” in jullie collectie?')
        self.assertEqual(state["route"], "search")
        self.assertEqual(state["answer"], "Ik vind dit recept niet in de collectie.")
        self.assertFalse(state.get("hits"))
        self.assertFalse(state.get("tool_result"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
