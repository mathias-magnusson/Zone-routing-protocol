import numpy as np
import sys
import simpy
import Node
import LoadData
import time
import csv

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


    data = [[],[]]
    for i in range(run_time):
        find_node_neighbours(nodes, i)
        start = env.now
        packet_count = 0
        for node in nodes:
            node.routing_table_new.clear()
            node.metrics_table_new.clear()
            node.paths_to_destinations.clear()
            node.packet_count = 0
            yield env.process(node.iarp())
            node.routing_table = node.routing_table_new
            node.metrics_table = node.metrics_table_new

            node.routing_table = sort_table(node.routing_table)
            node.metrics_table = sort_table(node.metrics_table)
            packet_count = packet_count + node.packet_count
            print(f"Node {node.node_id} processed. Packet count: {packet_count}")
            
        # nodes[0].routing_table_new.clear()
        # nodes[0].metrics_table_new.clear()
        # nodes[0].paths_to_destinations.clear()
        # nodes[0].packet_count = 0
        # yield env.process(nodes[0].iarp())
        # nodes[0].routing_table = nodes[0].routing_table_new
        # nodes[0].metrics_table = nodes[0].metrics_table_new

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
zone_radius = 5
for i in range(18):
    nodes.append(Node.Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

# Run the simulation
env.process(network_simulator(env,nodes))
env.run()