#!/usr/bin/env python3

'''
The script implements a 2 factor approximation for Min-Time Period for single agent case

Inputs
1. Graph (Strongly Connected)
2. Priority Nodes

Outputs
1. Lower Bound on Time Period
2. Time Period Corresponding to the patrol strategy
3. Patrol Strategy
4. Length of the patrol strategy
'''

import sys
import networkx as nx
import random as rn
import math
from tsp_or_tools import TSP_OR
import csv


class TSP_CONCAT:

    def __init__(self, graph, graph_name, priority_nodes):

        self.graph_name = graph_name
        self.priority_nodes = priority_nodes  
        self.num_prior = len(self.priority_nodes)
        self.graph_original = graph
        for e in self.graph_original.edges():
            self.graph_original[e[0]][e[1]]['length'] = int(self.graph_original[e[0]][e[1]]['length'])
        self.graph_complete = self.graph_original.copy()
        self.nodes = list(self.graph_original.nodes())
        self.paths = {}
        self.dist_from_pn = {}
        self.dist_to_pn = {}
        self.remaining_nodes = self.nodes.copy()
        self.lower_bound = 0
        self.time_period = 0
        self.upper_bound = math.inf
        for n in self.priority_nodes:
            self.remaining_nodes.remove(n)
            self.dist_to_pn[n] = {}
            self.dist_from_pn[n] = {}
        # print('1')
        paths = dict(nx.all_pairs_dijkstra_path(self.graph_original, weight = 'length'))
        # print('2')
        for i in self.nodes:
            f = False
            if i in self.priority_nodes:
                f = True
            for j in self.nodes:
                t = False
                if j in self.priority_nodes:
                    t = True
                # if i == j and not (i, j) in self.graph_complete.edges():
                #     self.graph_complete.add_edge(i, j)
                #     self.graph_complete[i][j]['name'] = '{}to{}'.format(i, j)
                #     self.graph_complete[i][j]['length'] = 0
                #     self.paths[(i, j)] = [i, j]
                if i != j and not (i, j) in self.graph_complete.edges():
                    self.graph_complete.add_edge(i, j)
                    self.graph_complete[i][j]['name'] = '{}to{}'.format(i, j)
                    self.graph_complete[i][j]['length'] = 0
                    self.paths[(i, j)] = paths[i][j]
                    for k in range(len(self.paths[i, j]) - 1):
                        self.graph_complete[i][j]['length'] += self.graph_original[paths[i][j][k]][paths[i][j][k + 1]]['length']
                elif i != j:
                    self.paths[(i, j)] = [i, j]
                
                if f:
                    if i == j:
                        self.dist_from_pn[i][j] = 0
                    else:
                        self.dist_from_pn[i][j] = self.graph_complete[i][j]['length']
                if t:
                    if i == j:
                        self.dist_to_pn[j][i] = 0
                    else:
                        self.dist_to_pn[j][i] = self.graph_complete[i][j]['length']


        self.patterns = []
        self.pattern_templates = []

    def get_next_pattern(self):

        next_key = rn.sample(self.remaining_nodes, 1)[0]
        next_nodes = self.priority_nodes.copy()
        next_nodes.append(next_key)
        sub_graph = self.graph_complete.subgraph(next_nodes)

        # print('key - ', next_key)
        
        h = TSP_OR(sub_graph, self.priority_nodes[0])
        h.solve_for_tsp()
        next_data = h.output_solution()

        next_pattern = []
        for n in next_data[0]:
            if n in self.priority_nodes:
                next_pattern.append(n)

        return (next_pattern, next_data[1], next_data[0])

    def create_pattern(self):
        cpd = self.get_next_pattern()
        # print(cpd[2], cpd[1])
        if self.lower_bound < cpd[1]:
            self.lower_bound = cpd[1]
        dist_patterns = 0
        if len(self.patterns) > 1:
            dist_pattern_forward = self.get_pattern_dist(self.patterns[-1].pattern, cpd[0])
            cpd[0].reverse()
            dist_pattern_backward = self.get_pattern_dist(self.patterns[-1].pattern, cpd[0])
            if dist_pattern_backward > dist_pattern_forward:
                dist_patterns = dist_pattern_forward
                cpd[0].reverse()
            else:
                dist_patterns = dist_pattern_backward
        # if dist_patterns > cpd[1]:
            # print ('slack_pos', dist_patterns)
        return (cpd[0], max(dist_patterns, cpd[1]))


    def get_pattern_dist(self, p1, p2):
        dists = {i: 0 for i in self.priority_nodes}
        len1 = 0
        len2 = 0
        for j in range(self.num_prior):
            len1 += self.graph_complete[p1[j]][p1[j + 1]]['length']
            len2 += self.graph_complete[p2[j]][p2[j + 1]]['length']
            dists[p1[j + 1]] -= len1
            dists[p2[j + 1]] += len2

        max_dist = 0
        for j in self.priority_nodes:
            dists[j] += len1
            if dists[j] > max_dist:
                max_dist = dists[j]
        return max_dist


    def populate(self):
        # while len(self.remaining_nodes) > 0:
        # print('nodes remaining - ', len(self.remaining_nodes))
        nd = self.create_pattern()
        # print(self.lower_bound, self.time_period, nd[1])
        if nd[1] >= self.time_period:
            for pattern in self.patterns:
                pattern.update_circuits(nd[1])
                i = 0
                while i < len(self.remaining_nodes):
                    if not self.remaining_nodes[i] in pattern.remaining_nodes:
                        self.remaining_nodes.remove(self.remaining_nodes[i])
                    else:
                        i += 1

        self.time_period = max(nd[1], self.time_period)
        if not nd[0] in self.pattern_templates:
            self.patterns.append(Pattern(nd[0], self.time_period, self))
            self.upper_bound = min(self.patterns[-1].pattern_max, self.upper_bound)
            self.pattern_templates.append(nd[0])
            i = 0
            while i < len(self.remaining_nodes):
                if not self.remaining_nodes[i] in self.patterns[-1].remaining_nodes:
                    self.remaining_nodes.remove(self.remaining_nodes[i])
                else:
                    i += 1



    def solve(self):
        while len(self.remaining_nodes) > 0:
            self.populate()
        print('done')
        # print('lower bound', self.lower_bound)
        # print('time period', self.time_period)
        # print('pattern maximums')

        # for pat in self.patterns:
            # print(pat.pattern_max, len(pat.remaining_nodes))

        
    

    def output(self, file_name, rand_string):
        fields = ['rand_string', 'graph', 'num_priority', 'priority_nodes', 'lower_bound', 'upper_bound', 'time_period', 'num_patterns']
        vals = {}
        vals[fields[0]] = rand_string
        vals[fields[1]] = self.graph_name
        vals[fields[2]] = str(len(self.priority_nodes))
        vals[fields[3]] =(' ').join(self.priority_nodes)
        vals[fields[4]] = str(self.lower_bound)
        vals[fields[5]] = str(self.upper_bound)
        vals[fields[6]] = str(self.time_period)
        vals[fields[7]] = str(len(self.patterns))
        with open(file_name, 'a+') as f:
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writerow(vals)



