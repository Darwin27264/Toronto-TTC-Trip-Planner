from stop_Info import Stops_Info


class Input:
    def __init__(self, starting_stop, ending_stop, age, hasPresto, budget, additional_stops_list, pref_transit):
        self.starting_stop = Stops_Info(starting_stop[0], starting_stop[1][0], starting_stop[1][1])
        self.ending_stop = Stops_Info(ending_stop[0], ending_stop[1][0], ending_stop[1][1])
        self.age = age
        self.hasPresto = hasPresto
        self.budget = budget
        self.pref_transit = pref_transit
        stops_list = []
        for i in additional_stops_list:
            stops_list.append(Stops_Info(i[0], i[1][0], i[1][1]))
        self.additional_stops_list = stops_list;
