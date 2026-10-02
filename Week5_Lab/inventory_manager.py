import json
from json.tool import main
from pathlib import Path

INVENTORY_FILE = Path(__file__).resolve().parent / "inventory.json"


def load_inventory():
    if not INVENTORY_FILE.exists():
        print("inventory.json not found. Starting with empty inventory.")
        return []

    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        inventory = json.load(file)

    print("Inventory loaded successfully.")
    return inventory

def display_all(inventory):
    if not inventory:
        print("Inventory is empty.")
        return

    for product in inventory:
        print(
            f"ID: {product['id']} | "
            f"Name: {product['name']} | "
            f"Price: ${product['price']:.2f} | "
            f"Stock: {product['stock']}"
        )

def add_product(inventory):
    # Collect ID, name, price, and stock.
    product_id = input("Product ID: ").strip().upper()
    product_name = input("Product Name: ").strip()

    if not product_id or not product_name:
        print("Product ID and name cannot be empty.")
        return inventory

    for product in inventory:
        if product["id"].strip().casefold() == product_id.casefold():
            print("Product ID already exists.")
            return inventory

    try:
        product_price = float(input("Price: "))
        product_stock = int(input("Stock Quantity: "))
    except ValueError:
        print("Enter a numeric price and a whole number for stock.")
        return inventory

    if product_price < 0 or product_stock < 0:
        print("Price and stock cannot be negative.")
        return inventory

    # Create a product dictionary and append it to inventory.
    new_product = {
        "id": product_id,
        "name": product_name,
        "price": product_price,
        "stock": product_stock
    }

    inventory.append(new_product)
    print("Product added successfully.")

    return inventory

def update_stock(inventory):
    # Ask for a product ID.
    product_id = input("Enter the product ID to update: ").strip().casefold()

    # Find the matching dictionary.
    for product in inventory:
        if product["id"].strip().casefold() == product_id:
            print(f"Product: {product['name']}")
            print(f"Current stock: {product['stock']}")

            try:
                new_stock = int(input("Enter the new stock quantity: "))
            except ValueError:
                print("Stock must be a whole number.")
                return inventory

            if new_stock < 0:
                print("Stock cannot be negative.")
                return inventory

            # Replace its stock value with the new quantity.
            product["stock"] = new_stock
            print("Stock updated successfully.")

            return inventory

    print("Product not found.")
    return inventory

def search_product(inventory):
    # Ask for a product ID.
    product_id = input("Enter the product ID to search for: ")
    # Find and display the matching product.
    for product in inventory:
        if product["id"] == product_id:
            print(
                f"ID: {product['id']} | "
                f"Name: {product['name']} | "
                f"Price: ${product['price']:.2f} | "
                f"Stock: {product['stock']}"
            )
            return
    print("Product not found.")

def main():
    inventory = load_inventory()

    add_product(inventory)
    update_stock(inventory)
    search_product(inventory)
    display_all(inventory)

if __name__ == "__main__":
    main()