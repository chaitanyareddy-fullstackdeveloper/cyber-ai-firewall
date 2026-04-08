import gradio as gr
import matplotlib.pyplot as plt
import random
import time
import json
import os
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()



client = OpenAI(api_key=os.getenv("OPENAIAPIKEY"))
MODEL = os.getenv("MODEL_NAME")



def generate_training_data(n=500):
    X, y = [], []

    for _ in range(n):
        failed = random.randint(0, 25)
        spike = random.choice([0, 1])
        rate = random.uniform(50, 800)

        label = 1 if (failed > 10 or spike == 1 or rate > 400) else 0

        X.append([failed, spike, rate])
        y.append(label)

    return np.array(X), np.array(y)

X, y = generate_training_data()
model = DecisionTreeClassifier()
model.fit(X, y)

def detect_attack_ml(state):
    data = np.array([[state[0], int(state[1]), state[2]]])
    return model.predict(data)[0] == 1



def ai_decision(state):
    try:
        prompt = f"""
        You are a cybersecurity firewall AI.

        State:
        - Failed Logins: {state[0]}
        - Traffic Spike: {state[1]}
        - Request Rate: {state[2]}

        Choose ONE action:
        allow / block / rate_limit

        Only return the action.
        """

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        action = response.choices[0].message.content.strip().lower()
        return action if action in ["allow", "block", "rate_limit"] else "allow"

    except Exception as e:
        print("AI Error:", e)
        return "allow"



def generate_random_state():
    return (
        random.randint(0, 25),
        random.choice([True, False]),
        random.uniform(50, 800)
    )

def process_state(state, history):
    action = ai_decision(state)
    is_attack = detect_attack_ml(state)

    reward = 10 if (is_attack and action in ["block", "rate_limit"]) else (
        5 if (not is_attack and action == "allow") else -5
    )

    history.append({
        "state": state,
        "action": action,
        "reward": reward
    })

    # keep only last 10 safely
    if len(history) > 10:
        history.pop(0)

    # Graph
    rewards = [h["reward"] for h in history]

    plt.figure()
    plt.plot(rewards)
    plt.title("Reward Trend")
    fig = plt.gcf()
    plt.close()

    alert = "🚨 Attack Detected" if is_attack else "✅ Normal Traffic"

    history_html = "".join([
        f"<div>• {h['state']} → {h['action']} ({h['reward']})</div>"
        for h in history
    ])

    result = f"""
    <b>{alert}</b><br>
    <b>State:</b> {state}<br>
    <b>Action:</b> {action}
    <hr>
    <b>History:</b><br>{history_html}
    """

    return result, fig, history



def manual_mode(failed, spike, rate, history):
    state = (failed or 0, spike or False, rate or 0)
    result, graph, history = process_state(state, history)
    return result, graph, "Analysis Completed", history



def auto_stream(history):
    while True:
        state = generate_random_state()
        result, graph, history = process_state(state, history)
        yield result, graph, "Live Monitoring Running...", history
        time.sleep(1)




def clear_history():
    return "History Cleared", None, []

def download_history(history):
    path = "history.json"
    with open(path, "w") as f:
        json.dump(history, f)
    return path


with gr.Blocks() as demo:
    gr.Markdown("#  CyberShield AI Dashboard")

    session_history = gr.State([])

    with gr.Row():
        with gr.Column():
            failed = gr.Number(label="Failed Logins", value=5)
            spike = gr.Checkbox(label="Traffic Spike")
            rate = gr.Number(label="Request Rate", value=100)

            analyze_btn = gr.Button("Analyze")

        with gr.Column():
            output_text = gr.HTML()
            output_graph = gr.Plot()

    status = gr.Textbox(label="System Status")

    analyze_btn.click(
        manual_mode,
        inputs=[failed, spike, rate, session_history],
        outputs=[output_text, output_graph, status, session_history]
    )

    gr.Markdown("### Live Monitoring")

    stream_btn = gr.Button("Start Live Stream")
    stop_btn = gr.Button("Stop Live Stream")

    # Start streaming
    stream_event = stream_btn.click(
        auto_stream,
        inputs=[session_history],
        outputs=[output_text, output_graph, status, session_history]
    )

    # Stop streaming (correct way)
    stop_btn.click(
        None,
        None,
        None,
        cancels=[stream_event]
    )

    # Controls
    clear_btn = gr.Button("Clear History")
    download_btn = gr.Button("Download History")
    file_output = gr.File()

    clear_btn.click(
        clear_history,
        outputs=[status, output_graph, session_history]
    )

    download_btn.click(
        download_history,
        inputs=[session_history],
        outputs=file_output
    )

demo.queue().launch()