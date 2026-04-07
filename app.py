import gradio as gr
import matplotlib.pyplot as plt
import random
import time
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ==============================
# 🔐 OpenAI Setup
# ==============================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("MODEL_NAME")

# ==============================
# 🧠 AI Decision
# ==============================

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

    except:
        return "allow"

# ==============================
# Core Logic
# ==============================

def detect_attack(state):
    return state[0] > 10 or state[1] or state[2] > 400

def generate_random_state():
    return (
        random.randint(0, 25),
        random.choice([True, False]),
        random.uniform(50, 800)
    )

def process_state(state, history):
    action = ai_decision(state)
    is_attack = detect_attack(state)

    reward = 10 if (is_attack and action in ["block", "rate_limit"]) else (
        5 if (not is_attack and action == "allow") else -5
    )

    history.append({
        "state": state,
        "action": action,
        "reward": reward
    })

    history = history[-20:]

    # Graph
    plt.figure()
    plt.bar(["Reward"], [reward])
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

# ==============================
# Manual Mode
# ==============================

def manual_mode(failed, spike, rate, history):
    state = (failed or 0, spike or False, rate or 0)
    result, graph, history = process_state(state, history)
    return result, graph, "Analysis Completed", history

# ==============================
# 🔴 STREAM CONTROL
# ==============================

def toggle_stream(is_streaming):
    return not is_streaming, (
        "Stop Live Stream" if not is_streaming else "Start Live Stream"
    )

def auto_stream(history, is_streaming):
    while is_streaming:
        state = generate_random_state()
        result, graph, history = process_state(state, history)
        yield result, graph, "Live Monitoring Running...", history
        time.sleep(1)

# ==============================
# Stop Stream
# ==============================

def stop_stream():
    return "Live streaming stopped", "Start Live Stream"

# ==============================
# Controls
# ==============================

def clear_history():
    return "History Cleared", None, []

def download_history(history):
    path = "history.json"
    with open(path, "w") as f:
        json.dump(history, f)
    return path

# ==============================
# UI
# ==============================

with gr.Blocks() as demo:
    gr.Markdown("# 🛡️ CyberShield AI Dashboard")

    session_history = gr.State([])
    is_streaming = gr.State(False)

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

    # Toggle Start/Stop
    stream_btn.click(
        toggle_stream,
        inputs=[is_streaming],
        outputs=[is_streaming, stream_btn]
    ).then(
        auto_stream,
        inputs=[session_history, is_streaming],
        outputs=[output_text, output_graph, status, session_history]
    )

    # Stop button logic
    stream_btn.click(
        stop_stream,
        inputs=[],
        outputs=[status, stream_btn]
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
