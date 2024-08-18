class HealthAnalyzer:
    """
    A class to analyze the health status of detected chickens based on hue and moisture levels.

    Attributes:
        chickens_detected (int): Number of chickens detected.
        flu_chickens (int): Number of chickens identified as sick.
    """
    
    def __init__(self):
        """
        Initializes the HealthAnalyzer with counters for detected and sick chickens.
        """
        self.chickens_detected = 0
        self.flu_chickens = 0

    def analyze_health(self, mean_hue: float, moisture: float) -> str:
        """
        Analyzes the health status of a chicken based on mean hue and moisture level.

        Args:
            mean_hue (float): The mean hue value of the detected area.
            moisture (float): The moisture level.

        Returns:
            str: The health status ("Sick" or "Healthy").
        """
        self.chickens_detected += 1
        if 50 < moisture < 100 and 40 < mean_hue < 50:
            self.flu_chickens += 1
            status = "Sick"
        else:
            status = "Healthy"
        return status

    def get_health_data(self) -> dict:
        """
        Retrieves the health data.

        Returns:
            dict: A dictionary containing the number of chickens detected and sick chickens.
        """
        return {
            'chickens_detected': self.chickens_detected,
            'flu_chickens': self.flu_chickens
        }
