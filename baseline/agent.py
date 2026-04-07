import random

class SmartAgent:
    def __init__(self):
        self.history = []

    def act(self, state):
        failed_logins, spike, rate = state

        # Basic intelligence
        if failed_logins > 12:
            action = "block"
        elif spike and rate > 500:
            action = "rate_limit"
        elif rate > 600:
            action = "block"
        else:
            # slight randomness (exploration)
            action = random.choice(["allow", "rate_limit"])

        self.history.append((state, action))
        return action