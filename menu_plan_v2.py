# -*- coding: utf-8 -*-
"""
Weekly Menu Plan PDF Generator — v3 (full redesign)
Marina's Sunday meal planner
─────────────────────────────────────────────────
• Two-column recipe cards (ingredients | method)
• Minimum 8 pt body text — nothing cramped or overlapping
• Brand-new recipes generated fresh each week
─────────────────────────────────────────────────
Update WEEK below, then run:
  python3 menu_plan_v2.py
Output: Weekly_Menu_Plan.pdf  (same folder as this script)
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime

# ── UPDATE THIS EACH WEEK ─────────────────────────────────────────────────────
WEEK = "September 7–13, 2026"
# ─────────────────────────────────────────────────────────────────────────────

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"Weekly_Menu_Plan_{datetime.now().strftime('%Y-%m-%d')}.pdf")

# ── COLOUR PALETTE ────────────────────────────────────────────────────────────
FOREST    = colors.HexColor("#1B4332")   # deep forest — primary dark
SAGE      = colors.HexColor("#2D6A4F")   # sage — section headers
LEAF      = colors.HexColor("#D8F3DC")   # pale mint — alt rows
AMBER     = colors.HexColor("#C47A1A")   # warm amber — calories / highlights
GOLD      = colors.HexColor("#EFA600")   # gold — cover accent
RUST      = colors.HexColor("#A83232")   # rust red — protein macro
NAVY      = colors.HexColor("#1A4D72")   # navy — carb macro
WHITE     = colors.white
CARD_BG   = colors.HexColor("#F9FBFA")   # near-white card background
BORDER    = colors.HexColor("#C5DDD0")   # subtle green border
GREY_LT   = colors.HexColor("#F4F5F4")
GREY_MD   = colors.HexColor("#DCDCDC")
TEXT      = colors.HexColor("#1A1A1A")   # near-black body
MUTED     = colors.HexColor("#6B7280")   # grey subtitles

PAGE_W, PAGE_H = A4
MARGIN    = 1.5 * cm
USABLE_W  = PAGE_W - 2 * MARGIN         # ≈ 510 pt ≈ 18 cm

# Column split for two-column recipe cards
ING_W  = USABLE_W * 0.40   # ingredients  ≈ 204 pt
METH_W = USABLE_W * 0.60   # method       ≈ 306 pt

# ── STYLE FACTORY ─────────────────────────────────────────────────────────────
_n = [0]
def s(base="Normal", **kw):
    _n[0] += 1
    return ParagraphStyle(f"_s{_n[0]}", parent=getSampleStyleSheet()[base], **kw)

def P(text, style):
    return Paragraph(str(text), style)

# ── HEADER / FOOTER CANVAS ────────────────────────────────────────────────────
class HFCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        self._saved = []
        super().__init__(*args, **kwargs)

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for state in self._saved:
            self.__dict__.update(state)
            self._draw_hf()
            super().showPage()
        super().save()

    def _draw_hf(self):
        pg = self._pageNumber
        if pg == 1:
            return
        w, h = A4
        # ── top rule
        self.setStrokeColor(FOREST)
        self.setLineWidth(0.8)
        self.line(MARGIN, h - MARGIN * 0.75, w - MARGIN, h - MARGIN * 0.75)
        self.setFont("Helvetica-Bold", 6.5)
        self.setFillColor(FOREST)
        self.drawString(MARGIN, h - MARGIN * 0.75 + 3.5, "WEEKLY MENU PLAN & RECIPES")
        self.setFont("Helvetica", 6.5)
        self.setFillColor(MUTED)
        self.drawRightString(w - MARGIN, h - MARGIN * 0.75 + 3.5, WEEK)
        # ── bottom rule
        self.setStrokeColor(FOREST)
        self.setLineWidth(0.5)
        self.line(MARGIN, MARGIN * 0.65, w - MARGIN, MARGIN * 0.65)
        self.setFont("Helvetica", 6.5)
        self.setFillColor(MUTED)
        self.drawString(MARGIN, MARGIN * 0.35, "No pork · No seafood · Fish & meat welcome · Serves 3–4")
        self.drawRightString(w - MARGIN, MARGIN * 0.35, f"Page {pg}")

# New weekly data — September 7–13, 2026
# Cuisines: Greek, Japanese, Thai, Spanish, Ethiopian, Turkish, French

DAYS = [
    {
        "day":     "Monday",
        "cuisine": "Greek",
        "flag":    "GR",
        "kcal":    "~1870",
        "meals": [
            {
                "type": "BREAKFAST", "kcal": "~430",
                "name": "Strapatsada (Greek Tomato & Feta Scrambled Eggs) with Village Bread & Greek Coffee",
                "subtitle": "Silky eggs simmered with sweet tomato and briny feta, mopped up with crusty village bread and strong Greek coffee",
                "time": "Prep 10 min  ·  Cook 15 min",
                "macros": "Protein 20 g  |  Carbs 46 g  |  Fat 20 g",
                "ingredients": [
                    "8 eggs",
                    "Ripe tomatoes, grated; olive oil, dried oregano",
                    "Feta cheese, crumbled",
                    "Horiatiko (village) bread, warmed; Greek coffee, briki-brewed",
                ],
                "method": [
                    "Sauté grated tomato in olive oil with a pinch of oregano until jammy and reduced, 8 min.",
                    "Pour in beaten eggs and stir gently over low heat until softly curdled.",
                    "Fold in crumbled feta just before the eggs finish setting.",
                    "Serve warm with torn village bread and a small cup of Greek coffee.",
                ],
                "drink": None,
            },
            {
                "type": "LUNCH", "kcal": "~600",
                "name": "Chicken Souvlaki with Tzatziki, Pita & Horiatiki Salad",
                "subtitle": "Char-grilled lemon-oregano chicken skewers wrapped in warm pita with cool tzatziki and a chunky Greek salad",
                "time": "Prep 15 min  ·  Marinate 20 min  ·  Cook 15 min",
                "macros": "Protein 36 g  |  Carbs 56 g  |  Fat 20 g",
                "ingredients": [
                    "900 g chicken thigh, cubed, marinated in lemon, olive oil, garlic, oregano",
                    "Pita bread, warmed",
                    "Cucumber, garlic, dill, Greek yogurt (tzatziki)",
                    "Tomato, cucumber, red onion, kalamata olives, feta (horiatiki salad)",
                ],
                "method": [
                    "Marinate chicken in lemon juice, olive oil, garlic and oregano at least 20 min; thread onto skewers.",
                    "Grill skewers, turning, until charred and cooked through, about 12 min.",
                    "Grate cucumber, squeeze dry, and stir into yogurt with garlic and dill for tzatziki.",
                    "Toss tomato, cucumber, red onion, olives and feta with olive oil; serve chicken in warm pita with tzatziki and salad.",
                ],
                "drink": None,
            },
            {
                "type": "DINNER", "kcal": "~840",
                "name": "Beef Youvetsi (Braised Beef with Orzo) with Kefalotyri & Crusty Bread",
                "subtitle": "Slow-braised cinnamon-spiced beef in a rich tomato sauce baked with orzo pasta and finished with salty grated cheese",
                "time": "Prep 15 min  ·  Cook 1.5 hr",
                "macros": "Protein 45 g  |  Carbs 58 g  |  Fat 42 g",
                "ingredients": [
                    "900 g beef chuck, cubed",
                    "Onion, garlic, cinnamon stick, bay leaf, tomato paste, crushed tomatoes",
                    "400 g orzo pasta",
                    "Kefalotyri (or parmesan), grated; crusty bread",
                ],
                "method": [
                    "Brown beef in olive oil in a wide pot; remove and sauté onion and garlic until soft.",
                    "Stir in tomato paste, crushed tomatoes, cinnamon and bay leaf; return beef and simmer, covered, until tender, 1 hr.",
                    "Stir orzo into the pot with a little water and simmer until the pasta is cooked and has soaked up the sauce, 12–15 min.",
                    "Spoon into bowls, shower with grated kefalotyri, and serve with crusty bread.",
                ],
                "drink": "Greek red wine (Agiorgitiko), glass  ·  Mocktail: lemon-mint soda with a sprig of basil",
            },
        ],
    },
    {
        "day":     "Tuesday",
        "cuisine": "Japanese",
        "flag":    "JP",
        "kcal":    "~1870",
        "meals": [
            {
                "type": "BREAKFAST", "kcal": "~425",
                "name": "Tamagoyaki (Japanese Rolled Omelette) with Steamed Rice & Kombu Miso Soup",
                "subtitle": "Delicately sweet-savory layered rolled omelette sliced over hot rice, with a warming vegetarian miso soup",
                "time": "Prep 10 min  ·  Cook 15 min",
                "macros": "Protein 19 g  |  Carbs 48 g  |  Fat 17 g",
                "ingredients": [
                    "8 eggs, beaten with soy sauce, mirin, sugar",
                    "400 g steamed short-grain rice",
                    "Umeboshi (pickled plum); nori strips",
                    "Kombu (dried kelp), white miso paste, scallion (miso soup)",
                ],
                "method": [
                    "Whisk eggs with a little soy sauce, mirin and sugar.",
                    "Pour a thin layer into a rectangular tamagoyaki pan, and as it sets, roll it toward you and push to one side; repeat, building layers.",
                    "Steep kombu in hot water 10 min to make a simple dashi, then whisk in miso paste off the heat.",
                    "Slice the rolled omelette and serve over rice with pickled plum, nori and a bowl of miso soup.",
                ],
                "drink": None,
            },
            {
                "type": "LUNCH", "kcal": "~605",
                "name": "Chicken Katsu with Steamed Rice, Shredded Cabbage & Tonkatsu Sauce",
                "subtitle": "Crisp panko-breaded chicken cutlets sliced over rice with a tangy-sweet sauce and cool shredded cabbage",
                "time": "Prep 15 min  ·  Cook 20 min",
                "macros": "Protein 36 g  |  Carbs 60 g  |  Fat 20 g",
                "ingredients": [
                    "900 g chicken breast, pounded thin",
                    "Flour, egg wash, panko breadcrumbs",
                    "500 g rice, steamed",
                    "Cabbage, finely shredded; tonkatsu sauce, Kewpie mayonnaise",
                ],
                "method": [
                    "Dredge chicken cutlets in flour, egg wash, then panko, pressing to coat well.",
                    "Shallow-fry in neutral oil until deep golden and cooked through, 3–4 min per side.",
                    "Rest briefly, then slice into strips.",
                    "Serve sliced katsu over rice with shredded cabbage, tonkatsu sauce and a drizzle of Kewpie mayonnaise.",
                ],
                "drink": None,
            },
            {
                "type": "DINNER", "kcal": "~840",
                "name": "Beef Sukiyaki with Udon Noodles & Dipping Egg",
                "subtitle": "Thinly sliced beef simmered in a sweet soy-mirin broth with vegetables, udon and a silky dipping egg",
                "time": "Prep 20 min  ·  Cook 20 min",
                "macros": "Protein 44 g  |  Carbs 56 g  |  Fat 44 g",
                "ingredients": [
                    "900 g beef sirloin, very thinly sliced",
                    "Soy sauce, mirin, sugar, kombu dashi (sukiyaki broth)",
                    "Napa cabbage, shiitake mushroom, scallion, tofu, udon noodles",
                    "Eggs, for dipping (per person)",
                ],
                "method": [
                    "Simmer soy sauce, mirin, sugar and kombu dashi together to make the sukiyaki broth.",
                    "Arrange beef, napa cabbage, mushrooms, scallion and tofu in a wide shallow pan with the broth; simmer until the beef is just cooked and vegetables tender.",
                    "Add udon noodles to the pan for the last few minutes to warm through and soak up the broth.",
                    "Serve each portion with a lightly beaten raw egg on the side for dipping, if desired.",
                ],
                "drink": "Green tea  ·  Japanese sake, small cup  ·  Mocktail: yuzu-honey soda",
            },
        ],
    },
    {
        "day":     "Wednesday",
        "cuisine": "Thai",
        "flag":    "TH",
        "kcal":    "~1860",
        "meals": [
            {
                "type": "BREAKFAST", "kcal": "~420",
                "name": "Thai Omelette (Khai Jeow) with Jasmine Rice, Sriracha & Thai Iced Tea",
                "subtitle": "Puffy, crisp-edged fried omelette over fragrant jasmine rice with a squeeze of sriracha and sweet iced tea",
                "time": "Prep 5 min  ·  Cook 10 min",
                "macros": "Protein 18 g  |  Carbs 46 g  |  Fat 20 g",
                "ingredients": [
                    "8 eggs, beaten with a splash of fish sauce",
                    "400 g jasmine rice, steamed",
                    "Scallion, white pepper",
                    "Sriracha; Thai iced tea (black tea, condensed milk, sugar, ice)",
                ],
                "method": [
                    "Beat eggs vigorously with a splash of fish sauce and white pepper until frothy.",
                    "Heat plenty of oil in a wok until shimmering, then pour in eggs all at once; let the edges puff and crisp.",
                    "Flip carefully once golden underneath, then slide onto steamed rice.",
                    "Top with sliced scallion and sriracha; serve with a tall glass of Thai iced tea.",
                ],
                "drink": None,
            },
            {
                "type": "LUNCH", "kcal": "~600",
                "name": "Chicken Pad Thai with Peanuts, Bean Sprouts & Lime",
                "subtitle": "Wok-tossed rice noodles with tamarind-tangy sauce, tender chicken, crushed peanuts and fresh lime",
                "time": "Prep 15 min  ·  Cook 15 min",
                "macros": "Protein 35 g  |  Carbs 60 g  |  Fat 20 g",
                "ingredients": [
                    "900 g chicken thigh, sliced thin",
                    "400 g flat rice noodles, soaked",
                    "Tamarind paste, fish sauce, palm sugar (pad Thai sauce)",
                    "Bean sprouts, garlic chives, crushed peanuts, lime wedges, eggs",
                ],
                "method": [
                    "Soak rice noodles in warm water until pliable but firm.",
                    "Stir-fry chicken in a hot wok until just cooked, push to one side, then scramble in a beaten egg.",
                    "Add drained noodles and the tamarind-fish sauce-palm sugar mixture; toss well over high heat until coated and tender.",
                    "Fold in bean sprouts and garlic chives, then plate topped with crushed peanuts and lime wedges.",
                ],
                "drink": None,
            },
            {
                "type": "DINNER", "kcal": "~840",
                "name": "Beef Panang Curry with Jasmine Rice & Thai Basil",
                "subtitle": "Rich, nutty red curry beef simmered in coconut milk with kaffir lime leaf, served over fragrant jasmine rice",
                "time": "Prep 15 min  ·  Cook 35 min",
                "macros": "Protein 45 g  |  Carbs 54 g  |  Fat 46 g",
                "ingredients": [
                    "900 g beef sirloin, sliced",
                    "Panang curry paste, coconut milk, palm sugar, fish sauce",
                    "Kaffir lime leaves, Thai basil, red chili, sliced",
                    "500 g jasmine rice, steamed",
                ],
                "method": [
                    "Simmer the thick part of a can of coconut milk with panang curry paste until fragrant and the oil separates, 5 min.",
                    "Add beef and cook until it changes color, then pour in the remaining coconut milk.",
                    "Season with palm sugar and fish sauce; simmer until the beef is tender and the sauce is thick, 20–25 min.",
                    "Stir in torn kaffir lime leaves and Thai basil; serve over jasmine rice, garnished with sliced red chili.",
                ],
                "drink": "Thai iced tea  ·  Thai lager, glass  ·  Mocktail: lemongrass-ginger cooler",
            },
        ],
    },
    {
        "day":     "Thursday",
        "cuisine": "Spanish",
        "flag":    "ES",
        "kcal":    "~1860",
        "meals": [
            {
                "type": "BREAKFAST", "kcal": "~425",
                "name": "Tortilla Española with Pan con Tomate & Café con Leche",
                "subtitle": "Thick, tender potato-onion omelette sliced into wedges, with garlicky tomato-rubbed toast and milky coffee",
                "time": "Prep 15 min  ·  Cook 30 min",
                "macros": "Protein 18 g  |  Carbs 48 g  |  Fat 20 g",
                "ingredients": [
                    "8 eggs",
                    "Potatoes, thinly sliced; onion, olive oil",
                    "Baguette or rustic bread, garlic, ripe tomato (pan con tomate)",
                    "Café con leche (espresso, steamed milk)",
                ],
                "method": [
                    "Slowly fry potato and onion slices in plenty of olive oil until soft, not browned, 15–20 min; drain.",
                    "Beat eggs, fold in the potato-onion mixture, and pour back into a hot pan.",
                    "Cook until set on the bottom, then flip using a plate to finish the other side; slice into wedges.",
                    "Rub toasted bread with garlic and ripe tomato, drizzle with olive oil, and serve alongside with café con leche.",
                ],
                "drink": None,
            },
            {
                "type": "LUNCH", "kcal": "~595",
                "name": "Chicken Paella (Paella de Pollo) with Green Salad",
                "subtitle": "Saffron-golden rice studded with tender chicken, roasted red pepper and green beans, straight from the pan",
                "time": "Prep 15 min  ·  Cook 35 min",
                "macros": "Protein 36 g  |  Carbs 58 g  |  Fat 18 g",
                "ingredients": [
                    "900 g chicken thigh, cut into pieces",
                    "500 g bomba (or short-grain) rice, saffron, smoked paprika",
                    "Roasted red pepper, green beans, tomato, garlic",
                    "Lemon wedges; mixed greens salad",
                ],
                "method": [
                    "Brown chicken pieces in olive oil in a wide paella pan; remove and set aside.",
                    "Sauté garlic, tomato and green beans until softened, then stir in rice, saffron and smoked paprika to coat.",
                    "Return chicken to the pan, pour in hot stock, and simmer without stirring until the rice is tender and a crust forms on the bottom, 18–20 min.",
                    "Rest 5 min, scatter roasted red pepper on top, and serve with lemon wedges and a green salad.",
                ],
                "drink": None,
            },
            {
                "type": "DINNER", "kcal": "~840",
                "name": "Beef in Rioja Wine Sauce (Carrillada de Ternera) with Patatas Bravas & Padrón Peppers",
                "subtitle": "Fall-apart beef braised for hours in Rioja red wine, served with crispy paprika potatoes and blistered peppers",
                "time": "Prep 15 min  ·  Cook 2.5 hr",
                "macros": "Protein 45 g  |  Carbs 56 g  |  Fat 44 g",
                "ingredients": [
                    "900 g beef cheek or chuck, cubed",
                    "Onion, carrot, garlic, Rioja red wine, beef stock, bay leaf",
                    "Potatoes, cubed and fried; smoked paprika aioli (patatas bravas)",
                    "Padrón peppers, olive oil, flaky salt",
                ],
                "method": [
                    "Brown beef in olive oil; remove and sauté onion, carrot and garlic until soft.",
                    "Return beef to the pot, pour in Rioja wine and stock, add bay leaf, and simmer covered until fork-tender, 2–2.5 hr.",
                    "Fry cubed potatoes until golden and crisp; toss with smoked paprika aioli for patatas bravas.",
                    "Blister padrón peppers in a hot dry pan with olive oil and flaky salt; serve everything together.",
                ],
                "drink": "Rioja red wine, glass  ·  Mocktail: sparkling grape-berry sangria (non-alcoholic)",
            },
        ],
    },
    {
        "day":     "Friday",
        "cuisine": "Ethiopian",
        "flag":    "ET",
        "kcal":    "~1860",
        "meals": [
            {
                "type": "BREAKFAST", "kcal": "~420",
                "name": "Enkulal Tibs (Ethiopian Spiced Scrambled Eggs) with Injera & Ethiopian Coffee",
                "subtitle": "Turmeric and jalapeño-spiced scrambled eggs with tomato and onion, scooped up with spongy injera and strong coffee",
                "time": "Prep 10 min  ·  Cook 15 min",
                "macros": "Protein 19 g  |  Carbs 46 g  |  Fat 18 g",
                "ingredients": [
                    "8 eggs",
                    "Onion, tomato, jalapeño, turmeric, garlic",
                    "Injera (or flatbread), warmed",
                    "Ethiopian coffee (buna), lightly spiced with cinnamon",
                ],
                "method": [
                    "Sauté onion, jalapeño and garlic in niter kibbeh (spiced butter) or oil until soft.",
                    "Add chopped tomato and turmeric; cook until the tomato breaks down, 5 min.",
                    "Pour in beaten eggs and scramble gently until just set.",
                    "Serve with torn injera for scooping and a small cup of spiced coffee.",
                ],
                "drink": None,
            },
            {
                "type": "LUNCH", "kcal": "~600",
                "name": "Doro Wat (Ethiopian Chicken Stew) with Injera & Cabbage Salad",
                "subtitle": "Deeply spiced berbere-chicken stew simmered slow with onions, served over spongy injera with a simple cabbage salad",
                "time": "Prep 15 min  ·  Cook 45 min",
                "macros": "Protein 36 g  |  Carbs 58 g  |  Fat 20 g",
                "ingredients": [
                    "900 g chicken thigh/drumstick",
                    "Onion (lots), berbere spice blend, garlic, ginger, niter kibbeh",
                    "Injera, warmed",
                    "Cabbage, carrot, onion, turmeric (side salad)",
                ],
                "method": [
                    "Cook a large quantity of finely chopped onion slowly in niter kibbeh until deeply softened and golden, 20 min.",
                    "Stir in berbere, garlic and ginger; cook until fragrant, then add chicken and a little water.",
                    "Cover and simmer until the chicken is tender and the sauce is thick and deep red, 20–25 min.",
                    "Serve the stew over injera with a side of lightly spiced cabbage and carrot salad.",
                ],
                "drink": None,
            },
            {
                "type": "DINNER", "kcal": "~840",
                "name": "Beef Tibs with Injera, Gomen & Awaze",
                "subtitle": "Quick-seared beef with rosemary, onion and jalapeño, served with braised collard greens and a fiery chili paste",
                "time": "Prep 15 min  ·  Cook 20 min",
                "macros": "Protein 45 g  |  Carbs 54 g  |  Fat 44 g",
                "ingredients": [
                    "900 g beef sirloin, cubed",
                    "Onion, jalapeño, rosemary, garlic, niter kibbeh",
                    "Injera, warmed",
                    "Collard greens, garlic, ginger (gomen); berbere, oil (awaze paste)",
                ],
                "method": [
                    "Sear beef cubes in niter kibbeh or oil over high heat until browned but still tender, 8–10 min.",
                    "Add onion, jalapeño, garlic and rosemary; toss until the onion softens and everything is fragrant.",
                    "Separately braise collard greens with garlic and ginger until tender, about 15 min.",
                    "Whisk berbere into a little oil for awaze; serve beef tibs with injera, gomen and awaze on the side.",
                ],
                "drink": "Ethiopian coffee (buna)  ·  Tej (honey wine), glass  ·  Mocktail: hibiscus-ginger cooler",
            },
        ],
    },
    {
        "day":     "Saturday",
        "cuisine": "Turkish",
        "flag":    "TR",
        "kcal":    "~1865",
        "meals": [
            {
                "type": "BREAKFAST", "kcal": "~425",
                "name": "Menemen (Turkish Eggs with Tomato & Peppers) with Simit & Turkish Tea",
                "subtitle": "Soft-set eggs cooked into a sizzling pan of sweet peppers and tomato, with sesame-crusted bread and hot tea",
                "time": "Prep 10 min  ·  Cook 15 min",
                "macros": "Protein 19 g  |  Carbs 48 g  |  Fat 18 g",
                "ingredients": [
                    "8 eggs",
                    "Green pepper, tomato, onion, olive oil, chili flakes",
                    "Simit (or crusty bread), warmed",
                    "Turkish tea (çay), brewed strong",
                ],
                "method": [
                    "Sauté onion and green pepper in olive oil until softened, 6–8 min.",
                    "Add chopped tomato and chili flakes; simmer until juicy and slightly reduced.",
                    "Crack in eggs directly and stir gently until just set, keeping some texture.",
                    "Serve straight from the pan with warm simit and a glass of Turkish tea.",
                ],
                "drink": None,
            },
            {
                "type": "LUNCH", "kcal": "~600",
                "name": "Chicken Şiş Kebab with Bulgur Pilaf & Cacık",
                "subtitle": "Char-grilled marinated chicken skewers with nutty bulgur pilaf and a cooling garlic-cucumber yogurt",
                "time": "Prep 15 min  ·  Marinate 20 min  ·  Cook 15 min",
                "macros": "Protein 36 g  |  Carbs 56 g  |  Fat 20 g",
                "ingredients": [
                    "900 g chicken thigh, cubed, marinated in yogurt, garlic, paprika, olive oil",
                    "500 g bulgur, onion, tomato paste (pilaf)",
                    "Cucumber, garlic, dill, yogurt (cacık)",
                    "Sumac onions, parsley, to garnish",
                ],
                "method": [
                    "Marinate chicken in yogurt, garlic, paprika and olive oil at least 20 min; thread onto skewers.",
                    "Grill until charred and cooked through, about 12 min.",
                    "Sauté onion in butter, stir in bulgur and tomato paste, then simmer with stock until fluffy.",
                    "Grate cucumber into yogurt with garlic and dill for cacık; serve chicken skewers over pilaf with cacık and sumac onions.",
                ],
                "drink": None,
            },
            {
                "type": "DINNER", "kcal": "~840",
                "name": "Beef Adana Kebab with Turkish Rice Pilaf, Grilled Tomatoes & Ezme",
                "subtitle": "Hand-minced spicy beef kebabs charred over high heat, with buttery rice, smoky grilled tomato and a fiery chopped salad",
                "time": "Prep 25 min  ·  Cook 20 min",
                "macros": "Protein 45 g  |  Carbs 56 g  |  Fat 45 g",
                "ingredients": [
                    "900 g ground beef (fattier blend), red pepper flakes, cumin, sumac, garlic, parsley",
                    "500 g rice, butter, vermicelli, stock (pilaf)",
                    "Tomatoes and long green peppers, grilled",
                    "Tomato, onion, parsley, pomegranate molasses, chili (ezme salad)",
                ],
                "method": [
                    "Mix ground beef with red pepper flakes, cumin, sumac, garlic and parsley; knead well and mold onto flat skewers.",
                    "Grill kebabs over high heat, turning, until well charred outside and cooked through, 10–12 min.",
                    "Toast vermicelli in butter, add rice and stock, and simmer until fluffy; grill tomatoes and peppers alongside.",
                    "Finely chop tomato, onion and parsley with pomegranate molasses and chili for ezme; serve everything together.",
                ],
                "drink": "Turkish tea (çay)  ·  Turkish red wine, glass  ·  Mocktail: pomegranate şerbet",
            },
        ],
    },
    {
        "day":     "Sunday",
        "cuisine": "French",
        "flag":    "FR",
        "kcal":    "~1860",
        "meals": [
            {
                "type": "BREAKFAST", "kcal": "~420",
                "name": "Omelette aux Fines Herbes with Croissants & Café au Lait",
                "subtitle": "Silky folded herb omelette with a buttery, flaky croissant and a big bowl of milky coffee",
                "time": "Prep 8 min  ·  Cook 10 min",
                "macros": "Protein 19 g  |  Carbs 46 g  |  Fat 20 g",
                "ingredients": [
                    "8 eggs",
                    "Chives, parsley, tarragon, finely chopped; butter",
                    "Croissants, warmed",
                    "Café au lait (strong coffee, steamed milk)",
                ],
                "method": [
                    "Beat eggs with a pinch of salt and the chopped herbs.",
                    "Melt butter in a non-stick pan over medium-low heat, pour in eggs, and stir gently with a fork as they begin to set.",
                    "Let the base set, then fold the omelette in thirds and slide onto a plate.",
                    "Serve immediately with a warm croissant and a bowl of café au lait.",
                ],
                "drink": None,
            },
            {
                "type": "LUNCH", "kcal": "~600",
                "name": "Coq au Vin (Chicken Braised in Red Wine) with Crusty Bread & Green Salad",
                "subtitle": "Chicken slowly braised in red wine with mushrooms and pearl onions, served with crusty bread to mop up the sauce",
                "time": "Prep 15 min  ·  Cook 45 min",
                "macros": "Protein 35 g  |  Carbs 54 g  |  Fat 22 g",
                "ingredients": [
                    "900 g chicken thigh, bone-in",
                    "Pearl onions, mushrooms, garlic, thyme, bay leaf, red wine",
                    "Chicken stock, tomato paste, flour (to thicken)",
                    "Crusty baguette; mixed green salad with vinaigrette",
                ],
                "method": [
                    "Brown chicken thighs in a little oil; remove and sauté pearl onions and mushrooms until golden.",
                    "Stir in garlic and a spoonful of flour to lightly thicken, then pour in red wine and stock.",
                    "Return chicken to the pot with thyme and bay leaf; cover and simmer until tender, 35–40 min.",
                    "Serve the chicken and sauce with crusty bread and a simple dressed green salad.",
                ],
                "drink": None,
            },
            {
                "type": "DINNER", "kcal": "~840",
                "name": "Beef Bourguignon with Mashed Potatoes & Haricots Verts",
                "subtitle": "Classic red wine-braised beef with mushrooms and pearl onions, over silky mashed potatoes with buttered green beans",
                "time": "Prep 20 min  ·  Cook 2.5 hr",
                "macros": "Protein 45 g  |  Carbs 52 g  |  Fat 46 g",
                "ingredients": [
                    "900 g beef chuck, cubed",
                    "Carrot, onion, garlic, tomato paste, red Burgundy wine, beef stock, thyme, bay leaf",
                    "Pearl onions, mushrooms, butter",
                    "Potatoes, butter, milk (mash); green beans, butter (haricots verts)",
                ],
                "method": [
                    "Brown beef in batches in a heavy pot; remove and sauté carrot, onion and garlic until soft.",
                    "Stir in tomato paste, then pour in red wine and stock; return beef with thyme and bay leaf.",
                    "Cover and simmer gently until meltingly tender, 2–2.5 hr, adding pearl onions and mushrooms in the last 30 min.",
                    "Whip potatoes with butter and milk for a silky mash; blanch and butter green beans, and serve alongside the beef.",
                ],
                "drink": "French red wine (Burgundy), glass  ·  Mocktail: French 75 mocktail (lemon, sugar, sparkling water)",
            },
        ],
    },
]

MACRO_DATA = [
    ("Monday",    "Greek",      "Breakfast",  430, 20, 46, 20),
    ("",          "",           "Lunch",      600, 36, 56, 20),
    ("",          "",           "Dinner",     840, 45, 58, 42),
    ("Tuesday",   "Japanese",   "Breakfast",  425, 19, 48, 17),
    ("",          "",           "Lunch",      605, 36, 60, 20),
    ("",          "",           "Dinner",     840, 44, 56, 44),
    ("Wednesday", "Thai",       "Breakfast",  420, 18, 46, 20),
    ("",          "",           "Lunch",      600, 35, 60, 20),
    ("",          "",           "Dinner",     840, 45, 54, 46),
    ("Thursday",  "Spanish",    "Breakfast",  425, 18, 48, 20),
    ("",          "",           "Lunch",      595, 36, 58, 18),
    ("",          "",           "Dinner",     840, 45, 56, 44),
    ("Friday",    "Ethiopian",  "Breakfast",  420, 19, 46, 18),
    ("",          "",           "Lunch",      600, 36, 58, 20),
    ("",          "",           "Dinner",     840, 45, 54, 44),
    ("Saturday",  "Turkish",    "Breakfast",  425, 19, 48, 18),
    ("",          "",           "Lunch",      600, 36, 56, 20),
    ("",          "",           "Dinner",     840, 45, 56, 45),
    ("Sunday",    "French",     "Breakfast",  420, 19, 46, 20),
    ("",          "",           "Lunch",      600, 35, 54, 22),
    ("",          "",           "Dinner",     840, 45, 52, 46),
]

SHOPPING = {
    "Meat, Poultry & Fish": [
        "Chicken (thigh, breast, bone-in) — 6.3 kg total (souvlaki, katsu, pad Thai, paella, doro wat, şiş kebab, coq au vin)",
        "Beef (sirloin, chuck, cheek, ground) — 5.4 kg total (youvetsi, sukiyaki, panang curry, carrillada, tibs, adana, bourguignon)",
    ],
    "Dairy & Eggs": [
        "Eggs — 64 large",
        "Greek yogurt — 500 g; feta — 250 g; kefalotyri or parmesan — 150 g",
        "Butter — 300 g; milk — 500 ml; Kewpie mayonnaise — small jar",
    ],
    "Bread & Grains": [
        "Rice (short-grain, jasmine, bomba/paella) — 2.4 kg total",
        "Bulgur — 500 g; orzo — 400 g; flat rice noodles — 400 g; udon noodles — 400 g; vermicelli — 100 g",
        "Pita, simit, injera (or flatbread), croissants, baguette, village bread, panko breadcrumbs",
    ],
    "Tinned & Jarred": [
        "Crushed tomatoes; tomato paste; panang curry paste; berbere spice blend; niter kibbeh (or ghee)",
        "Tamarind paste; coconut milk; tonkatsu sauce; sriracha; pomegranate molasses",
        "Soy sauce; mirin; fish sauce; kalamata olives; red wine, Rioja & Burgundy style (for cooking)",
    ],
    "Produce — Vegetables": [
        "Onions — 18; garlic — 14 heads; ginger — 1 knob",
        "Tomatoes — 14; potatoes — 10; cucumbers — 4; green/red peppers — 8; padrón or shishito peppers — 200 g",
        "Napa or green cabbage — 1 head; collard greens — 1 bunch; carrots — 6; mushrooms — 400 g; pearl onions — 300 g; green beans — 300 g",
    ],
    "Herbs & Seasonal Fruit": [
        "Parsley — 2 bunches; dill — 1 bunch; Thai basil — 1 bunch; chives & tarragon — small bunches; scallion — 1 bunch",
        "Lemons — 8; limes — 4; kaffir lime leaves — 10; umeboshi (pickled plum) — 6",
        "Peanuts, crushed — 80 g",
    ],
    "Pantry & Spice": [
        "Saffron, smoked paprika, sumac, cumin, coriander, oregano, thyme, bay leaf, cinnamon stick",
        "Turmeric, berbere, chili flakes, white pepper, palm sugar",
        "Olive oil; sesame/neutral oil; sugar; red wine, Rioja & Burgundy (for cooking)",
    ],
}

BUDGET = [
    ("Meat, Poultry & Fish",         "$150–186"),
    ("Dairy & Eggs",                 "$27–33"),
    ("Bread & Grains",               "$30–36"),
    ("Produce (veg, herbs, fruit)",  "$58–70"),
    ("Tinned & Jarred",              "$26–32"),
    ("Condiments & Spices",          "$24–30"),
    ("Pantry & Other",               "$10–14"),
    ("TOTAL (3–4 people)",           "~$325–401"),
    ("Per person / week",            "~$81–100"),
    ("Per person / day",             "~$12–14"),
]

MEAL_PREP = [
    ("Saturday — Main Prep Day", [
        "Brown and start Sunday's beef bourguignon a day ahead — the flavor deepens overnight in the fridge",
        "Marinate Saturday's chicken şiş and Monday's souvlaki chicken ahead — both keep well overnight",
        "Slow-cook Thursday's Rioja beef cheeks early — the long braise rewards a head start",
        "Cook down Friday's berbere onion base for doro wat a day ahead",
        "Whip Saturday's cacık and Monday's tzatziki ahead — both keep well chilled for the week",
    ]),
    ("Sunday — Light Setup", [
        "Marinate Wednesday's panang curry beef and Monday's souvlaki the night before for a flying start to the week",
        "Pre-chop Sunday's bourguignon vegetables (carrot, onion, garlic) to speed up that simmer night",
        "Cook extra rice and bulgur in advance for the week's grain sides",
        "Prep Friday's awaze paste and Saturday's ezme salad base ahead — both keep for days",
    ]),
    ("During the Week", [
        "Mon: Extra youvetsi orzo sauce keeps 3–4 days and reheats beautifully with a splash of stock",
        "Tue: Leftover miso paste and pickled plum make a quick soup base for busy nights",
        "Wed: Extra panang curry sauce freezes well for a future quick beef or vegetable curry",
        "Thu: Leftover smoked paprika aioli is great spooned over any roasted vegetable later in the week",
    ]),
]

LEFTOVERS = [
    ("Monday Beef Youvetsi",       "Tue. orzo remix",      "Reheat with a splash of stock and stir through freshly grated cheese"),
    ("Tuesday Beef Sukiyaki",      "Wed. noodle remix",    "Toss cold beef and broth through leftover udon for a quick soupy lunch"),
    ("Wednesday Beef Panang Curry","Thu. rice bowl remix", "Reheat gently and spoon over rice with a squeeze of lime"),
    ("Thursday Beef Carrillada",   "Fri. sandwich remix",  "Shred and pile into crusty bread with a spoonful of the braising sauce"),
    ("Friday Beef Tibs",           "Sat. wrap remix",      "Warm and tuck into flatbread with a spoonful of awaze"),
    ("Any grilled or roasted protein", "Next-day grain bowl", "Slice cold and scatter over rice or bulgur with a quick lemon-oil dressing"),
]


# ── SECTION HEADER ────────────────────────────────────────────────────────────
def section_header(title, subtitle=None):
    h_sty = s(fontName="Helvetica-Bold", fontSize=13, textColor=WHITE, alignment=TA_CENTER, leading=16)
    s_sty = s(fontName="Helvetica-Oblique", fontSize=8, textColor=colors.HexColor("#BBCCBB"),
              alignment=TA_CENTER, leading=11)
    rows = [[P(title, h_sty)]]
    if subtitle:
        rows.append([P(subtitle, s_sty)])
    t = Table(rows, colWidths=[USABLE_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), FOREST),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    return [t, Spacer(1, 0.35 * cm)]


# ── COVER PAGE ────────────────────────────────────────────────────────────────
def cover_page(week, days):
    elems = []

    # ── big title block
    T = s(fontName="Helvetica-Bold",    fontSize=38, textColor=WHITE, alignment=TA_CENTER, spaceAfter=0, leading=48)
    I = s(fontName="Helvetica-Oblique", fontSize=20, textColor=GOLD,  alignment=TA_CENTER, spaceAfter=6, leading=26)
    W = s(fontName="Helvetica-Bold",    fontSize=14, textColor=WHITE, alignment=TA_CENTER, spaceAfter=0, leading=18)
    X = s(fontName="Helvetica",         fontSize=8.5, textColor=colors.HexColor("#AACCAA"), alignment=TA_CENTER, spaceAfter=0, leading=12)

    header_rows = [
        [P("Weekly Menu Plan", T)],
        [P("&amp; Recipes", I)],
        [Spacer(1, 0.3 * cm)],
        [P(f"Week of {week}", W)],
        [Spacer(1, 0.25 * cm)],
        [HRFlowable(width="55%", thickness=0.8, color=colors.HexColor("#6A9A7A"), hAlign="CENTER", spaceAfter=6)],
        [Spacer(1, 0.1 * cm)],
        [P("7 days · 21 meals · Serves 3–4 · No pork · Fish &amp; meat welcome", X)],
        [P("Full recipes · Calories &amp; macros · Drink pairings · Meal prep guide", X)],
        [P("Leftovers map · Shopping list · Budget estimate", X)],
        [Spacer(1, 0.35 * cm)],
    ]
    hdr_t = Table(header_rows, colWidths=[USABLE_W])
    hdr_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), FOREST),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elems.append(Spacer(1, 1.5 * cm))
    elems.append(hdr_t)
    elems.append(Spacer(1, 0.7 * cm))

    # ── day-cuisine grid
    day_sty  = s(fontName="Helvetica-Bold",    fontSize=9.5, textColor=WHITE)
    cuis_sty = s(fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.HexColor("#D0EAD8"))
    kcal_sty = s(fontName="Helvetica",         fontSize=8.5, textColor=GOLD, alignment=TA_RIGHT)

    grid_data = []
    for i, d in enumerate(days):
        bg = SAGE if i % 2 == 0 else colors.HexColor("#265C42")
        grid_data.append(([
            P(d["day"].upper(), day_sty),
            P(d["cuisine"], cuis_sty),
            P(d["kcal"] + " kcal", kcal_sty),
        ], bg))

    col_w = [3.2 * cm, 10.5 * cm, 4.3 * cm]
    grid_rows = [r for r, _ in grid_data]
    grid = Table(grid_rows, colWidths=col_w)
    style_cmds = [
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.3, FOREST),
    ]
    for i, (_, bg) in enumerate(grid_data):
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    grid.setStyle(TableStyle(style_cmds))
    elems.append(grid)

    elems.append(Spacer(1, 0.8 * cm))
    credit = s(fontName="Helvetica-Oblique", fontSize=8, textColor=MUTED, alignment=TA_CENTER)
    elems.append(P(f"Created by Marina  ·  {datetime.now().strftime('%B %Y')}", credit))
    elems.append(PageBreak())
    return elems


# ── WEEKLY OVERVIEW TABLE ─────────────────────────────────────────────────────
def weekly_overview(days):
    elems = section_header(
        "Weekly Overview",
        "All 7 days at a glance — one cuisine per day, breakfast through dinner"
    )

    H  = s(fontName="Helvetica-Bold",    fontSize=8,   textColor=WHITE,     alignment=TA_CENTER)
    D  = s(fontName="Helvetica-Bold",    fontSize=8.5, textColor=FOREST)
    C  = s(fontName="Helvetica-Oblique", fontSize=7.5, textColor=MUTED)
    MN = s(fontName="Helvetica-Bold",    fontSize=8,   textColor=TEXT)
    KC = s(fontName="Helvetica",         fontSize=7.5, textColor=AMBER)
    DT = s(fontName="Helvetica-Bold",    fontSize=9,   textColor=AMBER,     alignment=TA_CENTER)

    header = [
        [P("Day / Cuisine", H), P("Breakfast", H), P("Lunch", H), P("Dinner", H), P("Total\nkcal", H)],
    ]

    rows = list(header)
    for i, d in enumerate(days):
        m = d["meals"]
        day_cell = [P(d["day"], D), Spacer(1, 2), P(d["cuisine"], C)]

        def mc(meal):
            return [P(meal["name"], MN), Spacer(1, 2), P(meal["kcal"] + " kcal", KC)]

        row = [day_cell, mc(m[0]), mc(m[1]), mc(m[2]), [P(d["kcal"], DT)]]
        rows.append(row)

    col_w = [3.5 * cm, 4.5 * cm, 4.5 * cm, 4.5 * cm, 1.5 * cm]
    t = Table(rows, colWidths=col_w, repeatRows=1)
    ts = [
        ("BACKGROUND",    (0, 0), (-1, 0), FOREST),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY_MD),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]
    for i in range(1, len(rows)):
        bg = LEAF if i % 2 == 0 else WHITE
        ts.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(ts))
    elems.append(t)
    elems.append(PageBreak())
    return elems


# ── MEAL PREP & LEFTOVERS ─────────────────────────────────────────────────────
def prep_page():
    elems = section_header("Meal Prep Guide", "A little weekend effort = breezy weeknight cooking")

    sec_sty  = s(fontName="Helvetica-Bold", fontSize=9,   textColor=WHITE)
    item_sty = s(fontName="Helvetica",      fontSize=8.5, textColor=TEXT, leftIndent=10, spaceAfter=3)

    SEC_COLORS = [FOREST, SAGE, AMBER]
    for idx, (section, items) in enumerate(MEAL_PREP):
        sc = SEC_COLORS[idx % len(SEC_COLORS)]
        sec_row = Table([[P(section, sec_sty)]], colWidths=[USABLE_W])
        sec_row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), sc),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ]))
        elems.append(sec_row)
        for item in items:
            elems.append(P(f"✓  {item}", item_sty))
        elems.append(Spacer(1, 0.3 * cm))

    elems.append(Spacer(1, 0.3 * cm))
    elems += section_header("Leftovers Map", "Turn tonight's dinner into tomorrow's shortcut")

    H   = s(fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE)
    C   = s(fontName="Helvetica",      fontSize=8,   textColor=TEXT)
    CB  = s(fontName="Helvetica-Bold", fontSize=8,   textColor=FOREST)

    lft_data = [[P("Original Dish", H), P("Best Reuse", H), P("How to Use It", H)]]
    for orig, reuse, how in LEFTOVERS:
        lft_data.append([P(orig, CB), P(reuse, C), P(how, C)])

    lft = Table(lft_data, colWidths=[4.5 * cm, 3.5 * cm, 10.0 * cm])
    lt_style = [
        ("BACKGROUND",    (0, 0), (-1, 0), SAGE),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY_MD),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]
    for i in range(1, len(lft_data)):
        bg = LEAF if i % 2 == 0 else WHITE
        lt_style.append(("BACKGROUND", (0, i), (-1, i), bg))
    lft.setStyle(TableStyle(lt_style))
    elems.append(lft)
    elems.append(PageBreak())
    return elems


# ── PER-DAY RECIPE PAGES ──────────────────────────────────────────────────────
def day_pages(days):
    elems = []

    TYPE_COLORS = {
        "BREAKFAST": colors.HexColor("#B55A1E"),   # warm terracotta
        "LUNCH":     SAGE,
        "DINNER":    FOREST,
    }

    day_title = s(fontName="Helvetica-Bold",    fontSize=13,  textColor=WHITE, leading=16)
    day_kcal  = s(fontName="Helvetica-Bold",    fontSize=9.5, textColor=GOLD,   alignment=TA_RIGHT)
    type_sty  = s(fontName="Helvetica-Bold",    fontSize=8.5, textColor=WHITE)
    time_sty  = s(fontName="Helvetica",         fontSize=8,   textColor=WHITE,   alignment=TA_RIGHT)
    name_sty  = s(fontName="Helvetica-Bold",    fontSize=11,  textColor=TEXT,    spaceAfter=2, leading=14)
    sub_sty   = s(fontName="Helvetica-Oblique", fontSize=8.5, textColor=MUTED,   spaceAfter=3)
    mac_sty   = s(fontName="Helvetica-Bold",    fontSize=8,   textColor=SAGE,    spaceAfter=3)
    ing_hdr   = s(fontName="Helvetica-Bold",    fontSize=8,   textColor=FOREST,  spaceAfter=3)
    ing_sty   = s(fontName="Helvetica",         fontSize=8,   textColor=TEXT,    leftIndent=6, spaceAfter=2)
    mth_hdr   = s(fontName="Helvetica-Bold",    fontSize=8,   textColor=FOREST,  spaceAfter=3)
    mth_sty   = s(fontName="Helvetica",         fontSize=8,   textColor=TEXT,    leftIndent=6, spaceAfter=3)
    drk_sty   = s(fontName="Helvetica-Oblique", fontSize=8,   textColor=NAVY,    spaceAfter=2)

    for d in days:
        # ── day banner
        day_row = Table(
            [[P(f"{d['day']}  —  {d['cuisine']}", day_title),
              P(f"Daily Total: {d['kcal']} kcal / person", day_kcal)]],
            colWidths=[USABLE_W * 0.6, USABLE_W * 0.4]
        )
        day_row.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), FOREST),
            ("TOPPADDING",    (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ("LEFTPADDING",   (0, 0), (-1, -1), 11),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 11),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elems.append(day_row)
        elems.append(Spacer(1, 0.3 * cm))

        for meal in d["meals"]:
            tc = TYPE_COLORS.get(meal["type"], SAGE)

            # ── type bar: meal type left, time right
            type_bar = Table(
                [[P(meal["type"], type_sty), P(meal["time"], time_sty)]],
                colWidths=[USABLE_W * 0.5, USABLE_W * 0.5]
            )
            type_bar.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), tc),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ]))

            # ── kcal + name + subtitle + macros (full width header block)
            header_block = [
                type_bar,
                Spacer(1, 0.15 * cm),
                P(f"{meal['name']}  <font color='#C47A1A' size='9'>{meal['kcal']} kcal</font>", name_sty),
                P(meal["subtitle"], sub_sty),
                P(meal["macros"], mac_sty),
            ]

            # ── two-column: ingredients (left) | method (right)
            ing_content  = [P("INGREDIENTS", ing_hdr)]
            for ing in meal["ingredients"]:
                ing_content.append(P(f"• {ing}", ing_sty))

            mth_content  = [P("METHOD", mth_hdr)]
            for i, step in enumerate(meal["method"], 1):
                mth_content.append(P(f"{i}.  {step}", mth_sty))

            two_col = Table(
                [[ing_content, mth_content]],
                colWidths=[ING_W, METH_W],
            )
            two_col.setStyle(TableStyle([
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
                ("LINEAFTER",     (0, 0), (0, -1),  0.5, BORDER),
                ("BACKGROUND",    (0, 0), (-1, -1), CARD_BG),
            ]))

            card_content = header_block + [two_col]

            if meal.get("drink"):
                card_content.append(Spacer(1, 0.1 * cm))
                card_content.append(
                    Table([[P(f"Drink pairing:  {meal['drink']}", drk_sty)]],
                          colWidths=[USABLE_W])
                )
                card_content[-1].setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#EEF4FF")),
                    ("TOPPADDING",    (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
                ]))

            # wrap in outer card with border
            outer = Table([[card_content]], colWidths=[USABLE_W])
            outer.setStyle(TableStyle([
                ("BOX",           (0, 0), (-1, -1), 0.6, BORDER),
                ("TOPPADDING",    (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                ("BACKGROUND",    (0, 0), (-1, -1), CARD_BG),
            ]))
            elems.append(KeepTogether(outer))
            elems.append(Spacer(1, 0.3 * cm))

        elems.append(PageBreak())
    return elems


# ── SHOPPING PAGE ─────────────────────────────────────────────────────────────
def shopping_page(shopping):
    elems = section_header("Shopping List", "All quantities for 3–4 people for the full week")

    # 3-column grid
    CATS = list(shopping.keys())
    COL_W = (USABLE_W - 0.4 * cm) / 3

    cat_hdr  = s(fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE)
    item_sty = s(fontName="Helvetica",      fontSize=7.5, textColor=TEXT, leftIndent=5, spaceAfter=2)

    def cat_block(cat):
        if cat is None:
            return Spacer(1, 0.1 * cm)
        rows = [[P(cat, cat_hdr)]]
        for item in shopping[cat]:
            rows.append([P(f"• {item}", item_sty)])
        t = Table(rows, colWidths=[COL_W])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), SAGE),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING",   (0, 0), (-1, -1), 7),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
            ("BOX",           (0, 0), (-1, -1), 0.3, GREY_MD),
        ]))
        return t

    triplets = []
    for i in range(0, len(CATS), 3):
        triplets.append((
            CATS[i],
            CATS[i + 1] if i + 1 < len(CATS) else None,
            CATS[i + 2] if i + 2 < len(CATS) else None,
        ))

    for a, b, c in triplets:
        row = Table(
            [[cat_block(a), cat_block(b), cat_block(c)]],
            colWidths=[COL_W, COL_W, COL_W],
        )
        row.setStyle(TableStyle([
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING",   (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
        ]))
        elems.append(KeepTogether(row))
        elems.append(Spacer(1, 0.2 * cm))

    elems.append(PageBreak())
    return elems


# ── BUDGET PAGE ───────────────────────────────────────────────────────────────
def budget_page(budget):
    elems = section_header("Estimated Budget",
                           "Approximate USD grocery cost. Prices vary by location and store.")

    H   = s(fontName="Helvetica-Bold", fontSize=9,   textColor=WHITE,   alignment=TA_CENTER)
    cat = s(fontName="Helvetica",      fontSize=9,   textColor=TEXT)
    val = s(fontName="Helvetica",      fontSize=9,   textColor=TEXT,    alignment=TA_CENTER)
    Th  = s(fontName="Helvetica-Bold", fontSize=9.5, textColor=WHITE)
    Tv  = s(fontName="Helvetica-Bold", fontSize=9.5, textColor=GOLD,    alignment=TA_CENTER)

    rows = [[P("Category", H), P("Estimated Cost", H)]]
    for cat_name, cost in budget:
        is_total = cat_name.startswith("TOTAL") or cat_name.startswith("Per")
        rows.append([P(cat_name, Th if is_total else cat),
                     P(cost,     Tv if is_total else val)])

    t = Table(rows, colWidths=[11 * cm, 4 * cm], hAlign="LEFT")
    style = [
        ("BACKGROUND",    (0, 0), (-1, 0), SAGE),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY_MD),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]
    total_rows = [i + 1 for i, (cn, _) in enumerate(budget)
                  if cn.startswith("TOTAL") or cn.startswith("Per")]
    for ri in total_rows:
        style.append(("BACKGROUND", (0, ri), (-1, ri), FOREST))
    for i in range(1, len(rows)):
        if i not in total_rows:
            bg = LEAF if i % 2 == 0 else WHITE
            style.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(style))
    elems.append(t)
    elems.append(PageBreak())
    return elems


# ── MACRO SUMMARY ─────────────────────────────────────────────────────────────
def macro_page(data):
    elems = section_header("Calorie & Macro Summary",
                           "Approximate values per serving (1 person). Actual amounts vary.")

    H  = s(fontName="Helvetica-Bold",    fontSize=8,   textColor=WHITE,   alignment=TA_CENTER)
    D  = s(fontName="Helvetica-Bold",    fontSize=8,   textColor=TEXT)
    CI = s(fontName="Helvetica-Oblique", fontSize=7.5, textColor=MUTED)
    M  = s(fontName="Helvetica",         fontSize=8,   textColor=TEXT,    alignment=TA_CENTER)
    KC = s(fontName="Helvetica-Bold",    fontSize=8,   textColor=AMBER,   alignment=TA_CENTER)
    PR = s(fontName="Helvetica",         fontSize=8,   textColor=RUST,    alignment=TA_CENTER)
    CB = s(fontName="Helvetica",         fontSize=8,   textColor=NAVY,    alignment=TA_CENTER)
    TL = s(fontName="Helvetica-Bold",    fontSize=8,   textColor=WHITE,   alignment=TA_CENTER)
    TV = s(fontName="Helvetica-Bold",    fontSize=8,   textColor=GOLD,    alignment=TA_CENTER)

    rows = [[P("Day", H), P("Cuisine", H), P("Meal", H),
             P("Calories", H), P("Protein", H), P("Carbs", H), P("Fat", H)]]

    for day, cuis, meal, kcal, prot, carb, fat in data:
        rows.append([
            P(day,  D  if day  else M),
            P(cuis, CI if cuis else M),
            P(meal, M),
            P(f"~{kcal}", KC),
            P(f"{prot} g", PR),
            P(f"{carb} g", CB),
            P(f"{fat} g",  M),
        ])

    # totals
    tk = sum(r[3] for r in data)
    tp = sum(r[4] for r in data)
    tc = sum(r[5] for r in data)
    tf = sum(r[6] for r in data)
    rows.append([P("DAILY AVG", TL),   P("", TL), P("", TL),
                 P(f"~{tk//7}",    TV), P(f"{tp//7} g", TV), P(f"{tc//7} g", TV), P(f"{tf//7} g", TV)])
    rows.append([P("WEEKLY TOTAL", TL), P("", TL), P("", TL),
                 P(f"~{tk}",      TV), P(f"{tp} g",    TV), P(f"{tc} g",    TV), P(f"{tf} g",    TV)])

    col_w = [2.8 * cm, 3.5 * cm, 2.6 * cm, 2.4 * cm, 2.2 * cm, 2.2 * cm, 2.3 * cm]
    t = Table(rows, colWidths=col_w, repeatRows=1)
    ts = [
        ("BACKGROUND",    (0, 0),  (-1, 0),  FOREST),
        ("GRID",          (0, 0),  (-1, -1), 0.3, GREY_MD),
        ("TOPPADDING",    (0, 0),  (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0),  (-1, -1), 5),
        ("LEFTPADDING",   (0, 0),  (-1, -1), 6),
        ("BACKGROUND",    (0, -1), (-1, -1), FOREST),
        ("BACKGROUND",    (0, -2), (-1, -2), FOREST),
    ]
    for i in range(1, len(rows) - 2):
        bg = LEAF if i % 3 == 0 else WHITE
        ts.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(ts))
    elems.append(t)
    elems.append(Spacer(1, 0.5 * cm))

    note = s(fontName="Helvetica-Oblique", fontSize=7.5, textColor=MUTED, alignment=TA_CENTER)
    elems.append(P(
        "Estimates are approximate. Check your pantry before shopping — spices, oils and staples may already be stocked.",
        note
    ))
    return elems


# ── BUILD ──────────────────────────────────────────────────────────────────
# -- BUILD PDF ----------------------------------------------------------------
def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN,  bottomMargin=MARGIN,
    )
    story  = []
    story += cover_page(WEEK, DAYS)
    story += weekly_overview(DAYS)
    story += prep_page()
    story += day_pages(DAYS)
    story += shopping_page(SHOPPING)
    story += budget_page(BUDGET)
    story += macro_page(MACRO_DATA)
    doc.build(story, canvasmaker=HFCanvas)
    print("PDF saved to " + OUTPUT_FILE)


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Render the saved menu or a freshly AI-generated JSON plan.")
    parser.add_argument("--plan", type=Path, help="JSON file from generate_recipes.py")
    args = parser.parse_args()
    if args.plan:
        from generate_recipes import renderer_data
        try:
            plan = renderer_data(json.loads(args.plan.read_text(encoding="utf-8")))
        except (ValueError, OSError, KeyError, TypeError) as exc:
            parser.error(f"Cannot load plan: {exc}")
        WEEK = plan["WEEK"]
        DAYS = plan["DAYS"]
        MACRO_DATA = plan["MACRO_DATA"]
        SHOPPING = plan["SHOPPING"]
        BUDGET = plan["BUDGET"]
        MEAL_PREP = plan["MEAL_PREP"]
        LEFTOVERS = plan["LEFTOVERS"]
    build_pdf()
