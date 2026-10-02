import json
from pathlib import Path

INVENTORY_FILE = Path(__file__).resolve().parent / "inventory.json"


def load_inventory():
    if not INVENTORY_FILE.exists():
        print("inventory.json not found. Starting with empty inventory.")
        return []

    print("inventory.json found.")

    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        inventory = json.load(file)

    print("Inventory loaded successfully.")
    return inventory


def display_all(inventory):
    print("\nCurrent Inventory")
    print("-" * 48)

    if not inventory:
        print("Inventory is empty.")
    else:
        for product in inventory:
            print(
                f"ID: {product['id']} | "
                f"Name: {product['name']} | "
                f"Price: ${product['price']:.2f} | "
                f"Stock: {product['stock']}"
            )

    print("-" * 48)


def add_product(inventory):
    print("\nAdd New Product")
    product_id = input("Product ID: ").strip()
    product_name = input("Product Name: ").strip()

    if not product_id or not product_name:
        print("\nProduct ID and name cannot be empty.")
        return inventory

    for product in inventory:
        if product["id"] == product_id:
            print("\nProduct ID already exists.")
            return inventory

    try:
        product_price = float(input("Price: "))
        product_stock = int(input("Stock Quantity: "))
    except ValueError:
        print("\nEnter a numeric price and a whole number for stock.")
        return inventory

    if product_price < 0 or product_stock < 0:
        print("\nPrice and stock cannot be negative.")
        return inventory

    new_product = {
        "id": product_id,
        "name": product_name,
        "price": product_price,
        "stock": product_stock
    }

    inventory.append(new_product)
    print("\nProduct added successfully!")
    return inventory


def update_stock(inventory):
    print("\nUpdate Stock")
    product_id = input("Enter Product ID: ").strip()

    for product in inventory:
        if product["id"] == product_id:
            print("\nProduct Found:")
            print(f"Name: {product['name']}")
            print(f"Current Stock: {product['stock']}")

            try:
                new_stock = int(input("\nNew Stock Quantity: "))
            except ValueError:
                print("\nStock must be a whole number.")
                return inventory

            if new_stock < 0:
                print("\nStock cannot be negative.")
                return inventory

            product["stock"] = new_stock
            print("\nStock updated successfully!")
            return inventory

    print("\nProduct not found.")
    return inventory


def search_product(inventory):
    print("\nSearch Product")
    product_id = input("Enter Product ID: ").strip()

    for product in inventory:
        if product["id"] == product_id:
            print("\nProduct Found")
            print("-" * 48)
            print(f"ID: {product['id']}")
            print(f"Name: {product['name']}")
            print(f"Price: ${product['price']:.2f}")
            print(f"Stock: {product['stock']}")
            print("-" * 48)
            return

    print("\nProduct not found.")


def save_inventory(inventory):
    with INVENTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(inventory, file, indent=4)


def main():
    print("=" * 40)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 40)
    print()

    inventory = load_inventory()

    print("\n----------- MENU -----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("----------------------------")

    while True:
        choice = input("\nEnter option: ").strip()

        if choice == "1":
            display_all(inventory)

        elif choice == "2":
            add_product(inventory)

        elif choice == "3":
            update_stock(inventory)

        elif choice == "4":
            search_product(inventory)

        elif choice == "5":
            print("\nSaving inventory...")
            save_inventory(inventory)
            print("Inventory saved successfully to inventory.json.")

        elif choice == "6":
            print("\nSaving inventory before exit...")
            save_inventory(inventory)
            print("Inventory saved successfully.")
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break

        else:
            print("\nInvalid option. Please choose 1 to 6.")


if __name__ == "__main__":
    main()