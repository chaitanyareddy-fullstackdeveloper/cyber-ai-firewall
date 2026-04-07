import random
from baseline.agent import SmartAgent
from visualize import plot_results


def generate_live_state():
    return (
        random.randint(0, 25),
        random.choice([True, False]),
        random.uniform(50, 800)
    )


def get_manual_state():
    try:
        failed_logins = int(input("Enter failed logins: "))
        spike_input = input("Traffic spike (True/False): ")
        spike = spike_input.lower() == "true"
        rate = float(input("Enter request rate: "))
        return (failed_logins, spike, rate)
    except:
        print("Invalid input, using default values")
        return (0, False, 100.0)


def detect_attack(state):
    failed_logins, spike, rate = state
    return failed_logins > 10 or spike or rate > 400


def main():
    agent = SmartAgent()

    print("\n🚀 CyberShield One-Step Smart Demo\n")
    print("1. Auto Mode")
    print("2. Manual Mode")

    choice = input("Enter choice (1/2): ")

    # 👉 ONE STEP ONLY
    if choice == "1":
        state = generate_live_state()
        mode = "Auto"
    elif choice == "2":
        state = get_manual_state()
        mode = "Manual"
    else:
        print("Invalid choice")
        return

    action = agent.act(state)
    is_attack = detect_attack(state)

    # Reward logic
    if is_attack:
        reward = 10 if action in ["block", "rate_limit"] else -10
    else:
        reward = 5 if action == "allow" else -5

    # Metrics
    tp = fp = tn = fn = 0

    if is_attack:
        if reward > 0:
            tp += 1
        else:
            fn += 1
    else:
        if reward > 0:
            tn += 1
        else:
            fp += 1

    accuracy = 1.0 if reward > 0 else 0.0
    score = reward / 10

    print("\n🔹 RESULT")
    print(f"Mode: {mode}")
    print(f"State: {state}")
    print(f"Attack: {is_attack}")
    print(f"Action: {action}")
    print(f"Reward: {reward}")
    print(f"Accuracy: {accuracy}")
    print(f"Score: {score}")
    print(f"True Positive: {tp}, False Positive: {fp}, False Positive: {tn}, True Negative: {fn}")

    # 🔥 Comparison (Agent vs Ideal)
    results = []

    results.append({
        "name": "Agent",
        "score": score,
        "accuracy": accuracy,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn
    })

    results.append({
        "name": "Ideal",
        "score": 1.0,
        "accuracy": 1.0,
        "tp": 1 if is_attack else 0,
        "fp": 0,
        "tn": 1 if not is_attack else 0,
        "fn": 0
    })

    plot_results(results)


if __name__ == "__main__":
    main()