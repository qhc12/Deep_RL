import csv
import os
import pickle

import yaml


def map_road_type(road_class):
    if road_class == "city":
        return "URBAN"
    elif road_class == "rural_major" or road_class == "rural_minor":
        return "PROVINCIAL"
    elif road_class == "highway_link" or road_class == "highway":
        return "HIGHWAY"


def parse_tabular_route(file):
    """
    Parse tabular route.
    """
    final_road = []
    turn_events = []
    curvature_events = []
    roundabout_events = []
    odd_events = []
    # TODO FOR LATER
    road_work_events = []
    lane_marking_events = []
    current_position = 0.0
    edge_positions = {}

    with open(file, newline='') as route:
        reader = csv.DictReader(route)
        prev_row = None
        for row in reader:
            edge_id = int(row["edge_id"])
            position = float(row["cumul_length"])
            edge_positions[edge_id] = position
            road_type = row["road_class"]
            road_length = float(row["length"])
            speed = int(row["speed_limit"])
            if len(final_road) > 0 and final_road[-1][0] == road_type and final_road[-1][2] == speed:
                final_road[-1][1] = final_road[-1][1] + road_length
            else:
                final_road.append([road_type, road_length, speed])

            # If within_odd_static == 0, put in ODD
            if row["within_odd_static"] == "0":
                if prev_row and prev_row["within_odd_static"] == "0":
                    odd_events[-1][2] += road_length
                else:
                    odd_events.append(["ODD", current_position, current_position + road_length])

            # If turn == 1, put in Turn
            if row["turn"] == "1":
                if prev_row and prev_row["turn"] == "1":
                    turn_events[-1][2] = turn_events[-1][2] + road_length
                else:
                    turn_events.append(["Turn", current_position, current_position + road_length])

            # If turn == 1, put in Turn
            if not (row["curvature"] == "slightly_curved" or row["curvature"] == "straight"):
                if prev_row and not (prev_row["curvature"] == "slightly_curved" or prev_row["curvature"] == "straight"):
                    curvature_events[-1][2] = curvature_events[-1][2] + road_length
                else:
                    curvature_events.append(["Curvature", current_position, current_position + road_length])

            # If roundabout == 1, also put in Roundabout
            if row["roundabout"] == "1":
                if prev_row and prev_row["intersection"] == "1" or prev_row["roundabout"] == "1":
                    roundabout_events[-1][2] += road_length
                else:
                    roundabout_events.append(["Roundabout", current_position, current_position + road_length])

            # If ambiguous == 1, put in Poor Lane Marking
            if row["center_lane"] == "0" or row["right_lane"] == "0" or row["ambiguous"] == "1":
                if prev_row and (prev_row["center_lane"] == "0" or prev_row["right_lane"] == "0" or
                                 prev_row["ambiguous"] == "1"):
                    lane_marking_events[-1][2] += road_length
                else:
                    lane_marking_events.append(["PoorLaneMarking", current_position, current_position + road_length])

            current_position += road_length
            prev_row = row

        final_static_events = sorted([[event[0], round(event[1] / 1000.0, 3), round(event[2] / 1000.0, 3)] for event in
                                      turn_events + curvature_events + roundabout_events + lane_marking_events +
                                      odd_events],
                                     key=lambda entry: entry[1])
        final_road = [[road_part[0], round(road_part[1] / 1000.0, 2), road_part[2]] for road_part in final_road]

        return final_road, final_static_events, edge_positions


road, static_events, edge_pos = parse_tabular_route("tabular_route_R3_v3.csv")
road_yaml = {"road": road, "static_events": static_events}
with open("new_route.yaml", 'w', newline='', encoding='utf-8') as f:
    yaml.safe_dump(road_yaml, f, default_flow_style=None)

with open('edge_positions.pkl', 'wb') as f:
    pickle.dump(edge_pos, f)
