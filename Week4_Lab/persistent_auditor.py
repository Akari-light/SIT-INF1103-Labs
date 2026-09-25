import json
from pathlib import Path

INVENTORY_FILE = Path(__file__).with_name("inventory.txt")

# 1. Persistence
def load_inventory():
    try:
        with INVENTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return 0, [], []

    return data["total_inventory"], data["transaction_history"], data.get("orders", [])

# 3. Write-back
def save_inventory(total, history, orders):
    data = {
        "total_inventory": total,
        "transaction_history": history,
        "orders": orders,
    }

    with INVENTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")

# Calculates the new total and returns it.
def process_delivery(current_total, new_value):
    return current_total + new_value

# takes a delivery amount and returns the tax (10% of that specific delivery).
def calculate_tax(amount):
    return amount * 0.10

# Handles the prompt, handles input validation, and returns a valid integer or a "quit" signal
def get_valid_input():
    product_name = input("Enter Product Name (or 'quit'): ").strip()
    if product_name.lower() == "quit":
        return "quit"
    if not product_name:
        raise ValueError("Product name cannot be empty.")

    quantity_input = input("Enter Quantity: ").strip()
    if quantity_input.lower() == "quit":
        return "quit"

    try:
        quantity = int(quantity_input)
    except ValueError:
        raise ValueError("Invalid input. Please enter a whole number.")

    if quantity < 0:
        raise ValueError("Stock quantity cannot be negative.")

    return product_name, quantity


def format_order(order):
    return f'{order["id"]}, {order["product_name"]}, {order["quantity"]}'


def show_current_orders(orders):
    print("Current Orders:")
    if orders:
        for order in orders:
            print(format_order(order))
    else:
        print("(none)")
    print()

# A dedicated function to print the final summary
def generate_report(total_inventory, failed_attempts):
    print("\n" + "=" * 35)
    print("AUDIT SUMMARY REPORT")
    print("=" * 35)
    print(f"Total Units in Inventory: {total_inventory}")
    print(f"Failed/Rejected Entries: {failed_attempts}")
    print("=" * 35)

def main():
    # initialize variables
    total_inventory, history, orders = load_inventory()
    failed_entries = 0
    deliveries_processed = 0
    next_order_id = max((order["id"] for order in orders), default=1000) + 1

    print("--- Smart Inventory Auditor ---")
    print("Type 'quit' to exit:\n")
    show_current_orders(orders)

    # continuous loop
    while True:
        try:
            entry = get_valid_input()
        except ValueError as error:
            print(f"Error: {error}\n")
            failed_entries += 1
            continue

        if entry == "quit":
            break

        # manage state
        product_name, quantity = entry
        order = {
            "id": next_order_id,
            "product_name": product_name,
            "quantity": quantity,
        }
        orders.append(order)
        next_order_id += 1
        total_inventory = process_delivery(total_inventory, quantity)
        history.append(quantity)
        deliveries_processed += 1

        print("\nNew Order Added:")
        print(format_order(order))
        print(f"Current Total: {total_inventory}")
        print(f"Tax for this delivery: {calculate_tax(quantity):.2f}\n")

        # trigger overstock alert
        if total_inventory > 500:
            print(f"ALERT: Inventory capacity exceeded! Current Total: {total_inventory}\nStopping system automatically...")
            break

    save_inventory(total_inventory, history, orders)
    print(f"Inventory successfully saved to {INVENTORY_FILE.name}")
    generate_report(total_inventory, failed_entries)
    print(f"Transaction History: {history}")
    print(f"Total Deliveries Processed: {deliveries_processed}")

if __name__ == "__main__":
    main()
