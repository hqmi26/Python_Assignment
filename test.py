
"""
Midway Theme Park Operations Console
-------------------------------------
Module   : operations_manager_rides.py
Author   : Operations Manager role - Ride Record Management
Covers   : Add Ride, Update Ride, Delete Ride, View/Search Rides
           (the first 4 items of the Operations Manager menu)
 
Design notes:
- Procedural style only: no classes, no OOP, no external libraries.
- Each ride record is stored as a LIST of 9 fields (not a dictionary
  object) so the whole program stays plain lists + loops + conditionals,
  as required by the assignment brief.
- Data is persisted to a plain text file (rides.txt) using "|" as the
  field delimiter, so ride names may safely contain commas.
- This file can be run on its own (see the __main__ block) to demo the
  4 functions, or the functions below can be imported into the group's
  shared main.py and wired into the full role-based menu.
 
rides.txt layout (one ride per line):
    RideID|RideName|Zone|Status|Capacity|CycleTimeMin|StaffRequired|StaffAssigned|WaitTimeMin
Lines starting with "#" are treated as comments/headers and skipped.
"""
 
import os
 
# ---------------------------------------------------------------------------
# Constants (symbolic constants instead of "magic numbers/strings")
# ---------------------------------------------------------------------------
RIDES_FILE = "rides.txt"
 
# Index positions inside each ride record (a list of 9 elements)
ID_IDX = 0
NAME_IDX = 1
ZONE_IDX = 2
STATUS_IDX = 3
CAPACITY_IDX = 4
CYCLE_TIME_IDX = 5
STAFF_REQUIRED_IDX = 6
STAFF_ASSIGNED_IDX = 7
WAIT_TIME_IDX = 8
FIELD_COUNT = 9
 
VALID_STATUSES = ["OPEN", "CLOSED", "MAINTENANCE"]
VALID_ZONES = [1, 2, 3, 4]
DELIMITER = "|"
 
 
# ---------------------------------------------------------------------------
# File handling
# ---------------------------------------------------------------------------
def load_rides():
    """Read rides.txt and return a list of ride records (each a list).
    Handles a missing file gracefully by creating an empty one instead
    of crashing the program."""
    rides = []
 
    if not os.path.exists(RIDES_FILE):
        try:
            open(RIDES_FILE, "w").close()
        except OSError as error:
            print("ERROR: could not create", RIDES_FILE, "-", error)
        return rides
 
    try:
        data_file = open(RIDES_FILE, "r")
    except OSError as error:
        print("ERROR: could not open", RIDES_FILE, "-", error)
        return rides
 
    for raw_line in data_file:
        line = raw_line.strip()
        if line == "" or line.startswith("#"):
            continue
 
        parts = line.split(DELIMITER)
        if len(parts) != FIELD_COUNT:
            print("WARNING: skipped a corrupted line in rides.txt ->", line)
            continue
 
        rides.append(parts)
 
    data_file.close()
    return rides
 
 
def save_rides(rides):
    """Overwrite rides.txt with the current in-memory list of rides.
    Returns True on success, False if the write failed."""
    try:
        data_file = open(RIDES_FILE, "w")
    except OSError as error:
        print("ERROR: could not save", RIDES_FILE, "-", error)
        return False
 
    data_file.write("# Midway Theme Park - Ride Records\n")
    data_file.write("# Format: RideID|RideName|Zone|Status|Capacity|"
                     "CycleTimeMin|StaffRequired|StaffAssigned|WaitTimeMin\n")
 
    for ride in rides:
        data_file.write(DELIMITER.join(ride) + "\n")
 
    data_file.close()
    return True
 
 
# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
def find_ride_index(rides, ride_id_text):
    """Return the list index of the ride whose ID matches ride_id_text,
    or -1 if it is not found."""
    for index in range(len(rides)):
        if rides[index][ID_IDX] == ride_id_text:
            return index
    return -1
 
 
