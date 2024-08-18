from loguru import logger

class HealthAnalyzer:
    def __init__(self):
        self.chickens_detected = 0
        self.flu_chickens = 0

    def analyze_health(self, mean_hue: float, moisture: float):
        self.chickens_detected += 1
        if 50 < moisture < 100 and 40 < mean_hue < 50:
            self.flu_chickens += 1
            status = "Sick"
        else:
            status = "Healthy"

        logger.info(f"Health analyzed: mean_hue={mean_hue}, moisture={moisture}, status={status}")
        return status

    def get_health_data(self):
        return {
            'chickens_detected': self.chickens_detected,
            'flu_chickens': self.flu_chickens
        }
