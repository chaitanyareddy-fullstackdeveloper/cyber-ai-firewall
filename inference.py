import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# --- 1. Environment Variables ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("OPENAIAPIKEY")

# --- 2. OpenAI Client Initialization (SAFE) ---
client = None
if HF_TOKEN:
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url=API_BASE_URL,
            api_key=HF_TOKEN
        )
    except Exception:
        client = None

# --- 3. FastAPI App ---
app = FastAPI()

# --- 4. Mock / Real Environment ---
try:
    from environment.tasks import task_1_easy
    env = task_1_easy()
except Exception:
    class MockEnv:
        def reset(self):
            return [0, 0, 0], {}
        def step(self, action):
            return [0, 1, 0], 1.0, True, {}
    env = MockEnv()

# --- 5. Agent (Fallback Safe) ---
try:
    from baseline.agent import SmartAgent
    agent = SmartAgent()
except Exception:
    class MockAgent:
        def act(self, state):
            return "allow"
    agent = MockAgent()

# --- 6. Global State ---
state = None
step_counter = 0
rewards_list = []

# --- 7. Request Models ---
class ResetRequest(BaseModel):
    task_id: str
    seed: int

class StepInput(BaseModel):
    action: Optional[str] = None

# --- 8. RESET ENDPOINT ---
@app.post("/reset")
def reset(req: ResetRequest):
    global state, step_counter, rewards_list

    res = env.reset()

    if isinstance(res, tuple) and len(res) == 2:
        state, _ = res
    else:
        state = res

    step_counter = 0
    rewards_list = []

    return {
        "observation": state if isinstance(state, list) else [0, 0, 0],
        "info": {}
    }

# --- 9. STEP ENDPOINT ---
@app.post("/step")
def step(input_data: Optional[StepInput] = None):
    global state, step_counter, rewards_list

    action = "allow"

    # Use provided action or fallback to agent
    if input_data and input_data.action:
        action = input_data.action
    else:
        try:
            action = agent.act(state)
        except Exception:
            action = "allow"

    try:
        res = env.step(action)

        if isinstance(res, tuple) and len(res) >= 3:
            state = res[0]
            reward = float(res[1])
            done = bool(res[2])
        else:
            state = res
            reward = 0.0
            done = True

    except Exception:
        state = [0, 0, 0]
        reward = 0.0
        done = True

    step_counter += 1
    rewards_list.append(reward)

    return {
        "observation": state if isinstance(state, list) else [0, 0, 0],
        "reward": reward,
        "done": done,
        "info": {}
    }

# --- 10. STATE ENDPOINT ---
@app.get("/state")
def get_state():
    return {
        "state": state if state is not None else {}
    }

# --- 11. RUN SERVER ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)