# Some custom imports including time, SQLite
from datetime import datetime
import sqlite3
import os
import platform

# importing geopy library
from geopy.geocoders import Nominatim
from geopy import distance

# importing output objects
from input import Input

# Importing database
data_stop = sqlite3.connect('stops.db')
s = data_stop.cursor()

# Find OS and set clear termial command
if platform.system() == 'Windows':
    clearTermial = 'cls'
elif platform.system() == 'Darwin':
    clearTermial = 'clear'
elif platform.system() == 'Linux':
    clearTermial = 'clear'
else:
    clearTermial = 'clear'


def distance_finder(location, ttc_stops):
    """
    Finds distances between two coordinates (of type tuple) using
    Geopy distance

    :param location:
    :param ttc_stops:
    :return: distance in km
    """
    return distance.distance(location, ttc_stops).km


def get_stop_id_coord(stop_id):
    """
    Gets the coordinates of a stop_id

    :param stop_id:
    :return:
    """
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop_id})
    the_stop = s.fetchall()[0]

    return (the_stop[2], the_stop[3])


def find_closest_stop(location):
    """
    Finds the stop_id that's the closest to the location given

    :param location:
    :return: min_stop_id
    """
    s.execute("SELECT * FROM stops")
    all_stops = s.fetchall()

    min_stop_id = all_stops[0][0]
    min_dis = distance_finder(location, (all_stops[0][2], all_stops[0][3]))

    for i in all_stops:
        cur_dis = distance_finder(location, (i[2], i[3]))
        if cur_dis < min_dis:
            min_dis = cur_dis
            min_stop_id = i[0]

    return min_stop_id


def print_address(address):
    """
    print_address prints the address of the location
    found from the geocoder library
    """
    print("\nLocation Address: " + address.address)
    print("\nLatitude: ", address.latitude, "")
    print("Longitude: ", address.longitude)


