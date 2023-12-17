import pandas as pd

headers = [f"sat{i}" for i in range(0,66)]
data_518 = []
data_618 = []
data_718 = []
data_818 = []
data_918 = []

data_518.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_18_100_min_200_samples_518.csv", names=headers))
data_518.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_30_100_min_200_samples_518.csv", names=headers))
data_518.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_42_100_min_200_samples_518.csv", names=headers))
data_518.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_54_100_min_200_samples_518.csv", names=headers))
data_518.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_66_100_min_200_samples_518.csv", names=headers))

data_618.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_18_100_min_200_samples_618.csv", names=headers))
data_618.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_30_100_min_200_samples_618.csv", names=headers))
data_618.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_42_100_min_200_samples_618.csv", names=headers))
data_618.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_54_100_min_200_samples_618.csv", names=headers))
data_618.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_66_100_min_200_samples_618.csv", names=headers))

data_718.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_18_100_min_200_samples_718.csv", names=headers))
data_718.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_30_100_min_200_samples_718.csv", names=headers))
data_718.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_42_100_min_200_samples_718.csv", names=headers))
data_718.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_54_100_min_200_samples_718.csv", names=headers))
data_718.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_66_100_min_200_samples_718.csv", names=headers))

data_818.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_18_100_min_200_samples_818.csv", names=headers))
data_818.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_30_100_min_200_samples_818.csv", names=headers))
data_818.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_42_100_min_200_samples_818.csv", names=headers))
data_818.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_54_100_min_200_samples_818.csv", names=headers))
data_818.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_66_100_min_200_samples_818.csv", names=headers))

data_918.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_18_100_min_200_samples_918.csv", names=headers))
data_918.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_30_100_min_200_samples_918.csv", names=headers))
data_918.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_42_100_min_200_samples_918.csv", names=headers))
data_918.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_54_100_min_200_samples_918.csv", names=headers))
data_918.append(pd.read_csv("Zone-routing-protocol/Mobility_models/walkerStar/walkerStar_66_100_min_200_samples_918.csv", names=headers))

def get_element(value):
    element_mapping = {
        18: 0,
        30: 1,
        42: 2,
        54: 3,
        66: 4
    }

    return element_mapping.get(value, -1)

def get_position_data(satIndex: int, num_nodes : int, altitude : int):
    if altitude == 518:
        return data_518[get_element(num_nodes)].iloc[:,satIndex]
    elif altitude == 618:
        return data_618[get_element(num_nodes)].iloc[:,satIndex]
    elif altitude == 718:
        return data_718[get_element(num_nodes)].iloc[:,satIndex]
    elif altitude == 818:
        return data_818[get_element(num_nodes)].iloc[:,satIndex]
    elif altitude == 918:
        return data_918[get_element(num_nodes)].iloc[:,satIndex]