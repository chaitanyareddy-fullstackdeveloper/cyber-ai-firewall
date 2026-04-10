import os
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional, Any

app = FastAPI()

# Global state
state = [0, 0, 0]
step_counter = 0
rewards_list = []

# Request models
class ResetRequest(BaseModel):
    task_id: str
    seed: int

class StepInput(BaseModel):
    action: Optional[str] = None


def _normalize_observation(value: Any):
    """
    Always return a simple 3-item list so OpenEnv gets a stable observation.
    """
    if isinstance(value, list) and len(value) == 3:
        return value
    return [0, 0, 0]


# OpenEnv reset: POST OK
@app.api_route("/reset", methods=["POST", "GET"])
def reset(req: ResetRequest = Body(...)):
    global state, step_counter, rewards_list

    step_counter = 0
    rewards_list = []
    state = [0, 0, 0]

    return {
        "observation": state,
        "info": {}
    }


# OpenEnv step: POST OK
@app.api_route("/step", methods=["POST", "GET"])
def step(input_data: Optional[StepInput] = None):
    global state, step_counter, rewards_list

    action = "allow"
    if input_data and input_data.action:
        action = input_data.action

    if action == "block":
        state = [0, 1, 0]
        reward = 1.0
        done = True
    elif action == "rate_limit":
        state = [1, 0, 0]
        reward = 0.5
        done = False
    else:
        state = [0, 0, 1]
        reward = 0.2
        done = False

    state = _normalize_observation(state)
    step_counter += 1
    rewards_list.append(reward)

    return {
        "observation": state,
        "reward": reward,
        "done": done,
        "info": {}
    }


# State endpoint: GET OK
@app.api_route("/state", methods=["GET", "POST"])
def get_state():
    return {
        "state": state if isinstance(state, list) else [0, 0, 0]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)