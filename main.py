import numpy as np
import sys
import simpy
import Node
import LoadData
from time import sleep

def network_simulator(env, nodes):
    while True:
        for node in nodes:
            node.routing_table_new.clear()
            node.metrics_table_new.clear()
            yield env.process(node.iarp())
            node.routing_table = node.routing_table_new
            node.metrics_table = node.metrics_table_new
            print(f"Node {node.node_id} routing table: {node.routing_table}")
        
        sleep(60)
        #yield env.process(nodes[2].iarp())
        #yield env.timeout(1)

# Create environment
env = simpy.Environment()

# Create nodes
nodes = []
zone_radius = 2
for i in range(5):
    nodes.append(Node.Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

# finding neighbour nodes for all nodes at time: 0
for node in nodes:
    node.find_neighbour_nodes(nodes, 0)
    node.set_all_nodes(nodes)

# Run the simulation
env.process(network_simulator(env,nodes))
env.run(until=20)
