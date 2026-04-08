from environment.tasks import task_1_easy, task_2_medium, task_3_hard
from evaluation.grader import grade
from baseline.agent import SmartAgent
from visualize import plot_results


def run_task(env):
    agent = SmartAgent()

    state, _ = env.reset()
    total_reward = 0
    done = False
    steps = 0

    correct = 0
    incorrect = 0

    tp = fp = tn = fn = 0

    print("\n--- Step Logs ---")

    while not done:
        action = agent.act(state)

        failed_logins, spike, rate = state
        is_attack = failed_logins > 10 or spike or rate > 400

        state, reward, done, _ = env.step(action)

        total_reward += reward
        steps += 1

        if reward > 0:
            correct += 1
        else:
            incorrect += 1

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

        print(f"Step {steps}: Action={action}, Reward={reward}")

    total = correct + incorrect
    accuracy = correct / total if total > 0 else 0

    return total_reward, steps, accuracy, tp, fp, tn, fn


def main():
    tasks = [
        ("Easy", task_1_easy(), 100),
        ("Medium", task_2_medium(), 100),
        ("Hard", task_3_hard(), 100),
    ]

    results = []

    print("\n CyberShield AI Advanced Evaluation\n")

    for name, env, max_reward in tasks:
        total_reward, steps, accuracy, tp, fp, tn, fn = run_task(env)
        score = grade(total_reward, max_reward)

        results.append({
            "name": name,
            "score": score,
            "accuracy": accuracy,
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn
        })

        print(f"\n🔹 {name} Task")
        print(f"Total Reward: {total_reward}")
        print(f"Steps: {steps}")
        print(f"Accuracy: {round(accuracy, 2)}")
        print(f"Score: {round(score, 2)}")
        print(f"True Positive: {tp}, False Positive: {fp}, False Positive: {tn}, True Negative: {fn}")
        print("=" * 40)

    #  Graphs at the END
    plot_results(results)


if __name__ == "__main__":
    main()