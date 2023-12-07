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

iteration_counter = 0

def network_process(env, nodes):
    first_run = True
    runned_at_time = 0
    while True:
        if first_run: 
            yield env.process(IARP_process(env, nodes))
            first_run = False
        elif (env.now - runned_at_time) >= 30:
            runned_at_time = env.now
            yield env.process(IARP_process(env, nodes))
            
        yield env.process(send_data_process(env, nodes))
        yield env.timeout(1)

# Periodic process
def IARP_process(env, nodes):
    global iteration_counter
    np.random.seed(41)
    find_node_neighbours(nodes, iteration_counter)
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
    iteration_counter += 1

def send_data_process(env, nodes):
        packet_count_IERP = 0
        source = [0]
        destination = [4]

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

# Create environment
env = simpy.Environment()
res = simpy.PriorityResource(env, capacity = 1)

# Create nodes
nodes = []
zone_radius = 2
for i in range(30):
    nodes.append(Node.Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

#Start the periodic process IARP
#env.process(IARP_process(env, nodes, 30))


# Start the non-perioic process IERP
env.process(network_process(env, nodes))

env.run()