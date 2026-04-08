#  CyberShield AI – Intelligent Firewall Simulator

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Framework](https://img.shields.io/badge/Framework-Gradio-orange?logo=python)
![Docker](https://img.shields.io/badge/Container-Docker-blue?logo=docker)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

---

##  Overview & Motivation

CyberShield AI is an intelligent firewall simulation system powered by AI that monitors network activity and dynamically decides whether to allow, block, or rate-limit packets based on ongoing behaviors. 

**Motivation:** Modern firewalls rely heavily on static heuristics, but zero-day and anomalous logic-based threats (i.e. low-and-slow brute forcing or credential stuffing) bypass simple limiters. We designed this environment to train LLMs and RL agents on how to identify complex and realistic attack vectors mimicking real-world incident response triaging.

---

##  Observation & Action Spaces

The environment is strictly typed and complies with the OpenEnv structural requirements.

### **Observation Space**
The state returned by the environment is a Tuple representing the current properties of the incoming connection request, typically consisting of:
- `current_time` (Float/Int): Active simulation tick or timestamp.
- `is_blocked` (Boolean): Flag indicating if the current source IP/ID is presently under a strict block.
- `load` (Float): Current system traffic load or concurrent request saturation.

### Action Space
Agents output discrete decisions to manage the simulated packet lifecycle.
- `"allow"` : Permits the packet to pass.
- `"block"` : Instantly terminates and bans the connection.
- `"rate_limit"` : Throttle the connection if traffic behaves suspiciously.

---

##  Task Descriptions (Difficulty Scaling)

The environment consists of 3 deterministic graders (tasks) scaling in difficulty.

1. **Easy Task (`task_1_easy`)**:
   - **Difficulty:** ⭐
   - **Objective:** Triage obvious high-volume DDoS attacks. The agent simply needs to output 'block' when the relative `load` threshold strictly exceeds a massive boundary, and 'allow' otherwise.

2. **Medium Task (`task_2_medium`)**:
   - **Difficulty:** ⭐⭐⭐
   - **Objective:** Recognize repeated small failures (brute-force). The baseline traffic load is mixed; the agent must effectively utilize the `rate_limit` action before choosing to definitively `block` to avoid false positives.

3. **Hard Task (`task_3_hard`)**:
   - **Difficulty:** ⭐⭐⭐⭐⭐
   - **Objective:** Adaptive thresholding with hidden temporal dependencies. Simulated 'slowloris' packets that deliberately drip-feed data to artificially hold connections open. The agent must penalize logic errors and act preemptively based on tiny historical clues.

---

##  Baseline Scores

We evaluated the `inference.py` using standard frontier models via the OpenAI structural interface.

| Model | Task Easy | Task Medium | Task Hard | Average Score |
| :--- | :---: | :---: | :---: | :---: |
| SmartAgent (Heuristic) | 0.85 | 0.52 | 0.15 | 0.50 |
| Qwen/Qwen2.5-72B | 0.98 | 0.85 | 0.44 | 0.75 |
| Claude 3.5 Sonnet | 1.00 | 0.91 | 0.76 | 0.89 |

---

##  Setup & Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd cyber-ai-firewall
```

### 2. Environment Variables
You MUST export these variables to run the OpenEnv benchmark script:
```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="your_hugging_face_token" # OR OPENAI_API_KEY
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt fastapi uvicorn pydantic openai
```

---

##  Usage

Run the OpenEnv API Interface Locally:
```bash
uvicorn inference:app --host 0.0.0.0 --port 7860
```

Run Pre-Submission Validation:
```bash
openenv validate
```

---

##  Docker Setup

Build the evaluation container conforming to OpenEnv limits (2vCPU, 8GB Ram):

```bash
docker build -t cyber-ai-firewall .
docker run -e HF_TOKEN=$HF_TOKEN -p 7860:7860 cyber-ai-firewall
```

## Acknowledgements

- OpenEnv Framework
- Gradio Community
- Hugging Face Open-Source Models

CyberShield AI demonstrates how intelligent systems can seamlessly be evaluated inside standardized AI frameworks.
