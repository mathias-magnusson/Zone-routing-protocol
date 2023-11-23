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


run_time = 200
sample_time = 1

def network_simulator(env, nodes):

    data = [[],[]]
    for i in range(run_time):
        find_node_neighbours(nodes=nodes, index=i)

        start = env.now

        nodes[0].routing_table_new.clear()
        nodes[0].metrics_table_new.clear()
        nodes[0].paths_to_destinations.clear()
        yield env.process(nodes[0].iarp())
        nodes[0].routing_table = nodes[0].routing_table_new
        nodes[0].metrics_table = nodes[0].metrics_table

        nodes[0].routing_table = sort_table(nodes[0].routing_table)
        nodes[0].metrics_table = sort_table(nodes[0].metrics_table)

        # for node in nodes:
        #     node.routing_table_new.clear()
        #     node.metrics_table_new.clear()
        #     node.paths_to_destinations.clear()
        #     yield env.process(node.iarp())
        #     node.routing_table = node.routing_table_new
        #     node.metrics_table = node.metrics_table_new

        #     node.routing_table = sort_table(node.routing_table)
        #     node.metrics_table = sort_table(node.metrics_table)

            #print(f"Node {node.node_id} routing table: {node.routing_table}\n")
            #print(f"Node {node.node_id} metric table: {node.metrics_table}\n")

        source = 0
        destination = 49

        #yield env.process(nodes[source].ierp(destination))
        stop = env.now
       # print(nodes[source].paths_to_destinations)
       # print(nodes[source].get_best_path_ierp(destination, True))
        print(f"Elapsed time for T = {i}: {stop-start}")

        # Write to data
        data[0].append(i)
        data[1].append(stop-start)
    with open('/Users/mathiasmagnusson/Zone-routing-protocol/iarp-test-5.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(data)

# Create environment
env = simpy.Environment()

# Create nodes
nodes = []
zone_radius = 5
for i in range(66):
    nodes.append(Node.Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

# Run the simulation
env.process(network_simulator(env,nodes))
env.run()