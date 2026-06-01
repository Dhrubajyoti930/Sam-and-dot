import time

class ATC:
    def __init__(self, target_latency=2.0):
        self.target = target_latency
        self.max_concurrency = 3
        self.integral = 0
        self.last_error = 0
        self.min_c, self.max_c = 1, 5

    def update(self, observed_latency):
        error = self.target - observed_latency
        self.integral += error
        derivative = error - self.last_error
        
        # PID coefficients
        adjustment = (error * 0.1) + (self.integral * 0.01) + (derivative * 0.05)
        self.max_concurrency = max(self.min_c, min(self.max_c, int(self.max_c + adjustment)))
        self.last_error = error
        return self.max_concurrency