class State:
    def __init__(self, failed_logins=0, traffic_spike=False, request_rate=0.0):
        self.failed_logins = failed_logins
        self.traffic_spike = traffic_spike
        self.request_rate = request_rate

    def to_tuple(self):
        return (self.failed_logins, self.traffic_spike, self.request_rate)