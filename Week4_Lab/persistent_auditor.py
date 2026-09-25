INVENTORY_FILE = "inventory.txt"

# 1. Persistence
def load_inventory():
    try:
        with open(INVENTORY_FILE, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return 0, []

    if not lines:
        return 0, []

    total = int(lines[0])
    history = [int(line) for line in lines[1:]]
    return total, history

# Calculates the new total and returns it.
def process_delivery(current_total, new_value):
    return current_total + new_value

# takes a delivery amount and returns the tax (10% of that specific delivery).
def calculate_tax(amount):
    return amount * 0.10

# Handles the prompt, handles input validation, and returns a valid integer or a "quit" signal
def get_valid_input():
    usr_input = input("Enter stock quantity: ").strip()

    if usr_input.lower() == "quit":
        return "quit"

    try:
        stock_quantity = int(usr_input)
    except ValueError:
        raise ValueError("Invalid input. Please enter a whole number.")

    if stock_quantity < 0:
        raise ValueError("Stock quantity cannot be negative.")

    return stock_quantity

# A dedicated function to print the final summary
def generate_report(total_inventory, failed_attempts):
    print("\n" + "=" * 35)
    print("AUDIT SUMMARY REPORT")
    print("=" * 35)
    print(f"Total Units Processed  : {total_inventory}")
    print(f"Failed/Rejected Entries: {failed_attempts}")
    print("=" * 35)

def main ():
    # initialize variables
    total_inventory, history = load_inventory()
    failed_entries = 0
    deliveries_processed = 0

    print("--- Smart Inventory Auditor ---")
    print("Type 'quit' to exit:\n")

    # continuous loop
    while True:
        try:
            stock_quantity = get_valid_input()
        except ValueError as error:
            print(f"Error: {error}")
            failed_entries += 1
            continue

        if stock_quantity == "quit":
            break

        # manage state
        total_inventory = process_delivery(total_inventory, stock_quantity)
        tax = calculate_tax(stock_quantity)
        deliveries_processed += 1
        print(f"Added {stock_quantity} units. Current Total: {total_inventory}.\nTax for this delivery: {tax:.2f}")

        # trigger overstock alert
        if total_inventory > 500:
            print(f"ALERT: Inventory capacity exceeded! Current Total: {total_inventory}\nStopping system automatically...")
            break

    generate_report(total_inventory, failed_entries)
    print(f"Total Deliveries Processed: {deliveries_processed}")

if __name__ == "__main__":
    main()