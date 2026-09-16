import os

Rides_File = "rides.txt"

ID_Ride = 0
NAME_Ride = 1
ZONE_Ride = 2
STATUS_Ride = 3
CAPACITY_Ride = 4
CYCLE_TIME_Ride = 5
WAIT_TIME_IDX = 6
 
VALID_STATUSES = ["OPEN", "CLOSED", "MAINTENANCE"]
VALID_ZONES = [1, 2, 3, 4]
DELIMITER = "|"

def load_rides():
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