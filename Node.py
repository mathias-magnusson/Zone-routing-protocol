import simpy
import random

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


def network_simulator(env, nodes):
    # Simulate packet sending process for each node
    for node in nodes:
        env.process(node.send_packet())

    intial_packet = "Initial packet"
    nodes[0].packet_queue.put(intial_packet)

    # Run simulation for 5 time units
    yield env.timeout(5)


# Create environment
env = simpy.Environment()

# Create 3 nodes
nodes = []
zone_radius = 2
for i in range(3):
    nodes.append(Node(env,i,zone_radius))

# Find and set neighbours
neighbours_id_list = [(nodes[(i-1) % len(nodes)].node_id, nodes[(i+1) % len(nodes)].node_id) for i in range(len(nodes))]
print(f"Neigbours id: {neighbours_id_list}")

for node in nodes:
    neighbour_tuple = neighbours_id_list[node.node_id]
    node.neighbours = list(filter(lambda n: n.node_id == neighbour_tuple[0] or 
                                  n.node_id ==neighbour_tuple[1], nodes))

# Run the simulation
env.process(network_simulator(env, nodes))
env.run()