def generate_next_id(rides):
    """Auto-generate the next Ride ID (highest existing ID + 1, starting
    at 101) so the user is never asked to invent an ID by hand."""
    highest = 100
    for ride in rides:
        try:
            current_id = int(ride[ID_IDX])
            if current_id > highest:
                highest = current_id
        except ValueError:
            continue
    return str(highest + 1)
 
 
def read_non_empty_text(prompt):
    """Keep asking until the user enters non-blank text that does not
    contain the '|' delimiter (which would corrupt the data file)."""
    while True:
        value = input(prompt).strip()
        if value == "":
            print("Input cannot be empty. Please try again.")
        elif DELIMITER in value:
            print("Input cannot contain the '|' character. Please try again.")
        else:
            return value
 
 
def read_int_in_range(prompt, minimum, maximum):
    """Keep asking until the user enters a whole number within
    [minimum, maximum]. Rejects text, decimals, and out-of-range values."""
    while True:
        raw_value = input(prompt).strip()
        try:
            value = int(raw_value)
        except ValueError:
            print("Please enter a whole number (no letters or decimals).")
            continue
 
        if value < minimum or value > maximum:
            print("Value must be between", minimum, "and", str(maximum) + ".")
            continue
 
        return value
 
 
def read_status(prompt):
    """Keep asking until the user enters a valid ride status."""
    while True:
        value = input(prompt).strip().upper()
        if value in VALID_STATUSES:
            return value
        print("Status must be one of:", ", ".join(VALID_STATUSES))
 
 
# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------
def print_ride_header():
    print("-" * 96)
    print("{:<6}{:<20}{:<6}{:<12}{:<10}{:<10}{:<12}{:<12}{:<10}".format(
        "ID", "Name", "Zone", "Status", "Capacity", "Cycle", "StaffReq",
        "StaffHas", "WaitMin"))
    print("-" * 96)
 
 
def print_ride_row(ride):
    print("{:<6}{:<20}{:<6}{:<12}{:<10}{:<10}{:<12}{:<12}{:<10}".format(
        ride[ID_IDX], ride[NAME_IDX], ride[ZONE_IDX], ride[STATUS_IDX],
        ride[CAPACITY_IDX], ride[CYCLE_TIME_IDX], ride[STAFF_REQUIRED_IDX],
        ride[STAFF_ASSIGNED_IDX], ride[WAIT_TIME_IDX]))
 
 
def print_rides_table(rides):
    if len(rides) == 0:
        print("No ride records to display.")
        return
    print_ride_header()
    for ride in rides:
        print_ride_row(ride)
    print("-" * 96)
    print("Total rides:", len(rides))
 
 
# ---------------------------------------------------------------------------
# CORE FUNCTION 1: Add Ride
# ---------------------------------------------------------------------------
def add_ride(rides):
    print("\n--- ADD NEW RIDE ---")
 
    new_id = generate_next_id(rides)
    print("Assigned Ride ID:", new_id)
 
    name = read_non_empty_text("Ride name: ")
    zone = read_int_in_range("Zone (1-4): ", 1, 4)
    status = read_status("Status (OPEN/CLOSED/MAINTENANCE): ")
    capacity = read_int_in_range("Capacity per cycle (1-200): ", 1, 200)
    cycle_time = read_int_in_range("Cycle time in minutes (1-60): ", 1, 60)
    staff_required = read_int_in_range("Staff required (0-20): ", 0, 20)
    staff_assigned = read_int_in_range("Staff currently assigned (0-20): ", 0, 20)
    wait_time = read_int_in_range("Current wait time in minutes (0-240): ", 0, 240)
 
    new_ride = [new_id, name, str(zone), status, str(capacity),
                str(cycle_time), str(staff_required), str(staff_assigned),
                str(wait_time)]
 
    rides.append(new_ride)
 
    if save_rides(rides):
        print("Ride", new_id, "(" + name + ") added successfully.")
        if staff_assigned < staff_required:
            print("NOTE: this ride is currently UNDERSTAFFED "
                  "(" + str(staff_assigned) + "/" + str(staff_required) + ").")
    else:
        print("Ride was added in memory but could NOT be saved to file.")
 
 
