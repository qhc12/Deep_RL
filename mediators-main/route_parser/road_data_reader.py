import csv
import pickle


def parse_route_data(file):
    """
    Parse additional data from a single drive.
    """
    timestamps = []
    route_data = {}

    with open('edge_positions.pkl', 'rb') as f:
        edge_positions = pickle.load(f)

    with open(file, newline='') as route:
        reader = csv.DictReader(route)
        start_time = 0
        for i, row in enumerate(reader):
            unix_time = float(row['unixtimestamp'])
            if i == 0:
                start_time = unix_time
            time_passed = unix_time - start_time
            timestamps.append(time_passed)
            edge_id = int(row['edge_id'])
            end_position_edge = edge_positions[edge_id]
            meters_left_on_edge = float(row['length_m_left_on_edge'])
            position = end_position_edge - meters_left_on_edge
            speed = float(row['vehicle_speed_kmh'])
            ttaf = float(row['TTAF_manual_to_L2_this'])
            ttau = float(row['TTAU_L2_this'])
            route_data[time_passed] = {
                'position': position,
                'speed': speed,
                'ttaf': ttaf,
                'ttau': ttau
            }

    route_data['timestamps'] = timestamps

    with open('route_data.pkl', 'wb') as f:
        pickle.dump(route_data, f)


parse_route_data("routedata_10jan2022_v2_pessim.csv")
