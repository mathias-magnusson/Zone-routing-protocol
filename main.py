import numpy as np
import sys
import simpy
import Node
import LoadData
from time import sleep

def find_node_neighbours(nodes: [], index : int):
    for node in nodes:
        node.find_neighbour_nodes(nodes, index)
        node.set_all_nodes(nodes)


def network_simulator(env, nodes):
    while True:
        for node in nodes:
            node.routing_table_new.clear()
            node.metrics_table_new.clear()
            yield env.process(node.iarp())
            node.routing_table = node.routing_table_new
            node.metrics_table = node.metrics_table_new
            print(f"Node {node.node_id} routing table: {node.routing_table}\n")
        
        sleep(60)

# Create environment
env = simpy.Environment()

# Create nodes
nodes = []
zone_radius = 2
for i in range(66):
    nodes.append(Node.Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

# finding neighbour nodes for all nodes at time: 0
find_node_neighbours(nodes, 0)

# Run the simulation
env.process(network_simulator(env,nodes))
env.run(until=20)



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