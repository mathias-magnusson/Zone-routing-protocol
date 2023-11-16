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

def network_simulator(env, nodes):
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

        #print(f"Node {node.node_id} routing table: {node.routing_table}\n")
        #print(f"Node {node.node_id} metric table: {node.metrics_table}\n")

    source = 0
    destination = 3

    yield env.process(nodes[source].ierp(destination))
    stop = env.now
    print(nodes[source].paths_to_destinations)
    print(nodes[source].get_best_path_ierp(destination, True))
    print(f"Elapsed time: {stop-start}")

# Create environment
env = simpy.rt.RealtimeEnvironment(factor=0.1)

# Create nodes
nodes = []
zone_radius = 2
for i in range(22):
    nodes.append(Node.Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

# finding neighbour nodes for all nodes at time: 0
find_node_neighbours(nodes, 0)

# Run the simulation
env.process(network_simulator(env,nodes))
env.run()


### Run every sample

"""run_time = 120
sample_time = 1

def network_simulator(env, nodes):
    for i in range(run_time):

        find_node_neighbours(nodes,i)
        
        for node in nodes:
            node.routing_table_new.clear()
            node.metrics_table_new.clear()
            yield env.process(node.iarp())
            node.routing_table = node.routing_table_new
            node.metrics_table = node.metrics_table_new
            print(f"Node {node.node_id} routing table: {node.routing_table}\n")
    
        sleep(sample_time)"""