def get_location_1():
    """
    get_location_1 is the first option for the user to find a specific location.
    The function asks for a general location name and will find 2 locations. 
    The first location is just exactly what the user inputs into the function, 
    the second location is the user input with "Toronto" concatenated to the end.
    If the none of the locations are found, the function prints "Location is not found",
    if none of the locations are withing the boundaries of Toronto, the function
    prints "Location is not in Toronto". If only one of the locations is defined in
    Toronto, the function defaults to that location. If both locations are defined
    in Toronto, the user is asked to pick one of the two locations.
    
    Once a location has been decided on, the function finds the bus stop closest to the
    location that was chosen and asks the user if it is the station that they are at.
    If yes, the stop_id is returned, if not, the function lists out all of the stops
    within 200 meters of the original stop and asks the user if they are at any of the
    listed stops. If yes, the selected stop_id is returned, if not, the user is redirected
    back to the 3 options
    """
    # Geopy preloading
    loc = Nominatim(user_agent="GetLoc")
    # Max and min coordinates defining Toronto Boundaries
    max_lat = 43.909707
    max_lon = -79.123111
    min_lat = 43.591811
    min_lon = -79.649908

    origin = input("Enter the location (Example: Yonge St, Zoo, 382 Yonge St, etc...): ")
    # entering the location name
    getLoc_no_toronto = loc.geocode(origin)
    getLoc_toronto = loc.geocode(origin + " Toronto")

    if getLoc_toronto is None and getLoc_no_toronto is None:
        print("\nLocation is not found!\n")
        return False
    elif getLoc_toronto is None:
        within_bound_no_toronto = min_lat <= getLoc_no_toronto.latitude <= max_lat and min_lon <= \
                                  getLoc_no_toronto.longitude <= max_lon
        if within_bound_no_toronto == True:
            print_address(getLoc_no_toronto)
            origin_coords = (getLoc_no_toronto.latitude, getLoc_no_toronto.longitude)
        else:
            print("\nLocation is not in Toronto!\n")
            return False
    elif getLoc_no_toronto is None:
        within_bound_toronto = min_lat <= getLoc_toronto.latitude <= max_lat and min_lon <= \
                               getLoc_toronto.longitude <= max_lon
        if within_bound_toronto == True:
            print_address(getLoc_toronto)
            origin_coords = (getLoc_toronto.latitude, getLoc_toronto.longitude)
        else:
            print("\nLocation is not in Toronto!\n")
            return False
    elif getLoc_toronto != None and getLoc_no_toronto != None:
        within_bound_no_toronto = min_lat <= getLoc_no_toronto.latitude <= max_lat and min_lon <= \
                                  getLoc_no_toronto.longitude <= max_lon
        within_bound_toronto = min_lat <= getLoc_toronto.latitude <= max_lat and min_lon <= \
                               getLoc_toronto.longitude <= max_lon
        if getLoc_toronto.address == getLoc_no_toronto.address:
            if within_bound_no_toronto and within_bound_toronto:
                # printing address
                print_address(getLoc_no_toronto)
                origin_coords = (getLoc_no_toronto.latitude, getLoc_no_toronto.longitude)
            else:
                print("\nLocation is not in Toronto!\n")
                return False
                # print("Ok, you will be leaving from: " + getLoc_no_toronto.address)
        else:
            if within_bound_no_toronto and within_bound_toronto:
                print("\nWe have gotten two different locations based on your inputs, "
                      "\nPlease select the one you are at: \n")

                print("(1) " + getLoc_no_toronto.address)
                print("(2) " + getLoc_toronto.address)

                is_Valid = False
                while is_Valid == False:
                    correct_location = input("\nEnter 1 or 2 to select: ")
                    if correct_location == "1" or correct_location == "2":
                        is_Valid = True
                    else:
                        os.system(clearTermial)
                        print("\nPlease enter either 1 or 2\n")
                        print("(1) " + getLoc_no_toronto.address)
                        print("(2) " + getLoc_toronto.address)

                if int(correct_location) == 1:
                    print(getLoc_no_toronto)
                    origin_coords = (getLoc_no_toronto.latitude, getLoc_no_toronto.longitude)
                elif int(correct_location) == 2:
                    print_address(getLoc_toronto)
                    origin_coords = (getLoc_toronto.latitude, getLoc_toronto.longitude)
            elif within_bound_toronto and within_bound_no_toronto == False:
                print_address(getLoc_toronto)
                origin_coords = (getLoc_toronto.latitude, getLoc_toronto.longitude)
            elif within_bound_toronto == False and within_bound_no_toronto:
                print(getLoc_no_toronto)
                origin_coords = (getLoc_no_toronto.latitude, getLoc_no_toronto.longitude)
            elif within_bound_toronto == False and within_bound_no_toronto == False:
                print("\nLocation is not in Toronto!\n")
                return False
    return origin_coords


def get_location_2():
    """
    get_location_2 is the second option for the user to find a specific location.
    The user is asked to enter the exact name from the TTC website and then function
    converts all of the characters to uppercase and checks the data base for a matching name.
    If nothing is found, the user is redirected to the three options, if the stop is found,
    the stop_id is returned.
    """
    specific_stop = input("Enter the specific stop name (ones found in the TTC website): ")

    s.execute("SELECT * FROM stops WHERE stop_name=:stop_name", {'stop_name': specific_stop.upper()})
    stop = s.fetchall()

    if len(stop) != 0:
        return (stop[0][2], stop[0][3])
    else:
        # Clear terminal
        os.system(clearTermial)
        print("\nStop does not exist in database\n")
        return False


def is_number(string):
    """
    Is numeric alternative for float numbers

    :param string:
    :return: True or False
    """

    try:
        float(string)
        return True
    except ValueError:
        return False


def get_location_3():
    """
    get_location_3 is the third option for the user to find a specific location.
    The function asks the user to input a set of coordinates (lat,lon) and
    checks if the coordinates are within the boundaries of Toronto. If yes, the
    function finds the bus stop that is closest to the coordinates and returns 
    the stop_id, if not, the user is redirected back to the three options.
    """
    # Max and min coordinates defining Toronto Boundaries
    max_lat = 43.909707
    max_lon = -79.123111
    min_lat = 43.591811
    min_lon = -79.649908
    valid_input = False

    while not valid_input:
        coords = input("Enter coordinate values in this format --- lat, lon: ").replace(" ", "")

        if "," in coords:

            x, y = coords.split(',')[0], coords.split(',')[1]

            if is_number(x) and is_number(y):
                if min_lat <= float(x) <= max_lat and min_lon <= float(y) <= max_lon:
                    return tuple(float(i) for i in coords.split(','))
                else:
                    # Clear terminal
                    os.system(clearTermial)
                    print("\nCoordinates are not in Toronto\n")
                    return False
            else:
                # Clear terminal
                os.system(clearTermial)
                print("Please enter numeric values\n")
        else:
            print("Please enter the coordinates in the correct format\n")


