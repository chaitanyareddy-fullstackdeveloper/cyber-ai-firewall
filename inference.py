import os
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional

# --- FastAPI App ---
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

# --- RESET ENDPOINT (STRICT FIX) ---
@app.post("/reset")
def reset(req: ResetRequest = Body(...)):
    global state, step_counter, rewards_list

    # Always reset to default valid observation
    state = [0, 0, 0]
    step_counter = 0
    rewards_list = []

    return {
        "observation": state,
        "info": {}
    }

# --- STEP ENDPOINT ---
@app.post("/step")
def step(input_data: Optional[StepInput] = None):
    global state, step_counter, rewards_list

    # Default action
    action = "allow"

    if input_data and input_data.action:
        action = input_data.action

    # Simple logic for demo
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

    step_counter += 1
    rewards_list.append(reward)

    return {
        "observation": state,
        "reward": reward,
        "done": done,
        "info": {}
    }

# --- STATE ENDPOINT ---
@app.get("/state")
def get_state():
    return {
        "state": state
    }

# --- RUN SERVER ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)