# ---------------------------------------------------------------------------
# CORE FUNCTION 2: Update Ride
# ---------------------------------------------------------------------------
def update_ride(rides):
    print("\n--- UPDATE RIDE ---")
 
    if len(rides) == 0:
        print("There are no rides to update yet.")
        return
 
    ride_id = input("Enter Ride ID to update: ").strip()
    index = find_ride_index(rides, ride_id)
 
    if index == -1:
        print("No ride found with ID", ride_id + ".")
        return
 
    ride = rides[index]
    print("Current record:")
    print_ride_header()
    print_ride_row(ride)
    print("\nPress ENTER on any field to keep its current value.\n")
 
    # Name
    new_name = input("New name [" + ride[NAME_IDX] + "]: ").strip()
    if new_name != "":
        if DELIMITER in new_name:
            print("Name cannot contain '|'. Keeping previous name.")
        else:
            ride[NAME_IDX] = new_name
 
    # Zone
    new_zone = input("New zone 1-4 [" + ride[ZONE_IDX] + "]: ").strip()
    if new_zone != "":
        if new_zone.isdigit() and int(new_zone) in VALID_ZONES:
            ride[ZONE_IDX] = new_zone
        else:
            print("Invalid zone. Keeping previous zone.")
 
    # Status
    new_status = input("New status OPEN/CLOSED/MAINTENANCE [" +
                        ride[STATUS_IDX] + "]: ").strip().upper()
    if new_status != "":
        if new_status in VALID_STATUSES:
            ride[STATUS_IDX] = new_status
        else:
            print("Invalid status. Keeping previous status.")
 
    # Capacity
    new_capacity = input("New capacity [" + ride[CAPACITY_IDX] + "]: ").strip()
    if new_capacity != "":
        if new_capacity.isdigit() and 1 <= int(new_capacity) <= 200:
            ride[CAPACITY_IDX] = new_capacity
        else:
            print("Invalid capacity. Keeping previous capacity.")
 
    # Cycle time
    new_cycle = input("New cycle time minutes [" +
                       ride[CYCLE_TIME_IDX] + "]: ").strip()
    if new_cycle != "":
        if new_cycle.isdigit() and 1 <= int(new_cycle) <= 60:
            ride[CYCLE_TIME_IDX] = new_cycle
        else:
            print("Invalid cycle time. Keeping previous value.")
 
    # Staff required
    new_staff_req = input("New staff required [" +
                           ride[STAFF_REQUIRED_IDX] + "]: ").strip()
    if new_staff_req != "":
        if new_staff_req.isdigit() and 0 <= int(new_staff_req) <= 20:
            ride[STAFF_REQUIRED_IDX] = new_staff_req
        else:
            print("Invalid value. Keeping previous staff required.")
 
    # Staff assigned
    new_staff_has = input("New staff assigned [" +
                           ride[STAFF_ASSIGNED_IDX] + "]: ").strip()
    if new_staff_has != "":
        if new_staff_has.isdigit() and 0 <= int(new_staff_has) <= 20:
            ride[STAFF_ASSIGNED_IDX] = new_staff_has
        else:
            print("Invalid value. Keeping previous staff assigned.")
 
    # Wait time
    new_wait = input("New wait time minutes [" +
                      ride[WAIT_TIME_IDX] + "]: ").strip()
    if new_wait != "":
        if new_wait.isdigit() and 0 <= int(new_wait) <= 240:
            ride[WAIT_TIME_IDX] = new_wait
        else:
            print("Invalid value. Keeping previous wait time.")
 
    rides[index] = ride
 
    if save_rides(rides):
        print("Ride", ride_id, "updated successfully.")
    else:
        print("Ride was updated in memory but could NOT be saved to file.")
 
 
