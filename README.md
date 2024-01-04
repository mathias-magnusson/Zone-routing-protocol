# Zone-routing-protocol
Python implementation for Zone Routing Protocol in a satellite network

## Main
In main the Nodes (satellites) are created based on a chosen mobility model. Main also creates the SimPy environment where the processes are made.

### Prosesses
The simulation consists of three processes created in main. 
The network_process is the main process, which calls the IARP_process once each 30th second, and calls the send_data_process continuously. 

The IARP_process updates the routing tables for each node, and calculates the number of packets and the time it takes to compute them. 

The send_data_process checks whether it is time to send some data. If this is true, a route will be computed with IERP if the destination node is not already within the zone of the origin node. 
When all the possible routes to a destination have been calculated the number of packets and time it took to compute them is printed. 

## Simulation
The simulation is running for 6000 seconds (100 minutes), which is a bit over one orbit around Earth.

It is run by choosing a mobility model / satellite constellation. This model is based on the number of nodes (num_nodes) and the altitude chosen. 
Furthermore, in main the zone radius is chosen, to figure out when it is optimal.  

The planned tranmissions are loaded based on the number of nodes if the manually created planned_transmissions are used. Otherwise the transmissions can be generated randomly with generate_planned_transmission().

When all routes to a destination have been found the best one, based on the accumulated ETX value, is printed and can be evaluated with MATLAB in the SatelliteView.

## MATLAB
The MATLAB code is found in the Mobility_models folder, which also includes all the mobility models of different constellations. 
Within the MATLAB file called MobilityModel.m, new constellations can be created if desired. Furthermore, by looking at the SatelliteView, the routes found in Python can be verified. 
