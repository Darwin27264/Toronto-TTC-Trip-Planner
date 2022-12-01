from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import likelihood

# Encoding that will store all of your constraints
T = Encoding()


# Class for Time propositions
@proposition(T)
class time_prop:
    # instantiate with name to be given to the proposition
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"T.{self.data}"


# Time
rush_hour = time_prop('rush hour (>70% of trip within rush hours detected)')
valid_start_time = time_prop('valid start time (bus)')
valid_end_time = time_prop('valid end time (bus)')
more_than_fifty_strtcar_bus = time_prop('more than 50% busses or street cars within trip')

within_time_cons = time_prop('within time constraint')


def time_to_int(time_str):
    """
    Feed in 'xx:yy:zz' to get xxyy

    :param time_str:
    :return: int - time in xxyy format
    """

    time_parts_str = time_str.split(":")
    hr_min = (time_parts_str[0] + time_parts_str[1])

    return int(hr_min)


def rh_factor_calc(single_trip):
    """
    Calculates the amount, in percentage, of the routes with transit type
    street car or busses to see if it could be valid is rush hour is true.

    --- Transit Types Classifier ---
    0 - streetcar
    1 - subway
    3 - bus
    -1 - walking (200m)

    --- Rush Hour Periods ---
    7am - 10am OR 7:00 - 10:00
    4pm - 7pm OR 16:00 - 19:00

    :return:
    percent - int - percentage of street cars and busses within a trip
    """

    # Calculate the percentage of trip transit types that are slow during rush hour
    transit_types = []
    times = []

    # Morning rush hour period
    m_rush_hour_st = 700
    m_rush_hour_ed = 1000
    # Evening rush hour period
    e_rush_hour_st = 1600
    e_rush_hour_ed = 1900

    rush_hour_counter = 0

    # Only is taken into consideration if the total steps in
    # the trip has more than 3 steps
    if len(single_trip) <= 3:

        for every_step in single_trip:
            times.append(every_step[1])

        trip_start_time = time_to_int(times[0][0])
        trip_end_time = time_to_int(times[-1][1])

        return (trip_start_time, trip_end_time, 0, 0)
    else:
        for every_step in single_trip:
            transit_types.append(every_step[0][-1])
            times.append(every_step[1])

        sum_of_slow_transit_type = transit_types.count(0) + transit_types.count(3)
        total_slow_transit_type = (sum_of_slow_transit_type / len(transit_types)) * 100

        # Calculate the amount of trip that happens within rush hour
        for i in times:
            # i is in [(start_time, end_time)] format
            j = i[0]
            # j is in (start_time, end_time) format
            t_s = time_to_int(j[0])
            t_e = time_to_int(j[1])

            if m_rush_hour_st <= t_s <= m_rush_hour_ed or e_rush_hour_st <= t_s <= e_rush_hour_ed:
                rush_hour_counter += 1
            elif m_rush_hour_st <= t_e <= m_rush_hour_ed or e_rush_hour_st <= t_e <= e_rush_hour_ed:
                rush_hour_counter += 1

        total_rh_percentage = (rush_hour_counter / len(times)) * 100

        print(times)

        trip_start_time = time_to_int(times[0][0][0])
        trip_end_time = time_to_int(times[-1][0][1])

    return (trip_start_time, trip_end_time, int(total_slow_transit_type), int(total_rh_percentage))


def time_theory(user_departure_time, user_arrival_time):
    # Compare the user defined time with the algorithm given time
    # should already be in int time format
    user_st_time = user_departure_time
    user_ed_time = user_arrival_time

    trip_data = rh_factor_calc(sample_trip)
    # Trip start and end times
    given_st = trip_data[0]
    given_ed = trip_data[1]
    # Trip transit type and rush hour related data
    rush_hour_percent = trip_data[2]
    slow_during_rh_percent = trip_data[3]

    # Valid if the trips first bus departure time is after user's desired departure time
    if given_st > user_st_time:
        T.add_constraint(valid_start_time)

    # Valid if the trips last bus arrival time is before user's desired end time
    if given_ed < user_ed_time:
        T.add_constraint(valid_end_time)

    # If 60% of the trip is within rush hour periods
    if rush_hour_percent >= 60:
        T.add_constraint(rush_hour)

    # If 50% of the transit types are slow during rush hours
    if slow_during_rh_percent >= 50:
        T.add_constraint(more_than_fifty_strtcar_bus)

    # Rush hour implies there can't be more than 50% slow transit types within the trip
    T.add_constraint(~rush_hour | ~more_than_fifty_strtcar_bus)
    T.add_constraint(
        ~((valid_start_time & valid_end_time) & rush_hour & ~more_than_fifty_strtcar_bus) | within_time_cons)


sample_trip = [((4049, 574, 'close_to_close', 61367, 3), [('7:51:08', '9:40:10')]),
               ((4049, 574, 'close_to_close', 61367, 3), [('9:51:08', '10:40:10')]),
               ((4049, 574, 'close_to_close', 61367, 1), [('10:51:08', '11:40:10')]),
               ((4049, 574, 'close_to_close', 61367, 0), [('11:51:08', '12:40:10')]),
               ((4049, 574, 'close_to_close', 61367, -1), [('12:51:08', '13:40:10')]),
               ((4049, 574, 'close_to_close', 61367, -1), [('13:51:08', '14:40:10')]),
               ((4049, 574, 'close_to_close', 61367, 0), [('13:51:08', '14:40:10')]),
               ((4049, 574, 'close_to_close', 61367, 3), [('13:51:08', '14:40:10')])]

print(rh_factor_calc(sample_trip))
