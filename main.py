from datetime import datetime #a libary that is built-in python library language 
import time #same thing

USERS_RECORD = "users.txt" #all users password n everythin
RIDES_RECORD = "rides.txt" #all those goofy ahh rides and ID for stupid rides 4 zones 16 rides
TICKETS_RECORD = "tickets_purchases.txt" #guest that bougth whatever TICKETS
SHOP_RECORD = "shop.txt" #shop items
SHOP_PURCHASES_RECORD = "shop_purchases.txt" #guest that bought whatever SHOP item
WALKIN_RECORD = "walkin.txt" #record the stupid queue id for those who wants walkin
SETTINGS_RECORD = "settings.txt" #record the stock for (express,plus/express,premier/normal,plus/normal,premier) price, stocks and other settings

#i only made the text file that i needed for guest and yall cn use the file to connect ur parts
USERS_HEADERS = ["user_id", "username", "password", "role"]
RIDES_HEADERS = ["ride_id", "ride_name", "zone", "status", "wait_time(normal)", "wait_time(express)"]
TICKETS_HEADERS = ["ticket_id", "user_id", "ticket_type", "ticket_tier", "quantity", "entry date", "entry time", "price"]
SHOP_HEADERS = ["item_id", "item_name", "price", "stock"]
SHOP_PURCHASES_HEADERS = ["purchases_id", "user_id", "item_id", "item_name", "quantity", "price", "purchase_date"]
WALKIN_HEADERS = ["user_id" , "queue_id"]


ROLES = ["OPERATION MANAGER", "RIDE_SUPERVISOR", "GUEST"]
RIDE_STATUS = ["OPEN", "CLOSED", "UNDER_MAINTAINANCE"]
TICKET_TIER = ["PLUS", "PREMIER"]

def read_file(filename, headers):
    records = []
    try: #file access or onversion can fail; the matching except block can handles the failure politely instead of stopping the program
        data_file = open(filename, "r")
        lines = data_file.readlines() #can directly reuse the "lines" later on
        data_file.close() #it continues the current operation
    except FileNotFoundError: #user can receive a text if it detects error on the file
        print(f"{filename} not found! Returning empty list.")
        return records
    except OSError: #specific expected error so the user can receive a test rather than a technical traceback
        print(f"Error reading from {filename}")
        return records

    if not lines: #check before continuing. testing first
        print(f"{filename} is empty! Warning!")
        return records
    if lines[0].strip().split("|") != headers:
        print(f"{filename} has a header error and was ignored.")
        return records
    for line_number in range(1, len(lines)):
        values = line_clean(lines[line_number]).split("|")
        if len(values) == len(headers) and values != [""]:
            records.append(values)
        elif line_clean(lines[line_number]) != "":
            print("There is an invalid row" + str(line_number + 1) + "in " + filename + " was ignored")
    return records

def line_clean(value): #removes line break characters so later when compare will not fail because of the invisible whitespace
    return value.strip().replace("\n", "").replace("\r","")

"""
def write_file(filename, headers, records):
    try:
        data_file = open(filename, "w")
        data_file.write("|")
        bru idk bro dont understand shit d
"""
