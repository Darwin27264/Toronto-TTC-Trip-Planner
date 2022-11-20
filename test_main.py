# from bauhaus import Encoding, proposition, constraint
# from bauhaus.utils import count_solutions, likelihood

# Some custom imports including time, SQLite
from datetime import datetime
import sqlite3
import json
import geocoder
import os

# importing geopy library
from geopy.geocoders import Nominatim
from geopy import distance

# Importing database
data = sqlite3.connect('routes.db')
d = data.cursor()

data_trip = sqlite3.connect('trips.db')
t = data_trip.cursor()

data_stop = sqlite3.connect('stops.db')
s = data_stop.cursor()


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
    # printing address
    print("\nLocation Address: " + address.address)

    # printing latitude and longitude
    print("\nLatitude: ", address.latitude, "")
    print("Longitude: ", address.longitude)


def get_location_1():
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
                        os.system('cls')
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
    specific_stop = input("Enter the specific stop name (ones found in the TTC website): ")

    s.execute("SELECT * FROM stops WHERE stop_name=:stop_name", {'stop_name': specific_stop.upper()})
    stop = s.fetchall()

    if len(stop) != 0:
        return (stop[0][2], stop[0][3])
    else:
        # Clear terminal
        os.system('cls')
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
                    os.system('cls')
                    print("\nCoordinates are not in Toronto\n")
                    return False
            else:
                # Clear terminal
                os.system('cls')
                print("Please enter numeric values\n")
        else:
            print("Please enter the coordinates in the correct format\n")


def get_location(str):
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
            os.system('cls')
            print("Please enter 1, 2, or 3\n")

    if int(input_method) == 1:
        # Clear terminal
        os.system('cls')
        origin_coords = get_location_1()
    elif int(input_method) == 2:
        # Clear terminal
        os.system('cls')
        origin_coords = get_location_2()
    elif int(input_method) == 3:
        # Clear terminal
        os.system('cls')
        origin_coords = get_location_3()
    return origin_coords


def call_get_location(msg1, msg2, msg3):
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
                os.system('cls')
                print("Please enter Y or N")
                print("\n" + str(stop_name[0][1]) + " --- StopID: " + str(stop_name[0][0]) + "\n")
        if correct.upper() == "Y":
            correct_stop = True
            return stop_name[0][0]
        elif correct.upper() == "N":
            near_stops = nearby_stops(stop_name[0][0])
            if len(near_stops)==0:
                os.system('cls')
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
                        print("(" + str(j) + ") " +  str(near_stop[0][1]) + " --- StopID: " + str(near_stop[0][0]))
                        options.append(str(j))
                        j += 1
                    print("(" + str(j) + ") None of these")
                    options.append(str(j))
                    near_input = input("\nEnter your input: ")
                    if near_input not in options:
                        os.system('cls')
                        print("Please select one of the options")
                    else:
                        valid_Input = True
                if int(near_input) == len(options):
                    os.system('cls')
                    print("Try a different method\n")
                else:
                    return near_stops[int(near_input)-1]
                        

def validate_time(msg):
    validTime = False
    while validTime == False:
        time = input(msg)
        time = time.replace("(", "").replace(")", "").replace(" ", "")
        if len(time) == 5 and ":" in time:
            hours, mins = time.split(":")[0], time.split(":")[1]
            if hours.isnumeric() == False:
                os.system('cls')
                print("Hours must be numeric\n")
            elif 0 > int(hours) or int(hours) > 23:
                os.system('cls')
                print("Hours must be between 0 and 23\n")
            elif mins.isnumeric() == False:
                os.system('cls')
                print("Hours must be numeric\n")
            elif 0 > int(mins) or int(mins) > 59:
                os.system('cls')
                print("Minutes must be between 0 and 59\n")
            else:
                validTime = True
        else:
            os.system('cls')
            print("Please write in format (HH:MM)\n")
    return (int(hours), int(mins))


def get_start_time(str):
    print(str)
    validInput = False
    while validInput == False:
        timeinput = input("(1) Current Time\n(2) Specific Time\n\nEnter 1 or 2 to select: ")
        os.system('cls')
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
    valid_Time = False
    while valid_Time == False:
        ending_time = validate_time(msg1)
        if check_time_after(starting_time, ending_time):
            valid_Time = True
        else:
            os.system('cls')
            print(msg)
    return ending_time


def check_time_before(starting, ending):
    if starting[0] < ending[0]:
        return False
    if starting[0] == ending[1]:
        if starting[1] <= ending[1]:
            return False
    return True


def check_time_after(starting, ending):
    if starting[0] > ending[0]:
        return False
    if starting[0] == ending[1]:
        if starting[1] >= ending[1]:
            return False
    return True


def get_age():
    valid_Age = False
    while valid_Age == False:
        age = input("Enter your age (for trip price calculation): ")
        if age.isnumeric() == False:
            os.system('cls')
            print("Input must be a number\n")
        elif float(age) % 1 != 0:
            os.system('cls')
            print("Input must be an integer\n")
        else:
            valid_Age = True
    return age


def get_presto():
    valid_Presto = False
    while valid_Presto == False:
        presto = input("Do you have a presto card? (Y/N): ")
        if presto.upper() == "Y" or presto.upper() == "N":
            valid_Presto = True
        else:
            os.system('cls')
            print("Please enter either Y or N\n")
    if presto.upper() == "Y":
        return True
    elif presto.upper() == "N":
        return False


