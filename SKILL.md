---
name: weekly-menu-plan
description: Create Marina's weekly meal plan with complete step-by-step recipes in a PDF and email body; send the direct PDF attachment when requested or covered by an authorized scheduled run.
---

Generate a new weekly meal plan PDF for Marina for 3–4 people covering the upcoming Monday–Sunday week, unless the user specifies another week. Use recipients.txt as the recipient source. For a requested delivery or authorized scheduled run, send an email with the PDF attached directly (no Google Drive upload) and full recipe content in the body. A review or instruction-edit request alone does not trigger generation or email delivery.

## Steps

### 1. Read the recipients list
- Read the file at: `C:\Users\kraso\Documents\Claude\Projects\recipes\recipients.txt`
- Parse the `[TO]` section — these are the TO recipients (usually just Marina)
- Parse the `[BCC]` section — these are the BCC recipients (family/friends)
- Skip any line starting with `#` (comments) and ignore blank lines and section headers like `[TO]` / `[BCC]`

### 2. Generate fresh recipes through a free AI model
- Use `generate_recipes.py` in this folder. It calls OpenRouter's `openrouter/free` endpoint, with the API key supplied locally through `OPENROUTER_API_KEY`. See README.md for setup. Never include credentials in chat, source code or a prompt.
- Run `python -u .\generate_recipes.py --week-start YYYY-MM-DD` with the target Monday. The script selects seven different cuisines and requests breakfast, lunch and dinner for each, followed by matching shopping, budget, preparation and leftovers data. Use `--cuisines` with seven quoted cuisine names when specific cuisines are requested.
- Use the newly saved JSON as the source for both PDF and email. Review and correct its cooking details and quantities before rendering. The renderer derives macro-table and daily calorie totals from the meal nutrition estimates.
- Free-service failures, missing credentials, invalid output or quota limits must be reported. Never silently substitute the script's old menu, a local recipe rotation or a paid model.

#### Fresh AI generation each week, without history matching
- Make fresh model requests for every weekly run. Do not read archived menus to select, exclude or rotate recipes; the user explicitly chose live AI generation instead of history-based selection.
- Request 21 distinct dishes across seven different cuisines, with regional variety and complete cooking steps. Cuisines and staple ingredients may recur in later weeks. Do not merely rename a dish or change its garnish to create variety within the same plan.
- Keep the meal-prep and leftovers map as optional uses for this week's food, not replacements for the 21 meals.
- Describe these as AI-generated recipes, not recipes retrieved from verified websites. Fresh generation encourages variety but cannot guarantee that a dish will never recur without history matching; do not promise that guarantee.

#### Recipe detail standard — apply to all 21 meals
- Write instructions a home cook can follow from raw ingredients to serving without looking up missing techniques. A dish description or high-level preparation summary is not a method.
- State the recipe yield (use 4 servings within the 3–4 person target) and list measured quantities for every ingredient, including oil, water or stock, seasonings, sauces and accompaniments. State whether rice, pasta and similar ingredients are weighed dry or cooked. Distinguish purchased ready-to-use components from components made in the recipe.
- Store each sequential cooking step as a separate string in `method`; the PDF renderer supplies the numbers. Use one main action per step, splitting preparation, cooking stages, sauces, sides and serving when they require separate actions. Use as many steps as the dish needs; do not compress a complex recipe into four summary bullets or pad a simple recipe to meet a quota.
- Start with necessary washing, chopping, measuring, draining, preheating and equipment setup. Specify pan or pot size when it affects the result.
- Give the ingredient amounts used at each stage when an ingredient is divided. Include heat settings, oven temperatures in °C and °F, approximate cooking times, stirring/turning instructions, and observable doneness cues. Include verified safe internal temperatures where relevant.
- Explain techniques such as rolling an omelette, breading a cutlet or reducing a sauce. Replace phrases such as "make tzatziki", "cook rice", "braise until done" and "prepare salad" with actual steps, or explicitly identify a purchased prepared component.
- Cover every component promised in the meal title, including grains, sauces, salads and prepared drinks. Explain when to start parallel components so they finish together, and include resting, draining and final assembly where needed.
- Make prep, marinating, cooking and total elapsed times agree with the actual method. Keep the batch meal-prep guide as additional scheduling help; each recipe must still be independently usable.
- Example of an actionable step: "Heat 1 tbsp olive oil in a 28 cm skillet over medium heat. Add the diced onion and cook for 5–7 minutes, stirring every minute, until softened and translucent."
- Use the same complete ingredients and numbered steps in the PDF and email. In HTML, use an ordered list (`<ol><li>…</li></ol>`) for each recipe; retain numbered steps in the plain-text body. Do not replace the email recipes with summaries or a reference to the attachment.

