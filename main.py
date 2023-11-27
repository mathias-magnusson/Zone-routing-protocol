import numpy as np
import sys
import simpy
import Node
import LoadData
import time

def find_node_neighbours(nodes: [], index : int):
    for node in nodes:
        node.find_neighbour_nodes(nodes, index)
        node.set_all_nodes(nodes)

def sort_table(table):
    sorted_routing = sorted(table.items())
    return dict(sorted_routing)

run_time = 120
sample_time = 1

def network_simulator(env, nodes):
    for i in range(run_time):
        find_node_neighbours(nodes, i)
        start = env.now

        for node in nodes:
            node.routing_table_new.clear()
            node.metrics_table_new.clear()
            node.paths_to_destinations.clear()
            yield env.process(node.iarp())
            node.routing_table = node.routing_table_new
            node.metrics_table = node.metrics_table_new

            node.routing_table = sort_table(node.routing_table)
            node.metrics_table = sort_table(node.metrics_table)

        source = 0
        destination = 3

        yield env.process(nodes[source].send_data(destination))
        stop = env.now
        full_path, ETX_path = nodes[source].get_best_path_ierp(destination)
        print(f"Best path: {full_path}   -   ETX: {ETX_path}")

# Create environment
env = simpy.Environment()

# Create nodes
nodes = []
zone_radius = 2
for i in range(66):
    nodes.append(Node.Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

# Run the simulation
env.process(network_simulator(env,nodes))
env.run()