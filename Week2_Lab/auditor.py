def main ():
    # 1. initialize variables
    total_inventory = 0
    failed_entries = 0

    print("--- Smart Inventory Auditor ---")
    print("Type 'quit' to exit:\n")

    # 2. continuous loop
    while True:
        usr_input = input("Enter stock quantity: ")

        # check for exit command 
        if usr_input.lower() == "quit":
            break

        # 4. handle invalid input
        if not usr_input.isdigit():
            print("Error: Invalid input. Please enter a whole number.")
            continue

        # 3. accept stock values as integers
        stock_quantity = int(usr_input)

        #5 reject negative stock values
        if stock_quantity < 0:
            print("Error: Stock quantity cannot be negative.")
            continue

        #6 manage state
        total_inventory += stock_quantity
        print(f"Added {stock_quantity} units. Current Total: {total_inventory}\n")

if __name__ == "__main__":
    main()