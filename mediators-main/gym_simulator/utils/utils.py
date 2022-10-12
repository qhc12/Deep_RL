from scipy.special import ndtri
import sys


def calculate_probability_per_timestep(timesteps, required_probability):
    """
    Function to calculate the probability of success that is needed per timestep, to get to a desired probability of
    success over the entire sequence of timesteps. E.g. you have 10 timesteps, and you want a probability of success
    of 0.4. Then the probability of success in each individual timestep needs to be 0.05 (rounded).

    The function to calculate this is:
    p_a = 1 - (1 - p_r) ^ (1 / t), where p_a is the acceptance prob. per timestep, p_r is the required overall
    acceptance probability, and t is the number of timesteps.
    """
    return 1 - ((1 - required_probability) ** (1 / float(timesteps)))


def calculate_gaussian_distribution(start, end, success_probability, skew=0.0):
    """
    This function calculates mean and standard deviation for a Gaussian distribution such that the probability that a
    number drawn from this distribution is between start and end is equal to the defined success_probability. Skew can
    take a float in the range of [-1.0, 1.0] to shift the mean more to the left or the right within the interval
    [start, end]. If skew == 0, the mean will equal (start - end) / 2.

    The math to calculate mean and sigma is as follows. Let x1 = start, x2 = end, ps = success_probability, and
    pf = fail_probability = 1 - ps.
    Let s = skew.
    Let lb = left percentile and ub = right percentile, and lb + rb = 1.0.
    lb = -0.5 * pf * s + 0.5 * pf
    ub = -0.5 * pf * s + (1 - 0.5 * pf)
    Let z1 and z2 be the values of the quantile function belonging to the left percentile and the right percentile, i.e.
    Pr(X <= z1) = lb and Pr(X <= z2) = ub for the normal distribution with mean = 0 and std = 1.
    We know that z1 = (x1 - mu) / sigma and z2 = (x1 - mu) / sigma
    Solving for sigma and mu gives:
    sigma = (x1 - x2) / (z1 - z2)
    mu = (z1 * x2 - z2 * x1) / (z1 - z2)
    """
    failure_prob = 1.0 - success_probability
    half_p_fail = failure_prob / 2.0
    left_percentile = (-half_p_fail * skew) + half_p_fail
    right_percentile = (-half_p_fail * skew) + (1 - half_p_fail)

    # Epsilon is added to z1 and z2 for the case that left_percentile == 0 or right_percentile == 1
    epsilon = 0.0000001
    z1 = ndtri(left_percentile + epsilon)
    z2 = ndtri(right_percentile - epsilon)

    sigma = (start - end) / (z1 - z2)
    mu = ((z1 * end) - (z2 * start)) / (z1 - z2)
    return mu, sigma


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


def increment_level(level):
    """
    Increase current level by one (if not max level already)
    """
    if level == "L0":
        return "L2"
    elif level == "L2":
        return "L3"
    elif level == "L3" or level == "L4":
        return "L4"


def decrement_level(level):
    """
    Decrease current level by one (if not min level already)
    """
    if level == "L0" or level == "L2":
        return "L0"
    elif level == "L3":
        return "L2"
    elif level == "L4":
        return "L3"
