import numpy as np
import sys
import simpy

import Node
import LoadData

# Create environment
env = simpy.Environment()

# Create nodes
nodes = []
zone_radius = 2
for i in range(10):
    nodes.append(Node.Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

# finding neighbour nodes for all nodes at time: 0 
for node in nodes:
    node.find_neighbour_nodes(nodes, 0)
    node.set_all_nodes(nodes)
    #print(f"Node {node.node_id} neigbours:", end= " ")
    #for neigh in node.neighbours:
    #    print(neigh.node_id, end=" ")
    #print()

def network_simulator(env, nodes):
    #while True:
        # Simulate packet sending process for each node
        #for node in nodes:
    yield env.process(nodes[2].iarp())

        # initial_packet = "Initial packet"
        # hello_packet = "Hello"

        # Run simulation for 1 time units
    yield env.timeout(1)

# Run the simulation
env.process(network_simulator(env,nodes))
env.run(until=20)
