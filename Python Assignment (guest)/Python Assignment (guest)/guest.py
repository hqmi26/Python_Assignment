from datetime import datetime #a libary that is built-in python library language 
import time #same thing

USERS_RECORD = "users.txt" #all users password n everythin
RIDES_RECORD = "rides.txt" #stores ride information and ride IDs
TICKETS_RECORD = "tickets_purchases.txt" #guest that bougth whatever TICKETS
SHOP_RECORD = "shop.txt" #shop items
SHOP_PURCHASES_RECORD = "shop_purchases.txt" #guest that bought whatever SHOP item
WALKIN_RECORD = "walkin.txt" #record the stupid queue id for those who wants walkin
TICKET_CATALOG_RECORD = "tickets.txt" #availability of tickets

#i only made the text file that i needed for guest and yall cn use the file to connect ur parts
USERS_HEADERS = ["user_id", "username", "password", "role"]
RIDES_HEADERS = ["ride_id", "ride_name", "zone", "status", "wait_time(normal)", "wait_time(express)"]
TICKETS_HEADERS = ["ticket_id", "user_id", "ticket_type", "ticket_tier", "quantity", "entry date", "entry time", "price"]
SHOP_HEADERS = ["item_id", "item_name", "price", "stock"]
SHOP_PURCHASES_HEADERS = ["purchases_id", "user_id", "item_id", "item_name", "quantity", "price", "purchase_date"]
WALKIN_HEADERS = ["user_id" , "queue_id", "reservation_date"]
TICKET_CATALOG_HEADER = ["ticket_type", "ticket_tier", "price", "stock"]

#file handling
def write_file(filename, data):
    try:
        with open(filename, "a") as file:
            file.write(data + "\n")
    except IOError:
        print(f"Error writing to {filename}!")


def read_file(filename):
    try:
        with open(filename, "r") as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"{filename} not found! Returning empty list.")
        return []
    except IOError:
        print(f"Error reading from {filename}!")
        return []

def id_generator(filename, prefix, pad=4, id_index=0):
    lines = read_file(filename)
    highest_number = 0

    for line in lines:
        parts = line.split("|")
        if len(parts) <= id_index:
            continue
        existing_id = parts[id_index]

       
        if existing_id.startswith(prefix):
            number_part = existing_id[len(prefix):]
            
            if number_part.isdigit():
                highest_number = max(highest_number, int(number_part))

   
    next_num = str(highest_number + 1).zfill(pad)
    return f"{prefix}{next_num}"


def confirmation(prompt):
    # ask until user enters y or n
    while True:
        answer = input(prompt + " (y/n): ").strip().lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print("Please type 'y' or 'n'.")

def check_choice(prompt, choices):
    while True:
        value = input(prompt).strip().upper()
        if value in choices:
            return value
        print("WRONG choice. Allowed values: " + " , ".join(choices))

def check_integer(prompt, minimum, maximum):
    while True:
        try:
            value = int(input(prompt).strip())
            if minimum <= value <= maximum:
                return value
            print("Enter a whole number from " + str(minimum) + " to " + str(maximum) + ".")
        except ValueError:
            print("Enter a valid whole number.")


def check_date(prompt):
    while True:
        value = input(prompt).strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Use a real date in YYYY-MM-DD format.")

def check_hour(prompt):
    #Keep asking until the user enters a whole number from 8 to 14.
    return check_integer(prompt, 8 , 14)
              