def get_budget():
    valid_Budget = False
    while valid_Budget == False:
        budget = input("Enter your spending budget: ")
        budget = budget.replace("$", "").replace(" ", "")
        if budget.isnumeric() == False:
            os.system('cls')
            print("Budget must be a number\n")
        elif float(budget) <= 0:
            os.system('cls')
            print("Budget must be more than 0\n")
        else:
            valid_Budget = True
    return budget


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
            os.system('cls')
            print("Please enter either Y or N\n")
    if more_stops.upper() == "Y":
        more = False
        while more == False:
            stop_message1 = "Let's find your additional stop \n"
            stop_message2 = "Is this the stop want to go to? (Y/N): "
            stop_message3 = "\nAre any of these the stop you are looking for?\n"
            stop_id = call_get_location(stop_message1, stop_message2, stop_message3)
            string = "Enter the time you wish to arrive at your stop (HH:MM): "
            time = get_end_time(start_time_var, "Stop time must be after the previous stop time\n", string)
            no_overflow = False
            while no_overflow == False:
                no_exceed_time = False
                while no_exceed_time == False:
                    staytime = validate_time("\nHow long do you want to stay at this stop?"
                                                    "(HH:MM)(Example: 2 hours and 30 minutes --> (02:30)): ")
                    if check_time_before(staytime, end_time):
                        no_exceed_time = True
                    else:
                        os.system('cls')
                        print("Cannot visit stop after ending stop\n")
                minutes = time[1] + staytime[1]
                hours = time[0] + (minutes // 60)
                if hours >= 24:
                    os.system('cls')
                    print("Cannot stay at stop until next day\n")
                else:
                    leave_time = (hours, minutes % 60)
                    if check_time_before(leave_time, end_time):
                        no_overflow = True
                    else:
                        os.system('cls')
                        print("Cannot stay at stop until after ending stop time\n")
            additional_stops.append(stop_id, (time, leave_time))
            valid_another = False
            while valid_another == False:
                another = input("\nWould you like to add another stop? (Y/N): ")
                if another.upper() == "Y" or another.upper() == "N":
                    valid_another = True
                else:
                    os.system('cls')
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

        if dis_between_stops <= 0.200 and every_stop[0]!=closest_stop:
            all_nearby_stops.append(every_stop[0])

    return all_nearby_stops


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

    os.system('cls')
    # Gets the stop id of the destination the user want to go to
    end_message1 = "Now let's find your destination stop \n"
    end_message2 = "Is this the stop want to go to? (Y/N): "
    end_message3 = "\nAre any of these the stop you want to go to?\n"
    destination = call_get_location(end_message1, end_message2, end_message3)

    # Getting current time
    os.system('cls')
    print("Now let's get your trip's starting time\n")
    starting_time = get_start_time("Would you like to use the current time or indicate a specific time?")

    # The time user wants to get to the final destination by

    # user's additional stops shouldn't exceed this time, need a constraint for this
    os.system('cls')
    print("Now let's get your trip's ending time\n")
    string = "Ending time must be after starting time and within the same day\n"
    string2 = "Enter the time you wish to arrive at your destination (HH:MM): "
    ending_time = get_end_time(starting_time, string, string2)

    os.system('cls')
    age = get_age()

    os.system('cls')
    hasPresto = get_presto()

    os.system('cls')
    budget = get_budget()

    os.system('cls')
    additional_stops_list = get_additional_stops(starting_time, ending_time)

    return (start, (starting_time, starting_time)), (destination, (ending_time, ending_time)), int(
        age), hasPresto, budget, additional_stops_list


# Clear terminal
os.system('cls')
test_array = get_input()
os.system('cls')
s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': test_array[0][0]})
starting_point = s.fetchone()
print("Starting Point: " + str(starting_point[1]) + " --- StopID: " + str(starting_point[0]) + " --- Time(Hours,Minutes): " + str(test_array[0][1]))
s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': test_array[1][0]})
ending_point = s.fetchone()
print("Ending Point: " + str(ending_point[1]) + " --- StopID: " + str(ending_point[0]) + " --- Time(Hours,Minutes): " + str(test_array[1][1]))
print("Age: " + str(test_array[2]))
print("Has Presto: " + str(test_array[3]))
print("Budget: " + str(test_array[4]))
for i in test_array[5]:
    s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': i[0]})
    stop = s.fetchone()
    print("Additional Stop: " + str(stop[1]) + " --- StopID: " + str(stop[0]) + " --- Time(Hours,Minutes): " + str(i[1]))

#print(nearby_stops(467))
# print(test_array[0])
# print(distance_finder((43.6950093, -79.3959279), (43.909707, -79.123111)))
# starting_stop = find_closest_stop(test_array[0])
# s.execute("SELECT * FROM stops WHERE stop_id=:stop_id", {'stop_id': starting_stop})
# starting_stop_name = s.fetchall()
# print(str(starting_stop_name[0][0])+ " " + str(starting_stop_name[0][1]) + " " + str(starting_stop_name[0][2]) + "," +str(starting_stop_name[0][3]))
