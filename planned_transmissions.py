import random

def generate_planned_transmission():
    # Number of nodes and time interval
    random.seed(41)
    num_nodes = 66
    time_interval = 6000  # 0 to 6000 seconds = 100 minutes
    num_planned_transmissions = 1000

    # Initialize a contact plan as a list of tuples (node1, node2, start_time)
    contact_plan = []

    # Randomly generate contacts between nodes
    for _ in range(num_planned_transmissions): 
        node1, node2 = random.sample(range(num_nodes), 2)
        start_time = random.randint(0, time_interval)
        contact_plan.append((node1, node2, start_time))

    # Sort the contact plan by start time
    contact_plan.sort(key=lambda x: x[2])

    return contact_plan


    