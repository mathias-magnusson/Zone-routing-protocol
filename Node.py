import simpy
import random
from tabulate import tabulate
import LoadData
from math import acos, sin, cos
import distance
import numpy as np
import copy
from queue import Queue
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import halfnorm

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
        self.periphiral_nodes = []
        self.packet_queue = Queue()
        self.BRP_packet_queue = Queue()
        self.position = position
        self.nodes = []
        self.paths_to_destinations = []

######## IARP ########

    def iarp(self):
        self.generate_iarp_packet()
        yield self.env.process(self.send_packet())
    
    def send_packet(self):
        while (self.packet_queue.qsize() > 0):
            yield self.env.timeout(0.1)
            packet = self.packet_queue.get(0)             
            packet_type = packet["Type"]
            next_node_string = packet["Next_node"]

            if(packet["Type"] == "ADVERTISEMENT"):
                ##print(f"Node {self.node_id} sending {packet_type} to Node {next_node_string}")
                next_node = self.find_node_by_id(packet["Next_node"])
                yield self.env.process(next_node.receive_packet(packet))
            elif(packet["Type"] == "ADVERTISEMENT REPLY"):
                path = packet["Path"]
                index_dest = path.index(self.node_id) - 1
                destination_node = self.find_node_by_id(path[index_dest])
                ##print(f"Node {self.node_id} sending {packet_type} to Node {destination_node.node_id}")
                yield self.env.process(destination_node.receive_packet(packet))
            else:
                print("I don't know this packet type")

    def receive_packet(self, packet):
        yield self.env.timeout(0.1)
        if(packet["Type"] == "ADVERTISEMENT"):
            ##print(f"Node {self.node_id}: Received ADVERTISMENT")
            half_normal_data = halfnorm.rvs(size=1)
            # Apply a power transformation with a negative exponent
            power_parameter = -3
            transformed_data = 1 - np.exp(power_parameter * half_normal_data)

            packet["Packet loss"].append(transformed_data[0])

            packet["Path"].append(self.node_id)       
            
            if (packet["TTL"] == 0):
                packet["Type"] = "ADVERTISEMENT REPLY"
                self.packet_queue.put(packet)
                yield self.env.process(self.send_packet())
            else:
                packet["TTL"] = packet["TTL"] - 1
                self.generate_iarp_packet(packet)              
                yield self.env.process(self.send_packet())
                
        elif(packet["Type"] == "ADVERTISEMENT REPLY"):
            ##print(f"Node with id {self.node_id}: Received ADVERTISEMENT REPLY")
            path = packet["Path"]

            if(path[0] == self.node_id):
                ##print(f"Back at origin. Updating routing table")
                self.update_tables(packet["Path"], packet["Packet loss"])
            else:
                self.packet_queue.put(packet)
                yield self.env.process(self.send_packet())    

    def generate_iarp_packet(self, currentPacket = None):
        if (currentPacket == None):
            for neighbour in self.neighbours:
                packet = {
                    "Type": "ADVERTISEMENT",
                    "Node Id": self.node_id,
                    "Next_node": neighbour.node_id,
                    "TTL" : self.zone_radius - 1,
                    "Path" : [self.node_id],
                    "Packet size": 0,
                    "Packet loss" : []
                }
                self.packet_queue.put(packet)
        else:
            for neighbour in self.neighbours:
                node_not_in_path = True
                for path_id in currentPacket["Path"]:
                    if (neighbour.node_id == path_id):
                        node_not_in_path = False
                        
                if (node_not_in_path == True):
                    packet = copy.deepcopy(currentPacket)
                    packet["Next_node"] = neighbour.node_id
                    self.packet_queue.put(packet)

            if (self.packet_queue.qsize() == 0):           # If no packet is appended a reply should be sent - fx when no neighbours and a full path isn't found
                packet = copy.deepcopy(currentPacket)
                packet["Next_node"] = neighbour.node_id
                packet["TTL"] = 0
                packet["Type"] = "ADVERTISEMENT REPLY"
                self.packet_queue.put(packet)

    def get_best_path_iarp(self, destination: int, return_packet_loss = False):
        if destination not in self.metrics_table:
            return None, None  # Key not found in metrics_table

        ## Finding index that has the smallest sum of packet_loss
        expected_transmission_count = []       
        for packet_loss in self.metrics_table[destination]:
            packet_loss_sum = 0
            for item in packet_loss:
                packet_loss_sum = packet_loss_sum + 1/(item**2)
            
            expected_transmission_count.append(packet_loss_sum)

        min_ETX = min(expected_transmission_count)
        index_of_min_packet_loss = expected_transmission_count.index(min_ETX)

        if (return_packet_loss == True):
            return (copy.deepcopy(self.routing_table[destination][index_of_min_packet_loss]), min_ETX)
        else:
            return copy.deepcopy(self.routing_table[destination][index_of_min_packet_loss])

