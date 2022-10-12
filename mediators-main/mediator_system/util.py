import sys


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def level_index(level, includes_l0=False):
    """
    Gets the index of a value in an array corresponding to an automation level. If L0 is included in the array,
    indexing is:
    L0 -> 0
    L2 -> 1
    L3 -> 2
    L4 -> 3
    Else:
    L2 -> 0
    L3 -> 1
    L4 -> 2
    """
    l0_shift = int(includes_l0)
    if level == "L0":
        return 0
    elif level == "L2":
        return 0 + l0_shift
    elif level == "L3":
        return 1 + l0_shift
    elif level == "L4":
        return 2 + l0_shift
    return sys.maxsize


def get_position_in_time(speeds, current_position, time):
    """
    Calculates the position the car will be in in time seconds, given the speed limits of the road. Speeds is a list
    of tuples in the form of (speed_limit, end), where end specifies the ending position of that speed limit on the
    road, where ending position is defined as the distance travelled since the start of the route (in KM).
    current_position specifies the current location of the car as distance travelled (in KM) since the start.
    """
    current_speed_index = next(i for i, (_, end) in enumerate(speeds) if
                               end >= current_position and (i == 0 or current_position > speeds[i - 1][1]))

    for (speed, end) in speeds[current_speed_index:]:
        time_to_end = (float(end - current_position) / speed) * 3600
        if time_to_end > time:
            current_position += (speed * time) / float(3600)
            break
        else:
            current_position = end
            time -= time_to_end

    return current_position
