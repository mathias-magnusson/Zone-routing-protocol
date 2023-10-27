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
        self.routing_table_new = {}
        self.metrics_table = {}
        self.metrics_table_new = {}
        self.neighbours = neighbours # List of nodes
        self.packet_queue = []
        self.position = position
        self.nodes = []

    def iarp(self):
        self.generate_iarp_packet()
        yield self.env.process(self.send_packet())

    def send_packet(self):
        for node in self.neighbours:       
            if (len(self.packet_queue) == 0):
                return
            packet = self.packet_queue.pop(0)             
            packet_type = packet["Type"]

            if(packet["Type"] == "ADVERTISEMENT"):
                node_not_in_path = True
                for path_id in packet["Path"]:
                    if node.node_id == path_id:
                        node_not_in_path = False
                    
                if (node_not_in_path == True):
                    print(f"Node {self.node_id} sending {packet_type} to Node {node.node_id}")
                    yield self.env.process(node.receive_packet(packet))

            elif(packet["Type"] == "ADVERTISEMENT REPLY"):
                path = packet["Path"]
                index_dest = path.index(self.node_id) - 1
                destination_node = self.find_node_by_id(path[index_dest])
                print(f"Node {self.node_id} sending {packet_type} to Node {destination_node.node_id}")
                yield self.env.process(destination_node.receive_packet(packet))
            else:
                print("I don't know this packet type")
            
            #if (self.packet_queue.empty()):
            #    yield env.timeout(0)

    def receive_packet(self, packet):
        if(packet["Type"] == "ADVERTISEMENT"):
            print(f"Node {self.node_id}: Received ADVERTISMENT")

            packet["Path"].append(self.node_id)       
            
            if (packet["TTL"] == 0):
                packet["Type"] = "ADVERTISEMENT REPLY"
                print(packet["Path"])
                self.packet_queue.append(packet)
                yield self.env.process(self.send_packet())
            else:
                packet["TTL"] = packet["TTL"] - 1
                self.generate_iarp_packet(packet)
                yield self.env.process(self.send_packet())
                
        elif(packet["Type"] == "ADVERTISEMENT REPLY"):
            print(f"Node with id {self.node_id}: Received ADVERTISEMENT REPLY")
            path = packet["Path"]

            if(path[0] == self.node_id):
                print(f"Back at origin. Updating routing table\n")
                self.update_routing_table(destination=packet["Path"][-1], path=packet["Path"])
                self.update_metrics_table(destination=packet["Path"][-1], metrics=[1, 1])
            else:
                self.packet_queue.append(packet)
                yield self.env.process(self.send_packet())    

    def generate_iarp_packet(self, currentPacket = None):
        if (currentPacket == None):
            for neighbour in self.neighbours:
                packet = {
                    "Type": "ADVERTISEMENT",
                    "Node Id": self.node_id,
                    "TTL" : self.zone_radius - 1,
                    "Source neighbours": self.neighbours,
                    "Path" : [self.node_id],
                    "Packet size": 0
                }
                self.packet_queue.append(packet)
        else:
            for neighbour in self.neighbours:
                packet = {
                    "Type": currentPacket["Type"],
                    "Node Id": currentPacket["Node Id"],
                    "TTL" : currentPacket["TTL"],
                    "Source neighbours": currentPacket["Source neighbours"],
                    "Path" : currentPacket["Path"],
                    "Packet size":currentPacket["Packet size"]
                }
                self.packet_queue.append(packet)

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
    
    def get_best_path_iarp(self, destination: int):
        if destination not in self.metrics_table:
            return None  # Key not found in metrics_table

        lists = self.metrics_table[destination]

        # Initialize variables to track the best index and the minimum sum
        best_index = 0
        min_sum = sum(lists[0])

        for index, sublist in enumerate(lists):
            current_sum = sum(sublist)
            if current_sum < min_sum:
                best_index = index
                min_sum = current_sum

        values_for_destination = self.routing_table[destination]
        best_path = values_for_destination[best_index]
        return best_path           

    def update_routing_table(self, destination: int, path: list):
        # Check if key exists
        if not destination in self.routing_table_new:
            self.routing_table_new[destination] = []
        
        self.routing_table_new[destination].append(path)


    def update_metrics_table(self, destination: int, metrics: list):
        if not destination in self.metrics_table_new:
            self.metrics_table_new[destination] = []
        
        self.metrics_table_new[destination].append(metrics)

    
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