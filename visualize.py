import matplotlib.pyplot as plt


def plot_results(results):
    tasks = [r["name"] for r in results]
    scores = [r["score"] for r in results]
    accuracy = [r["accuracy"] for r in results]

    #  Highlight correct vs wrong
    correctness = ["Correct" if r["accuracy"] == 1 else "Wrong" for r in results]

    # -------- Score Graph --------
    plt.figure()
    plt.bar(tasks, scores)
    plt.title("Score Comparison")
    plt.xlabel("Mode")
    plt.ylabel("Score")
    plt.show()

    # -------- Accuracy Graph --------
    plt.figure()
    plt.bar(tasks, accuracy)
    plt.title("Accuracy Comparison")
    plt.xlabel("Mode")
    plt.ylabel("Accuracy")
    plt.show()

    # -------- Confusion Matrix --------
    tp = [r["tp"] for r in results]
    fp = [r["fp"] for r in results]
    tn = [r["tn"] for r in results]
    fn = [r["fn"] for r in results]

    x = range(len(tasks))

    plt.figure()
    plt.bar(x, tp)
    plt.bar(x, fp, bottom=tp)
    plt.bar(x, tn, bottom=[tp[i] + fp[i] for i in x])
    plt.bar(x, fn, bottom=[tp[i] + fp[i] + tn[i] for i in x])

    plt.xticks(x, tasks)
    plt.title("Decision Breakdown (True Positive/False Positive/False Positive/True Negative)")
    plt.xlabel("Mode")
    plt.ylabel("Count")
    plt.legend(["True Positive", "False Positive", "False Positive", "True Negative"])
    plt.show()

    # -------- Text Insight --------
    print("\n📊 INSIGHTS:")
    for i, r in enumerate(results):
        if r["accuracy"] == 1:
            print(f"{tasks[i]} → ✅ Correct Decision")
        else:
            print(f"{tasks[i]} → ❌ Wrong Decision")