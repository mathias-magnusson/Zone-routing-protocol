import numpy as np
import simpy
import Node
import LoadData
import planned_transmissions as pt

#all_tranmissions = pt.generate_planned_transmission()

# 18: [(0, 5, 0), (6, 15, 5), (10, 14, 11), (11, 7, 17), (9, 13, 23)]
# 30: [(0, 7, 0), (2, 26, 5), (22, 11, 11), (15, 8, 17), (27, 20, 23)]
# 42: [(0, 4, 0), (34, 25, 5), (9, 12, 11), (32, 2, 17), (39, 8, 23)]
# 54: [(48, 52, 0), (33, 12, 5), (28, 7, 11), (51, 2, 17), (42, 20, 23)]
# 66: [(58, 7, 0), (44, 19, 5), (13, 29, 11), (35, 20, 17), (8, 2, 23)]

print_once = True
packet_count_IERP = 0
IARP_time = 0

all_tranmissions = [(58, 7, 0), (44, 19, 5), (13, 29, 11), (35, 20, 17), (8, 2, 23)]
iteration_counter = 0

def find_node_neighbours(nodes: [], index : int):
    for node in nodes:
        node.find_neighbour_nodes(nodes, index)
        node.set_all_nodes(nodes)

def sort_table(table):
    sorted_routing = sorted(table.items())
    return dict(sorted_routing)

def calculate_execution_time():
    execution_time = 0
    total_paths = 0

    for node in nodes:
        total_paths = sum(len(entry) for entry in node.routing_table.values())
        for key in node.routing_table:
            total_paths += sum(len(entry) for entry in nodes[key].routing_table.values())
        execution_time += total_paths * 0.0001   

    execution_time = execution_time/num_nodes
    yield env.timeout(execution_time)

def network_process(env, nodes):
    first_run = True
    runned_at_time = 0
    while True:
        if first_run: 
            yield env.process(IARP_process(env, nodes))
            first_run = False
        #elif (env.now - runned_at_time) >= 30:
        #    runned_at_time = env.now
        #    yield env.process(IARP_process(env, nodes))
            
        yield env.process(send_data_process(env, nodes))

def IARP_process(env, nodes):
    global iteration_counter
    global IARP_time
    np.random.seed(41)
    find_node_neighbours(nodes, iteration_counter)

    print(f"\nIARP starting - Time: {env.now}")

    packet_count_iarp = 0
    for node in nodes:
        packet_count = 0
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
        
        packet_count_iarp += packet_count
        print(f"Node {node.node_id} finished")

    start_time = env.now
    yield env.process(calculate_execution_time())
    print(f"IARP finished - Time: {env.now-start_time} - Packet count: {packet_count_iarp}")
    IARP_time = env.now-start_time
    iteration_counter += 1

def send_data_process(env, nodes):
        global packet_count_IERP
        global print_once

        IERP_start_time = env.now
        
        for tranmission in all_tranmissions:
            origin_node_id, destination_node_id, start_time = tranmission

            if (start_time < env.now):
                node_start = env.now
                #print(f"Node {origin_node_id} trying to send at time: {env.now}")
                packet_counter = 0
                
                yield env.process(nodes[origin_node_id].send_data(destination_node_id))
                full_path, ETX_path = nodes[origin_node_id].get_best_path_ierp()
                print(f"Best path: {full_path}   -   ETX: {ETX_path}")

                for n in nodes:
                    packet_counter = packet_counter + n.packet_count_ierp
                    n.packet_count_ierp = 0
                packet_count_IERP = packet_count_IERP + packet_counter

                #print(f"Send_data() finished - Time: {env.now-node_start} - Packet count ierp: {packet_counter}")
                all_tranmissions.pop(all_tranmissions.index(tranmission))
        
        if not all_tranmissions and print_once == True:
            print_once = False
            print(f"Ierp finished - Time {IERP_start_time-IARP_time} - Average No. of packets: {packet_count_IERP/5}") 
        else:
            yield env.timeout(0.01)         
  
# Create environment
env = simpy.Environment()

# Create nodes
nodes = []
zone_radius = 4
num_nodes = 66
for i in range(num_nodes):
    nodes.append(Node.Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

env.process(network_process(env, nodes))
env.run(until=6000)                         # 6000 = 100 minutes in seconds