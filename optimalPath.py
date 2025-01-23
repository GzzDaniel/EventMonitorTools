from tableparser import GetDict, roomdict
from math import modf
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from prettytable import PrettyTable

UconnTMatrix = [
    # ditance matrix of the uconn building that an event monitos has to visit regularly. The integers are time in minutes.
                [0, 9, 9, 3, 3, 8, 9, 4, 3, 4, 8, 5, 8, 8, 15, 13],             # Student union
                [10, 0, 9, 8, 9, 10, 4, 8, 6, 7, 2, 5, 2, 13, 11, 6],           # Arjona
                [9, 8, 0, 10, 6, 3, 5, 4, 8, 8, 7, 7, 7, 7, 6, 10],             # Austin
                [3, 7, 10, 0, 5, 10, 8, 6, 2, 3, 7, 5, 7, 10, 15, 12],          # Business
                [3, 9, 6, 6, 0, 6, 8, 1, 4, 4, 8, 6, 8, 5, 12, 13],             # Castleman
                [9, 10, 3, 11, 6, 0, 7, 4, 8, 8, 9, 7, 9, 4, 9, 12],            # Chemistry
                [9, 4, 6, 9, 8, 7, 0, 7, 6, 6, 3, 4, 3, 12, 8, 6],              # family Studies
                [5, 8, 5, 7, 2, 4, 7, 0, 4, 4, 7, 4, 7, 5, 11, 12],             # Gentry
                [3, 6, 8, 3, 3, 8, 6, 4, 0, 1, 5, 2, 5, 8, 13, 10],             # ITE
                [4, 6, 8, 3, 4, 7, 6, 3, 1, 0, 5, 2, 5, 8, 13, 10],             # Mchugh
                [9, 2, 7, 8, 8, 9, 3, 7, 5, 6, 0, 4, 1, 12, 11, 6],             # Montheith
                [5, 4, 7, 5, 5, 7, 4, 4, 2, 2, 3, 0, 3, 9, 11, 8],              # Oak / Herbst
                [8, 2, 7, 8, 8, 9, 3, 7, 5, 5, 0, 3, 0, 12, 11, 6],             # Schenker
                [8, 13, 8, 11, 5, 4, 11, 6, 9, 9, 13, 10, 12, 0, 12, 17],       #Torrey
                [16, 11, 7, 16, 12, 9, 9, 11, 13, 13, 12, 12, 12, 12, 0, 11],   # Young
                [14, 6, 10, 13, 14, 12, 6, 12, 11, 11, 6, 9, 6, 17, 11, 0]      # Shipee
                ]

buildingList = list(roomdict.keys())
# ____________ FUNCTIONS _______________

def num2text(num):
    '''from 17.58 -> 5:32 PM'''
    time = "AM"
    if num > 12:
        num -= 12
        time = "PM"
    
    min, hour = modf(num)
    
    return f"{int(hour)}:{int(min*60):02} {time}"
    
# ____________ FINDING OPTIMAL PATH  _______________

def create_data_model(bookingsDict):    
    data = {}
    data["buildings"] = ['Student Union Uconn'] + bookingsDict["building"]
    data["time_matrix"] = []
    
    blgamount = len( data["buildings"])
    for i in range(blgamount):
        building1 = data["buildings"][i]
        sublist = []
        for j in range(len(data["buildings"])):
            building2 = data["buildings"][j]
            sublist.append(UconnTMatrix[buildingList.index(building1)][buildingList.index(building2)])
            #print(sublist)
        data["time_matrix"].append(sublist)
    
    data["time_windows"] = [(0,400)] + bookingsDict['timeWindow']
    data["num_vehicles"] = 2
    data["depot"] = 0
    data["room"] = ['SU'] + bookingsDict["room"]
    data['stStr'] = ["5:30 PM"] + bookingsDict['stStr']
    data['etStr'] = ["-------"] + bookingsDict['etStr']
    
    return data

def print_solution(data, manager, routing, solution):
    """Prints solution on console. Example code from Google Ortools Guide  https://developers.google.com/optimization/routing/vrptw"""
    print(f"Objective: {solution.ObjectiveValue()}")
    time_dimension = routing.GetDimensionOrDie("Time")
    total_time = 0
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            plan_output += (
                f"{manager.IndexToNode(index)}"
                f" Time({solution.Min(time_var)},{solution.Max(time_var)})"
                " -> "
            )
            index = solution.Value(routing.NextVar(index))
        time_var = time_dimension.CumulVar(index)
        plan_output += (
            f"{manager.IndexToNode(index)}"
            f" Time({solution.Min(time_var)},{solution.Max(time_var)})\n"
        )
        plan_output += f"Time of the route: {solution.Min(time_var)}min\n"
        print(plan_output)
        total_time += solution.Min(time_var)
    print(f"Total time of all routes: {total_time}min")
    
    
