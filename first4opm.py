"""
Midway Theme Park - Operations Manager Console
==============================================

Role     : Operations Manager (Ride Record Management)
File     : first4opm.py
Data file: rides.txt

WHAT THIS PROGRAM DOES
----------------------
Menu-driven console program that manages the park's ride records:
    1. Add Ride            - create a new ride with validated input
    2. Update Ride         - change a ride's name or status
    3. Delete Ride         - remove a ride (soft delete, see below)
    4. View / Search Rides - list all, or search by zone / status / name
    5. Refresh Wait Times  - simulate current queue lengths
    6. Exit

DATA FORMAT (rides.txt)
-----------------------
The first line is the column-name header row. Every line after it is
one ride, six fields separated by "|":

    ride_id|ride_name|zone|status|wait_time(normal)|wait_time(express)
    1|Bumper Cars|A|OPEN|25|10

The header row must match RIDES_HEADERS in the group's main.py exactly,
or the shared read_file() helper rejects the whole file. Zones are
A, B, C, D. Status is OPEN, CLOSED, UNDER_MAINTAINANCE or REMOVED.

SHARED CODE
-----------
Reading is done by read_file() in the group's main.py, so every role
loads its data the same way. main.py is imported as "shared" because
this file has its own main() function, which would otherwise overwrite
the imported module name.

Saving still uses the local save_rides() below: main.py's write_file()
is not finished yet. When it is, save_rides() can call it, as long as it
opens in "w" mode and writes the whole list at once - appending one line
at a time would break Delete and Update.

HOW THE DATA MOVES
------------------
    rides.txt  --load_rides()-->  rides list  --save_rides()-->  rides.txt
                                   (memory)

The file is read once into a list of lists. All adding, deleting,
updating and searching happens on that list, then the whole list is
written back. A text file cannot be edited line by line, so every
change means rewriting the file.

DESIGN DECISION: SOFT DELETE
----------------------------
Deleting a ride does NOT remove its line from rides.txt. Instead the
status is set to REMOVED and the row is hidden from all displays and
searches.

Reason: other roles in the group project (e.g. the Ride Supervisor)
store incident reports that reference a Ride ID. If IDs were reused,
an old incident report would silently point at a different ride and
the record would be wrong. Keeping the row means its ID is permanently
taken, so IDs are never reused and old reports stay accurate.

PYTHON FEATURES AND TOOLS USED
------------------------------
Modules      : random (wait times), datetime (peak-hour detection),
               main (the group's shared read_file helper)
File I/O     : open() in "w" write mode, .close(); reading is delegated
               to the shared read_file() helper
String tools : .strip(), .split(), .join(), .upper(), .startswith()
Lists        : list of lists, .append(), .sort() with a key function,
               index lookup rides[i][FIELD]
Loops        : for-each, for with range(len()), while True with return
Conditionals : if / elif / else, and, !=, in
Conversion   : str() to store values, int() to compare them
Formatting   : "{:<5}".format() for aligned table columns
Validation   : re-prompting loops that only exit on valid input
Structure    : functions with parameters and return values,
               symbolic constants instead of magic numbers,
               if __name__ == "__main__" entry point
"""

import random
import datetime

import main as shared      # the group's shared module: read_file(), line_clean()
                           # aliased because this file defines its own main()


# --- file settings ---------------------------------------------------
# Taken from main.py so the whole group uses one definition. If the file
# name or the column names change there, this file follows automatically.
rides_file = shared.RIDES_RECORD
delimiter = "|"

# --- business rules --------------------------------------------------
valid_zones = ["A", "B", "C", "D"]
max_per_zone = 0          # 0 = unlimited rides per zone; set to 4, 8, etc. to cap it
valid_statuses = ["OPEN", "CLOSED", "UNDER_MAINTAINANCE"]
REMOVED_STATUS = "REMOVED"   # deliberately NOT in valid_statuses, so the
                             # user cannot set it through Add or Update

# --- field positions inside one ride record --------------------------
# A ride is a list of 6 strings. These constants name each position so
# the code reads ride[NAME] instead of the meaningless ride[1].
ID = 0
NAME = 1
ZONE = 2
STATUS = 3
WAIT_TIME = 4
EXPRESS_TIME = 5
FIELD = 6                 # how many fields a valid line must split into

# Column names written as the first line of rides.txt, taken from the
# group's main.py so there is only one definition of the file layout.
RIDES_HEADERS = shared.RIDES_HEADERS


def load_rides():
    """Read rides.txt and return the rides as a list of lists.

    Uses the group's shared read_file() helper from main.py, which opens the
    file, checks that the first line matches RIDES_HEADERS, splits every
    remaining line on "|" and reports any row with the wrong number of
    fields. It returns the rides already split, so nothing is left to do
    here.

    Returns an empty list if the file is missing, empty, or its header
    row does not match - the file is rejected rather than half-loaded.
    """
    return shared.read_file(rides_file, RIDES_HEADERS)