def get_location(str):
    """
    get_location displays the three options the user has to pick a specific location.
    This function will call the corredsponding functions based on what the user
    selects. Refer to the documentation above for the explanation for each method.
    
    str: a string to make this function more dynamic and output a different instruction
    based on the input
    """
    input_valid = False
    while not input_valid:
        print(str)
        input_method = input("Your input methods are: \n"
                             "(1) Address/General Location (Example: Yonge St, Zoo, 382 Yonge St, etc...)\n"
                             "(2) Exact Stop Names from TTC Website\n"
                             "(3) (Latitude, Longitude)\n\nEnter 1, 2 or 3 to select: ")
        if input_method == '1' or input_method == '2' or input_method == '3':
            input_valid = True
        else:
            # Clear terminal
            os.system(clearTermial)
            print("Please enter 1, 2, or 3\n")

    if int(input_method) == 1:
        # Clear terminal
        os.system(clearTermial)
        origin_coords = get_location_1()
    elif int(input_method) == 2:
        # Clear terminal
        os.system(clearTermial)
        origin_coords = get_location_2()
    elif int(input_method) == 3:
        # Clear terminal
        os.system(clearTermial)
        origin_coords = get_location_3()
    return origin_coords


def call_get_location(msg1, msg2, msg3):
    """
    call_get_location does the error checking for the get_location function.
    If False is returned from any of the methods, the three methods are presented
    to user to try again. The function also asks the user if the stop chosen by
    the code is the corret one. If not then the function lists all of the stops
    within 200 meters of the original stop and asks the user to pick the one they are
    at. If they choose one, the stop_id of the chosen stop is given, if they do not, then
    they are redirected to the three methods again.
    
    If a stop id is finally chosen, the information about the stop is returned to
    the calling function
    
    msg1 msg2 msg3: are dynamic variables used to customise the function call to the
    purpose it is used for.
    """
    correct_stop = False
    while correct_stop == False:
        origin_coords = get_location(msg1)
        is_Valid = False
        while is_Valid == False:
            if origin_coords != False:
                is_Valid = True
            else:
                origin_coords = get_location(msg1)

        stop = find_closest_stop(origin_coords)
        s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': stop})
        stop_name = s.fetchall()
        print("\n" + str(stop_name[0][1]) + " --- StopID: " + str(stop_name[0][0]) + "\n")
        valid = False
        while valid == False:
            correct = input(msg2)
            if correct.upper() == "Y" or correct.upper() == "N":
                valid = True
            else:
                os.system(clearTermial)
                print("Please enter Y or N")
                print("\n" + str(stop_name[0][1]) + " --- StopID: " + str(stop_name[0][0]) + "\n")
        if correct.upper() == "Y":
            correct_stop = True
            return stop_name[0][0]
        elif correct.upper() == "N":
            near_stops = nearby_stops(stop_name[0][0])
            if len(near_stops) == 0:
                os.system(clearTermial)
                print("Try a different method\n")
            else:
                valid_Input = False
                while valid_Input == False:
                    print(msg3)
                    options = []
                    j = 1
                    for i in near_stops:
                        s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': i})
                        near_stop = s.fetchall()
                        print("(" + str(j) + ") " + str(near_stop[0][1]) + " --- StopID: " + str(near_stop[0][0]))
                        options.append(str(j))
                        j += 1
                    print("(" + str(j) + ") None of these")
                    options.append(str(j))
                    near_input = input("\nEnter your input: ")
                    if near_input not in options:
                        os.system(clearTermial)
                        print("Please select one of the options")
                    else:
                        valid_Input = True
                if int(near_input) == len(options):
                    os.system(clearTermial)
                    print("Try a different method\n")
                else:
                    return near_stops[int(near_input) - 1]


