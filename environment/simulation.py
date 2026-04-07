import random
from environment.state import State


class Simulation:
    def __init__(self, scenario="normal"):
        self.scenario = scenario

    def generate_state(self):
        if self.scenario == "brute_force":
            return State(
                failed_logins=random.randint(10, 20),
                traffic_spike=False,
                request_rate=random.uniform(50, 150),
            )

        elif self.scenario == "traffic_spike":
            return State(
                failed_logins=random.randint(0, 5),
                traffic_spike=True,
                request_rate=random.uniform(400, 800),
            )

        elif self.scenario == "mixed":
            return State(
                failed_logins=random.randint(0, 20),
                traffic_spike=random.choice([True, False]),
                request_rate=random.uniform(50, 800),
            )

        else:  # normal
            return State(
                failed_logins=random.randint(0, 3),
                traffic_spike=False,
                request_rate=random.uniform(50, 200),
            )