#### Content checks before building
- Confirm 7 days, exactly 3 meals per day, 21 complete ingredient lists and methods, and 7 dinner drink pairings.
- Confirm all 21 dishes are distinct within the generated week, including renamed dishes and minor variations. Replace within-week duplicates before building; no historical comparison is required.
- Cross-check that ingredients used in each method are listed, quantities cover the declared servings, and the shopping list totals all recipes without counting the same pantry item twice.
- Keep calories and macros consistent between recipe cards, daily totals and `MACRO_DATA`; label them as estimates per serving. State the budget currency and serving basis for per-person costs.
- Anchor make-ahead work to actual dates relative to the target week. Verify storage, freezing, thawing and reheating guidance against authoritative food-safety sources; do not assume a weekend preparation keeps in the fridge for the entire week.

### 3. Run the script
- From the recipes folder on Windows, execute: `python -u .\menu_plan_v2.py --plan '<newly generated JSON path>'` (use `py -3` if that is the available launcher). The renderer requires ReportLab. Always pass the fresh plan for weekly runs; omitting `--plan` renders the legacy embedded menu.
- Confirm it prints: `PDF saved to` followed by the full path
- Verify the exact path printed by the script exists and has nonzero size, using `Get-Item -LiteralPath '<printed PDF path>'` in PowerShell.
- Render and inspect the generated PDF: all 21 recipes must retain their full ingredient lists and numbered steps without clipping, overlap or missing text. Allow more pages for detailed recipes; do not shorten the methods or shrink recipe body text below 8 pt to fit. If a long card cannot fit on one page, adapt the layout to permit continuation before delivery.
- Note the exact Windows path of the generated PDF: `C:\Users\kraso\Documents\Claude\Projects\recipes\Weekly_Menu_Plan_YYYY-MM-DD.pdf` (matching today's date) — this is the file you will attach to the email in step 4.

### 4. Send the email with the PDF attached
- Use the Gmail Send MCP tool `send_email` (from the `gmail-send` server).
- Only perform delivery when authorized by the user's request or scheduled run. If the tool is unavailable, report that the PDF is ready and delivery is blocked. Do not claim the email was sent without a successful tool result; do not automatically retry an ambiguous send result that could produce a duplicate.
- `to`: addresses from the `[TO]` section
- `bcc`: addresses from the `[BCC]` section
- `attachment_paths`: a list containing the absolute Windows path to the PDF generated in step 3, e.g. `["C:\\Users\\kraso\\Documents\\Claude\\Projects\\recipes\\Weekly_Menu_Plan_YYYY-MM-DD.pdf"]`
- Do NOT upload anything to Google Drive and do NOT include a Drive link — the PDF must be sent as a direct email attachment only.
- Subject: `🍽️ Your Weekly Menu Plan is Here — [current week date range]`
- HTML body: A warm greeting written for the people Marina cares about — tone feels like it's coming from Marina to her loved ones. Include:
  - A prominent note at the top: "📎 This week's full menu plan PDF is attached — save it or print it out!"
  - The week date range and 7 cuisines
  - All 21 meals with serving yields, measured ingredients, complete numbered cooking steps, timing, calories &amp; macros
  - Drink pairings for every dinner
  - Meal prep guide and leftovers map
  - Shopping list + budget estimate
  - A warm closing note
- Sign off with: "With love from Marina 💕"
- Also supply `body` with a readable plain-text version containing the same full recipes, and pass the rich-text version as `html_body`.

## Constraints
- No pork, no seafood. Fish and meat are allowed.
- 3 meals per day for 3–4 people.
- Fresh recipes requested from the free AI service every week; no local recipe rotation or history-based selection.
- 7 different cuisines and 21 distinct dishes within each weekly plan.
- Warm, fun tone.
- Never upload the summary to Google Drive — the PDF is sent as a direct email attachment instead.

## File locations
- Recipients: `C:\Users\kraso\Documents\Claude\Projects\recipes\recipients.txt`
- Script: `C:\Users\kraso\Documents\Claude\Projects\recipes\menu_plan_v2.py`
- AI generator: `C:\Users\kraso\Documents\Claude\Projects\recipes\generate_recipes.py`
- Generated recipe source: the exact `generated_menu_*.json` path printed by the AI generator.
- Output PDF (also the email attachment): `C:\Users\kraso\Documents\Claude\Projects\recipes\Weekly_Menu_Plan_YYYY-MM-DD.pdf`

## Success criteria
- New date-stamped PDF saved in the recipes folder.
- Successful fresh free-model generation of 21 distinct dishes across seven cuisines, with the resulting JSON used for PDF and email.
- All 21 recipes are independently cookable, with measured ingredients and complete sequential instructions, and the PDF has been visually checked.
- For an authorized delivery: email sent to all TO and BCC recipients with that PDF file attached (not a Drive link), full step-by-step recipes in both email bodies, and a confirmed send result.
