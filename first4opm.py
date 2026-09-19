import os
import random 
import datetime



rides_file = "rides.txt"
delimiter = "|"
valid_zones =[ "A","B","C","D"]
max_per_zone = 4
valid_statuses = ["OPEN","CLOSED","MAINTENANCE"]
REMOVED_STATUS = "REMOVED"

ID = 0
NAME = 1
ZONE = 2
STATUS = 3
WAIT_TIME = 4
EXPRESS_TIME = 5
FIELD = 6

def load_rides():
    rides = []

    if not os.path.exists(rides_file):
        print("ERROR: rides.txt not found.")
        return rides

    data_file = open(rides_file, "r")

    for raw_line in data_file:
        line = raw_line.strip()

        if line == "" or line.startswith("#"):
            continue

        parts = line.split(delimiter)

        if len(parts) != FIELD:
            print("WARNING: skipped corrupted line ->", line)
            continue

        rides.append(parts)

    data_file.close()
    return rides


def print_rides_table(rides):
    visible = []
    for ride in rides:
        if ride[STATUS] != REMOVED_STATUS:
            visible.append(ride)

    if len(visible) == 0:
        print("No rides to display.")
        return

    print("-" * 70)
    print("{:<5}{:<24}{:<7}{:<14}{:<10}{:<10}".format(
        "ID", "Name", "Zone", "Status", "Wait", "Express"))
    print("-" * 70)

    for ride in visible:
        print("{:<5}{:<24}{:<7}{:<14}{:<10}{:<10}".format(
            ride[ID], ride[NAME], ride[ZONE], ride[STATUS],
            ride[WAIT_TIME], ride[EXPRESS_TIME]))

    print("-" * 70)
    print("Total:", len(visible), "ride(s)")



def save_rides(rides):
    data_file = open(rides_file, "w")

    data_file.write("# Midway Theme Park - Ride Records\n")
    data_file.write("# Format: RideID|RideName|Zone|Status|WaitTimeMin|ExpressWaitMin\n")
    data_file.write("# Status one of this: OPEN, CLOSED, MAINTENANCE\n")
    data_file.write("# IDs are permanent and never reused. Names are alphabetical within a zone.\n")

    for ride in rides:
        data_file.write(delimiter.join(ride) + "\n")

    data_file.close()
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


def delete_ride(rides):
    print("\n--- DELETE RIDE ---")

    print_rides_table(rides)

    zone = input("Enter zone (A/B/C/D): ").strip().upper()
    ride_id = input("Enter ride ID: ").strip()
    index = -1
    for i in range(len(rides)):
        if rides[i][ZONE] == zone and rides[i][ID] == ride_id and rides[i][STATUS] != REMOVED_STATUS:
            index = i
            break


    # STEP 4: not found?
    if index == -1:
        print("No ride found...")
        return

    print("You are about to delete:", rides[index][NAME])
    confirm = input("Type YES to confirm: ").strip().upper()
    if confirm != "YES":
        print("NOT DELETED")
        return

    deleted_name = rides[index][NAME]
    rides[index][STATUS] = REMOVED_STATUS     # was: del rides[index]
    rides[index][WAIT_TIME] = "0"
    rides[index][EXPRESS_TIME] = "0"
    save_rides(rides)
    print(deleted_name, "deleted successfully.")


    
    # STEP 6: del rides[index]
    #         save_rides(rides)



def zone_then_name(ride):
    return (ride[ZONE], ride[NAME].upper())

def read_zone():
    while True:
        value = input("Enter zone (A/B/C/D): ").strip().upper()
        if value in valid_zones:
            return value
        print("Zone must be A, B, C or D.")

def read_name():
    while True:
        value = input("Enter ride name: ").strip()      # no .upper() — keep the user's capitalisation
        if value == "":
            print("Name cannot be empty.")
        elif delimiter in value:
            print("Name cannot contain the | character.")
        else:
            return value
def read_status():
    while True:
        value = input("Enter Status:(OPEN/CLOSED/MAINTENANCE) ").strip().upper()
        if value in valid_statuses:
            return value
        print("Status must be OPEN,CLOSED or MAINTENANCE")
         

def add_ride(rides):
    print("\n--- ADD RIDE ---")

    zone = read_zone()

    # 1. is the zone full?
    count = 0
    for ride in rides:
        if ride[ZONE] == zone and ride[STATUS] != REMOVED_STATUS:
            count = count + 1

    if count >= max_per_zone:
        print("Zone", zone, "is full (max", max_per_zone, "rides).")
        return

    name = read_name()
    status = read_status()

    # 2. new ID = highest in this zone + 1
    highest = 0
    for ride in rides:
        if ride[ZONE] == zone and int(ride[ID]) > highest:
            highest = int(ride[ID])
    new_id = str(highest + 1)

    # 3. build the ride — six fields, all strings
    new_ride = [new_id, name, zone, status, "0", "0"]

    # 4. add it, then re-sort so names stay alphabetical
    rides.append(new_ride)
    rides.sort(key=zone_then_name)

    save_rides(rides)
    print("Added", name, "to zone", zone, "with ID", new_id)


def update_ride(rides):
    print("\n--- UPDATE RIDE---")
    print_rides_table(rides)
    
    zone = input("Enter zone (A/B/C/D): ").strip().upper()
    ride_id = input("Enter ride ID: ").strip()

    # 2. find it
    index = -1
    for i in range(len(rides)):
        if rides[i][ZONE] == zone and rides[i][ID] == ride_id:
            index = i
            break

    if index == -1:
        print("No ride found.")
        return

    # 3. show it
    print("Current record:")
    print_rides_table([rides[index]])


    print("What do you want to update?")
    print("1. Name")
    print("2. Status")
    print("3. Cancel")
    choice = input("Select an option (1-3): ").strip()

    # 5. change it
    if choice == "1":
        rides[index][NAME] = read_name()
        rides.sort(key=zone_then_name)
    elif choice == "2":
        rides[index][STATUS] = read_status()
    elif choice == "3":
        print("Update cancelled.")
        return
    else:
        print("Invalid option.")
        return

    # 6. save
    save_rides(rides)
    print("Ride updated.")
    
def refresh_wait_times(rides):
    now = datetime.datetime.now()
    peak_hours = 11 <= now.hour <= 15        # lunchtime rush

    for ride in rides:
        if ride[STATUS] != "OPEN":
            ride[WAIT_TIME] = "0"
            ride[EXPRESS_TIME] = "0"
        else:
            if peak_hours:
                wait = random.randint(30, 75)
            else:
                wait = random.randint(5, 30)

            ride[WAIT_TIME] = str(wait)
            ride[EXPRESS_TIME] = str(int(wait * 0.4))


def main():
    rides = load_rides()
    refresh_wait_times(rides)
    save_rides(rides)

    while True:
        print("\n===== OPERATIONS MANAGER =====")
        print("1. Add Ride")
        print("2. Update Ride")
        print("3. Delete Ride")
        print("4. View / Search Rides")
        print("5. Refresh Wait Times")
        print("6. Exit")

        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            add_ride(rides)
        elif choice == "2":
            update_ride(rides)
        elif choice == "3":
            delete_ride(rides)
        elif choice == "4":
            view_search_rides(rides)
        elif choice == "5":
            refresh_wait_times(rides)
            save_rides(rides)
            print("Wait times refreshed.")
            print_rides_table(rides)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Choose 1-6.")


if __name__ == "__main__":
    main()
