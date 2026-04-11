import os
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional, Any

app = FastAPI()

# --- Global State ---
state = [0, 0, 0]
step_counter = 0
rewards_list = []

# --- Request Models ---
class ResetRequest(BaseModel):
    task_id: str
    seed: int

class StepInput(BaseModel):
    action: Optional[str] = None


# --- Utility ---
def _normalize_observation(value: Any):
    if isinstance(value, list) and len(value) == 3:
        return value
    return [0, 0, 0]


# =====================================================
# 🔥 RESET ENDPOINT (STRICT REQUIRED FORMAT)
# =====================================================
@app.post("/reset")
def reset(req: ResetRequest):
    global state, step_counter, rewards_list

    step_counter = 0
    rewards_list = []

    # Initialize environment state
    state = [0, 0, 0]

    return {
        "task_id": req.task_id,
        "seed": req.seed,
        "observation": state
    }


# =====================================================
# 🚀 STEP ENDPOINT
# =====================================================
@app.post("/step")
def step(input_data: Optional[StepInput] = None):
    global state, step_counter, rewards_list

    action = "allow"
    if input_data and input_data.action:
        action = input_data.action

    # Simulated environment logic
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


# =====================================================
# 📊 STATE ENDPOINT
# =====================================================
@app.get("/state")
def get_state():
    return {
        "state": state if isinstance(state, list) else [0, 0, 0]
    }


# =====================================================
# ▶️ RUN SERVER
# =====================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7860)