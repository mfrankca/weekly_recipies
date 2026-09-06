"""Generate a fresh weekly menu through OpenRouter's free-only router.

Uses Python's standard library. Never reads recipients, credentials files or
previous menus. Produces JSON for review and menu_plan_v2.py --plan.
"""

import argparse
from datetime import date, timedelta
import json
import os
from pathlib import Path
import random
import re
import sys
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
MODEL = "openrouter/free"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
CUISINES = [
    "Greek", "Japanese", "Thai", "Spanish", "Ethiopian", "Turkish", "French",
    "Italian", "Mexican", "Indian", "Moroccan", "Lebanese", "Korean", "Vietnamese",
    "Persian", "Georgian", "Peruvian", "Brazilian", "Indonesian", "Malaysian",
    "Portuguese", "Hungarian", "Polish", "Jamaican", "Egyptian", "Filipino",
    "Tunisian", "Nepalese", "Sri Lankan", "Uzbek",
]


def meal_schema(kind):
    properties = {
        "type": {"type": "string", "enum": [kind]},
        "servings": {"type": "integer", "enum": [4]},
        **{name: {"type": "string"} for name in ["name", "subtitle", "time"]},
        **{name: {"type": "array", "items": {"type": "string"}} for name in ["ingredients", "method"]},
        "nutrition": {"type": "object", "properties": {
            name: {"type": "number"} for name in ["kcal", "protein", "carbs", "fat"]},
            "required": ["kcal", "protein", "carbs", "fat"], "additionalProperties": False},
        "drink": {"type": "string" if kind == "DINNER" else ["string", "null"]},
    }
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


class ModelOutputError(ValueError):
    """A completed API request whose model output cannot be consumed."""


class RequestCompatibilityError(ValueError):
    """The provider explicitly rejected optional formatting/reasoning settings."""


def api_error_detail(exc, key):
    """Extract error messages only, redact credentials, never print raw bodies."""
    messages = []
    try:
        payload = json.loads(exc.read(16384))
        error = payload.get("error", {}) if isinstance(payload, dict) else {}
        if isinstance(error, dict):
            if isinstance(error.get("message"), str):
                messages.append(error["message"])
            metadata = error.get("metadata", {})
            raw = metadata.get("raw") if isinstance(metadata, dict) else None
            if isinstance(raw, str):
                try:
                    raw = json.loads(raw)
                except ValueError:
                    raw = None
            if isinstance(raw, dict):
                nested = raw.get("error", raw)
                if isinstance(nested, dict) and isinstance(nested.get("message"), str):
                    messages.append(nested["message"])
    except (ValueError, OSError, TypeError):
        pass
    detail = " | ".join(messages)
    if key:
        detail = detail.replace(key, "[redacted]")
    detail = re.sub(r"(?i)bearer\s+\S+|sk-or-[A-Za-z0-9_-]+", "[redacted]", detail)
    return " ".join(detail.split())[:700] or "The provider supplied no readable error explanation."


def ask_json(key, prompt, schema=None, validator=None):
    compatibility = False
    for attempt in range(3):
        try:
            if compatibility:
                parsed, model = _ask_json_once(key, prompt, schema, compatibility=True)
            else:
                parsed, model = _ask_json_once(key, prompt, schema)
            if validator:
                try:
                    parsed = validator(parsed)
                except ValueError as exc:
                    raise ModelOutputError(f"Invalid model output: {exc}") from exc
            return parsed, model
        except RequestCompatibilityError as exc:
            if compatibility or attempt == 2:
                raise
            compatibility = True
            print(f"{exc}\nRetrying with basic JSON instructions on the free router; recipe validation remains enabled.", flush=True)
        except ModelOutputError:
            if attempt == 2:
                raise
            print("Model output was incomplete or malformed; retrying this request on the free router.", flush=True)


