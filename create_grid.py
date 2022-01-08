#!/usr/bin/env python3
import networkx as nx
import random as rn

def create_grid_graphs(size = 5, edge_length = 100, name = 'grid_5_5'):

    i = 0
    g = nx.DiGraph()

    for r in range(size):
        pos_x = r * edge_length
        for c in range(size):
            pos_y = c * edge_length
            g.add_node(str(i), x = pos_x, y = pos_y)
            

            if r > 0:
                g.add_edge(str(i), str(i - size), length = edge_length, name = '{}_to_{}'.format(i, i - size))
                g.add_edge(str(i - size), str(i), length = edge_length, name = '{}_to_{}'.format(i - size, i))
        
            if c > 0:
                g.add_edge(str(i), str(i - 1), length = edge_length, name = '{}_to_{}'.format(i, i - 1))
                g.add_edge(str(i - 1), str(i), length = edge_length, name = '{}_to_{}'.format(i - 1, i))
            i += 1
            
            
    
    nx.write_graphml(g, './graphs/{}.graphml'.format(name))
    return g

def randomize(g, name, num_edges = 5):

    h = g.copy()
    edges = list(g.edges())
    nodes = list(g.nodes())

    for _ in range(num_edges):
        # print(len(h.edges()))
        count = 0
        while True:
            count += 1
            print(count)
            node1 = rn.sample(nodes, 1)[0]
            neighs = list(h.successors(node1))
            while len(neighs) < 2:
                count += 1
                print(count)
                node1 = rn.sample(nodes, 1)[0]
                neighs = list(h.successors(node1))
            node2 = rn.sample(neighs, 1)[0]
            print(node1, neighs, node2)
            temp = h.copy()
            temp.remove_edge(node1, node2)
            temp.remove_edge(node2, node1)
            if nx.is_strongly_connected(temp):
                print(node1, node2)
                h = temp.copy()
                print(h.has_edge(node2, node1))
                print(list(h.successors(node1)))
                print(list(h.successors(node2)))
                break

    nx.write_graphml(h, './graphs/test/{}.graphml'.format(name))
        
    # return h



def random_graphs(g, count, num_edges, name):

    for n in num_edges:
        for i in range(count):
            print (n, i)
            randomize(g, '{}_rand_{}_{}'.format(name, n, i), n)
