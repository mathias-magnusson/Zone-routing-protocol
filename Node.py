import simpy
import random
from tabulate import tabulate
import LoadData
from math import acos, sin, cos
import distance
import numpy as np
import copy
import queue

class Node:
    def __init__(self, env, node_id: int, zone_radius: int, neighbours = None, position = None):
        self.env = env
        self.node_id = node_id
        self.zone_radius = zone_radius
        self.routing_table = {}
        self.neighbours = neighbours # List of nodes
        self.packet_queue = queue.Queue()
        self.position = position
        self.nodes = []

    def iarp(self):
        yield self.env.timeout(0)
        packet_list = []
        
        for neighbour in self.neighbours:
            packet = {
                "Type": "ADVERTISEMENT",
                "Node Id": self.node_id,
                "TTL" : self.zone_radius - 1,
                "Source neighbours": self.neighbours,
                "Path" : [self.node_id],
                "Packet size": 0
            }

            packet_list.append(packet)

        for packet in packet_list:
            self.packet_queue.put(packet)
        
        # Call once or just call for each neighbour?
        yield self.env.process(self.send_packet())
        
        # Append a list of e.g., 2-hop neighbours

    def send_packet(self): 
        for node in self.neighbours:            
            packet = self.packet_queue.get()             
            packet_type = packet["Type"]
            #self.env.timeout(random.uniform(0.1, 0.5)) # Simulate transmission
            print(f"Node {self.node_id} will try to send {packet_type} to its neigbours")

            if(packet["Type"] == "ADVERTISEMENT"):
                for path_id in packet["Path"]:
                    if node.node_id != path_id:
                        yield self.env.process(node.receive_packet(packet))
            elif(packet["Type"] == "ADVERTISEMENT REPLY"):
                path = packet["Path"]
                index_dest = path.index(self.node_id) - 1
                destination_node = self.find_node_by_id(path[index_dest])
                yield self.env.process(destination_node.receive_packet(packet))
            else:
                print("I don't know this packet type")
            
            #if (self.packet_queue.empty()):
            #    yield env.timeout(0)

    def receive_packet(self, packet):
        #yield self.env.timeout(0) # Process received packet immediately

        # Pass to handler if advertisement packet
        if(packet["Type"] == "ADVERTISEMENT"):
            print(f"Node {self.node_id}: Received ADVERTISMENT")

            # Update path.
            packet["Path"].append(self.node_id)                

            # If TTL is 0, change packet to ADV Reply and return it
            if (packet["TTL"] == 0):
                packet["Type"] = "ADVERTISEMENT REPLY"
                print(packet["Path"])
                self.packet_queue.put(packet)
                yield self.env.process(self.send_packet())
            # If not, forward advertisement to neighbours
            else:
                #packet["Source neighbours"] = self.neighbours
                packet["TTL"] = packet["TTL"] - 1
                self.packet_queue.put(packet)
                yield self.env.process(self.send_packet())
        elif(packet["Type"] == "ADVERTISEMENT REPLY"):
            print(f"Node with id {self.node_id}: Received ADVERTISEMENT REPLY")
            path = packet["Path"]

            if(path[0] == self.node_id):
                print(f"Back at origin. Updating routing table")
                print("\n")
                #yield self.env.timeout(0)
            else:
                self.packet_queue.put(packet)
                yield self.env.process(self.send_packet())    

    def find_neighbour_nodes(self, nodes, time_index):
        list = []
        for node in nodes:
            if (node is not self):
                if (self.is_neighbour_in_LOS(time_index, node)):
                    list.append(node)

        self.neighbours = list

    def set_all_nodes(self, nodes):
        self.nodes = nodes

    def compare_neighbours(self,source_list):
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
    
    def is_neighbour_in_LOS(self, time_index, neighbour):
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
    
    def find_node_by_id(self, node_id):
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None  # Node not found