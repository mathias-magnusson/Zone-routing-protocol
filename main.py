import numpy as np
import simpy
import sys
import Node
import LoadData


def find_node_neighbours(nodes: [], index : int):
    for node in nodes:
        node.find_neighbour_nodes(nodes, index)
        node.set_all_nodes(nodes)

def sort_table(table):
    sorted_routing = sorted(table.items())
    return dict(sorted_routing)

run_time = 1
sample_time = 1

def network_simulator(env, nodes):
    for i in range(run_time):
        np.random.seed(41)

        find_node_neighbours(nodes, i)
        start = env.now
        packet_count = 0
        
        for node in nodes:
            node.routing_table_new.clear()
            node.metrics_table_new.clear()
            node.paths_to_destinations.clear()
            yield env.process(node.iarp())
            node.routing_table = node.routing_table_new
            node.metrics_table = node.metrics_table_new

            node.routing_table = sort_table(node.routing_table)
            node.metrics_table = sort_table(node.metrics_table)

            for n in nodes:
                packet_count = packet_count + n.packet_count_iarp
                n.packet_count_iarp = 0
            
            print(f"Node {node.node_id} processed - Packet count: {packet_count}")
            
        print(f"Packet count iarp: {packet_count}")

        ### Count number og IERP packet for different paths. ###
        source = [2, 23, 8, 30, 40, 27]
        destination = [12, 13, 24, 28, 1, 24]
        packet_count_IERP = 0

        for x in range(len(source)):
            packet_counter = 0
            yield env.process(nodes[source[x]].send_data(destination[x]))
            stop = env.now
            full_path, ETX_path = nodes[source[x]].get_best_path_ierp(destination[x])
            print(f"Best path: {full_path}   -   ETX: {ETX_path}")

            for n in nodes:
                packet_counter = packet_counter + n.packet_count_ierp
                n.packet_count_ierp = 0
            packet_count_IERP = packet_count_IERP + packet_counter
            
            print(f"Packet count ierp: {packet_counter}")

        print(packet_count_IERP/len(source))

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