def _ask_json_once(key, prompt, schema=None, compatibility=False):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You write complete, practical recipes. Return only valid JSON, without Markdown. All text values must be plain text, not HTML."},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 9000,
        "reasoning": {"enabled": False},
    }
    if schema:
        payload["response_format"] = {"type": "json_schema", "json_schema": {
            "name": "recipe", "strict": True, "schema": schema}}
    if compatibility:
        payload.pop("response_format", None)
        payload.pop("reasoning", None)
        if schema:
            payload["messages"][1]["content"] += "\nReturn JSON matching this schema: " + json.dumps(schema)
    request = Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
    })
    try:
        with urlopen(request, timeout=180) as response:
            result = json.load(response)
    except HTTPError as exc:
        detail = api_error_detail(exc, key)
        message = f"Free-model request failed (HTTP {exc.code}): {detail}"
        if exc.code == 400 and re.search(r"reasoning|json_schema|response_format|structured output", detail, re.I) and re.search(r"unsupported|not support|cannot|must|invalid|mandatory|disable|not allowed", detail, re.I):
            raise RequestCompatibilityError(message) from None
        raise ValueError(message + " No paid model was used.") from None
    except (URLError, TimeoutError) as exc:
        raise ValueError(f"Free-model connection failed ({type(exc).__name__}); no fallback was used.") from None
    choices = result.get("choices") or []
    if not choices or choices[0].get("finish_reason") != "stop":
        reason = choices[0].get("finish_reason", "unknown") if choices else "no choices"
        raise ModelOutputError(f"Free model returned an incomplete or unsuccessful response (finish reason: {reason}); no complete plan was saved.")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str):
        raise ModelOutputError("Free model returned no JSON text.")
    content = content.strip()
    if content.startswith("```") and content.endswith("```"):
        content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        raise ModelOutputError("Free model returned invalid JSON; no complete plan was saved.") from None
    if not isinstance(parsed, dict):
        raise ModelOutputError("Expected a JSON object from the free model.")
    return parsed, result.get("model", MODEL)


def require_text(value, label):
    if not isinstance(value, str) or not value.strip() or "<" in value or ">" in value:
        raise ValueError(f"{label} must be nonempty plain text (received {type(value).__name__}: {str(value)[:100]!r}).")


def normalize_meal(meal):
    """Preserve timing detail when a provider ignores the string schema."""
    if isinstance(meal, dict) and isinstance(meal.get("drink"), dict):
        drink = meal["drink"]
        if drink and all(isinstance(v, str) and v.strip() for v in drink.values()):
            meal["drink"] = " | ".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in drink.items())
    if isinstance(meal, dict) and isinstance(meal.get("time"), dict):
        timing = meal["time"]
        if timing and all(isinstance(v, (str, int, float)) and not isinstance(v, bool) for v in timing.values()):
            meal["time"] = " | ".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in timing.items())
    if isinstance(meal, dict) and isinstance(meal.get("nutrition"), dict):
        nutrition = meal["nutrition"]
        for field in ["protein", "carbs", "fat"]:
            if field not in nutrition and field + "_g" in nutrition:
                nutrition[field] = nutrition[field + "_g"]
        for field in ["kcal", "protein", "carbs", "fat"]:
            value = nutrition.get(field)
            if isinstance(value, str):
                match = re.fullmatch(r"\s*~?\s*(\d+(?:\.\d+)?)\s*(?:g|kcal)?\s*", value)
                if match:
                    nutrition[field] = float(match.group(1))
    return meal


def require_list(value, label):
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a nonempty list.")


def dish_key(name):
    return " ".join(name.casefold().split())


def validate_generated_meal(meal, kind, existing_names=()):
    meal = normalize_meal(meal)
    validate_meal(meal, kind)
    if dish_key(meal["name"]) in {dish_key(name) for name in existing_names}:
        raise ValueError(f"Duplicate dish: {meal['name']}. Choose a different dish, not a renamed version.")
    return meal


def validate_meal(meal, kind):
    if not isinstance(meal, dict) or meal.get("type") != kind or meal.get("servings") != 4:
        raise ValueError("Meals must be breakfast, lunch and dinner, each serving four.")
    for field in ["name", "subtitle", "time"]:
        require_text(meal.get(field), field)
    for field in ["ingredients", "method"]:
        require_list(meal.get(field), field)
        for item in meal[field]:
            require_text(item, field)
    nutrition = meal.get("nutrition")
    if not isinstance(nutrition, dict):
        raise ValueError("Missing per-serving nutrition estimates.")
    for field in ["kcal", "protein", "carbs", "fat"]:
        number = nutrition.get(field)
        if type(number) not in (int, float) or not 0 <= number < 10000:
            raise ValueError(f"Invalid nutrition value: {field} ({number!r}).")
    if nutrition["kcal"] <= 0:
        raise ValueError("Calories must be positive.")
    if kind == "DINNER" or meal.get("drink") is not None:
        require_text(meal.get("drink"), "drink")


def validate_day(day, expected_day, expected_cuisine):
    if not isinstance(day, dict) or day.get("day") != expected_day or day.get("cuisine") != expected_cuisine:
        raise ValueError("Generated day or cuisine does not match the request.")
    require_text(day.get("flag"), "flag")
    meals = day.get("meals")
    if not isinstance(meals, list) or len(meals) != 3:
        raise ValueError("Each day must contain three meals.")
    for meal, kind in zip(meals, ["BREAKFAST", "LUNCH", "DINNER"]):
        validate_meal(meal, kind)


