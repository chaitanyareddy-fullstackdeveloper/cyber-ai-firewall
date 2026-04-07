from environment.env import CyberEnv


def task_1_easy():
    return CyberEnv({"scenario": "brute_force"})


def task_2_medium():
    return CyberEnv({"scenario": "traffic_spike"})


def task_3_hard():
    return CyberEnv({"scenario": "mixed"})