######## IERP ########

    def ierp(self, destination: int, packet = None):
        if (self.routing_table.get(destination) is not None):
            #print("Destination in zone")

            if (packet == None):
                self.paths_to_destinations.append(self.get_best_path_iarp(destination))
                return

            packet["Type"] = "Reply"
            self.BRP_packet_queue.put(packet)
            yield self.env.process(self.send_BRP_packet())
        else:
            ##print(f"Node {self.node_id} sending BRP packet to peripheral nodes")
            self.find_periphiral_nodes()            
            if (packet != None):
                self.generate_BRP_packet(destination, packet)
            else:
                self.generate_BRP_packet(destination)
            yield self.env.process(self.send_BRP_packet())

    def generate_BRP_packet(self, destination: int, currentPacket = None):
        if (currentPacket == None):
            for node_id in self.periphiral_nodes:
                BRP_packet = {
                    "Query Source Address": self.node_id,
                    "Query Destination Address": destination,
                    "Query ID": self.node_id,
                    "Query Extension" : True,
                    "Previous Bordercast Address" : self.node_id,
                    "Path" : [self.node_id],
                    "Periphiral nodes" : [self.node_id],
                    "Type" : "Bordercast",
                    "Next_node": node_id       # Periphiral node
                }
                self.BRP_packet_queue.put(BRP_packet)

            for packet in self.BRP_packet_queue.queue:
                for node_id in self.periphiral_nodes:
                    packet["Periphiral nodes"].append(node_id)

        else:
            new_nodes = []
            for peri_id in self.periphiral_nodes:
                not_periphiral_node = True
                for path_node_id in currentPacket["Path"]:
                    if (not_periphiral_node == False):
                        break
                    for zone_node_id in self.get_all_nodes_in_zone(path_node_id):
                        if (peri_id == zone_node_id and self.node_id != path_node_id):
                            not_periphiral_node = False
                            break
                        
                if (not_periphiral_node == True):
                    BRP_packet = copy.deepcopy(currentPacket)
                    BRP_packet["Query ID"] = self.node_id
                    BRP_packet["Previous Bordercast Address"] = self.node_id
                    BRP_packet["Next_node"] = peri_id               # Periphiral node
                    self.BRP_packet_queue.put(BRP_packet)
                    new_nodes.append(peri_id)
            
            for packet in self.BRP_packet_queue.queue:
                for node_id in new_nodes:
                    packet["Periphiral nodes"].append(node_id)

    def send_BRP_packet(self):
        while (self.BRP_packet_queue.qsize() > 0):
            yield self.env.timeout(0.1)
            packet = self.BRP_packet_queue.get(0)         

            if (packet["Type"] == "Bordercast"):
                periphiral_node_id = packet["Next_node"]
                ##print(f"Node {self.node_id} Bordercasting to {periphiral_node_id}")
                best_path = self.get_best_path_iarp(periphiral_node_id)
                yield self.env.process(self.find_node_by_id(best_path.pop(0)).receive_BRP_packet(packet, best_path))
            elif (packet["Type"] == "Reply"):
                path = packet["Path"]
                index_dest = path.index(self.node_id) - 1       
                destination_node = self.find_node_by_id(path[index_dest])
                ##print(f"Node {self.node_id} sending reply to
                # {destination_node.node_id}")
                yield self.env.process(destination_node.receive_BRP_packet(packet))

    def receive_BRP_packet(self, packet, best_path = None): 
        yield self.env.timeout(0.1)
        if (packet["Type"] == "Bordercast"):
            ##print(f"Node {self.node_id}: Received Bordercast")
            if (len(best_path) > 0):  
                yield self.env.process(self.forward_BRP_packet(best_path, packet))
            else:
                ##print(f"Periphiral node reached - Node: {self.node_id}")
                packet["Path"].append(self.node_id)
                yield self.env.process(self.ierp(packet["Query Destination Address"], packet))
        elif (packet["Type"] == "Reply"):
            path = packet["Path"]
            ##print(f"Node {self.node_id}: Received Reply")
            if(path[0] == self.node_id):
                ##print(f"Back at origin")
                path.append(packet["Query Destination Address"])  # Add destination to path
                self.paths_to_destinations.append(path)
            else:
                self.BRP_packet_queue.put(packet)
                yield self.env.process(self.send_BRP_packet())   

    def forward_BRP_packet(self, best_path, packet):
        ##print(f"Forwarding to {best_path[0]}")
        yield self.env.timeout(0.1)
        yield self.env.process(self.find_node_by_id(best_path.pop(0)).receive_BRP_packet(packet, best_path))

    def get_best_path_ierp(self, destination : int):
        paths = []
        packet_loss_for_path = []

        for path in self.paths_to_destinations:         ## Check if the path is within the zone of the start node
            if (self.routing_table.get(destination) is not None):
                return path

            asking_node_id = path[0]
            path = path[1:]
            full_path_list = [self.node_id]
            packet_loss_sum = 0        

            for node_id in path:
                path_to_destination, packet_loss = self.nodes[asking_node_id].get_best_path_iarp(node_id, True)
                asking_node_id = node_id
                
                for item in path_to_destination:
                    full_path_list.append(item)
                
                packet_loss_sum += packet_loss
            
            packet_loss_for_path.append(packet_loss_sum)
            paths.append(full_path_list)

        # Find smallest packet_loss for entire path in all paths 
        min_packet_loss = min(packet_loss_for_path)
        index_of_min_packet_loss = packet_loss_for_path.index(min_packet_loss)
        # Returning both periphiral path and full path
        return (self.paths_to_destinations[index_of_min_packet_loss], paths[index_of_min_packet_loss], min_packet_loss)