def validate_plan(plan):
    if not isinstance(plan, dict):
        raise ValueError("Plan must be an object.")
    require_text(plan.get("WEEK"), "WEEK")
    days = plan.get("DAYS")
    if not isinstance(days, list) or len(days) != 7:
        raise ValueError("Plan must contain seven days.")
    cuisines, names = set(), set()
    for day, label in zip(days, DAYS):
        if not isinstance(day, dict):
            raise ValueError("Each day must be an object.")
        require_text(day.get("cuisine"), "cuisine")
        validate_day(day, label, day["cuisine"])
        cuisines.add(day["cuisine"].strip().casefold())
        for meal in day["meals"]:
            name = dish_key(meal["name"])
            if name in names:
                raise ValueError("Duplicate dish in the generated week.")
            names.add(name)
    if len(cuisines) != 7:
        raise ValueError("Seven different cuisines are required.")
    shopping = plan.get("SHOPPING")
    if not isinstance(shopping, dict) or not shopping:
        raise ValueError("Missing shopping list.")
    for category, items in shopping.items():
        require_text(category, "shopping category")
        require_list(items, "shopping items")
        for item in items:
            require_text(item, "shopping item")
    for field, width in [("BUDGET", 2), ("MEAL_PREP", 2), ("LEFTOVERS", 3)]:
        require_list(plan.get(field), field)
        for row in plan[field]:
            if not isinstance(row, list) or len(row) != width:
                raise ValueError(f"Invalid {field} row.")
            require_text(row[0], field)
            if field == "MEAL_PREP":
                require_list(row[1], field)
                for item in row[1]:
                    require_text(item, field)
            else:
                for item in row[1:]:
                    require_text(item, field)


def renderer_data(plan):
    """Validate and derive duplicated display totals from numeric meal data."""
    validate_plan(plan)
    plan = json.loads(json.dumps(plan))
    macros = []
    for day in plan["DAYS"]:
        total = 0
        for index, meal in enumerate(day["meals"]):
            n = meal["nutrition"]
            kcal, protein, carbs, fat = [round(n[k]) for k in ("kcal", "protein", "carbs", "fat")]
            total += kcal
            meal["kcal"] = f"~{kcal}"
            meal["macros"] = f"Protein {protein} g | Carbs {carbs} g | Fat {fat} g"
            macros.append((day["day"] if index == 0 else "", day["cuisine"] if index == 0 else "", meal["type"].title(), kcal, protein, carbs, fat))
        day["kcal"] = f"~{total}"
    plan["MACRO_DATA"] = macros
    return plan


