import simpy
import random
from tabulate import tabulate
import LoadData
from math import acos, sin, cos
import distance
import numpy as np
import copy

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
        packet_list = []
        
        for neighbour in self.neighbours:
            packet = {
                "Type": "ADVERTISEMENT",
                "Node Id": self.node_id,
                "TTL" : zone_radius - 1,
                "Source neighbours": self.neighbours,
                "Path" : [self.node_id],
                "Packet size": 0
            }

            packet_list.append(packet)

        for packet in packet_list:
            self.packet_queue.put(packet)
        
        # Call once or just call for each neighbour?
        self.send_packet()
        
        # Append a list of e.g., 2-hop neighbours

    def send_packet(self):
        print("send_packet() running")
        while True:
            packet = yield self.packet_queue.get()
            packet_type = packet["Type"]
            yield self.env.timeout(random.uniform(0.1, 0.5)) # Simulate transmission
            print(f"Node {self.node_id} will try to send {packet_type} to its neigbours")

            if(packet["Type"] == "ADVERTISEMENT"):
                are_neighbours_equal = self._compare_neighbours(packet["Source neighbours"])
                
                if not(are_neighbours_equal):
                    source_neigbours = packet["Source neighbours"]
                    filtered_neighbours = list(filter(lambda x: x not in source_neigbours, self.neighbours))

                    for neighbour in filtered_neighbours:
                        yield self.env.process(neighbour.receive_packet(packet))
                
                else:
                    for neighbour in packet["Source neighbours"]:
                        yield self.env.process(neighbour.receive_packet(packet))

            elif(packet["Type"] == "ADVERTISEMENT REPLY"):
                path = packet["Path"]
                index_dest = path.index(self.node_id) - 1
                destination_node = list(filter(lambda x: x.node_id == index_dest, self.neighbours))
                yield self.env.process(destination_node.receive_packet(packet))
            
            else:
                print("I don't know this packet type")

    def receive_packet(self, packet):
        yield self.env.timeout(0) # Process received packet immediately

        # Pass to handler if advertisement packet
        if(packet["Type"] == "ADVERTISEMENT"):
            print(f"Node {self.node_id}: Received ADVERTISMENT")

            # Update path. Note: We only simulate 1 
            source_neighbours_ids = [neighbour.node_id for neighbour in packet["Source neighbours"]]

            if not any(id in packet["Path"] for id in source_neighbours_ids):
                packet["Path"].append(self.node_id)

            # If TTL is 0, change packet to ADV Reply and return it
            if (packet["TTL"] == 0):
                packet["Type"] = "ADVERTISEMENT REPLY"
                self.packet_queue.put(packet)
                self.send_packet()
            
            # If not, forward advertisement to neighbours
            else:
                packet["Source neighbours"] = self.neighbours
                packet["TTL"] = packet["TTL"] - 1
                self.packet_queue.put(packet)
                self.send_packet()

        elif(packet["Type"] == "ADVERTISEMENT REPLY"):
            print(f"Node with id {self.node_id}: Received ADVERTISEMENT REPLY")
            path = packet["Path"]

            if(path[0] == self.node_id):
                print(f"Back at origin. Updating routing table")
            else:
                self.packet_queue.put(packet)
                self.send_packet()    

    def _compare_neighbours(self,source_list):
        source_ids = []
        self_neigbour_ids = []
        for node in source_list:
            source_ids.append(node.node_id)

        for node in self.neighbours:
            self_neigbour_ids.append(node.node_id)

        return source_ids == self_neigbour_ids

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

    # initial_packet = "Initial packet"
    # hello_packet = "Hello"

    # Run simulation for 5 time units
    yield env.timeout(5)

# Create environment
env = simpy.Environment()

# Create nodes
nodes = []
zone_radius = 2
for i in range(10):
    nodes.append(Node(env, i, zone_radius, position=LoadData.get_position_data(i)))

# finding neighbour nodes for all nodes at time: 0 
for node in nodes:
    node.findNeighbourNodes(nodes, 0)
    print(f"Node {node.node_id} neigbours:", end= " ")
    for neigh in node.neighbours:
        print(neigh.node_id, end=" ")
    print()

nodes[2].iarp()
"""
# Are neighbours still neighbours
los = nodes[0].areNeigboursInLOS(0)
print(los)
"""

# Run the simulation
env.process(network_simulator(env,nodes))
env.run(until=3)
