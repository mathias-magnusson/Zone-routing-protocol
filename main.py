import simpy
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

    data = [[],[]]
    for i in range(run_time):
        print("Finding neighbours...")
        find_node_neighbours(nodes, i)

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
            print(f"Node {node.node_id} processed. IARP Packet count: {packet_count}")

        source = 0
        destination = 3

        print(f"Finding path from Node {source} - Node {destination}")
        yield env.process(nodes[source].send_data(destination))
        packet_count_ierp = 0
        for node in nodes:
            packet_count_ierp += node.packet_count_ierp
        print(f"IERP Packet Count: {packet_count_ierp}")

        #full_path, ETX_path = nodes[source].get_best_path_ierp(destination)
        #print(f"Best path: {full_path}   -   ETX: {ETX_path}")

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