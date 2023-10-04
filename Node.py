import simpy
import random
from tabulate import tabulate

class Node:
    def __init__(self, env, node_id: int, zone_radius: int, neighbours = None):
        self.env = env
        self.node_id = node_id
        self.zone_radius = zone_radius
        self.routing_table = {}
        self.neighbours = neighbours # List of nodes
        self.packet_queue = simpy.Store(env)

    def send_packet(self):
        while True:
            packet = yield self.packet_queue.get()
            yield self.env.timeout(random.uniform(0.1, 0.5)) # Simulate transmission
            print(f"Node {self.node_id} sent packet to its neigbours {self.neighbours}")
            for neighbour in self.neighbours:
                # Get correct element in node array
                yield self.env.process(neighbour.receive_packet(packet))

    def receive_packet(self, packet):
        yield self.env.timeout(0) # Process received packet immediately
        print(f"Node {self.node_id} received packet: {packet}")

    def update_routing_table(self, destination: int, routes: list, metrics: list):
        # Routing table template
        # [(dest_addr_1, route list, metric list)]
        # Like this: [(1, [1], 5), (2, [1,2], [5, 10]), (3, [1,2,3], [5,10,15])]
        # To access the first item-set: routing_table[0]
        # To access the first item in the first set: routing_table[0][0]

        # Use case:
        #     1. If destination exsits in routing_table: update route + metrics
        #     2. Else add destination, routes, and metics to routing_table

        for i in range(len(self.routing_table)):
            if (self.routing_table[i][0] == destination):
                self.routing_table[i][1] == routes
                self.routing_table[i][2] == metrics

            else:
                self.routing_table.append(destination, routes, metrics)


def network_simulator(env, nodes):
    # Simulate packet sending process for each node
    for node in nodes:
        env.process(node.send_packet())

    initial_packet = "Initial packet"
    hello_packet = "Hello"
    # for node in nodes:
    #     hello_packet = hello_packet + f" from node {node.node_id}"
    #     nodes[node.node_id].packet_queue.put(initial_packet)
    #     nodes[node.node_id].packet_queue.put(hello_packet)
    for node in nodes:
        hello_packet = f" from node {node.node_id}"
        node.packet_queue.put(initial_packet)
        node.packet_queue.put(hello_packet)


    # Run simulation for 5 time units
    yield env.timeout(50)


# Create environment
env = simpy.Environment()

# Create 3 nodes for main nodes
nodes = []
zone_radius = 2
for i in range(3):
    nodes.append(Node(env,i,zone_radius))


# Find and set neighbours
neighbours_id_list = [(nodes[(i-1) % len(nodes)].node_id, nodes[(i+1) % len(nodes)].node_id) for i in range(len(nodes))]

for node in nodes:
    neighbour_tuple = neighbours_id_list[node.node_id]
    node.neighbours = list(filter(lambda n: n.node_id == neighbour_tuple[0] or 
                                  n.node_id ==neighbour_tuple[1], nodes))

# Run the simulation
env.process(network_simulator(env,nodes))
env.run(until=3)
