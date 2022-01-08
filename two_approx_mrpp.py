#!/usr/bin/env python3

import networkx as nx
from ortools.linear_solver import pywraplp


# class Problem:

#     def __init__(self, mrpp, num_agents):
        


class MRPP_2_IP:

    def __init__(self, graph, num_agents):

        self.num_agents = num_agents    
        self.graph_original = graph
        for e in self.graph_original.edges():
            self.graph_original[e[0]][e[1]]['length'] = int(self.graph_original[e[0]][e[1]]['length'])
        self.graph_complete = self.graph_original.copy()
        self.nodes = list(self.graph_original.nodes())
        self.paths = {}
        # self.dist_from_pn = {}
        # self.dist_to_pn = {}
        # self.remaining_nodes = self.nodes.copy()
        # self.time_period = 0
        # for n in self.priority_nodes:
        #     self.remaining_nodes.remove(n)
        #     self.dist_to_pn[n] = {}
        #     self.dist_from_pn[n] = {}
        # print('1')
        paths = dict(nx.all_pairs_dijkstra_path(self.graph_original, weight = 'length'))
        # print('2')
        for i in self.nodes:
            # f = False
            # if i in self.priority_nodes:
            #     f = True
            for j in self.nodes:
                # t = False
                # if j in self.priority_nodes:
                #     t = True
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

        self.edges = list(self.graph_complete.edges())
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        self.E = len(self.edges)
        self.N = len(self.nodes)
        
    def add_variables(self):
        self.x = {}
        for a in range(self.num_agents):
            self.x[a] = {}
            for i, j in enumerate(self.edges):
                self.x[a][j] = self.solver.IntVar(0, 1, 'x[{}, {}]'.format(j, a))
        self.a = {}
        for a in range(self.num_agents):
            self.a[a] = {}
            for i, j in enumerate(self.nodes):
                self.a[a][j] = self.solver.IntVar(0, 1, 'a[{}, {}]'.format(j, a))
        self.b = {}
        for a in range(self.num_agents):
            self.b[a] = {}
            for i, j in enumerate(self.nodes):
                self.b[a][j] = self.solver.IntVar(0, 1, 'b[{}, {}]'.format(j, a))
        self.c = self.solver.NumVar(0, self.solver.infinity(), 'c')


    def add_init_constraints(self):
        self.add_constraints1()
        self.add_constraints2()
        self.add_constraints3()
        self.add_constraints4()
        self.add_constraints5()

    def add_constraints1(self):
        for n in self.nodes:
            lhs = 0
            for a in range(self.num_agents):
                for j in list(self.graph_complete.in_edges(n)):
                    lhs += self.x[a][j]
            self.solver.Add(lhs == 1)

    def add_constraints2(self):
        for n in self.nodes:
            for a in range(self.num_agents):
                lhs = self.a[a][n] - self.b[a][n]
                for j in list(self.graph_complete.in_edges(n)):
                    lhs += self.x[a][j]
                for j in list(self.graph_complete.out_edges(n)):
                    lhs -= self.x[a][j]
                self.solver.Add(lhs == 0)

    def add_constraints3(self):
        for n in self.nodes:
            lhs = 0
            for a in range(self.num_agents):
                lhs += self.a[a][n] - self.b[a][n]
            self.solver.Add(lhs == 0)
        for a in range(self.num_agents):
            lhs1 = 0
            lhs2 = 0
            for n in self.nodes:
                lhs1 += self.a[a][n]
                lhs2 += self.b[a][n]
            self.solver.Add(lhs1 == 1)
            self.solver.Add(lhs2 == 1)

    def add_constraints4(self):
        for a in range(self.num_agents):
            for n in self.nodes:
                lhs1 = self.a[a][n]
                lhs2 = self.b[a][n]
                for j in list(self.graph_complete.out_edges(n)):
                    lhs1 -= self.x[a][j]
                for j in list(self.graph_complete.in_edges(n)):
                    lhs2 -= self.x[a][j]
                self.solver.Add(lhs1 <= 0)
                self.solver.Add(lhs2 <= 0)
    
    def add_constraints5(self):
        for a in range(self.num_agents):
            lhs = 0
            for e in self.edges:
                lhs += self.graph_complete[e[0]][e[1]]['length'] * self.x[a][e]
            self.solver.Add(lhs <= self.c)


    def objective(self):
        self.solver.Maximize(-1 * self.c)

    def process(self):
        self.status = self.solver.Solve()


    def get_solution(self):
