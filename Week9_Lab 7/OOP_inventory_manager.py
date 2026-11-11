import json
from pathlib import Path

INVENTORY_FILE = Path(__file__).resolve().parent / "inventory.json"

class Product:
    def __init__(self, product_id, name, price, stock):
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.set_stock(stock)

    def display_information(self):
        print( f"ID: {self.__product_id} | Name: {self.__name} | Price: ${self.__price:.2f} | Stock: {self.__stock}")

    def set_stock(self, quantity):
        if quantity < 0:
            raise ValueError("Stock cannot be negative.")

        self.__stock = quantity

    def get_product_id(self):
        return self.__product_id

    def create_product_dict(self):
        return {
            "id": self.__product_id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock
        }    

class Inventory:
    def __init__(self):
        self.__products = []

    def display_all(self):
        print("\nCurrent Inventory")
        print("-" * 48)

        if not self.__products:
            print("Inventory is empty.")
        else:
            for product in self.__products:
                product.display_information()

        print("-" * 48)

    def search_product(self, product_id):
        for product in self.__products:
            if product.get_product_id() == product_id:
                return product

        return None

    def add_product(self, product):
        product_id = product.get_product_id()

        if self.search_product(product_id) is not None:
            raise ValueError("Product ID already exists.")

        self.__products.append(product)    

    def create_product_list(self):
        products_data = []

        for product in self.__products:
            products_data.append(product.create_product_dict())

        return products_data   


def save_inventory(inventory):
    inventory_data = inventory.create_product_list()

    with INVENTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(inventory_data, file, indent=4)

def load_inventory():
    inventory = Inventory()

    if not INVENTORY_FILE.exists():
        print("inventory.json not found. Starting with empty inventory.")
        return inventory

    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        inventory_data = json.load(file)

    for product_data in inventory_data:
        product = Product(
            product_data["id"],
            product_data["name"],
            product_data["price"],
            product_data["stock"]
        )
        inventory.add_product(product)

    print("Inventory loaded successfully.")
    return inventory

##################

def add_product(inventory):
    print("\nAdd New Product")
    product_id = input("Product ID: ").strip()
    product_name = input("Product Name: ").strip()

    if not product_id or not product_name:
        print("\nProduct ID and name cannot be empty.")
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

    try:
        new_product = Product(
            product_id,
            product_name,
            product_price,
            product_stock
        )
        inventory.add_product(new_product)
    except ValueError as error:
        print(f"\n{error}")
        return inventory

    print("\nProduct added successfully!")
    return inventory


def update_stock(inventory):
    print("\nUpdate Stock")
    product_id = input("Enter Product ID: ").strip()

    product = inventory.search_product(product_id)

    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found:")
    product.display_information()

    try:
        new_stock = int(input("\nNew Stock Quantity: "))
    except ValueError:
        print("\nStock must be a whole number.")
        return

    try:
        product.set_stock(new_stock)
    except ValueError as error:
        print(f"\n{error}")
        return

    print("\nStock updated successfully!")


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
            inventory.display_all()

        elif choice == "2":
            add_product(inventory)

        elif choice == "3":
            update_stock(inventory)

        elif choice == "4":
            product_id = input("Enter Product ID: ").strip()
            product = inventory.search_product(product_id)

            if product is None:
                print("\nProduct not found.")
            else:
                print("-" * 48)
                print("Product Found: ", end="")
                product.display_information()
                print("-" * 48)

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