def validate_time(msg):
    """
    validate_time takes a string in the form (HH:MM) or HH:MM 
    with any whitespace and converts the hours and minutes into integer form
    
    The hours and minutes are returned in a tuple in the format (hours, minutes)
    """
    validTime = False
    while validTime == False:
        time = input(msg)
        time = time.replace("(", "").replace(")", "").replace(" ", "")
        if len(time) == 5 and ":" in time:
            hours, mins = time.split(":")[0], time.split(":")[1]
            if hours.isnumeric() == False:
                os.system(clearTermial)
                print("Hours must be numeric\n")
            elif 0 > int(hours) or int(hours) > 23:
                os.system(clearTermial)
                print("Hours must be between 0 and 23\n")
            elif mins.isnumeric() == False:
                os.system(clearTermial)
                print("Hours must be numeric\n")
            elif 0 > int(mins) or int(mins) > 59:
                os.system(clearTermial)
                print("Minutes must be between 0 and 59\n")
            else:
                validTime = True
        else:
            os.system(clearTermial)
            print("Please write in format (HH:MM)\n")
    return (int(hours), int(mins))


def get_start_time(str):
    """
    get_start_time gets the starting trip time from the user. 
    The user is given two options: either use the current time of their machine
    or enter a specific time. When using the second option, the input is error
    checked using the validate_time function. 
    
    get_start_time returns a tuple of the format (hours,minutes)
    """
    print(str)
    validInput = False
    while validInput == False:
        timeinput = input("(1) Current Time\n(2) Specific Time\n\nEnter 1 or 2 to select: ")
        os.system(clearTermial)
        if timeinput == "1" or timeinput == "2":
            validInput = True
        else:
            print("Please enter either 1 or 2\n")
    if timeinput == "1":
        now = datetime.now()
        time = now.strftime("%H:%M")
        hours, mins = time.split(":")[0], time.split(":")[1]
        return (int(hours), int(mins))
    elif timeinput == "2":
        string = "Enter the time you wish to leave by (HH:MM): "
        time = validate_time(string)
    return time


def get_end_time(starting_time, msg, msg1):
    """
    get_end_time gets the time at which the user wishes
    to arrive at their destination. The input is error checked using
    the function validate_time and also error checked to make sure
    that it is after the starting time.
    
    get_end_time returns a tuple of the format (hours, minutes)
    """
    valid_Time = False
    while valid_Time == False:
        ending_time = validate_time(msg1)
        if check_time(starting_time, ending_time):
            valid_Time = True
        else:
            os.system(clearTermial)
            print(msg)
    return ending_time


def check_time(starting, ending):
    """
    check_time checks if the first time comes before the second
    time. If yes, the function returns True, else, the function returns
    False
    """
    print(starting)
    print(ending)
    if starting[0] > ending[0]:
        return False
    if starting[0] == ending[0]:
        if starting[1] >= ending[1]:
            return False
    return True


def get_age():
    """
    get_age gets the user to input their age for the price calculation.
    the input is error checked the make sure that it is a numberical value
    and also an intger.
    
    get_age returns an integer
    """
    valid_Age = False
    while valid_Age == False:
        age = input("Enter your age (for trip price calculation): ")
        if age.isnumeric() == False:
            os.system(clearTermial)
            print("Input must be a number\n")
        elif float(age) % 1 != 0:
            os.system(clearTermial)
            print("Input must be an integer\n")
        else:
            valid_Age = True
    return age


def get_presto():
    """
    get_presto gets the user to input whether or not they own
    a presto card. This is also used in the price calculation.
    
    get_presto returns True or False
    """
    valid_Presto = False
    while valid_Presto == False:
        presto = input("Do you have a presto card? (Y/N): ")
        if presto.upper() == "Y" or presto.upper() == "N":
            valid_Presto = True
        else:
            os.system(clearTermial)
            print("Please enter either Y or N\n")
    if presto.upper() == "Y":
        return True
    elif presto.upper() == "N":
        return False


def get_budget():
    """
    get_budget gets the user to input how much they want to
    spend on their TTC trip. The function accepts any amount of
    whitespace and dollar signs. The input is also error checked
    to make sure it is a numerical value and more than 0.
    
    get_budget returns a float
    """
    valid_Budget = False
    while valid_Budget == False:
        budget = input("Enter your spending budget: ")
        budget = budget.replace("$", "").replace(" ", "")
        if budget.isnumeric() == False:
            os.system(clearTermial)
            print("Budget must be a number\n")
        elif float(budget) <= 0:
            os.system(clearTermial)
            print("Budget must be more than 0\n")
        else:
            valid_Budget = True
    return budget


