def main ():
    # initialize variables
    total_inventory = 0
    failed_entries = 0

    print("--- Smart Inventory Auditor ---")
    print("Type 'quit' to exit:\n")

    # continuous loop
    while True:
        usr_input = input("Enter stock quantity (tupe): ")

        # check for exit command 
        if usr_input.lower() == "quit":
            break

if __name__ == "__main__":
    main()