def generate(key, monday, cuisines, draft_path=None, resume=None):
    # Only the recipe-detail section is sent; recipient and delivery instructions stay local.
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    details = skill.split("#### Recipe detail standard", 1)[1].split("#### Content checks", 1)[0]
    week = f"{monday:%B %d, %Y} – {monday + timedelta(days=6):%B %d, %Y}"
    if resume and resume.get("WEEK") != week:
        raise ValueError("Resume draft week does not match --week-start.")
    saved_days = resume.get("DAYS", []) if resume else []
    if not isinstance(saved_days, list) or len(saved_days) > 7:
        raise ValueError("Invalid resume draft days.")
    for index, saved in enumerate(saved_days):
        if not isinstance(saved, dict) or saved.get("day") != DAYS[index] or saved.get("cuisine") != cuisines[index]:
            raise ValueError("Resume draft day/cuisine does not match the requested plan.")
        if not isinstance(saved.get("meals"), list) or len(saved["meals"]) > 3:
            raise ValueError("Invalid resume draft meals.")
    batch = uuid.uuid4().hex
    days, models = [], []
    selected_names = []
    for day_index, (label, cuisine) in enumerate(zip(DAYS, cuisines)):
        day = {"day": label, "cuisine": cuisine, "flag": cuisine[:2].upper(), "meals": []}
        saved_meals = saved_days[day_index]["meals"] if day_index < len(saved_days) else []
        for meal_index, kind in enumerate(["BREAKFAST", "LUNCH", "DINNER"]):
            if meal_index < len(saved_meals):
                try:
                    saved_meal = validate_generated_meal(saved_meals[meal_index], kind, selected_names)
                except ValueError as exc:
                    print(f"Replacing saved {label} {kind.lower()}: {exc}", flush=True)
                else:
                    day["meals"].append(saved_meal)
                    selected_names.append(saved_meal["name"])
                    models.append("retained from explicit resume draft")
                    print(f"Keeping {label} {kind.lower()}", flush=True)
                    continue
            print(f"Generating {label}: {cuisine} {kind.lower()}", flush=True)
            prompt = f"""Generate one fresh {cuisine} {kind.lower()} recipe for {label}, week {week}.
Creative batch identifier: {batch}. Explore regional and less-common dishes; do not use a fixed weekly menu rotation.
Four servings per recipe. No pork or shellfish/molluscs/crustaceans; finfish and meat allowed.
Give measured ingredients and complete sequential cooking instructions, not summaries.
Choose a dish different from ALL these already selected this week: {selected_names}.
Do not repeat or merely rename any of them.
Use these recipe requirements: {details}
Return ONE meal object, not a day or a list. It has type ({kind}), servings (4), name, subtitle, time
(prep, cook, marinating if relevant and total elapsed time), ingredients (list of measured plain-text ingredients),
method (list of unnumbered step strings), nutrition (numeric kcal, protein, carbs, fat PER SERVING),
and drink (null except dinner must include a drink pairing with a nonalcoholic option).
Nutrition is estimated. Do not claim recipes are sourced from websites. No HTML or Markdown in values.
"""
            meal, model = ask_json(key, prompt, schema=meal_schema(kind),
                                   validator=lambda value: validate_generated_meal(value, kind, selected_names))
            day["meals"].append(meal)
            selected_names.append(meal["name"])
            models.append(model)
            if draft_path:
                draft_path.write_text(json.dumps({"status": "incomplete draft, not for rendering or delivery",
                    "WEEK": week, "DAYS": days + [day], "models": models,
                    "cuisines": cuisines}, ensure_ascii=False, indent=2), encoding="utf-8")
        validate_day(day, label, cuisine)
        days.append(day)
    print("Generating shopping list, budget and preparation schedule", flush=True)
    support, model = ask_json(key, """For the following seven-day plan, return ONLY these JSON keys:
SHOPPING: object mapping grocery categories to lists of measured items aggregated across all recipes for four servings each;
BUDGET: list of [category, estimated USD cost range] pairs, ending with TOTAL (4 people), Per person / week, Per person / day;
MEAL_PREP: list of [dated heading, list of practical preparation tasks] pairs, anchored to the plan dates;
LEFTOVERS: list of [source meal, optional next use, instructions] triples. Do not replace scheduled meals with leftovers.
Include every ingredient and avoid double counting pantry items. Give cautious, practical storage/freezing/reheating directions.
Plain text only, no HTML. Budget is an estimate, not live store pricing.
Plan: """ + json.dumps({"WEEK": week, "DAYS": days}, ensure_ascii=False))
    plan = {**support, "WEEK": week, "DAYS": days,
            "generation": {"router": MODEL, "models": models + [model], "batch": batch,
                           "week_start": monday.isoformat(), "source": "AI-generated, requires recipe and layout review"}}
    validate_plan(plan)
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week-start", type=date.fromisoformat, help="Target Monday, YYYY-MM-DD; default is the next Monday")
    parser.add_argument("--cuisines", nargs=7, help="Seven distinct cuisines; default: randomly select seven from a broad cuisine list")
    parser.add_argument("--output", type=Path, help="New JSON output path (existing files are never overwritten)")
    parser.add_argument("--resume", type=Path, help="Continue an explicit partial draft, keeping valid distinct recipes")
    args = parser.parse_args()
    monday = args.week_start or date.today() + timedelta(days=(7 - date.today().weekday()) % 7 or 7)
    if monday.weekday() != 0:
        parser.error("--week-start must be a Monday")
    cuisines = args.cuisines or random.SystemRandom().sample(CUISINES, 7)
    resume = None
    if args.resume:
        try:
            resume = json.loads(args.resume.read_text(encoding="utf-8"))
            if not isinstance(resume, dict):
                raise ValueError("Draft must be an object")
            saved_cuisines = resume.get("cuisines") or [day["cuisine"] for day in resume["DAYS"]]
            if not isinstance(saved_cuisines, list) or len(saved_cuisines) != 7 or not all(isinstance(c, str) for c in saved_cuisines):
                raise ValueError("Resume draft must record all seven cuisines")
            if args.cuisines and args.cuisines != saved_cuisines:
                raise ValueError("--cuisines must match the resume draft")
            cuisines = saved_cuisines
        except (ValueError, OSError, KeyError, TypeError) as exc:
            parser.error(f"Cannot resume draft: {exc}")
    if len({c.strip().casefold() for c in cuisines}) != 7 or any(not c.strip() for c in cuisines):
        parser.error("Provide seven distinct, nonempty cuisines")
    output = args.output or ROOT / f"generated_menu_{monday.isoformat()}_{uuid.uuid4().hex[:8]}.json"
    if output.exists():
        parser.error("Output already exists; choose a new path")
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        parser.error("Set OPENROUTER_API_KEY locally first; do not put the key in chat or source files")
    try:
        draft_path = output.with_suffix(".partial.json")
        plan = generate(key, monday, cuisines, draft_path=draft_path, resume=resume)
        with output.open("x", encoding="utf-8") as stream:
            json.dump(plan, stream, ensure_ascii=False, indent=2)
    except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
        print(f"Generation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Menu saved to {output.resolve()}")
    print("Review recipe completeness, quantities and food safety before rendering and sending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
