import json
from pathlib import Path
from abc import ABC, abstractmethod

INVENTORY_FILE = Path(__file__).resolve().parent / "inventory.json"

class Supplier:
    def __init__(self, supplier_id: str, name: str, contact_email: str) -> None:
        self.supplier_id = supplier_id
        self.name = name
        self.contact_email = contact_email

    def display_information(self) -> None:
        print(
            f"ID: {self.supplier_id} | "
            f"Name: {self.name} | "
            f"Contact Email: {self.contact_email}"
        )

class Product(ABC):
    def __init__(
        self, product_id: str, name: str, price: float, stock: int,
        supplier: Supplier
    ) -> None:
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.set_stock(stock)
        self.supplier: Supplier = supplier

    def set_stock(self, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Stock cannot be negative.")

        self.__stock = quantity

    def get_product_id(self) -> str:
        return self.__product_id

    def get_price(self) -> float:
        return self.__price

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass

    def display_information(self) -> None:
        print(
            f"ID: {self.__product_id} | "
            f"Name: {self.__name} | "
            f"Price: ${self.__price:.2f} | "
            f"Stock: {self.__stock}"
        )

    def create_product_dict(self):
        return {
            "id": self.__product_id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock,
            "supplier": {
                "id": self.supplier.supplier_id,
                "name": self.supplier.name,
                "contact_email": self.supplier.contact_email,
            },            
        }    

class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass

@CanBeShipped.register
class PhysicalProduct(Product):
    def __init__(
        self, product_id: str, name: str, price: float, stock: int,
        weight: float, supplier: Supplier
    ) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        self.__weight = weight
        
    
    def get_fulfilment_info(self) -> str:
        return "This product requires physical shipping."

    def calculate_shipping_cost(self) -> float:
        return 5.00 + 2.00 * self.__weight
    
    def display_information(self) -> None:
        super().display_information()
        print(f"Weight: {self.__weight} kg")

    def create_product_dict(self):
        product_dict = super().create_product_dict()
        product_dict["type"] = "physical"
        product_dict["weight"] = self.__weight
        return product_dict

class DigitalProduct(Product):
    def __init__(
        self, product_id: str, name: str, price: float, stock: int,
        download_size: float, supplier: Supplier
    ) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        self.__download_size = download_size

    def get_fulfilment_info(self) -> str:
        return "This product is delivered digitally."

    def display_information(self) -> None:
        super().display_information()
        print(f"Download Size: {self.__download_size} MB")

    def create_product_dict(self):
        product_dict = super().create_product_dict()
        product_dict["type"] = "digital"
        product_dict["download_size"] = self.__download_size
        return product_dict

class Inventory:
    def __init__(self):
        self.__products: list[Product] = []

    def display_all(self) -> None:
        print("\nCurrent Inventory")
        print("-" * 48)

        if not self.__products:
            print("Inventory is empty.")
        else:
            for product in self.__products:
                product.display_information()
                print(product.get_fulfilment_info())

        print("-" * 48)

    def search_product(self, product_id: str) -> Product | None:
        for product in self.__products:
            if product.get_product_id() == product_id:
                return product

        return None

    def add_product(self, product: Product) -> None:
        product_id = product.get_product_id()

        if self.search_product(product_id) is not None:
            raise ValueError("Product ID already exists.")

        self.__products.append(product)    

    def remove_product(self, product_id: str) -> Product | None:
        product = self.search_product(product_id)

        if product is None:
            return None

        self.__products.remove(product)
        return product

    def create_product_list(self):
        products_data = []

        for product in self.__products:
            products_data.append(product.create_product_dict())

        return products_data   

#Discount Strategy Classes
class DiscountStrategy(ABC):
    @abstractmethod
    def apply_discount(self, total: float) -> float:
        pass

class FullPrice(DiscountStrategy):
    def apply_discount(self, subtotal: float) -> float:
        return subtotal

class PercentageDiscount(DiscountStrategy):
    def __init__(self, discount_percent: float) -> None:
        self.discount_percent = discount_percent

    def apply_discount(self, subtotal: float) -> float:
        discount_amount = subtotal * self.discount_percent / 100
        return subtotal - discount_amount

class BulkDiscount(DiscountStrategy):
    def __init__(self, minimum_subtotal: float, discount_amount: float) -> None:
        self.minimum_subtotal = minimum_subtotal
        self.discount_amount = discount_amount

    def apply_discount(self, subtotal: float) -> float:
        if subtotal >= self.minimum_subtotal:
            return subtotal - self.discount_amount
        return subtotal

# Order Processing Classes
class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        self.order_lines: list[OrderLine] = []

    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)
        self.order_lines.append(order_line)

    def calculate_total(self) -> float:
        total = 0.0

        for line in self.order_lines:
            total += line.calculate_subtotal()

        return total

class OrderLine:
    def __init__(self, product: Product, quantity: int) -> None:
        self.product = product
        self.quantity = quantity

    def calculate_subtotal(self) -> float:
        return self.product.get_price() * self.quantity

# Functions for saving and loading inventory
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
        product_type = product_data.get("type")

        common_args = (
            product_data["id"],
            product_data["name"],
            product_data["price"],
            product_data["stock"]
        )

        supplier_data = product_data["supplier"]
        supplier = Supplier(
            supplier_data["id"],
            supplier_data["name"],
            supplier_data["contact_email"],
        )

        if product_type == "physical":
            product = PhysicalProduct(*common_args, product_data["weight"], supplier)
        elif product_type == "digital":
            product = DigitalProduct(*common_args, product_data["download_size"], supplier)
        else:
            raise ValueError(f"Missing or unsupported product type: {product_type!r}")

        inventory.add_product(product)

    print("Inventory loaded successfully.")
    return inventory

# User Interaction Functions
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

    product_type = input("Product type (physical/digital): ").strip().lower()

    if product_type not in ("physical", "digital"):
        print("\nChoose physical or digital.")
        return inventory

    supplier_id = input("Supplier ID: ").strip()
    supplier_name = input("Supplier Name: ").strip()
    supplier_email = input("Supplier Contact Email: ").strip()

    if not supplier_id or not supplier_name or not supplier_email:
        print("\nSupplier ID, name, and contact email cannot be empty.")
        return inventory

    supplier = Supplier(supplier_id, supplier_name, supplier_email)

    try:
        if product_type == "physical":
            weight = float(input("Weight in kg: "))
            if weight < 0:
                raise ValueError("Weight cannot be negative.")

            new_product = PhysicalProduct(
                product_id, product_name, product_price, product_stock, weight, supplier
            )
        else:
            download_size = float(input("Download size in MB: "))
            if download_size < 0:
                raise ValueError("Download size cannot be negative.")

            new_product = DigitalProduct(
                product_id, product_name, product_price, product_stock, download_size, supplier
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