####### HELPER FUNCTIONS ########

    def find_periphiral_nodes(self):
        self.periphiral_nodes = []
        for key, values in self.routing_table.items():
            is_periphiral_node = True
            for sublist in values:
                if len(sublist) < self.zone_radius:
                    is_periphiral_node = False

            if (is_periphiral_node == True):
                self.periphiral_nodes.append(key)


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

    def update_tables(self, path: list, packet_loss: list):
        path = path[1:]         # Excluding the node itself

        while len(path) >= 1:
            destination = path[-1]                                            
            if not destination in self.routing_table_new:   # Check if key exists 
                self.routing_table_new[destination] = []
                self.metrics_table_new[destination] = []

            not_in_path = True
            for existing_path in self.routing_table_new[destination]:
                if (path == existing_path):
                    not_in_path = False
            
            if (not_in_path == True):
                self.routing_table_new[destination].append(path)            
                self.metrics_table_new[destination].append(packet_loss)       # metrics = number of hops

            path = path[:-1]
            packet_loss = packet_loss[:-1]
    
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
    
    def send_data(self):
        skrald = 0

    def get_all_nodes_in_zone(self, node_id):
        node = self.find_node_by_id(node_id)
        all_zone_nodes = []

        all_zone_nodes.append(node_id)

        for neighbours in node.neighbours:
            all_zone_nodes.append(neighbours.node_id)
        for peri_node in node.periphiral_nodes:
            all_zone_nodes.append(peri_node)

        return all_zone_nodes