def login():
    print("\n=== LOG IN ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    users = read_file(USERS_RECORD)
    for line in users:
        parts = line.split("|")
        if parts[1] == username and parts[2] == password:
            print("Successfully logged in. Welcome, " + parts[1] + " (" + parts[3] + ")")
            return parts

    print("Wrong username or password.")
    return None

def sign_up():
    print("\n=== SIGN UP ===")
    username = input("Write a username: ").strip()

    users = read_file(USERS_RECORD)
    for line in users:
        parts = line.split("|")
        if parts[1] == username:
            print("That username is already taken. Please write another username.")
            return None

    password = input("Write a password: ").strip()
    user_id = id_generator(USERS_RECORD, "G", 4)
    new_line = "|".join([user_id, username, password, "guest"])
    write_file(USERS_RECORD, new_line)

    print(f"Account created! Your User ID is {user_id}. You are now logged in as a guest!")
    return [user_id, username, password, "guest"]

def non_negative_int(prompt):
    # ask user to enter a whole number >= 0.
    while True:
        try:
            value = int(input(prompt).strip())
            if value >= 0:
                return value
            print("Please enter a whole number that is 0 or more.")
        except ValueError:
            print("Please enter a valid whole number.")


def positive_int(prompt):
    #ask user to enter a whole number >= 1.
    value = non_negative_int(prompt)
    while value < 1:
        print("Please enter a number of 1 or more.")
        value = non_negative_int(prompt)
    return value


def guest_menu(user):
    while True:
        print("\n")
        print("=====Guest Menu=====")
        print("A. Purchase Ticket")
        print("B. Purchase Ticket(Walk-in)")
        print("C. View Rides and Wait")
        print("D. Purchase Shop Item")
        print("E. View my transaction")
        print("F. Check Ticket Availability")
        print("G. Log Out")
        choice = check_choice("Select: ", ["A", "B", "C", "D", "E", "F", "G"])
        if choice == "A":
            purchase_ticket(user)
        elif choice == "B":
            walkin_ticket(user)
        elif choice == "C":
            view_search_rides() #haqimis part
        elif choice == "D":
            purchase_shop_item(user)
        elif choice == "E":
            view_guest_transactions(user[0])
        elif choice == "F":
            display_ticket_availability()
        elif choice =="G":
            if check_choice("Confirm log out?? [Y/N]: ", ["Y", "N"]) == "Y":
                print("Logged out. returning to the main menu.")
        else:
            print("Invalid option, please try again.")
            return
    
def search_catalog_row(catalog, ticket_type, tier):
    for row in catalog:
        if row[0] == ticket_type and row[1] == tier:
            return row
    return None

def load_ticket_catalog():
    lines = read_file(TICKET_CATALOG_RECORD)
    catalog = []
    for line in lines:
        line = line.strip()
        if line != "":
            catalog.append(line.strip().split("|"))
    return catalog
    
def display_ticket_availability():
    catalog = load_ticket_catalog()
    print("\n{:<8} {:<9} {:<10} {:<8}".format("Type", "Tier", "Price", "Stock"))
    for row in catalog:
        print("{:<8} {:<9} {:<10} {:<8}".format(row[0], row[1], row[2], row[3]))
        

def save_ticket_catalog(catalog):
    with open(TICKET_CATALOG_RECORD,"w") as file:
        for row in catalog:
            file.write("|".join(row)+"\n")


#option A (change prompts after completion)
def purchase_ticket(user):
    print("\n=====Purchase Ticket=====")
    display_ticket_availability()

    print("\na) Express    b) Normal")
    type_choice = input("Please choose (a/b): ").strip().lower()
    while type_choice not in ("a", "b"):
        print("Please choose a or b.")
        print("\na) Express    b) Normal")
        type_choice = input("Please choose (a/b): ").strip().lower()
    type = "EXPRESS" if type_choice == "a" else "NORMAL"

    print("\na) Plus (Same Day Entry)    b) Premier (Future Entry)")
    tier_choice = input("Please Choose (a/b): ").strip().lower()
    while tier_choice not in ("a", "b"):
        print("Please choose a or b.")
        print("\na) Plus (Same Day Entry)    b) Premier (Future Entry)")
        tier_choice = input("Please Choose (a/b): ").strip().lower()
    tier = "PLUS" if tier_choice == "a" else "PREMIER"

    catalog = load_ticket_catalog()
    row = search_catalog_row(catalog, type, tier)
    if row is None:
        print("Sorry, that ticket combination is not available.")
        return

    price = float(row[2])
    stock = int(row[3])
    if stock <= 0:
        print("Tier sold out for today.")
        return

    quantity = positive_int("Quantity: ")
    while quantity > stock:
        print("Only " + str(stock) + " left in stock for this tier.")
        quantity = positive_int("Quantity: ")
    if tier == "PLUS":
        entry_date = datetime.today().date().isoformat()
        print(f"Entry date: {entry_date}")
    else:
        while True:
            entry_date = check_date("Entry Date (YYYY-MM-DD): ")
            if datetime.strptime(entry_date, "%Y-%m-%d").date() > datetime.today().date():
                break
            print("Invalid date. Premier ticket must be a future date (not today or earlier)")
    
    entry_hour = check_hour("Select Entry Hour (8-14): ")
    total_price = round(price * quantity, 2)

    print("\n=====Confirmation=====")
    print("a) Purchase Type:", type)
    print("b) Tier:", tier)
    print("c) Quantity:", quantity)
    print("d) Total Price: RM" + str(total_price))

    if not confirmation("Confirm"):
        print("Purchase cancelled.")
        return

    ticket_id = id_generator(TICKETS_RECORD, "T", 4)
    today = datetime.today().date().isoformat()
    new_line = "|".join([ticket_id, user[0], "ONLINE", type, tier, str(quantity), entry_date, str(entry_hour), str(total_price), today])
    write_file(TICKETS_RECORD, new_line)

    # Reduce stock in the catalog and save it back.
    row[3] = str(stock - quantity)
    save_ticket_catalog(catalog)

    print(f"Purchase successful. Ticket {ticket_id} has been recorded!")

#option B 
def walkin_ticket(user):
    print("\n=====Purchase Ticket (Walk-in)=====")
    print("A walk-in ticket will be reserved for you with a Queue ID.")

    if not confirmation("Are you sure you want to reserve for a walk-in ticket?"):
        print("This reservation is cancelled.")
        return

    queue_id = id_generator(WALKIN_RECORD, "Q", 4, 1)  
    today = datetime.today().date().isoformat()
    new_line = "|".join([queue_id, user[0], "WALKIN", "-", "-", "1", "-", "-", "-", today])
    new_line_walkin = "|".join([user[0], queue_id, today])
    write_file(TICKETS_RECORD, new_line)
    write_file(WALKIN_RECORD, new_line_walkin)
    print(f"Walk-in ticket reserved. Your Queue ID is: {queue_id}")


#option C (Haqimi's code)

def print_rides_table(rides):
    visible = []
    for ride in rides:
        if ride[STATUS] != REMOVED_STATUS:
            visible.append(ride)

    if len(visible) == 0:
        print("No rides to display.")
        return

    print("-" * 70)
    print("{:<5}{:<24}{:<7}{:<14}{:<10}{:<10}".format("ID", "Name", "Zone", "Status", "Wait", "Express"))
    print("-" * 70)

    for ride in visible:
        print("{:<5}{:<24}{:<7}{:<14}{:<10}{:<10}".format(ride[ID], ride[NAME], ride[ZONE], ride[STATUS], ride[WAIT_TIME], ride[EXPRESS_TIME]))

    print("-" * 70)
    print("Total:", len(visible), "ride(s)")

ID = 0
NAME = 1
ZONE = 2
STATUS = 3
WAIT_TIME = 4
EXPRESS_TIME = 5
FIELD = 6
REMOVED_STATUS = "REMOVED"

def view_search_rides(rides):
    print("\n--- VIEW / SEARCH RIDES ---")
    print("1. View all rides")
    print("2. Search by Zone")
    print("3. Search by Status")
    print("4. Search by Ride Name")
    print("5. Back to menu")

    choice = input("Select an option (1-5): ").strip()

    if choice == "1":
        print_rides_table(rides)

    elif choice == "2":
        zone = input("Enter zone (A/B/C/D): ").strip().upper()
        matches = []
        for ride in rides:
            if ride[ZONE] == zone:
                matches.append(ride)
        print_rides_table(matches)

    elif choice == "3":
        status = input("(Enter OPEN/CLOSED/MAINTENANCE) : ").strip().upper()
        matches = []
        for ride in rides:
            if ride [STATUS] == status:
                matches.append(ride)
        print_rides_table(matches)
    elif choice == "4":
        name = input("Enter ride name (or part of it): ").strip().upper()
        matches = []
        for ride in rides:
            if name in ride[NAME].upper():
                matches.append(ride)
        print_rides_table(matches)

    elif choice == "5":
        return

    else:
        print("Invalid option. Please choose 1-5.")


#option D
def purchase_shop_item(user):
    print("\n=====Purchase Shop Item=====")
    catalog = display_shop_cat()

    item_id = input("\nItemID: ").strip().upper()
    item_row = None
    for row in catalog:
        if row[0] == item_id:
            item_row = row

    if item_row is None:
        print("No item found with that ID.")
        return

    price = float(item_row[2])
    stock = int(item_row[3])
    if stock <= 0:
        print("That item is out of stock.")
        return

    quantity = positive_int("Quantity: ")
    while quantity > stock:
        print("Only " + str(stock) + " left in stock.")
        quantity = positive_int("Quantity: ")

    total_price = round(price * quantity, 2)
    print("\n=====Confirmation=====")
    print("a) ItemID:", item_row[0])
    print("b) Item Name:", item_row[1])
    print("c) Quantity:", quantity)
    print("d) Total Price: RM" + str(total_price))

    if not confirmation("Confirm"):
        print("This transaction has been cancelled.")
        return

    purchase_id = id_generator(SHOP_PURCHASES_RECORD, "P", 4)
    today = datetime.today().date().isoformat()
    new_line = "|".join([purchase_id, user[0], item_row[0], item_row[1],str(quantity), str(total_price), today])
    write_file(SHOP_PURCHASES_RECORD, new_line)

    item_row[3] = str(stock - quantity)
    save_shop_cat(catalog)

    print(f"Shop purchase successful and recorded! Purchase ID: {purchase_id}")

def load_shop_cat():
    lines = read_file(SHOP_RECORD)
    catalog = []
    for line in lines:
        line = line.strip()
        if line != "":
            catalog.append(line.strip().split("|"))
    return catalog

def display_shop_cat():
    catalog = load_shop_cat()

    # .ljust(20) forces a string to take up 20 spaces
    print("\n" + "ID".ljust(8) + "Item".ljust(20) + "Price".ljust(10) + "Stock".ljust(8))
    
    for item_id, name, price, stock in catalog:
        print(str(item_id).ljust(8) + str(name).ljust(20) + str(price).ljust(10) + str(stock).ljust(8))

    return catalog

def save_shop_cat(catalog):
    with open(SHOP_RECORD,"w") as file:
        for row in catalog:
            file.write("|".join(row)+"\n")

#Option E
def view_guest_transactions(user):
    ticket_lines = read_file(TICKETS_RECORD)

    #Online ticket
    print("\n=====My Tickets (Online)=====")
    print("{:<6} {:<8} {:<9} {:<4} {:<12} {:<5} {:<8}".format("ID", "Type", "Tier", "Qty", "Entry Date", "Hour", "Price"))

    found_online = False
    for line in ticket_lines:
        parts = line.strip().split("|")
        if len(parts) < 9:
            continue

        ticket_id = parts[0]
        owner = parts[1]
        purchase_type = parts[2]

        if owner == user and purchase_type == "ONLINE":
            found_online = True
            ticket_type = parts[3]
            tier = parts[4]
            qty = parts[5]
            entry_date = parts[6]
            hour = parts[7]
            price = parts[8]
            print("{:<6} {:<8} {:<9} {:<4} {:<12} {:<5} {:<8}".format(ticket_id, ticket_type, tier, qty, entry_date, hour, price))

    if not found_online:
        print("(none)")

    #walk-in tickets
    print("\n=====My Tickets (Walk-in)=====")
    print("{:<10} {:<12}".format("QueueID", "Date"))

    walkin_ticket_lines = read_file(WALKIN_RECORD)
    found_walkin = False
    for line in walkin_ticket_lines:
        parts = line.strip().split("|")
        if len(parts) < 3:              
            continue

        owner = parts[0]                
        queue_id = parts[1]
        reserved_date = parts[2]

        if owner == user:
            found_walkin = True
            print("{:<10} {:<12}".format(queue_id, reserved_date))

    if not found_walkin:
        print("(none)")

    #shop purchases
    print("\n=====My Shop Purchases=====")
    print("{:>6} {:>12} {:>4} {:>8} {:>13}".format("ID", "Item Name", "Qty", "Price", "Date"))

    shop_lines = read_file(SHOP_PURCHASES_RECORD)
    found_shop = False
    for line in shop_lines:
        parts = line.split("|")
        if len(parts) < 7:
            continue
        
        purchase_id = parts[0]
        owner = parts[1]

        if owner == user:
            found_shop = True
            item_name = parts[3]
            qty = parts[4]
            price = parts[5]
            date = parts[6]
            print("{:>6} {:>12} {:>4} {:>8} {:>14}".format(purchase_id, item_name, qty, price, date))

    if not found_shop:
        print("(none)")

if __name__ == "__main__":
    test_user = ["G0001", "test", "1234", "guest"]
    guest_menu(test_user)

