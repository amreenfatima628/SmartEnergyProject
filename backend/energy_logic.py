import time

class SmartAppliance:
    def __init__(self, name, initial_kwh=0.0, rate_per_kwh=35.0):
        self.name = name
        self.rate = rate_per_kwh
        self.total_kwh = initial_kwh  # Resume from saved value
        self.last_update_time = time.time()

    def update_usage(self, current_watts):
        now = time.time()
        time_delta = now - self.last_update_time
        self.last_update_time = now

        if current_watts > 0:
            # kWh = (Watts * Seconds) / 3,600,000
            added_kwh = (current_watts * time_delta) / 3600000
            self.total_kwh += added_kwh

        return self.total_kwh * self.rate

    def reset_meter(self):
        self.total_kwh = 0.0