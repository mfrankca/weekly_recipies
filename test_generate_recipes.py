"""Offline integration tests; no credentials or model requests required."""
from datetime import date
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import generate_recipes as generator


def day_fixture(label, cuisine):
    return {"day": label, "cuisine": cuisine, "flag": "XX", "meals": [
        {"type": kind, "servings": 4, "name": f"{label} {kind} dish",
         "subtitle": "Fixture", "time": "Prep 5 min; cook 10 min; total 15 min",
         "ingredients": ["400 g test ingredient"], "method": ["Prepare the ingredient."],
         "nutrition": {"kcal": 400, "protein": 20, "carbs": 40, "fat": 18},
         "drink": "Water" if kind == "DINNER" else None}
        for kind in ["BREAKFAST", "LUNCH", "DINNER"]]}


def support_fixture():
    return {"SHOPPING": {"Produce": ["1 kg test ingredient"]},
            "BUDGET": [["TOTAL (4 people)", "$100–120"]],
            "MEAL_PREP": [["Monday", ["Prepare ingredients."]]],
            "LEFTOVERS": [["Monday dinner", "Optional lunch", "Reheat."]]}


class GenerationTests(unittest.TestCase):
    def make_plan(self):
        return {**support_fixture(), "WEEK": "September 7–13, 2026",
                "DAYS": [day_fixture(day, cuisine) for day, cuisine in zip(generator.DAYS, generator.CUISINES[:7])]}

    def test_smaller_requests_and_renderer_totals(self):
        responses = [(meal, "test/free") for d in self.make_plan()["DAYS"] for meal in d["meals"]]
        responses.append((support_fixture(), "test/free"))
        with patch.object(generator, "ask_json", side_effect=responses) as request:
            plan = generator.generate("test-key", date(2026, 9, 7), generator.CUISINES[:7])
        self.assertEqual(request.call_count, 22)
        rendered = generator.renderer_data(plan)
        self.assertEqual(len(rendered["MACRO_DATA"]), 21)
        self.assertEqual(rendered["DAYS"][0]["kcal"], "~1200")
        self.assertEqual(rendered["MACRO_DATA"][0][3:], (400, 20, 40, 18))
        self.assertNotIn("MACRO_DATA", plan)

    def test_duplicate_dish_and_missing_method_rejected(self):
        plan = self.make_plan()
        plan["DAYS"][1]["meals"][0]["name"] = plan["DAYS"][0]["meals"][0]["name"]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            generator.validate_plan(plan)
        plan = self.make_plan()
        plan["DAYS"][0]["meals"][0]["method"] = []
        with self.assertRaisesRegex(ValueError, "method"):
            generator.validate_plan(plan)

    def test_free_only_request(self):
        response = {"choices": [{"finish_reason": "stop", "message": {"content": '{"ok": true}'}}], "model": "test/free"}
        with patch.object(generator, "urlopen", return_value=io.BytesIO(json.dumps(response).encode())) as opener:
            self.assertEqual(generator.ask_json("test-key", "Test prompt")[0], {"ok": True})
        request = opener.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "openrouter/free")
        self.assertFalse(payload["reasoning"]["enabled"])
        self.assertNotIn("models", payload)
        self.assertEqual(request.full_url, generator.ENDPOINT)

    def test_quota_failure_does_not_retry_or_expose_error_body(self):
        error = HTTPError(generator.ENDPOINT, 429, "private response text", {}, None)
        with patch.object(generator, "urlopen", side_effect=error) as opener:
            with self.assertRaisesRegex(ValueError, "HTTP 429") as caught:
                generator.ask_json("test-key", "Test prompt")
        self.assertEqual(opener.call_count, 1)
        self.assertNotIn("private", str(caught.exception))

    def test_recipe_request_requires_string_timing(self):
        response = {"choices": [{"finish_reason": "stop", "message": {"content": "{}"}}]}
        with patch.object(generator, "urlopen", return_value=io.BytesIO(json.dumps(response).encode())) as opener:
            generator.ask_json("test-key", "Recipe", schema=generator.meal_schema("DINNER"))
        response_format = json.loads(opener.call_args.args[0].data)["response_format"]
        self.assertEqual(response_format["type"], "json_schema")
        self.assertTrue(response_format["json_schema"]["strict"])
        self.assertEqual(response_format["json_schema"]["schema"]["properties"]["time"], {"type": "string"})

    def test_separate_timing_fields_preserved(self):
        meal = generator.normalize_meal({"time": {"prep": "15 min", "cook": "30 min", "total": "45 min"}})
        self.assertEqual(meal["time"], "Prep: 15 min | Cook: 30 min | Total: 45 min")

    def test_truncated_response_rejected(self):
        response = {"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]}
        with patch.object(generator, "urlopen", side_effect=lambda *a, **k: io.BytesIO(json.dumps(response).encode())) as opener:
            with self.assertRaisesRegex(ValueError, "incomplete"):
                generator.ask_json("test-key", "Test prompt")
        self.assertEqual(opener.call_count, 3)

    def test_malformed_then_valid_response_recovers(self):
        values = ["not json", '```json\n{"ok": true}\n```']
        responses = [io.BytesIO(json.dumps({"choices": [{"finish_reason": "stop", "message": {"content": value}}]}).encode()) for value in values]
        with patch.object(generator, "urlopen", side_effect=responses) as opener:
            self.assertEqual(generator.ask_json("test-key", "Test")[0], {"ok": True})
        self.assertEqual(opener.call_count, 2)

    def test_nutrition_units_normalized_without_inventing_values(self):
        meal = generator.normalize_meal({"nutrition": {"protein": "20 g", "carbs": "~30g", "fat": "unknown", "kcal": "400 kcal"}})
        self.assertEqual(meal["nutrition"], {"protein": 20.0, "carbs": 30.0, "fat": "unknown", "kcal": 400.0})


if __name__ == "__main__":
    unittest.main()
