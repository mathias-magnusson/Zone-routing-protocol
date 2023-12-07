import numpy as np
import simpy
import Node
import LoadData

iteration_count = 0
iarp_guard = 0
ierp_guard = 0

def find_node_neighbours(nodes: [], index : int):
    for node in nodes:
        node.find_neighbour_nodes(nodes, index)
        node.set_all_nodes(nodes)

def sort_table(table):
    sorted_routing = sorted(table.items())
    return dict(sorted_routing)

# Periodic process
def IARP_process(env, nodes, source):
    global iteration_count, iarp_guard
    while True:
        np.random.seed(41)
        find_node_neighbours(nodes, iteration_count)
        packet_count = 0
        print(f"IARP starting at {env.now}")
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
            
            #print(f"Node {node.node_id} processed - Packet count: {packet_count}")
            
        print(f"IARP finished at {env.now}")
        iteration_count += 1

        nodes[source[0]].event.succeed()  # "reactivate"
        nodes[source[0]].event = env.event()
        iarp_guard += 1
        yield env.timeout(30)

def send_data_process(env, nodes):
        source = [7]
        destination = [23]
        packet_count_IERP = 0
        global iarp_guard
        while True:
            if (iarp_guard % 30 == 0):
                print("Passivating")
                yield nodes[source[0]].event  # "passivate"
            else:
                print(f"send_data() starting at {env.now}")
                for x in range(len(source)):
                    packet_counter = 0
                    
                    yield env.process(nodes[source[x]].send_data(destination[x]))
                    full_path, ETX_path = nodes[source[x]].get_best_path_ierp(destination[x])
                    print(f"Best path: {full_path}   -   ETX: {ETX_path}")

                    for n in nodes:
                        packet_counter = packet_counter + n.packet_count_ierp
                        n.packet_count_ierp = 0
                    packet_count_IERP = packet_count_IERP + packet_counter
                    
                    #print(f"Packet count ierp: {packet_counter}")

                #print(f"Average IERP count: {packet_count_IERP/len(source)}")
                print(f"send_data() finished at {env.now}")
                yield env.timeout(5)  # Some arbitrary interval for the other process

                # Increment guard
                iarp_guard += 1


# Create environment
env = simpy.Environment()

# Create nodes
nodes = []
zone_radius = 2
source = [7]
for i in range(66):
    nodes.append(Node.Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

#Start the periodic process IARP
env.process(IARP_process(env, nodes, source))

# Start the non-perioic process IERP
env.process(send_data_process(env, nodes))

env.run()