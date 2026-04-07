def grade(total_reward, max_reward):
    """
    Normalize score between 0 and 1
    """
    if max_reward == 0:
        return 0.0

    score = total_reward / max_reward

    # Clamp between 0 and 1
    return max(0.0, min(score, 1.0))