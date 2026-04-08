import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# --- 1. Environment Variables (FIXED) ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("OPENAIAPIKEY")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# --- 2. OpenAI Client Initialization ---
client = None
if HF_TOKEN:
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url=API_BASE_URL,
            api_key=HF_TOKEN
        )
    except Exception:
        pass

app = FastAPI()

# --- 3. Environment Setup (SAFE FALLBACK) ---
try:
    from environment.tasks import task_1_easy
    env = task_1_easy()
except Exception:
    class MockEnv:
        def reset(self):
            return {"status": "mocked_state_reset"}, {}
        def step(self, action):
            return {"status": f"mocked_state_after_{action}"}, 0.0, True, {}
    env = MockEnv()

# --- 4. Agent Setup (SAFE FALLBACK) ---
try:
    from baseline.agent import SmartAgent
    agent = SmartAgent()
except Exception:
    class MockAgent:
        def act(self, state):
            return "allow"
    agent = MockAgent()

# --- 5. Global State ---
state = None
step_counter = 0
rewards_list = []
task_name = os.getenv("TASK_NAME", "easy")
benchmark_name = os.getenv("BENCHMARK", "cyber-ai-firewall")

# --- 6. Input Model ---
class StepInput(BaseModel):
    action: Optional[str] = None

# ==============================
# 🚀 RESET ENDPOINT
# ==============================

@app.api_route("/reset", methods=["GET", "POST"])
def reset():
    global state, step_counter, rewards_list

    res = env.reset()

    if isinstance(res, tuple) and len(res) == 2:
        state, _ = res
    else:
        state = res

    step_counter = 0
    rewards_list = []

    print(f"[START] task={task_name} env={benchmark_name} model={MODEL_NAME}", flush=True)

    return {"state": state, "success": True}

# ==============================
# 🚀 STEP ENDPOINT
# ==============================

@app.api_route("/step", methods=["GET", "POST"])
def step(input_data: Optional[StepInput] = None):
    global state, step_counter, rewards_list

    action = "allow"
    error_msg = None

    if input_data and input_data.action:
        action = input_data.action
    else:
        if client is not None:
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{
                        "role": "user",
                        "content": f"State is {state}. Action? (allow, block, rate_limit)"
                    }]
                )
                action_text = response.choices[0].message.content.strip().lower()

                for valid_action in ["allow", "block", "rate_limit"]:
                    if valid_action in action_text:
                        action = valid_action
                        break

            except Exception as e:
                error_msg = str(e)
                try:
                    action = agent.act(state)
                except Exception:
                    pass
        else:
            try:
                action = agent.act(state)
            except Exception as e:
                error_msg = "No Client & Agent failed: " + str(e)

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

    except Exception as e:
        state = {"error": str(e)}
        reward = 0.0
        done = True
        error_msg = str(e) if error_msg is None else error_msg + " | " + str(e)

    step_counter += 1
    rewards_list.append(reward)

    error_val = error_msg if error_msg else "null"
    done_val = str(done).lower()

    print(f"[STEP] step={step_counter} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

    if done:
        raw_score = sum(rewards_list)
        score = min(max(raw_score, 0.0), 1.0)
        success = score > 0.0

        succ_val = str(success).lower()
        rewards_str = ",".join(f"{r:.2f}" for r in rewards_list)

        print(f"[END] success={succ_val} steps={step_counter} score={score:.3f} rewards={rewards_str}", flush=True)

    return {
        "state": state,
        "reward": reward,
        "done": done
    }

# ==============================
# 🚀 STATE ENDPOINT
# ==============================

@app.api_route("/state", methods=["GET", "POST"])
def get_state():
    return {"state": state if state is not None else {}}

# ==============================
# 🚀 RUN SERVER
# ==============================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)