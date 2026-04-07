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

client = OpenAI(api_key=os.getenv("OPENAIAPIKEY"))
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

        if action not in ["allow", "block", "rate_limit"]:
            return "allow"

        return action

    except Exception as e:
        print("API Error:", e)
        return "allow"

# ==============================
# 🧠 Core Logic
# ==============================

def detect_attack(state):
    failed_logins, spike, rate = state
    return failed_logins > 10 or spike or rate > 400

def generate_random_state():
    return (
        random.randint(0, 25),
        random.choice([True, False]),
        random.uniform(50, 800)
    )

def process_state(state, history):
    failed_logins, spike, rate = state

    failed_logins = failed_logins or 0
    rate = rate or 0
    spike = spike or False

    action = ai_decision((failed_logins, spike, rate))
    is_attack = detect_attack((failed_logins, spike, rate))

    if is_attack:
        reward = 10 if action in ["block", "rate_limit"] else -10
    else:
        reward = 5 if action == "allow" else -5

    ideal_reward = 10 if is_attack else 5
    accuracy = 1.0 if reward > 0 else 0.0

    history.append({
        "state": (failed_logins, spike, rate),
        "action": action,
        "reward": reward
    })
    history = history[-20:]

    plt.figure()
    plt.bar(["Agent", "Ideal"], [reward / 10, ideal_reward / 10])
    plt.title("Performance Comparison")
    fig = plt.gcf()
    plt.close()

    alert = "<h3 style='color:red;'>🚨 Attack Detected</h3>" if is_attack else "<h3 style='color:green;'>✅ Normal Traffic</h3>"

    history_html = "".join([
        f"<div>• {h['state']} → {h['action']} ({h['reward']})</div>"
        for h in history
    ])

    result = f"""
    {alert}
    <b>State:</b> {(failed_logins, spike, rate)} <br>
    <b>Action:</b> {action} <br>
    <b>Accuracy:</b> {accuracy}
    <hr>
    <b>Recent History:</b><br>
    {history_html}
    """

    return result, fig, history

# ==============================
# 🔹 Modes
# ==============================

def manual_mode(failed, spike, rate, history):
    state = (float(failed or 0), bool(spike), float(rate or 0))
    result, graph, history = process_state(state, history)
    return result, graph, "Analysis Completed", history

# ==============================
# 🔴 Streaming Control
# ==============================

def toggle_stream(is_streaming):
    return not is_streaming

def update_button_label(is_streaming):
    return "Stop Live Stream" if is_streaming else "Start Live Stream"

def auto_stream(history, is_streaming):
    if not is_streaming:
        yield "⛔ Live Streaming Stopped", None, "Stopped", history, is_streaming
        return

    for _ in range(50):
        state = generate_random_state()
        result, graph, history = process_state(state, history)

        yield result, graph, "Live Monitoring Running...", history, is_streaming
        time.sleep(1)

        if not is_streaming:
            yield "⛔ Live Streaming Stopped", None, "Stopped", history, is_streaming
            return

# ==============================
# 🗑️ Controls
# ==============================

def clear_history():
    return "History Cleared", None, []

def download_history(history):
    file_path = "user_history.json"
    with open(file_path, "w") as f:
        json.dump(history, f, indent=2)
    return file_path

# ==============================
# 🚀 UI
# ==============================

with gr.Blocks() as demo:

    gr.Markdown("# 🛡️ CyberShield AI Dashboard")

    session_history = gr.State([])
    streaming_state = gr.State(False)

    with gr.Row():

        with gr.Column():
            gr.Markdown("### Input Panel")

            failed = gr.Number(label="Failed Logins", value=5)
            spike = gr.Checkbox(label="Traffic Spike", value=False)
            rate = gr.Number(label="Request Rate", value=100)

            btn = gr.Button("Analyze")

        with gr.Column():
            output_text = gr.HTML()
            output_graph = gr.Plot()

    status = gr.Textbox(label="System Status")

    btn.click(
        fn=manual_mode,
        inputs=[failed, spike, rate, session_history],
        outputs=[output_text, output_graph, status, session_history]
    )

    gr.Markdown("### Live Monitoring")

    stream_btn = gr.Button("Start Live Stream")

    stream_btn.click(
        fn=toggle_stream,
        inputs=[streaming_state],
        outputs=[streaming_state]
    ).then(
        fn=update_button_label,
        inputs=[streaming_state],
        outputs=[stream_btn]
    ).then(
        fn=auto_stream,
        inputs=[session_history, streaming_state],
        outputs=[output_text, output_graph, status, session_history, streaming_state]
    )

    gr.Markdown("### History Controls")

    with gr.Row():
        clear_btn = gr.Button("Clear History")
        download_btn = gr.Button("Download History")

    file_output = gr.File()

    clear_btn.click(
        fn=clear_history,
        inputs=[],
        outputs=[status, output_graph, session_history]
    )

    download_btn.click(
        fn=download_history,
        inputs=[session_history],
        outputs=file_output
    )

print("Server running...")

demo.queue().launch(server_name="0.0.0.0", server_port=7860)
