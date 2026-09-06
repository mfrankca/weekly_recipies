"""Regression checks for content longer than a single PDF page."""
import io
import unittest
from reportlab.platypus import SimpleDocTemplate
import menu_plan_v2 as renderer


class PdfLayoutTests(unittest.TestCase):
    def test_long_recipe_and_shopping_category_can_continue(self):
        meal = {
            "type": "DINNER", "name": "Long recipe", "subtitle": "Layout fixture",
            "kcal": "~500", "macros": "Protein 20 g | Carbs 50 g | Fat 20 g",
            "time": "Prep 20 min | Cook 60 min", "drink": "Water",
            "ingredients": [f"Ingredient {i}: 100 g vegetables" for i in range(50)],
            "method": [f"Step {i}: " + "Stir gently over medium heat for five minutes until softened. " * 8 for i in range(30)],
        }
        days = [{"day": "Monday", "cuisine": "Test", "kcal": "~500", "meals": [meal]}]
        story = renderer.day_pages(days) + renderer.shopping_page({"Produce": [f"Item {i}: 200 g vegetables" for i in range(150)]})
        output = io.BytesIO()
        SimpleDocTemplate(output, pagesize=renderer.A4,
                          leftMargin=renderer.MARGIN, rightMargin=renderer.MARGIN,
                          topMargin=renderer.MARGIN, bottomMargin=renderer.MARGIN).build(story)
        self.assertTrue(output.getvalue().startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
