#!/usr/bin/env python3


'''
Wrapper to construct a TSP solution using OR-Tools package for a given complete graph
'''

import networkx as nx
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

class TSP_OR:

    def __init__(self, graph, start_node):
        self.graph = graph.copy()
        self.nodes = list(graph.nodes())


        self.num_vehicles = 1
        self.depot = self.nodes.index(start_node)

        self.manager = pywrapcp.RoutingIndexManager(len(self.nodes), self.num_vehicles, self.depot)
        self.routing = pywrapcp.RoutingModel(self.manager)
        self.transit_callback_index = self.routing.RegisterTransitCallback(self.distance_callback)
        self.routing.SetArcCostEvaluatorOfAllVehicles(self.transit_callback_index)
        # self.solve_for_tsp()


        # if self.solution:
        #     self.print_solution()


    def output_solution(self):
        index = self.routing.Start(0)
        plan_output = []
        route_distance = 0
        while not self.routing.IsEnd(index):
            plan_output.append(self.nodes[self.manager.IndexToNode(index)])
            previous_index = index
            index = self.solution.Value(self.routing.NextVar(index))
            route_distance += self.routing.GetArcCostForVehicle(previous_index, index, 0)
        plan_output.append(self.nodes[self.manager.IndexToNode(index)])

        return (plan_output, route_distance)
# 
    def print_solution(self):
    # """Prints solution on console."""
        print('Objective: {}'.format(self.solution.ObjectiveValue()))
        index = self.routing.Start(0)
        plan_output = 'Route:\n'
        route_distance = 0
        while not self.routing.IsEnd(index):
            plan_output += ' {} ->'.format(self.nodes[self.manager.IndexToNode(index)])
            previous_index = index
            index = self.solution.Value(self.routing.NextVar(index))
            route_distance += self.routing.GetArcCostForVehicle(previous_index, index, 0)
        plan_output += ' {}\n'.format(self.nodes[self.manager.IndexToNode(index)])
        plan_output += 'Objective: {}m\n'.format(route_distance)
        print(plan_output)

    def distance_callback(self, from_index, to_index):
        from_node = self.manager.IndexToNode(from_index)
        to_node = self.manager.IndexToNode(to_index)
        # print(self.graph[self.nodes[from_node]][self.nodes[to_node]]['length'])
        return self.graph[self.nodes[from_node]][self.nodes[to_node]]['length']
    
    def solve_for_tsp(self):
        self.search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        self.search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)
        self.search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        self.search_parameters.time_limit.seconds = 3
        self.solution = self.routing.SolveWithParameters(self.search_parameters)
        # print('Status', self.routing.status())


