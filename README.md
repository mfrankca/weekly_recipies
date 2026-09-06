# Weekly recipes

Weekly menu plans for Marina and friends: seven cuisines, three meals per day, and recipes serving 3–4 people.

Each weekly run requests fresh recipes from a free AI service across seven different cuisines. It does not read past plans or rotate a saved recipe collection. Fresh model generation does not guarantee that a familiar dish will never recur.

- `SKILL.md` defines the weekly workflow and the required recipe detail. Every meal needs measured ingredients and complete numbered cooking steps in the PDF and email.
- `generate_recipes.py` calls OpenRouter's free-only router, validates the response structure, and saves a fresh JSON menu. It uses only Python's standard library and does not send email.
- `menu_plan_v2.py` contains the current menu data and ReportLab PDF renderer. It renders the data already present; it does not generate new recipes or send email itself.
- `recipients.example.txt` documents the recipient format. Copy it to the ignored `recipients.txt` for local delivery configuration.
- `gmail_mcp/` contains the local email integration and private authentication files; the entire directory is currently ignored by Git.

## Free AI setup and weekly generation

1. Create an OpenRouter account and create an API key on its [Keys page](https://openrouter.ai/settings/keys). The code uses only [`openrouter/free`](https://openrouter.ai/docs/guides/routing/routers/free-router), which routes to available free models. Free quota and availability limits apply; there is no paid fallback.
2. In Windows, open **Edit environment variables for your account**, create a user variable named `OPENROUTER_API_KEY`, and paste the key into its value. Restart the terminal or app that will run the planner so it inherits the variable. Do not paste the key into chat or commit it. The script reads the environment, not `.env` files.
3. With Python installed, run these commands from this folder, replacing the date with the desired Monday:

```powershell
python -u .\generate_recipes.py --week-start 2026-09-07
```

The generator makes 22 requests: one per recipe and one for the shopping list, budget and preparation schedule. Smaller recipe responses reduce truncation risk; reasoning is disabled where supported to leave more room for recipe output. Seven cuisines are selected randomly from a broad cuisine list. To choose them explicitly:

```powershell
python -u .\generate_recipes.py --week-start 2026-09-07 --cuisines "Italian" "Korean" "Moroccan" "Mexican" "Indian" "Georgian" "Peruvian"
```

Review the JSON file printed by the command. It contains measured ingredients, sequential methods and estimated nutrition for four servings. Structure checks catch missing fields and exact duplicate dish names; they do not verify culinary accuracy, food safety, quantities or semantic duplicates. Then render it with ReportLab installed:

```powershell
python -u .\menu_plan_v2.py --plan '.\generated_menu_<exact filename printed above>.json'
```

Use the same JSON for the full email recipes. Inspect the PDF before delivery, especially long recipe cards. If the free service fails or returns invalid data, generation stops without saving a usable menu or falling back to old recipes. Model requests contain recipe requirements and generated food data, not recipients or archived plans.

Malformed, truncated or structurally invalid recipe responses get at most two additional free attempts per request; authentication and quota errors stop immediately. Each recipe is normalized and validated before saving: gram-suffixed nutrition keys and structured timing/drink fields are accepted without inventing missing values. Validated recipes are saved to a `.partial.json` draft while generation runs. Partial drafts are not complete plans and must not be rendered or sent.

The scripts do not install a scheduler. For an existing authorized weekly task, follow `SKILL.md` and run generation before rendering. The live connection and individual recipe generation have succeeded, but a complete seven-day run has not yet passed: free-provider output errors interrupted the tests. Offline tests cover formatting, totals, bounded retries and error handling. Keep weekly delivery supervised until a complete menu and PDF pass review.

## Render the legacy embedded plan

With Python and ReportLab installed, run from this folder in PowerShell:

```powershell
python -u .\menu_plan_v2.py
```

The script prints the saved path, `Weekly_Menu_Plan_YYYY-MM-DD.pdf`, using the generation date. Running it again on the same day overwrites that day's PDF. Update the weekly data using `SKILL.md` before generating a new plan, and inspect the PDF before delivery.

## Review findings and remaining improvements

- **Current recipe content:** the saved recipes still contain four short method steps apiece and many unmeasured ingredients. Expand all 21 recipes to the updated standard during the next menu revision. Updating the skill does not rewrite existing recipes or archived PDFs.
- **Long recipe layout:** recipe cards are nested single-row tables kept together. Detailed recipes may exceed a page; support continuation when expanding them. The overview table totals 18.5 cm and the macro table 18.0 cm, exceeding the approximately 18.0 cm content frame (the macro table slightly); derive widths from `USABLE_W`.
- **Shopping and nutrition consistency:** shopping quantities and macro tables are maintained separately from recipes. For example, Tuesday's sukiyaki lists tofu, but the shopping list omits it. Add validation or derive shared totals from structured ingredient and nutrition data.
- **Preparation schedule:** the existing weekend guide mixes meals from different points in the week and makes broad storage claims. Use dated preparation tasks and verified storage guidance in the next plan.
- **Reproducible setup:** dependency manifests are missing, and ignoring all of `gmail_mcp/` also excludes its reusable server code. Separate integration source from private credentials before tracking that code, and document dependencies.

The instruction update fixes the obsolete environment path, the seven-versus-21 recipe mismatch, and the missing requirement to include complete methods in both email formats.
