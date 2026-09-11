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
        
        # 3. accept stock values as integers
        stock_quantity = int(usr_input)

if __name__ == "__main__":
    main()