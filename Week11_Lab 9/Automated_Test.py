import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import OOP_inventory_manager as app

# Run the Lab 9 checks with python -B -m unittest -v Automated_Test.
class DiscountTests(unittest.TestCase):
    def setUp(self) -> None:
        supplier = app.Supplier("S001", "Test Supply", "sales@example.com")
        self.lamp = app.ProductFactory.create(
            "physical", "P001", "Desk Lamp", 50.0, 10, supplier, weight=1.2
        )

    def test_default_strategy_charges_full_subtotal(self) -> None:
        order = app.Order("O001")
        order.add_order_line(self.lamp, 5)
        self.assertAlmostEqual(order.calculate_total(), 250.0)

    def test_same_order_can_switch_discount_strategies(self) -> None:
        order = app.Order("O001", app.BulkDiscount(200, 20))
        order.add_order_line(self.lamp, 5)
        self.assertAlmostEqual(order.calculate_total(), 230.0)

        order.set_discount(app.PercentageDiscount(10))
        self.assertAlmostEqual(order.calculate_total(), 225.0)

    def test_bulk_discount_applies_at_the_threshold(self) -> None:
        discount = app.BulkDiscount(200, 20)
        self.assertAlmostEqual(discount.apply_discount(199.0), 199.0)
        self.assertAlmostEqual(discount.apply_discount(200.0), 180.0)

    def test_percentage_discount_respects_its_cap(self) -> None:
        order = app.Order("O001", app.CappedPercentageDiscount(10, 30))
        order.add_order_line(self.lamp, 5)
        self.assertAlmostEqual(order.calculate_total(), 225.0)

        order.add_order_line(self.lamp, 5)
        self.assertAlmostEqual(order.calculate_total(), 470.0)

    def test_order_can_use_a_new_discount_strategy(self) -> None:
        class FiveDollarsOff(app.DiscountStrategy):
            def apply_discount(self, subtotal: float) -> float:
                return subtotal - 5.0

        order = app.Order("O002", FiveDollarsOff())
        order.add_order_line(self.lamp, 2)
        self.assertAlmostEqual(order.calculate_total(), 95.0)

    def test_rejected_quantity_does_not_add_an_order_line(self) -> None:
        order = app.Order("O001")
        order.add_order_line(self.lamp, 1)
        for quantity in (0, -1):
            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(ValueError, "quantity must be greater than zero"):
                    order.add_order_line(self.lamp, quantity)
                self.assertEqual(len(order.order_lines), 1)
                self.assertAlmostEqual(order.calculate_total(), 50.0)


class FactoryAndValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.supplier = app.Supplier("S001", "Test Supply", "sales@example.com")

    def test_factory_creates_each_product_type_with_its_details(self) -> None:
        lamp = app.ProductFactory.create(
            "physical", "P001", "Desk Lamp", 25.0, 10, self.supplier, weight=1.2
        )
        software = app.ProductFactory.create(
            "digital", "D001", "Photo Editor", 49.9, 100, self.supplier, download_size=350
        )
        self.assertIsInstance(lamp, app.PhysicalProduct)
        self.assertIsInstance(software, app.DigitalProduct)
        self.assertEqual(lamp.create_product_dict()["weight"], 1.2)
        self.assertEqual(software.create_product_dict()["download_size"], 350)
        self.assertIs(lamp.supplier, self.supplier)
        self.assertIs(software.supplier, self.supplier)

    def test_factory_rejects_an_unknown_type(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown product type: service"):
            app.ProductFactory.create("service", "S001", "Installation", 30.0, 5, self.supplier)

    def test_factory_requires_the_detail_for_each_type(self) -> None:
        for product_type, message in (("physical", "require a weight"),
                                      ("digital", "require a download size")):
            with self.subTest(product_type=product_type):
                with self.assertRaisesRegex(ValueError, message):
                    app.ProductFactory.create(product_type, "X001", "Sample", 10.0, 1, self.supplier)

    def test_product_rejects_invalid_prices(self) -> None:
        for price in (0, -5, float("nan"), float("inf")):
            with self.subTest(price=price):
                with self.assertRaisesRegex(ValueError, "Price must be greater than zero"):
                    app.ProductFactory.create(
                        "physical", "P001", "Desk Lamp", price, 10, self.supplier, weight=1.2
                    )

    def test_stock_accepts_zero_and_rejects_negative_values(self) -> None:
        for product_type, details in (("physical", {"weight": 1.2}),
                                      ("digital", {"download_size": 350})):
            with self.subTest(product_type=product_type):
                with self.assertRaisesRegex(ValueError, "Stock cannot be negative"):
                    app.ProductFactory.create(
                        product_type, "X001", "Sample", 10.0, -1, self.supplier, **details
                    )
                product = app.ProductFactory.create(
                    product_type, "X001", "Sample", 10.0, 0, self.supplier, **details
                )
                with self.assertRaisesRegex(ValueError, "Stock cannot be negative"):
                    product.set_stock(-1)
                self.assertEqual(product.create_product_dict()["stock"], 0)

    def test_product_rejects_negative_measurements(self) -> None:
        for product_type, details, message in (
            ("physical", {"weight": -1}, "Weight must be finite and nonnegative"),
            ("digital", {"download_size": -1}, "Download size must be finite and nonnegative"),
        ):
            with self.subTest(product_type=product_type):
                with self.assertRaisesRegex(ValueError, message):
                    app.ProductFactory.create(
                        product_type, "X001", "Sample", 10.0, 1, self.supplier, **details
                    )


class InputAndFileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.supplier = app.Supplier("S001", "Test Supply", "sales@example.com")
        self.inventory = app.Inventory()

    def test_price_prompt_retries_until_input_is_valid(self) -> None:
        output = StringIO()
        with patch("builtins.input", side_effect=["abc", "-5", "12.50"]) as prompt:
            with redirect_stdout(output):
                price = app.get_positive_float("Price: ")

        self.assertEqual(prompt.call_count, 3)
        self.assertAlmostEqual(price, 12.50)
        self.assertEqual(output.getvalue().splitlines(), [
            "Please enter a valid number, e.g. 12.50",
            "Please enter a number greater than zero.",
        ])

    def test_missing_csv_reports_failure_then_finishes(self) -> None:
        output = StringIO()
        with TemporaryDirectory() as folder:
            missing = Path(folder) / "missing-products.csv"
            with redirect_stdout(output):
                app.load_products(missing, self.inventory, self.supplier)

        self.assertEqual(output.getvalue().splitlines(), [
            f"Products file not found: {missing}",
            "Load attempt finished.",
        ])
        self.assertEqual(self.inventory.create_product_list(), [])

    def test_csv_skips_bad_rows_and_continues_through_the_factory(self) -> None:
        output = StringIO()
        with patch.object(app.ProductFactory, "create", wraps=app.ProductFactory.create) as create:
            with redirect_stdout(output):
                app.load_products(app.PRODUCTS_FILE, self.inventory, self.supplier)

        self.assertEqual([call.args[1] for call in create.call_args_list],
                         ["P001", "D001", "S001", "P003"])
        self.assertEqual([row["id"] for row in self.inventory.create_product_list()],
                         ["P001", "D001", "P003"])
        messages = output.getvalue().splitlines()
        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0], "Skipped row 4: Unknown product type: service")
        self.assertTrue(messages[1].startswith("Skipped row 5:"))
        self.assertIn("abc", messages[1])
        self.assertEqual(messages[2:], ["3 products loaded.", "Load attempt finished."])

    def test_menu_import_is_saved_and_reloaded_from_json(self) -> None:
        answers = ["7", "S001", "Test Supply", "sales@example.com", "6"]
        with TemporaryDirectory() as folder:
            inventory_file = Path(folder) / "inventory.json"
            with patch.object(app, "INVENTORY_FILE", inventory_file):
                with patch("builtins.input", side_effect=answers), redirect_stdout(StringIO()):
                    app.main()
                self.assertTrue(inventory_file.is_file())
                with patch.object(app.ProductFactory, "create",
                                  wraps=app.ProductFactory.create) as create:
                    with redirect_stdout(StringIO()):
                        restored = app.load_inventory()
                self.assertEqual(create.call_count, 3)

        products = {row["id"]: row for row in restored.create_product_list()}
        self.assertEqual(set(products), {"P001", "D001", "P003"})
        self.assertEqual(products["P001"]["weight"], 1.2)
        self.assertEqual(products["D001"]["download_size"], 350)
        self.assertEqual(products["P001"]["supplier"]["id"], "S001")


if __name__ == "__main__":
    unittest.main(verbosity=2)
