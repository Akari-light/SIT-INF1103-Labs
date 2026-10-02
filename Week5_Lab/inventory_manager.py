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

def save_inventory(inventory):
    with INVENTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(inventory, file, indent=4)

    print("Inventory saved successfully.")

def main():
    inventory = load_inventory()

    while True:
        print("\n1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Save Inventory")
        print("6. Exit")

        choice = input("Enter option: ").strip()

        if choice == "1":
            display_all(inventory)
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            save_inventory(inventory)
        elif choice == "6":
            save_inventory(inventory)
            print("Thank you for using Inventory Management System.")
            break
        else:
            print("Invalid option. Please choose 1 to 6.")


if __name__ == "__main__":
    main()