# ---------------------------------------------------------------------------
# CORE FUNCTION 3: Delete Ride
# ---------------------------------------------------------------------------
def delete_ride(rides):
    print("\n--- DELETE RIDE ---")
 
    if len(rides) == 0:
        print("There are no rides to delete.")
        return
 
    ride_id = input("Enter Ride ID to delete: ").strip()
    index = find_ride_index(rides, ride_id)
 
    if index == -1:
        print("No ride found with ID", ride_id + ".")
        return
 
    print("You are about to delete:")
    print_ride_header()
    print_ride_row(rides[index])
 
    confirm = input("Type YES to confirm deletion: ").strip().upper()
    if confirm != "YES":
        print("Deletion cancelled.")
        return
 
    removed_name = rides[index][NAME_IDX]
    del rides[index]
 
    if save_rides(rides):
        print("Ride", ride_id, "(" + removed_name + ") deleted successfully.")
        print("NOTE: any incident/queue log records referencing this Ride ID "
              "will now be orphaned - flag them for the Ride Supervisor's "
              "'Handle Data Errors' function.")
    else:
        print("Ride was removed in memory but could NOT be saved to file.")
 
 
# ---------------------------------------------------------------------------
# CORE FUNCTION 4: View / Search Rides
# ---------------------------------------------------------------------------
def view_search_rides(rides):
    print("\n--- VIEW / SEARCH RIDES ---")
    print("1. View all rides")
    print("2. Search by Ride ID")
    print("3. Search by Zone")
    print("4. Search by Status")
    print("5. Search by maximum wait time")
    print("6. Back to menu")
 
    choice = input("Select an option (1-6): ").strip()
 
    if choice == "1":
        print_rides_table(rides)
 
    elif choice == "2":
        ride_id = input("Enter Ride ID: ").strip()
        index = find_ride_index(rides, ride_id)
        if index == -1:
            print("No ride found with ID", ride_id + ".")
        else:
            print_ride_header()
            print_ride_row(rides[index])
 
    elif choice == "3":
        zone = read_int_in_range("Enter zone (1-4): ", 1, 4)
        matches = []
        for ride in rides:
            if ride[ZONE_IDX] == str(zone):
                matches.append(ride)
        print_rides_table(matches)
 
    elif choice == "4":
        status = read_status("Enter status (OPEN/CLOSED/MAINTENANCE): ")
        matches = []
        for ride in rides:
            if ride[STATUS_IDX] == status:
                matches.append(ride)
        print_rides_table(matches)
 
    elif choice == "5":
        max_wait = read_int_in_range("Show rides with wait time at or below "
                                      "(0-240 minutes): ", 0, 240)
        matches = []
        for ride in rides:
            if int(ride[WAIT_TIME_IDX]) <= max_wait:
                matches.append(ride)
        print_rides_table(matches)
 
    elif choice == "6":
        return
 
    else:
        print("Invalid option. Please choose 1-6.")
 
 
# ---------------------------------------------------------------------------
# Menu loop (for standalone demo / can be called from the group's main menu)
# ---------------------------------------------------------------------------
def operations_manager_ride_menu():
    rides = load_rides()
 
    while True:
        print("\n===== OPERATIONS MANAGER - RIDE RECORD MANAGEMENT =====")
        print("1. Add Ride")
        print("2. Update Ride")
        print("3. Delete Ride")
        print("4. View / Search Rides")
        print("5. Exit")
 
        choice = input("Select an option (1-5): ").strip()
 
        if choice == "1":
            add_ride(rides)
        elif choice == "2":
            update_ride(rides)
        elif choice == "3":
            delete_ride(rides)
        elif choice == "4":
            view_search_rides(rides)
        elif choice == "5":
            print("Exiting Ride Record Management. Goodbye!")
            break
        else:
            print("Invalid option. Please choose a number from 1 to 5.")
 
 
if __name__ == "__main__":
    operations_manager_ride_menu()
 
