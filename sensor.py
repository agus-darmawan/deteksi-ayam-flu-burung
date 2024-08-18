from loguru import logger

class SensorDataHandler:
    def __init__(self):
        self.moisture = 0

    def update_moisture(self, moisture: float):
        self.moisture = moisture
        logger.info(f"Moisture updated: {moisture}")

    def get_sensor_data(self):
        return {'moisture': self.moisture}
