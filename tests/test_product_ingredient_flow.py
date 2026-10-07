import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import flet as ft

from database.database import Database
from services.calculadora import product_cost
from views.productos import productos_view


class TestPage:
    """Small page adapter for exercising the real Flet event callbacks."""

    def __init__(self):
        self.dialogs = []
        self.updated_controls = []

    def update(self, *controls):
        self.updated_controls.extend(controls)

    def show_dialog(self, dialog):
        self.dialogs.append(dialog)

    def pop_dialog(self):
        return self.dialogs.pop()


class ProductIngredientFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp_dir.name) / "costos.db")
        self.db.initialize()
        self.materials = {}
        for name, category, price, quantity, purchase_unit in [
            ("Harina QA", "Harinas", 20000, 25, "kilogramos"),
            ("Queso QA", "Quesos", 1000, 500, "gramos"),
            ("Levadura QA", "Otros", 5, 1, "gramos"),
            ("Aceite QA", "Aceites", 6000, 5, "litros"),
            ("Salsa QA", "Salsas", 500, 500, "mililitros"),
            ("Huevo QA", "Huevos", 1200, 12, "unidad"),
        ]:
            self.materials[name] = self.db.save_raw_material(
                {
                    "nombre": name,
                    "categoria": category,
                    "precio_compra": price,
                    "cantidad_compra": quantity,
                    "unidad_compra": purchase_unit,
                }
            )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_flet_086_does_not_mark_dropdown_options_assignment_dirty(self):
        dropdown = ft.Dropdown(options=[])
        dropdown.options = [ft.dropdown.Option(key="gramos", text="g")]
        self.assertNotIn("options", dropdown._dirty)

    def _open_product_form(self, page, product=None):
        if product is not None:
            view = productos_view(page, self.db, lambda: None)
            table = view.controls[2].controls[0]
            row = next(
                row
                for row in table.rows
                if row.cells[0].content.value == product["nombre"]
            )
            row.cells[4].content.controls[0].on_click(None)
        else:
            productos_view(page, self.db, lambda: None, open_new=True)
        return page.dialogs[-1]

    def _open_add_ingredient(self, page, product_dialog):
        product_dialog.content.content.controls[3].controls[1].on_click(None)
        return page.dialogs[-1]

    def _select_material(self, page, ingredient_dialog, name):
        selected = ingredient_dialog.content.controls[0]
        selected.value = str(self.materials[name])
        self.assertIsNotNone(selected.on_select)
        selected.on_select(SimpleNamespace(control=selected))
        unit_host = ingredient_dialog.content.controls[1].controls[1]
        unit = unit_host.content
        self.assertIn(unit_host, page.updated_controls)
        self.assertIn("content", unit_host._dirty)
        self.assertFalse(unit.disabled)
        self.assertTrue(unit.visible)
        self.assertEqual(unit.opacity, 1)
        self.assertEqual(unit.width, 180)
        self.assertIn("Control actual en contenedor: sí", ingredient_dialog.content.controls[2].value)
        unit.on_focus(SimpleNamespace(control=unit))
        self.assertIn("recibió foco/clic", ingredient_dialog.content.controls[2].value)
        return ingredient_dialog.content.controls[1].controls[0], unit

    def test_create_edit_switch_units_save_and_reopen_recipe(self):
        page = TestPage()
        product_dialog = self._open_product_form(page)
        form = product_dialog.content.content.controls
        form[0].value = "Receta QA"
        form[1].controls[0].value = "Pizzas"
        form[1].controls[1].value = "1 unidad"

        ingredient_dialog = self._open_add_ingredient(page, product_dialog)
        unit = ingredient_dialog.content.controls[1].controls[1].content
        self.assertFalse(unit.disabled)
        self.assertEqual(unit.options, [])
        self.assertTrue(unit.visible)

        # kg -> g/kg; 500 g of $20,000 / 25 kg costs $400.
        quantity, unit = self._select_material(page, ingredient_dialog, "Harina QA")
        self.assertEqual(
            {option.key for option in unit.options},
            {"miligramos", "gramos", "kilogramos"},
        )
        self.assertEqual(
            {option.text for option in unit.options},
            {"miligramos", "gramos", "kilogramos"},
        )
        quantity.value = "500"
        unit.value = "gramos"
        ingredient_dialog.actions[1].on_click(None)
        recipe_host = form[4]
        self.assertIn("$ 400,00", recipe_host.controls[1].value)

        # Edit the ingredient and switch to kg; the cost remains $400.
        recipe_host.controls[0].rows[0].cells[4].content.controls[0].on_click(None)
        ingredient_dialog = page.dialogs[-1]
        unit = ingredient_dialog.content.controls[1].controls[1].content
        self.assertEqual(unit.value, "gramos")
        self.assertEqual(
            {option.key for option in unit.options},
            {"miligramos", "gramos", "kilogramos"},
        )
        ingredient_dialog.content.controls[1].controls[0].value = "0.5"
        unit.value = "kilogramos"
        ingredient_dialog.actions[1].on_click(None)
        self.assertIn("$ 400,00", recipe_host.controls[1].value)

        # Change material: kg/g options must be replaced by ml/L immediately.
        recipe_host.controls[0].rows[0].cells[4].content.controls[0].on_click(None)
        ingredient_dialog = page.dialogs[-1]
        selected = ingredient_dialog.content.controls[0]
        selected.value = str(self.materials["Aceite QA"])
        selected.on_select(SimpleNamespace(control=selected))
        unit = ingredient_dialog.content.controls[1].controls[1].content
        self.assertEqual({option.key for option in unit.options}, {"mililitros", "litros"})
        self.assertEqual(unit.value, "mililitros")
        ingredient_dialog.content.controls[1].controls[0].value = "0.1"
        unit.value = "litros"
        ingredient_dialog.actions[1].on_click(None)
        self.assertIn("$ 120,00", recipe_host.controls[1].value)

        # Exercise g, L, ml and unit source families in separate ingredients.
        expected = [
            ("Queso QA", "gramos", "10"),
            ("Levadura QA", "miligramos", "100"),
            ("Salsa QA", "mililitros", "50"),
            ("Huevo QA", "unidad", "1"),
        ]
        for material_name, expected_unit, quantity_value in expected:
            ingredient_dialog = self._open_add_ingredient(page, product_dialog)
            quantity, unit = self._select_material(page, ingredient_dialog, material_name)
            allowed = {option.key for option in unit.options}
            self.assertIn(expected_unit, allowed)
            self.assertEqual(
                allowed,
                {
                    "Queso QA": {"miligramos", "gramos", "kilogramos"},
                    "Levadura QA": {"miligramos", "gramos", "kilogramos"},
                    "Salsa QA": {"mililitros", "litros"},
                    "Huevo QA": {"unidad"},
                }[material_name],
            )
            quantity.value = quantity_value
            unit.value = expected_unit
            ingredient_dialog.actions[1].on_click(None)

        self.assertIn("$ 290,50", recipe_host.controls[1].value)
        product_dialog.actions[1].on_click(None)

        product = self.db.list_products("Receta QA")[0]
        saved_ingredients = self.db.product_ingredients(product["id"])
        self.assertEqual(len(saved_ingredients), 5)
        self.assertEqual(product_cost(saved_ingredients), 290.5)

        # Reopening a saved product keeps its ingredients and selected units.
        reopened_page = TestPage()
        reopened = self._open_product_form(reopened_page, product)
        reopened_recipe = reopened.content.content.controls[4]
        self.assertEqual(len(reopened_recipe.controls[0].rows), 5)
        reopened_recipe.controls[0].rows[0].cells[4].content.controls[0].on_click(None)
        edit_dialog = reopened_page.dialogs[-1]
        self.assertEqual(
            edit_dialog.content.controls[1].controls[1].content.value,
            "litros",
        )
        self.assertEqual(
            {
                option.key
                for option in edit_dialog.content.controls[1].controls[1].content.options
            },
                {"mililitros", "litros"},
        )

    def test_recipe_uses_current_raw_material_price(self):
        flour_id = self.materials["Harina QA"]
        product_id = self.db.save_product(
            {"nombre": "Precio QA", "categoria": "Otros", "descripcion": "", "rendimiento": "1"},
            [{"materia_prima_id": flour_id, "cantidad": 500, "unidad": "gramos"}],
        )
        self.assertEqual(product_cost(self.db.product_ingredients(product_id)), 400)

        self.db.save_raw_material(
            {
                "nombre": "Harina QA",
                "categoria": "Harinas",
                "precio_compra": 25000,
                "cantidad_compra": 25,
                "unidad_compra": "kilogramos",
            },
            flour_id,
        )
        self.assertEqual(product_cost(self.db.product_ingredients(product_id)), 500)


if __name__ == "__main__":
    unittest.main()