def get_pref_transit():
    """
    get_pref_transit gets the user's prefferred transit method and returns 
    the corredsponding route_type
    """
    valid_input = False
    while valid_input == False:
        print("What is your preferred transit method?\n1) Bus\n2) Subway\n3) Streetcar\n4) Walking\n5) No Preference\n")
        pref_transit = input("Enter one of the options: ")
        inputs = ['1','2','3','4','5']
        if pref_transit not in inputs:
            os.system(clearTermial)
            print("Please enter one of the options\n")
        else: valid_input = True
    if pref_transit == '1':
        return 3
    elif pref_transit == '2':
        return 1
    elif pref_transit == '3':
        return 0
    elif pref_transit == '4':
        return -1
    elif pref_transit == '5':
        return 5

def get_additional_stops(start_time, end_time):
    """
    Records any extra stops the user wishes to take between
    origin and destination

    :param start_time:
    :param end_time:
    :return: additional_stops
    """

    additional_stops = []
    start_time_var = start_time
    valid_Ans = False
    while valid_Ans == False:
        more_stops = input("Would you like to take any additional stops \nin between your starting "
                           "location and final destination? (Y/N): ")
        if more_stops.upper() == "Y" or more_stops.upper() == "N":
            valid_Ans = True
        else:
            os.system(clearTermial)
            print("Please enter either Y or N\n")
    if more_stops.upper() == "Y":
        more = False
        while more == False:
            stop_message1 = "Let's find your additional stop \n"
            stop_message2 = "Is this the stop want to go to? (Y/N): "
            stop_message3 = "\nAre any of these the stop you are looking for?\n"
            stop_id = call_get_location(stop_message1, stop_message2, stop_message3)
            no_overflow = False
            while no_overflow == False:
                no_exceed_time = False
                while no_exceed_time == False:
                    string = "\nEnter the time you wish to arrive at your stop (HH:MM): "
                    time = get_end_time(start_time_var, "Stop time must be after the previous stop time\n", string)
                    staytime = validate_time("\nHow long do you want to stay at this stop?"
                                             "(HH:MM)(Example: 2 hours and 30 minutes --> (02:30)): ")
                    if check_time(time, end_time) == True:
                        no_exceed_time = True
                    else:
                        os.system(clearTermial)
                        print("Cannot visit stop after ending stop\n")
                minutes = time[1] + staytime[1] + (staytime[0] * 60)
                hours = time[0] + (minutes // 60)
                if hours >= 24:
                    os.system(clearTermial)
                    print("Cannot stay at stop until next day\n")
                else:
                    leave_time = (hours, minutes % 60)
                    if check_time(leave_time, end_time):
                        no_overflow = True
                    else:
                        os.system(clearTermial)
                        print("Cannot stay at stop until after ending stop time\n")
            additional_stops.append((stop_id, (time, leave_time)))
            valid_another = False
            while valid_another == False:
                os.system(clearTermial)
                another = input("\nWould you like to add another stop? (Y/N): ")
                if another.upper() == "Y" or another.upper() == "N":
                    valid_another = True
                else:
                    os.system(clearTermial)
                    print("Please enter either Y or N\n")
            if another.upper() == "N":
                more = True
            else:
                start_time_var = leave_time
    elif more_stops.upper() == "N":
        return additional_stops
    return additional_stops


def nearby_stops(closest_stop):
    """
    Finds all the alternative nearby stops within the 200m range
    to the closest stop found

    :param closest_stop:
    :return: all_nearby_stops
    """
    all_nearby_stops = []

    s.execute("SELECT * FROM stops")
    all_stops = s.fetchall()

    closest_coord = get_stop_id_coord(closest_stop)

    for every_stop in all_stops:
        dis_between_stops = distance_finder(closest_coord, (every_stop[2], every_stop[3]))

        if dis_between_stops <= 0.200 and every_stop[0] != closest_stop:
            all_nearby_stops.append(every_stop[0])

    return all_nearby_stops


def route_within_rh(start_time, end_time):
    """
    Gets the start and ending time of a route
    and checks if the times falls within the predefined
    rush hour period...

    (7am - 10am) & (4pm - 7pm)
    (07:00 - 10:00) & (16:00 - 19:00)

    :param start_time:
    :param end_time:
    :return: within_rh - Boolean - returns true if the route time given
                                    falls within the rush hour periods
    """

    within_rh = False

    start_time_int = start_time.split[":"][0]
    end_time_int = end_time.split[":"][0]

    if (7 < start_time_int < 10) or (16 < end_time_int < 19):
        within_rh = True

    return within_rh


def get_input():
    """
    Get initial user input.

    User will input their starting location, desired ending location,
    current time, desired arrival time, travel budget, age, extra
    visiting locations.

    :return:
    origin_coords - tuple - starting location coordinates (lon, lat)

    destination - string - final destination
    time_now - string - current time (system time)
    arrival_time - string - time the user wishes to arrive at

    age - int - user age

    additional_stops_list - Python array - array of extra stop
    desired_stops_time - Python array - array of amount time spent at each additional stops

    Note: the lists will still be returned if empty
    """

    # Gets the stop id of the current stop that the user is at
    start_message1 = "Welcome to the Toronto TTC Trip Planner, let's start by entering your starting stop \n"
    start_message2 = "Is this the stop you are currently at? (Y/N): "
    start_message3 = "\nAre any of these the stop you are currently at?\n"
    start = call_get_location(start_message1, start_message2, start_message3)

    os.system(clearTermial)
    # Gets the stop id of the destination the user want to go to
    end_message1 = "Now let's find your destination stop \n"
    end_message2 = "Is this the stop want to go to? (Y/N): "
    end_message3 = "\nAre any of these the stop you want to go to?\n"
    destination = call_get_location(end_message1, end_message2, end_message3)

    # Getting current time
    os.system(clearTermial)
    print("Now let's get your trip's starting time\n")
    starting_time = get_start_time("Would you like to use the current time or indicate a specific time?")

    # The time user wants to get to the final destination by

    # user's additional stops shouldn't exceed this time, need a constraint for this
    os.system(clearTermial)
    print("Now let's get your trip's ending time\n")
    string = "Ending time must be after starting time and within the same day\n"
    string2 = "Enter the time you wish to arrive at your destination (HH:MM): "
    ending_time = get_end_time(starting_time, string, string2)

    os.system(clearTermial)
    age = get_age()

    os.system(clearTermial)
    hasPresto = get_presto()

    os.system(clearTermial)
    budget = get_budget()

    # not enough time to implement this feature
    # os.system(clearTermial)
    # additional_stops_list = get_additional_stops(starting_time, ending_time)
    
    os.system(clearTermial)
    pref_transit = get_pref_transit()

    user_input = Input((start, (starting_time, starting_time)), (destination, (ending_time, ending_time)), int(
        age), hasPresto, budget, [], pref_transit)
    return user_input


def print_info(info):
    """
    print_info just prints information for debugging purposes
    """
    os.system(clearTermial)
    print("Starting stop_id: " + str(info.starting_stop.stop_id))
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': info.starting_stop.stop_id})
    starting_point = s.fetchone()
    print("Starting name: " + starting_point[1])
    print("Starting arrive time: " + str(info.starting_stop.arrive_time))
    print("Starting leave time: " + str(info.starting_stop.leave_time))
    print("\n")
    print("Ending stop_id: " + str(info.ending_stop.stop_id))
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': info.ending_stop.stop_id})
    ending_point = s.fetchone()
    print("Ending name: " + ending_point[1])
    print("Ending arrive time: " + str(info.ending_stop.arrive_time))
    print("Ending leave time: " + str(info.ending_stop.leave_time))
    print("\n")
    print("Age: " + str(info.age))
    print("\n")
    print("Has Presto: " + str(info.hasPresto))
    print("\n")
    print("Budget: " + str(info.budget))
    print("\n")
    print("Preferred Transit: " + str(info.pref_transit))
    print("\n")
    for i in info.additional_stops_list:
        print("Additional stop stop_id: " + str(i.stop_id))
        s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': i.stop_id})
        point = s.fetchone()
        print("Additional stop name: " + point[1])
        print("Additional stop arrive time: " + str(i.arrive_time))
        print("Additional stop leave time: " + str(i.leave_time))
        print("\n")