def myprintsolution(data, manager, routing, solution, vehicule, waitingtime):
    """ replaces the example code from Google. Prints a table similar to the the one in tableparser.py with the meetings in an optimal order """
    index = routing.Start(vehicule)
    time_dimension = routing.GetDimensionOrDie("Time")
    
    table = PrettyTable(["Srt Time", "End Time", "Room", "Time Window"])
    table.title = "Suggested Route"
    while not routing.IsEnd(index):
        time_var = time_dimension.CumulVar(index)
        i = manager.IndexToNode(index)
        timewindow = f"({num2text((solution.Min(time_var)+1050)/60)} - {num2text((solution.Max(time_var)+1050)/60)})"
        table.add_row((data['stStr'][i], data['etStr'][i], data['room'][i], timewindow))  
        
        index = solution.Value(routing.NextVar(index))
        
    print(table) 
    print("Max waiting time: ", waitingtime)
    

def main(bookingsDict):
    """Solve the VRP with time windows. Example code from Google Ortools Guide  https://developers.google.com/optimization/routing/vrptw """
    # Instantiate the data problem.
    data = create_data_model(bookingsDict)
    waitingtime = 4
    while(waitingtime < 30):
        #print(waitingtime)
        
        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(
            len(data["time_matrix"]), data["num_vehicles"], data["depot"]
        )
        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback.
        def time_callback(from_index, to_index):
            """Returns the travel time between the two nodes."""
            # Convert from routing variable Index to time matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["time_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(time_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Time Windows constraint.
    
        time = "Time"
        routing.AddDimension(
            transit_callback_index,
            waitingtime,  # allow waiting time
            300,  # maximum time per vehicle
            True,  # Don't force start cumul to zero.
            time,
        )
        
        time_dimension = routing.GetDimensionOrDie(time)
        # Add time window constraints for each location except depot.
        for location_idx, time_window in enumerate(data["time_windows"]):
            if location_idx == data["depot"]:
                continue
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        # Add time window constraints for each vehicle start node.
        depot_idx = data["depot"]
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(
                data["time_windows"][depot_idx][0], data["time_windows"][depot_idx][1]
            )

        # Instantiate route start and end times to produce feasible times.
        for i in range(data["num_vehicles"]):
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.Start(i))
            )
            routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

        # Solve the problem.
        #search_parameters.log_search = True
        solution = routing.SolveWithParameters(search_parameters)

        # Print solution on console.
        if solution:
            #print("solution found")
            manager.IndexToNode(routing.Start(0))
            manager.IndexToNode(solution.Value(routing.NextVar(routing.Start(0))))
            isempty0 = (manager.IndexToNode(routing.Start(0)) == manager.IndexToNode(solution.Value(routing.NextVar(routing.Start(0)))))
            isempty1 = (manager.IndexToNode(routing.Start(0)) == manager.IndexToNode(solution.Value(routing.NextVar(routing.Start(1)))))
            if isempty0:
                myprintsolution(data, manager, routing, solution, 1, waitingtime)
                return
            elif isempty1:
                #print_solution(data, manager, routing, solution)
                myprintsolution(data, manager, routing, solution, 0, waitingtime)
                return
        else:
            # is no solution was found, try and find a new solution using extra waiting time
            waitingtime += 1
        


if __name__ == "__main__":
    # The definition for the optimal path is yet to be decided. my definition, is the path where you walk the least, as this code was 
    # made for a friend I used his definition where the optimal path was where the optimal path is the one with the least waiting time
    
    # get the bookings data in a python dictionary, if offline, the script will use the previously downloaded html page for testing purposes
    bookingsDict = GetDict(offline=True, moredata=False, st = 17, printTable=True)
    
    # using PyInstaller crashes when trying to use the ortools library
    makeSuggested = input("Do you wish to get a suggested route? [this might crash the program] (Y/N)")

    if makeSuggested.lower() == "y" or makeSuggested.lower() == "yes":   
        # run the route optimization script using the Dictionary from the previous script
        main(bookingsDict)
    
    while True:
        print("press q and enter to quit")
        if input() == 'q':
            break
   