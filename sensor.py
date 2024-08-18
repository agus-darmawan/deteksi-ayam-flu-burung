from loguru import logger

class SensorDataHandler:
    """
    A class to handle sensor data, specifically moisture levels.

    Attributes:
        moisture (float): The current moisture level.
    """
    
    def __init__(self):
        """
        Initializes the SensorDataHandler with a default moisture level.
        """
        self.moisture = 0

    def update_moisture(self, moisture: float) -> None:
        """
        Updates the moisture level.

        Args:
            moisture (float): The new moisture level.
        """
        self.moisture = moisture
        logger.info(f"Moisture updated: {moisture}")

    def get_sensor_data(self) -> dict:
        """
        Retrieves the current sensor data.

        Returns:
            dict: A dictionary containing the current moisture level.
        """
        return {'moisture': self.moisture}