def print_rides_table(rides):
    """Print the given rides as a formatted table.

    Rides marked REMOVED are filtered out first, so soft-deleted rides
    never appear on screen. Because every search calls this function,
    filtering here hides them from all displays at once.

    Prints a message instead of an empty table when nothing matches.
    """
    visible = []
    for ride in rides:
        if ride[STATUS] != REMOVED_STATUS:
            visible.append(ride)

    if len(visible) == 0:
        print("No rides to display.")
        return

    print("-" * 76)
    print("{:<5}{:<24}{:<7}{:<20}{:<10}{:<10}".format(
        "ID", "Name", "Zone", "Status", "Wait", "Express"))
    print("-" * 76)

    for ride in visible:
        print("{:<5}{:<24}{:<7}{:<20}{:<10}{:<10}".format(
            ride[ID], ride[NAME], ride[ZONE], ride[STATUS],
            ride[WAIT_TIME], ride[EXPRESS_TIME]))

    print("-" * 76)
    print("Total:", len(visible), "ride(s)")


def save_rides(rides):
    """Write the whole rides list back to rides.txt.

    Uses the group's shared write_file() helper from main.py, which
    replaces the whole file: it writes RIDES_HEADERS as the first line,
    then one line per ride with "|" between the fields - the exact
    reverse of the .split() that read_file() does when loading.

    Because the header row it writes matches RIDES_HEADERS, the saved
    file still passes the header check the next time it is read.

    Must be called after any change to the list, or the change exists
    only in memory and is lost when the program closes.
    """
    shared.write_file(rides_file, RIDES_HEADERS, rides)


def view_search_rides(rides):
    """Show the view/search submenu and print whatever the user asks for.

    Read-only: this is the one feature that never changes the list, so
    it never calls save_rides().

    Each search builds a new 'matches' list and prints that, leaving the
    main rides list untouched. Zone and status use an exact match (they
    are short fixed values); ride name uses a partial match with 'in',
    so typing "bumper" finds "Bumper Cars".
    """
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
        status = input("(Enter OPEN/CLOSED/UNDER_MAINTAINANCE) : ").strip().upper()
        matches = []
        for ride in rides:
            if ride[STATUS] == status:
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
    """Soft-delete a ride: mark it REMOVED instead of removing the row.

    The user picks a ride by zone AND id, because every zone has a ride
    with id 1 - matching on id alone would delete the wrong ride.

    The search loop uses range(len(rides)) because the ride's POSITION
    is needed, not just the ride. index starts at -1 to mean "not found
    yet"; if it is still -1 after the loop, nothing matched.

    Already-removed rides are skipped by the search, so a ride cannot be
    deleted twice. The user must type YES to confirm, and that branch
    returns immediately - printing a refusal without returning would
    delete the ride anyway.
    """
    print("\n--- DELETE RIDE ---")

    print_rides_table(rides)

    zone = input("Enter zone (A/B/C/D): ").strip().upper()
    ride_id = input("Enter ride ID: ").strip()

    # find the ride's position in the list
    index = -1
    for i in range(len(rides)):
        if rides[i][ZONE] == zone and rides[i][ID] == ride_id and rides[i][STATUS] != REMOVED_STATUS:
            index = i
            break

    if index == -1:
        print("No ride found...")
        return

    print("You are about to delete:", rides[index][NAME])
    confirm = input("Type YES to confirm: ").strip().upper()
    if confirm != "YES":
        print("NOT DELETED")
        return

    # soft delete: the row stays so its ID can never be reused
    deleted_name = rides[index][NAME]
    rides[index][STATUS] = REMOVED_STATUS
    rides[index][WAIT_TIME] = "0"
    rides[index][EXPRESS_TIME] = "0"
    save_rides(rides)
    print(deleted_name, "deleted successfully.")


def zone_then_name(ride):
    """Sort key: group rides by zone, then alphabetically by name.

    Passed to rides.sort(key=...). Returning a pair means Python sorts
    by zone first and only uses the name to break ties within a zone.
    .upper() stops lowercase names sorting after uppercase ones.
    """
    return (ride[ZONE], ride[NAME].upper())


def read_zone():
    """Ask for a zone, re-asking until the answer is A, B, C or D.

    while True loops forever; the only way out is the return, which
    happens when the input is valid. .strip() removes stray spaces and
    .upper() accepts lowercase, so "  c  " is read as "C".
    """
    while True:
        value = input("Enter zone (A/B/C/D): ").strip().upper()
        if value in valid_zones:
            return value
        print("Zone must be A, B, C or D.")


