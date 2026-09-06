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

    def test_actual_provider_nutrition_aliases(self):
        meal = day_fixture("Tuesday", "Filipino")["meals"][2]
        meal["nutrition"] = {"kcal": 645, "protein_g": 42, "carbs_g": 58, "fat_g": 24}
        validated = generator.validate_generated_meal(meal, "DINNER")
        self.assertEqual([validated["nutrition"][k] for k in ["protein", "carbs", "fat"]], [42, 58, 24])

    def test_structured_drink_preserves_all_instructions(self):
        meal = generator.normalize_meal({"drink": {"name": "Cooler", "nonalcoholic_option": "Mix 30 ml juice with 200 ml water.", "serving_note": "Serve over ice."}})
        self.assertEqual(meal["drink"], "Name: Cooler | Nonalcoholic Option: Mix 30 ml juice with 200 ml water. | Serving Note: Serve over ice.")

    def test_missing_nutrition_retries_only_current_recipe(self):
        good = day_fixture("Monday", "Greek")["meals"][0]
        bad = json.loads(json.dumps(good))
        del bad["nutrition"]["protein"]
        with patch.object(generator, "_ask_json_once", side_effect=[(bad, "free"), (good, "free")]) as request:
            value, _ = generator.ask_json("test-key", "Recipe", validator=lambda meal: generator.validate_generated_meal(meal, "BREAKFAST"))
        self.assertEqual(request.call_count, 2)
        self.assertEqual(value["nutrition"]["protein"], 20)

    def test_missing_nutrition_stops_after_three_attempts(self):
        bad = day_fixture("Monday", "Greek")["meals"][0]
        del bad["nutrition"]["protein"]
        with patch.object(generator, "_ask_json_once", return_value=(bad, "free")) as request:
            with self.assertRaisesRegex(generator.ModelOutputError, "protein"):
                generator.ask_json("test-key", "Recipe", validator=lambda meal: generator.validate_generated_meal(meal, "BREAKFAST"))
        self.assertEqual(request.call_count, 3)

    def test_unsupported_request_settings_retry_without_them(self):
        error_body = {"error": {"message": "Provider returned error", "metadata": {"raw": json.dumps({"error": {"message": "reasoning is mandatory and cannot be disabled"}})}}}
        failure = HTTPError(generator.ENDPOINT, 400, "Bad Request", {}, io.BytesIO(json.dumps(error_body).encode()))
        good = day_fixture("Monday", "Greek")["meals"][0]
        response = {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(good)}}]}
        with patch.object(generator, "urlopen", side_effect=[failure, io.BytesIO(json.dumps(response).encode())]) as opener:
            meal, _ = generator.ask_json("test-key", "Recipe", schema=generator.meal_schema("BREAKFAST"), validator=lambda value: generator.validate_generated_meal(value, "BREAKFAST"))
        self.assertEqual(meal["name"], good["name"])
        retry = json.loads(opener.call_args_list[1].args[0].data)
        self.assertEqual(retry["model"], "openrouter/free")
        self.assertNotIn("reasoning", retry)
        self.assertNotIn("response_format", retry)
        self.assertIn("schema", retry["messages"][1]["content"])

    def test_unknown_400_stops_and_redacts_key(self):
        body = {"error": {"message": "Invalid input test-secret"}}
        failure = HTTPError(generator.ENDPOINT, 400, "Bad Request", {}, io.BytesIO(json.dumps(body).encode()))
        with patch.object(generator, "urlopen", side_effect=failure) as opener:
            with self.assertRaisesRegex(ValueError, "Invalid input") as caught:
                generator.ask_json("test-secret", "Recipe")
        self.assertEqual(opener.call_count, 1)
        self.assertNotIn("test-secret", str(caught.exception))

    def test_duplicate_recipe_retries_before_saving(self):
        bad = day_fixture("Monday", "Greek")["meals"][0]
        good = json.loads(json.dumps(bad))
        good["name"] = "Different dish"
        with patch.object(generator, "_ask_json_once", side_effect=[(bad, "free"), (good, "free")]) as request:
            meal, _ = generator.ask_json("key", "Recipe", validator=lambda value: generator.validate_generated_meal(value, "BREAKFAST", [bad["name"].upper()]))
        self.assertEqual(request.call_count, 2)
        self.assertEqual(meal["name"], "Different dish")

    def test_resume_replaces_only_duplicate_and_rebuilds_support(self):
        draft = self.make_plan()
        draft["WEEK"] = "September 07, 2026 – September 13, 2026"
        draft["DAYS"][6]["meals"][2]["name"] = draft["DAYS"][6]["meals"][1]["name"]
        replacement = day_fixture("Sunday", "French")["meals"][2]
        with patch.object(generator, "ask_json", side_effect=[(replacement, "free"), (support_fixture(), "free")]) as request:
            plan = generator.generate("key", date(2026, 9, 7), generator.CUISINES[:7], resume=draft)
        self.assertEqual(request.call_count, 2)
        self.assertEqual(plan["DAYS"][0]["meals"], draft["DAYS"][0]["meals"])
        self.assertIn(draft["DAYS"][6]["meals"][1]["name"], request.call_args_list[0].args[1])
        generator.validate_plan(plan)

    def test_resume_rejects_wrong_week_without_api_call(self):
        with patch.object(generator, "ask_json") as request:
            with self.assertRaisesRegex(ValueError, "week"):
                generator.generate("key", date(2026, 9, 7), generator.CUISINES[:7], resume=self.make_plan())
        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
