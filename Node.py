import simpy
import random
from tabulate import tabulate
import LoadData
from math import acos, sin, cos
import distance
import numpy as np

class Node:
    def __init__(self, env, node_id: int, zone_radius: int, neighbours = None, position = None):
        self.env = env
        self.node_id = node_id
        self.zone_radius = zone_radius
        self.routing_table = {}
        self.neighbours = neighbours # List of nodes
        self.packet_queue = simpy.Store(env, capacity=100)
        self.position = position

    def iarp(self):
        # Generate an advertisement packet with TTL = p - 1.
        packet = {
            "Type": "ADVERTISEMENT",
            "Node Id": self.node_id,
            "TTL" : zone_radius - 1,
            "Source neighbours": self.neighbours,
            "Originator neighbours": self.neighbours,
            "Path" : []
        }

        self.packet_queue.put(packet)
        self.send_packet()
        
        # Append a list of e.g., 2-hop neighbours

    def send_packet(self):
        while True:
            packet = yield self.packet_queue.get()
            yield self.env.timeout(random.uniform(0.1, 0.5)) # Simulate transmission
            print(f"Node {self.node_id} sent {packet} to its neigbours")

            if(packet["Type"] == "ADVERTISEMENT"):
                # Filter out neighbour that already received ADVERTISEMENT
                if(packet["Source neighbours"] == packet["Originator neighbours"]):
                    # It must be the source handling this: send to all neighbours without filtering
                    for neighbour in packet["Originator neighbours"]:
                        yield self.env.process(neighbour.receive_packet(packet))

                source_neigbours = packet["Source neighbours"]
                filtered_neighbours = list(filter(lambda x: x not in source_neigbours, self.neighbours))

                for neighbour in filtered_neighbours:
                    yield self.env.process(neighbour.receive_packet(packet))

            if(packet["Type"] == "ADVERTISEMENT REPLY"):
                path = packet["Path"]
                index_of_self = path.index(self.node_id)

                # if(index_of_self == path[0]):
                #     # We are at source node
                #     pass

                # We are not at source node. Follow the reverse path
                next_node_id = path[index_of_self-1]
                next_node = list(filter(lambda x: x.node_id == next_node_id, self.neighbours))
                yield self.env.process(next_node.receive_packet(packet))
            
            else:
                for neighbour in self.neighbours:
                    # Get correct element in node array
                    yield self.env.process(neighbour.receive_packet(packet))

    def receive_packet(self, packet):
        print(f"Node with id {self.node_id}: Received packet")
        yield self.env.timeout(0) # Process received packet immediately

        # Pass to handler if advertisement packet
        if(packet["Type"] == "ADVERTISEMENT"):
            print(f"Node with id {self.node_id}: Received ADVERTISMENT")

            self._handle_advertisement(packet)

        if(packet["Type"] == "ADVERTISEMENT REPLY"):
            print(f"Node with id {self.node_id}: Received ADVERTISEMENT REPLY")
            path = packet["Path"]
            index_of_self = path.index(self.node_id)

            if(index_of_self == path[0]):
                print(f"Node with id {self.node_id}: Updating Routing Table")
                #self.update_routing_table()

            else:
                print(f"Node with id {self.node_id}: What do I do now?")
                pass

        print(f"Node {self.node_id} received packet: {packet}")


    def _handle_advertisement(self, packet):
        """
        Handles advertisements. If TTL == 0 the advertisement is discarded and not forwarded.
        The node appends its ID to the path in order to return a reply to the source node.
        """
        # Update path
        packet["Path"].append(self.node_id)

        ttl = packet["TTL"] - 1
        # If TTL is 0, change packet to ADV Reply and return to source
        if (ttl >= 0):
            print(f"Node with id {self.node_id}: ADVERTISEMENT REPLY")
            packet["Type"] = "ADVERTISEMENT REPLY"
            # Send the new packet
            self.packet_queue.put(packet)
            self.send_packet()
        
        # If not, forward advertisement to neighbours
        self.send_packet()


    def _receive_advertisement(self, packet):
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
    
    def get_position_at_time(self, time_index: int):
        series_str = self.position[time_index]
        parts = series_str.split()
        # Check if there are at least two parts (numbers) in the string
        if len(parts) >= 2:
            # Convert the parts to float and create a tuple
            tuple_with_two_numbers = (float(parts[0]), float(parts[1]))
        else:
            print("Not enough numbers in the string to create a tuple")  
        return tuple_with_two_numbers
    
    def isNeighbourInLOS(self, time_index, neighbour):
        """ Assumes an altitude of 718km """

        self_coordinates = self.get_position_at_time(time_index)
        self_lat = self_coordinates[0]
        self_lon = self_coordinates[1]

        neighbour_coordinates = neighbour.get_position_at_time(time_index)
        neighbour_lat = neighbour_coordinates[0]
        neighbour_lon = neighbour_coordinates[1]

        if (distance.distance(self_lat, self_lon, neighbour_lat, neighbour_lon) < 6000):
            return True
        
        return False
    
    def areNeigboursInLOS(self, time_index):

        self_coordinates = self.get_position_at_time(time_index)
        self_lat = self_coordinates[0]
        self_lon = self_coordinates[1]

        for neighbour in self.neighbours:
            neighbour_coordinates = neighbour.get_position_at_time(time_index)
            neighbour_lat = neighbour_coordinates[0]
            neighbour_lon = neighbour_coordinates[1]

            if (distance.distance(self_lat, self_lon, neighbour_lat, neighbour_lon) > 6000):
                return False
            
        return True   

    def findNeighbourNodes(self, nodes, time_index):
        list = []
        for node in nodes:
            if (node is not self):
                if (self.isNeighbourInLOS(time_index, node)):
                    list.append(node)

        self.neighbours = list

def network_simulator(env, nodes):
    # Simulate packet sending process for each node
    for node in nodes:
        env.process(node.send_packet())

    initial_packet = "Initial packet"
    hello_packet = "Hello"

    # Run simulation for 5 time units
    yield env.timeout(5)

# Create environment
env = simpy.Environment()

# Create nodes
nodes = []
zone_radius = 2
for i in range(10):
    nodes.append(Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

#print(f"Node 0 position at T = 0: {nodes[0].get_position_at_time(0)}")
#print(f"Node 4 {nodes[4].get_position_at_time(0)}")

# finding neighbour nodes for all nodes at time: 0 
for node in nodes:
    node.findNeighbourNodes(nodes, 0)
    print(f"Node {node.node_id} neigbours:", end= " ")
    for neigh in node.neighbours:
        print(neigh.node_id, end=" ")
    print()

nodes[1].iarp()
"""
# Are neighbours still neighbours
los = nodes[0].areNeigboursInLOS(0)
print(los)
"""

# Run the simulation
env.process(network_simulator(env,nodes))
env.run(until=3)