class Pattern:

    def __init__(self, pattern, max_length, base_class):

        self.pattern = pattern
        # self.max_length = max_length
        self.base_class = base_class
        self.pattern_length = 0
        self.key_nodes = {}
        self.remaining_nodes = base_class.nodes.copy()
        self.remain_temp = self.remaining_nodes.copy()
        for i in range(len(pattern) - 1):
            self.key_nodes[i] = []
            self.pattern_length += base_class.graph_complete[pattern[i]][pattern[i + 1]]['length']
            path = base_class.paths[(pattern[i], pattern[i + 1])]
            for j in path:
                if j in self.remaining_nodes:
                    self.remaining_nodes.remove(j)
                    self.remain_temp.remove(j)
        self.get_pattern_max()
        self.update_circuits(max_length)


    def get_pattern_max(self):
        self.pattern_max = 0
        while len(self.remain_temp) > 0:
            n = self.remain_temp.pop(0)
            len_n = math.inf
            for i in range(len(self.pattern) - 1):
                s1 = self.pattern[i]
                s2 = self.pattern[i + 1]
                temp_n = self.base_class.dist_from_pn[s1][n] + self.base_class.dist_to_pn[s2][n] + self.pattern_length - self.base_class.graph_complete[s1][s2]['length']
                if len_n > temp_n:
                    len_n = temp_n
                    s1_n = s1
                    s2_n = s2
            for k in self.base_class.paths[(s1_n, n)]:
                if k in self.remain_temp:
                    self.remain_temp.remove(k)
            for k in self.base_class.paths[(n, s2_n)]:
                if k in self.remain_temp:
                    self.remain_temp.remove(k)

            if len_n > self.pattern_max:
                self.pattern_max = len_n


    def update_circuits(self, length):
        self.max_length = length
        # s1 = self.pattern[i]
        # s2 = self.pattern[i + 1]
        # slack = self.max_length - self.pattern_length + self.base_class.graph_complete[s1][s2]['length']
        j = 0
        while j < len(self.remaining_nodes):
            n = self.remaining_nodes[j]
            len_n = math.inf
            for i in range(len(self.pattern) - 1):
                s1 = self.pattern[i]
                s2 = self.pattern[i + 1]
                temp_n = self.base_class.dist_from_pn[s1][n] + self.base_class.dist_to_pn[s2][n] + self.pattern_length - self.base_class.graph_complete[s1][s2]['length']
                if len_n > temp_n:
                    len_n = temp_n
                    s1_n = s1
                    s2_n = s2
                    ind = i
            # print(slack, n, self.remaining_nodes)
            if len_n <= self.max_length:
                self.key_nodes[ind].append(n)
                for k in self.base_class.paths[(s1_n, n)]:
                    if k in self.remaining_nodes:
                        self.remaining_nodes.remove(k)
                
                for k in self.base_class.paths[(n, s2_n)]:
                    if k in self.remaining_nodes:
                        self.remaining_nodes.remove(k)
            else:
                j += 1

    # def update_circuits(self, length):
    #     self.max_length = length
    #     for i in range(len(self.pattern) - 1):
    #         self.get_all_i_circuits(i)



# class Circuit:

#     def __init__(self, graph, priority_nodes, circuit, key_node):
#         self.circuit = circuit
#         self.circuit_length = 0
#         for i in range(len(circuit) - 1):
#             self.circuit_length += graph[circuit[i]][circuit[i + 1]]['length']

#         priority_temp = priority_nodes[:]

#         self.key_node = key_node
#         self.priority_node_sequence = [self.key_node]

if __name__ == '__main__':
    pass