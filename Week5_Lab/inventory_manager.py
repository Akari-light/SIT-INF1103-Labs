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

def main():
    inventory = load_inventory()
    display_all(inventory)

if __name__ == "__main__":
    main()