def read_name():
    """Ask for a ride name, re-asking until it is usable.

    Rejects an empty name, and rejects any name containing "|" - that
    character separates the fields in rides.txt, so a name containing
    one would split into seven pieces and corrupt the record.

    No .upper() here: the user's capitalisation is kept, so the file
    stores "Bumper Cars" rather than "BUMPER CARS".
    """
    while True:
        value = input("Enter ride name: ").strip()
        if value == "":
            print("Name cannot be empty.")
        elif delimiter in value:
            print("Name cannot contain the | character.")
        else:
            return value


def read_status():
    """Ask for a status, re-asking until it is one of valid_statuses.

    REMOVED is not in that list on purpose, so the user cannot set a
    ride to REMOVED by hand - only delete_ride() does that.
    """
    while True:
        value = input("Enter Status:(OPEN/CLOSED/UNDER_MAINTAINANCE) ").strip().upper()
        if value in valid_statuses:
            return value
        print("Status must be OPEN,CLOSED or UNDER_MAINTAINANCE")


def add_ride(rides):
    """Create a new ride from validated user input and save it.

    The zone is asked first so a full zone can be rejected before the
    user types everything else. Removed rides do not count toward the
    zone limit, so deleting a ride frees a slot.

    The new ID is the highest ID in that zone plus 1. Because removed
    rides keep their row, their ID is still counted here - which is what
    stops a deleted ID from ever being handed out again.

    Wait times start at "0" and are filled in by refresh_wait_times().
    All six fields are stored as strings, because save_rides() joins
    them and "|".join() only accepts text.
    """
    print("\n--- ADD RIDE ---")

    zone = read_zone()

    # is the zone full? (removed rides do not take up a slot)
    count = 0
    for ride in rides:
        if ride[ZONE] == zone and ride[STATUS] != REMOVED_STATUS:
            count = count + 1

    if max_per_zone > 0 and count >= max_per_zone:
        print("Zone", zone, "is full (max", max_per_zone, "rides).")
        return

    name = read_name()
    status = read_status()

    # new ID = highest in this zone + 1 (int() to compare as numbers)
    highest = 0
    for ride in rides:
        if ride[ZONE] == zone and int(ride[ID]) > highest:
            highest = int(ride[ID])
    new_id = str(highest + 1)

    # build the ride - six fields, all strings
    new_ride = [new_id, name, zone, status, "0", "0"]

    # add it, then re-sort so names stay alphabetical within the zone
    rides.append(new_ride)
    rides.sort(key=zone_then_name)

    save_rides(rides)
    print("Added", name, "to zone", zone, "with ID", new_id)


def update_ride(rides):
    """Change an existing ride's name or status.

    Finds the ride the same way delete_ride() does - by zone AND id,
    skipping removed rides so a deleted ride cannot be edited back into
    use.

    Renaming re-sorts the list, because the new name may belong in a
    different alphabetical position. Changing the status does not affect
    the ordering, so that branch does not re-sort.

    Zone and ID are deliberately not editable: changing the zone would
    need a new ID, and changing the ID is exactly what the permanent-ID
    rule forbids. To move a ride, delete it and add it again.
    """
    print("\n--- UPDATE RIDE---")
    print_rides_table(rides)

    zone = input("Enter zone (A/B/C/D): ").strip().upper()
    ride_id = input("Enter ride ID: ").strip()

    # find it
    index = -1
    for i in range(len(rides)):
        if rides[i][ZONE] == zone and rides[i][ID] == ride_id and rides[i][STATUS] != REMOVED_STATUS:
            index = i
            break

    if index == -1:
        print("No ride found.")
        return

    # show the current record (wrapped in a list, as the table expects one)
    print("Current record:")
    print_rides_table([rides[index]])

    print("What do you want to update?")
    print("1. Name")
    print("2. Status")
    print("3. Cancel")
    choice = input("Select an option (1-3): ").strip()

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

    save_rides(rides)
    print("Ride updated.")


def refresh_wait_times(rides):
    """Simulate current queue lengths for every ride.

    The clock is checked once, before the loop, because the hour is the
    same for the whole park. The random pick is inside the loop, so each
    ride gets its own wait time rather than all showing the same number.

    Rules that keep the data believable:
      - anything not OPEN gets a wait of 0 (a closed ride has no queue)
      - queues are longer between 11:00 and 15:00 (lunchtime peak)
      - the express wait is 40% of the standard wait, never higher

    str() converts the numbers back to text before storing them, since
    every field in a ride must be a string for save_rides() to work.
    """
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
    """Run the Operations Manager menu until the user exits.

    The ride list is loaded ONCE here and passed to each feature, so
    every function works on the same list and changes carry over.

    Wait times are refreshed and saved at startup, so the queue lengths
    are different every time the program is opened.

    while True repeats the menu after each action; break on option 6 is
    the only way out.
    """
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


# Entry point: this block runs only when the file is run directly
# (python first4opm.py), not when another file imports it.
if __name__ == "__main__":
    main()
