from gym_simulator.evaluation.safety_types import SafetyType


def get_safety_color(safety_type):
    """
    Return color based on safety type.
    """
    if safety_type == SafetyType.CRITICAL:
        return 'red'
    if safety_type == SafetyType.MISC:
        return 'deeppink'
    if safety_type == SafetyType.UNCOMFORTABLE:
        return 'blue'
