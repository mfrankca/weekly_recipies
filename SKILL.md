---
name: weekly-menu-plan
description: Generate the weekly meal plan PDF and email Marina and family with the PDF attached + full recipes every Sunday morning.
---

Generate a new weekly meal plan PDF for Marina (marina.frank1818@gmail.com) for 3–4 people covering the upcoming week. Then send an email with the PDF file attached directly (no Google Drive upload) and full recipe content in the body.

## Steps

### 1. Read the recipients list
- Read the file at: `C:\Users\kraso\Documents\Claude\Projects\recipes\recipients.txt`
- Parse the `[TO]` section — these are the TO recipients (usually just Marina)
- Parse the `[BCC]` section — these are the BCC recipients (family/friends)
- Skip any line starting with `#` (comments) and ignore blank lines and section headers like `[TO]` / `[BCC]`

### 2. Update the script with the new week dates and fresh recipes
- Read the file at: `C:\Users\kraso\Documents\Claude\Projects\recipes\menu_plan_v2.py`
- Find the line near the top that defines `WEEK = "..."` and update it to reflect the current week's date range (e.g. "July 6–12, 2026").
- Update the `DAYS` list with 7 entirely new recipes — fresh cuisines, fresh dishes, nothing repeated from the previous week. Keep: no pork, no seafood, fish/meat allowed, 3 meals per day (breakfast, lunch, dinner), 7 different cuisines.
- Update `MACRO_DATA`, `SHOPPING`, `BUDGET`, `MEAL_PREP`, and `LEFTOVERS` to match the new recipes.

### 3. Run the script
- Execute: `python3 -u /sessions/keen-gifted-hamilton/mnt/recipes/menu_plan_v2.py`
- Confirm it prints: `PDF saved to` followed by the full path
- Verify with: `ls -lh /sessions/keen-gifted-hamilton/mnt/recipes/Weekly_Menu_Plan_*.pdf`
- Note the exact Windows path of the generated PDF: `C:\Users\kraso\Documents\Claude\Projects\recipes\Weekly_Menu_Plan_YYYY-MM-DD.pdf` (matching today's date) — this is the file you will attach to the email in step 4.

### 4. Send the email with the PDF attached
- Use the Gmail Send MCP tool `send_email` (from the `gmail-send` server).
- `to`: addresses from the `[TO]` section
- `bcc`: addresses from the `[BCC]` section
- `attachment_paths`: a list containing the absolute Windows path to the PDF generated in step 3, e.g. `["C:\\Users\\kraso\\Documents\\Claude\\Projects\\recipes\\Weekly_Menu_Plan_YYYY-MM-DD.pdf"]`
- Do NOT upload anything to Google Drive and do NOT include a Drive link — the PDF must be sent as a direct email attachment only.
- Subject: `🍽️ Your Weekly Menu Plan is Here — [current week date range]`
- HTML body: A warm greeting written for the people Marina cares about — tone feels like it's coming from Marina to her loved ones. Include:
  - A prominent note at the top: "📎 This week's full menu plan PDF is attached — save it or print it out!"
  - The week date range and 7 cuisines
  - All 21 meals with calories &amp; macros
  - Drink pairings for every dinner
  - Meal prep guide and leftovers map
  - Shopping list + budget estimate
  - A warm closing note
- Sign off with: "With love from Marina 💕"

## Constraints
- No pork, no seafood. Fish and meat are allowed.
- 3 meals per day for 3–4 people.
- 7 different cuisines — rotate, don't repeat last week's cuisines.
- Warm, fun tone.
- Never upload the summary to Google Drive — the PDF is sent as a direct email attachment instead.

## File locations
- Recipients: `C:\Users\kraso\Documents\Claude\Projects\recipes\recipients.txt`
- Script: `C:\Users\kraso\Documents\Claude\Projects\recipes\menu_plan_v2.py`
- Script (bash): `/sessions/keen-gifted-hamilton/mnt/recipes/menu_plan_v2.py`
- Output PDF (also the email attachment): `C:\Users\kraso\Documents\Claude\Projects\recipes\Weekly_Menu_Plan_YYYY-MM-DD.pdf`

## Success criteria
- New date-stamped PDF saved in the recipes folder.
- Email sent to all TO and BCC recipients with that PDF file attached (not a Drive link) and full recipe content in the body.
