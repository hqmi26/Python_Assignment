#Defining functions
def start_again():
    startAgain = input("Do you want to return to the previous menu? (y): ")
    return startAgain == "y"

#Welcome message

print("Current Role: Maintenance Supervisor")
print(f"Welcome!\n") #Placeholder to be changed

#Loop for invalid number
while True:
    
    #Main menu
    print("Available operations:")
    print("\t\t 1. Manage Maintenance Statuses") #Add maintenance status to facilities using facility codes + category, delete maintenance statuses, change maintenance statuses #add date
    print("\t\t 2. Manage Maintenance Tasks") #Assign Task, edit staff list, input task details, view tasks
    print("\t\t 3. View Maintenance Records") #View maintenance statuses and facility codes and staff in charge
    print("\t\t 4. Generate Maintenance Reports") #Generate report of maintenance, staff in charge, facility in charge by date
    print("\t\t 5. Exit") #Breaks the while true loop
    MenuChoice = input("\nPlease select an operation number to continue:") #Menu Choice 

    #Main Menu Output
        #Overall Operation Mapping:             
            #Input facility code, if entry exists, ask for overwrite + display current status(Input special character if want to delete), cancel option
            #if no exisiting, create new entry and input info, req for date, maintenance status (Completed / To be completed), Issue Type (Monthly Maintenance / Failure)
            #Display Entry Complete! (Display entry)


    #Menu Choice 1: Manage Maintenance Statuses
    if MenuChoice == "1":
        print("\n\nYou have chosen: Manage Maintenance Statuses")
        confirm = input("Please make sure this is the operation you want to carry out (y). \n Enter anything else to return to main menu: ")
        if confirm == "y":
            while True:
                facCode = input("Please input a facility code to modify status of: ")
                facFound = False #Current status of finding
                print()
                with open ("MaintenanceStatus.txt","r") as file:
                    #File line loop search
                    lines = file.readlines()

                matchedLine = None
                for line in lines:
                    if facCode in line:
                        facFound = True
                        matched_line = line
                        break

                #Existing Entry 
                if facFound:
                    print(f"Current entry: {matched_line.strip()}")
                    changeEntry = input(f"{facCode} already has an entry. Would you like to change it? (y/n): ")
                    if changeEntry == "y":
                        newDate = input("Enter corresponding date (dd/mm/yy): ")
                        newIssueType = input("Enter issue type (monthly maintenance / failure): ")
                        newStatus = input("Enter the new maintenance status (completed / not completed): ")
                        newEntryLine = f"{facCode},{newDate},{newIssueType},{newStatus}\n"

                        #Line replacement
                        updatedLine = []
                        for l in lines:
                            fields = l.strip().split(",")
                            if fields[0] == facCode:
                                updatedLine.append(newEntryLine)
                            else:
                                updatedLine.append(l)
                                
                        with open("MaintenanceStatus.txt", "w") as file:
                            file.writelines(updatedLine)

                        print("Entry Complete!")
                        print(f"Your new entry: {newEntryLine.strip()}")
                        if start_again():
                            continue
                        else:
                            break
                    else:
                        print("Returning to facility code menu...")
                        continue
                #No Existing Entry
                else:
                    print("Creating a new entry: ")
                    newDate = input("Enter corresponding date (dd/mm/yy): ")
                    newIssueType = input("Enter issue type (monthly maintenance / failure): ")
                    newStatus = input("Enter the new maintenance status (completed / not completed): ")
                    newEntryLine = f"{facCode},{newDate},{newIssueType},{newStatus}\n"

                    #Line creation
                    with open("MaintenanceStatus.txt", "a") as file:
                        file.write(newEntryLine)

                    print("Entry Complete!")
                    print(f"Your new entry: {newEntryLine.strip()}")
                    if start_again():
                        continue
                    else:
                        break
        else:
            continue


    # Menu Choice 2: Manage Maintenance Tasks
    elif MenuChoice == "2":
        #Overall Operation Mapping:
            #Options to 1) Assign staff for facility maintenance 2)Edit Staff List
            #1. Facilities that have the maintenance status of "to be completed" displayed with the issue type
            #Input for facility ID that has been chosen
            #Lists Staff and requests input for staff ID
            #Asks for any additional instructions (limit of 20 characters)(retry logic if exceeded)
            #2. Gives options: Add staff member, Remove Staff Member
            #To add staff member, input name (last name, first name), staff ID
            #To remove staff member, show all active staff, input for staff ID
            #Display operation successful Staff Name {name} has been added/removed
        print("\n\nYou have chosen: Manage Maintenance Tasks")
        confirm = input("Please make sure this is the operation you want to carry out (y). \n Enter anything else to return to main menu: ")
        if confirm == "y":
            while True:
                print("1. Assign staff for facility maintenance")
                print("2. Edit staff list")
                manage_choice = input("Please select an operation to continue: ")

                #Response to choosing operation
                if manage_choice == "1":
                    print("You have selected Option 1: Assign staff for facility maintenance")

                    #Locating unallocated maintenance
                    toBeCompletedCodes = []

                    with open("MaintenanceStatus.txt","r") as file:
                        lines = file.readlines()

                    for line in lines:
                        fields = line.split(",")
                        status = fields[3].strip()
                        if status == "to be completed":
                            facCode = fields[0]
                            toBeCompletedCodes.append(facCode)

                    #Displaying Facility Codes with unallocated maintenance
                    if toBeCompletedCodes:
                        print("Facilities with maintenance to be completed: ")
                        for code in toBeCompletedCodes:
                            print(code)
                        #Perpetual Loop until user inputs valid facility code
                        while True:
                            chosenFacCode = input("\nPlease enter the facility code to be assigned: ")
                            if chosenFacCode in toBeCompletedCodes:
                                break
                            else:
                                print("Invalid facility code. Please choose a valid facility code from the list.")
                        #Displaying all staff IDs
                        with open ("StaffList.txt", "r") as file:
                            staffLines = file.readlines()

                        staffIDs = []
                        for line in staffLines:
                            fields = line.strip().split(",")
                            staffIDs.append(fields[0])
                        
                        print("Available staff: ")
                        for staffID in staffIDs:
                            print(staffID)

                        #Loop until user inputs valid staff ID    
                        while True:
                            chosenID = input("Enter a valid staff ID: ")
                            if chosenID in staffIDs:
                                break
                            else:
                                print("Please enter a valid staff: ")
                                
                        #Append facCode to StaffList
                        updatedStaffEntry = []
                        for line in staffLines:
                            fields = line.strip().split(",")
                            if fields[0] == chosenID:
                                fields.append(chosenFacCode)
                                line = ",".join(fields) + "\n"
                            updatedStaffEntry.append(line)

                        with open ("StaffList.txt", "w") as file:
                            file.writelines(updatedStaffEntry)

                        #Changing maintenance status
                        with open ("MaintenanceStatus.txt", "r") as file:
                            statusLines = file.readlines()

                        updatedStatusLines = []
                        for line in statusLines:
                            fields = line.strip().split(",")
                            if fields[0] == chosenFacCode:
                                fields[3] = "completed"
                                line = ','.join(fields) + "\n"
                            updatedStatusLines.append(line)

                        with open ("MaintenanceStatus.txt", "w") as file:
                            file.writelines(updatedStatusLines)

                        print("Successful Maintenance Assigning")
                        print(f"{chosenFacCode} has been added to the responsibility of {chosenID}")

                    else:
                        print("No facilities currently have maintenance to be completed.")
                        print("Returning to menu")
                        continue
                    
                elif manage_choice == "2":
                    print("You have selected Option 2: Edit staff list \n")
                    print("1. Add staff")
                    print("2. Remove staff")
                    manage2_choice = input("Please select an action to carry out: ")

                    #Sub-branch (Adding staff member)
                    if manage2_choice == "1":
                    
                        print("You have selected to add a staff member \n")
                        newFirstName = input("Please enter the staff's first name: ")
                        newLastName = input("Please enter the staff's last name: ")
                                                
                        #Checking for no staffID overlaps
                        with open ("StaffList.txt", "r") as file:
                            staffIDLines = file.readlines()

                        currentIDs = []
                        for line in staffIDLines:
                            fields = line.strip().split(",")
                            currentIDs.append(fields[0])

                        while True:
                            newStaffID = input("Please enter the staff's ID: ")
                            if newStaffID in currentIDs:
                                print("Staff ID has already been taken")
                            else:
                                break
                            
                        #Adding staff info into txt

                        newStaffEntry = f"{newStaffID},{newLastName},{newFirstName}\n" #Staff Entry Format

                        with open("StaffList.txt", "a") as file:
                                  file.write(newStaffEntry)

                        print("Successful creation of new staff member")
                        print(f"Added {newFirstName} {newLastName}, Staff ID: {newStaffID}")
                                  
                    #Sub-branch (Removing staff member)    
                    elif manage2_choice == "2":
                        print("You have selected to remove a staff member \n")

                        with open("StaffList.txt", "r") as file:
                            staffIDs = file.readlines()

                        staffEntries = []
                        for line in staffIDs:
                            fields = line.strip().split(",")
                            staffEntries.append(fields[0])

                        print("Current Staff IDs:")
                        for staffID in staffEntries:
                            print(staffID)

                        while True:
                            removeID = input("\nEnter the staff ID to be removed: ")
                            if removeID in staffEntries:
                                break
                            else:
                                print("Invalid staff ID entered. Please try again.")

                        updatedStaffList = []
                        for line in staffIDs:
                            fields = line.strip().split(",")
                            if fields[0] != removeID:
                                updatedStaffList.append(line)

                        with open("StaffList.txt", "w") as file:
                            file.writelines(updatedStaffList)

                        print("Successful removal of staff member")
                        print(f"Staff ID: {removeID} has been removed")
                        
                    else:
                        print("Invalid action entered. Please try again.")
                        continue
                else:
                    print("Invalid operation. Returning to main menu")
                    continue
        else:
            continue

        
    #Menu Choice 3: View Maintenance Records
        #Mapping:
        #Pulls all maintenance info from file shared with MenuChoice 1. Lists: Facility Code, Date, Issue Type, Maintenance Status, Staff ID
        #Ordered with \t and \n
        
    elif MenuChoice == "3":
        print("\n\nYou have chosen: View Maintenance Records")
        confirm = input("Please make sure this is the operation you want to carry out (y). \n Enter anything else to return to main menu: ")
        if confirm == "y":
            print("Retrieving maintenance records ")

            #Reading MaintenanceStatus Text File
            with open("MaintenanceStatus.txt", "r") as file:
                maintenanceLines = file.readlines()

            with open("StaffList.txt", "r") as file:
                staffLines = file.readlines()

            #Finding StaffID from Facility Code
            facToStaff = {}
            for line in staffLines:
                fields = line.strip().split(",")
                staffID = fields[0]
                assignedCodes = fields[3:]
                for code in assignedCodes:
                    facToStaff[code] = staffID

            #Printing Table
            if maintenanceLines:
                #Table Header
                print("Facility Code\tDate\tIssue Type\tStatus\tStaff ID")
                for line in maintenanceLines:
                    fields = line.strip().split(",")
                    #Variable identification
                    facCode = fields[0]
                    date = fields[1]
                    issueType = fields[2]
                    status = fields[3]
                    #Table Body
                    assignedStaff = facToStaff.get(facCode, "N/A")
                    print(f"{facCode}\t{date}\t{issueType}\t{status}\t{assignedStaff}")
            else:
                print("There are no maintenance records to show")
        else:
            continue


    #Menu Choice 4: Generate Maintenance Reports
        #Mapping:
        #Pulls maintenance records for a specific day
    elif MenuChoice == "4":
        print("\n\nYou have chosen: Generate Maintenance Reports")
        confirm = input("Please make sure this is the operation you want to carry out (y). \n Enter anything else to return to main menu: ")
        if confirm == "y":
            dateInput = input("Enter the date for maintenance records: ")

            with open("MaintenanceStatus.txt", "r") as file:
                maintenanceLines = file.readlines()

            with open("StaffList.txt", "r") as file:
                staffLines = file.readlines()
                
            #Finding StaffID from Facility Code
            facToStaff = {}
            for line in staffLines:
                fields = line.strip().split(",")
                staffID = fields[0]
                assignedCodes = fields[3:]
                for code in assignedCodes:
                    facToStaff[code] = staffID

            matchingLines = []
            for line in maintenanceLines:
                fields = line.strip().split(",")
                if fields[1] == dateInput:
                    matchingLines.append(fields)

            #Printing Table
            if matchingLines:
                #Table Header
                print("Facility Code\tIssue Type\tStatus\tStaff ID")
                for fields in matchingLines:
                        #Variable identification
                        facCode = fields[0]
                        issueType = fields[2]
                        status = fields[3]
                        #Table Body
                        assignedStaff = facToStaff.get(facCode, "N/A")
                        print(f"{facCode}\t{issueType}\t{status}\t{assignedStaff}")
            else:
                print(f"There are no maintenance records to show for the date: {dateInput}")    
        else:
            continue
    elif MenuChoice == "5":
        break
    else:
        print("Please select a valid operation number")
