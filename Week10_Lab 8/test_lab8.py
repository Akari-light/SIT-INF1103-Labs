"""Lab 8 evidence. Run from this folder: python -B -m unittest -v test_lab8."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from typing import get_type_hints
from unittest.mock import patch

import OOP_inventory_manager as app


class Lab8Tests(unittest.TestCase):
    def setUp(self):
        self.supplier = app.Supplier("S001", "Tech Supply", "sales@example.com")
        self.mouse = app.PhysicalProduct("P002", "Mouse", 25.50, 40, 0.5, self.supplier)
        self.software = app.DigitalProduct("D001", "Photo Editor", 49.99, 10, 350, self.supplier)

    def test_supplier_association(self):
        supplier = app.Supplier("S002", "Example Supply", "orders@example.com")
        mouse = app.PhysicalProduct("P003", "Mouse", 25.50, 40, 0.5, supplier)
        software = app.DigitalProduct("D002", "Photo Editor", 49.99, 10, 350, supplier)
        self.assertIs(mouse.supplier, supplier)
        self.assertIsNot(mouse, supplier)
        del supplier
        self.assertIs(mouse.supplier, software.supplier)
        output = io.StringIO()
        with redirect_stdout(output):
            mouse.supplier.display_information()
            software.supplier.display_information()
        self.assertEqual(output.getvalue().count("orders@example.com"), 2)

    def test_inventory_aggregation_and_transfer(self):
        a, b = app.Inventory(), app.Inventory()
        a.add_product(self.mouse)
        self.assertIs(a.remove_product("P002"), self.mouse)
        self.assertIsNone(a.search_product("P002"))
        self.assertIsNone(a.remove_product("P002"))
        self.mouse.set_stock(20)
        b.add_product(self.mouse)
        self.assertIs(b.search_product("P002"), self.mouse)
        self.assertEqual(b.create_product_list()[0]["stock"], 20)

    def test_order_composition_and_totals(self):
        a, b = app.Order("O001"), app.Order("O002")
        a.add_order_line(self.mouse, 3)
        a.add_order_line(self.software, 1)
        b.add_order_line(self.mouse, 1)
        self.assertIsInstance(a.order_lines[0], app.OrderLine)
        self.assertIsNot(a.order_lines[0], b.order_lines[0])
        self.assertIs(a.order_lines[0].product, b.order_lines[0].product)
        self.assertIs(a.order_lines[0].product, self.mouse)
        self.assertAlmostEqual(a.order_lines[0].calculate_subtotal(), 76.50)
        self.assertAlmostEqual(a.calculate_total(), 126.49)
        self.assertAlmostEqual(b.calculate_total(), 25.50)
        del a
        self.assertIs(b.order_lines[0].product, self.mouse)
        self.assertAlmostEqual(b.calculate_total(), 25.50)

    def test_substitutability_and_polymorphic_inventory(self):
        def show_product_details(product: app.Product) -> None:
            product.display_information()
            print(product.get_fulfilment_info())

        inventory = app.Inventory()
        products: list[app.Product] = [self.mouse, self.software]
        for product in products:
            product.set_stock(20)
            with self.assertRaises(ValueError):
                product.set_stock(-5)
            self.assertEqual(product.create_product_dict()["stock"], 20)
            inventory.add_product(product)

        def display_products():
            for product in products:
                show_product_details(product)

        for display in (display_products, inventory.display_all):
            output = io.StringIO()
            with redirect_stdout(output):
                display()
            for text in ("Weight: 0.5 kg", "Download Size: 350 MB",
                         "requires physical shipping", "delivered digitally"):
                self.assertIn(text, output.getvalue())

    def test_type_hints(self):
        self.assertIs(get_type_hints(app.Product.__init__)["supplier"], app.Supplier)
        self.assertIs(get_type_hints(app.Inventory.add_product)["product"], app.Product)
        for method in (app.Inventory.search_product, app.Inventory.remove_product):
            self.assertEqual(get_type_hints(method)["return"], app.Product | None)
        self.assertIs(get_type_hints(app.Order.add_order_line)["product"], app.Product)
        self.assertIs(get_type_hints(app.OrderLine.__init__)["quantity"], int)
        self.assertIs(get_type_hints(app.Order.calculate_total)["return"], float)

    def test_json_round_trip_with_both_subclasses(self):
        inventory = app.Inventory()
        inventory.add_product(self.mouse)
        inventory.add_product(self.software)
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "inventory.json"
            with patch.object(app, "INVENTORY_FILE", file):
                app.save_inventory(inventory)
                data = json.loads(file.read_text(encoding="utf-8"))
                self.assertEqual([row["type"] for row in data], ["physical", "digital"])
                self.assertEqual(data[0]["supplier"]["id"], "S001")
                with redirect_stdout(io.StringIO()):
                    restored = app.load_inventory()
        mouse = restored.search_product("P002")
        software = restored.search_product("D001")
        self.assertIsInstance(mouse, app.PhysicalProduct)
        self.assertIsInstance(software, app.DigitalProduct)
        self.assertIsNot(mouse, self.mouse)
        self.assertEqual(mouse.supplier.contact_email, "sales@example.com")
        self.assertEqual(software.supplier.name, "Tech Supply")
        self.assertEqual(restored.create_product_list(), inventory.create_product_list())


if __name__ == "__main__":
    unittest.main(verbosity=2)
