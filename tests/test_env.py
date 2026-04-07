from environment.env import CyberEnv


def test_reset_returns_valid_state():
    env = CyberEnv()
    state, info = env.reset()

    assert isinstance(state, tuple)
    assert len(state) == 3


def test_step_returns_valid_types():
    env = CyberEnv()
    env.reset()

    state, reward, done, info = env.step("block")

    assert isinstance(state, tuple)
    assert isinstance(reward, (int, float))
    assert isinstance(done, bool)
    assert isinstance(info, dict)


def test_attack_block_gives_positive_reward():
    env = CyberEnv()
    env.reset()

    # Force attack state
    env.current_state.failed_logins = 20
    env.current_state.traffic_spike = True
    env.current_state.request_rate = 700

    _, reward, _, _ = env.step("block")

    assert reward > 0


def test_normal_allow_gives_positive_reward():
    env = CyberEnv()
    env.reset()

    # Force normal state
    env.current_state.failed_logins = 1
    env.current_state.traffic_spike = False
    env.current_state.request_rate = 100

    _, reward, _, _ = env.step("allow")

    assert reward > 0


def test_wrong_action_penalty():
    env = CyberEnv()
    env.reset()

    # Force attack state but allow it (wrong)
    env.current_state.failed_logins = 20
    env.current_state.traffic_spike = True
    env.current_state.request_rate = 700

    _, reward, _, _ = env.step("allow")

    assert reward < 0