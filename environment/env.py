from environment.simulation import Simulation
from environment.actions import Action


class CyberEnv:
    def __init__(self, config=None):
        self.config = config or {}
        self.simulation = Simulation(self.config.get("scenario", "normal"))
        self.current_state = None
        self.current_step = 0
        self.max_steps = 10

    def reset(self):
        self.current_step = 0
        self.current_state = self.simulation.generate_state()
        return self.state(), {}

    def state(self):
        return self.current_state.to_tuple()

    def step(self, action):
        self.current_step += 1

        # Convert action safely
        try:
            action = Action(action)
        except ValueError:
            return self.state(), -10, True, {"error": "Invalid action"}

        reward = self._calculate_reward(action)

        # Generate next state
        self.current_state = self.simulation.generate_state()

        done = self.current_step >= self.max_steps

        info = {
            "step": self.current_step
        }

        return self.state(), reward, done, info

    def _calculate_reward(self, action):
        failed_logins, spike, rate = self.current_state.to_tuple()

        is_attack = failed_logins > 10 or spike or rate > 400

        if is_attack:
            if action in [Action.BLOCK, Action.RATE_LIMIT]:
                return 10
            else:
                return -10
        else:
            if action == Action.ALLOW:
                return 5
            else:
                return -5