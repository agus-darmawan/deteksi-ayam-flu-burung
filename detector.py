import sys
import time
import argparse
from loguru import logger
import cv2 as cv
import numpy as np
import logging

from ultralytics import YOLO
from sensor import SensorDataHandler
from health_analyzer import HealthAnalyzer

class ChickenCombDetector(SensorDataHandler, HealthAnalyzer):
    def __init__(self, model_path: str, camera_index: int = 0, debug: bool = False):
        logging.getLogger("ultralytics").setLevel(logging.CRITICAL)
        # Configure Loguru logging
        logger.remove()
        logger.add(sys.stdout, level="DEBUG" if debug else "CRITICAL", format="{time} - {level} - {message}")

        SensorDataHandler.__init__(self)
        HealthAnalyzer.__init__(self)

        self.model = YOLO(model_path)
        self.cap = cv.VideoCapture(camera_index)
        self.prev_time = time.time()
        self.fps = 0
        self.debug = debug

        if not self.cap.isOpened():
            logger.error("Could not open webcam.")
            sys.exit()

    def calculate_fps(self) -> None:
        current_time = time.time()
        self.fps = 1.0 / (current_time - self.prev_time)
        self.prev_time = current_time

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to capture image.")
            return None
        frame = cv.resize(frame, (640, 480))
        frame = self.process_frame(frame)
        self.calculate_fps()
        return frame

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        results = self.model(frame)
        self.chickens_detected = len(results[0].boxes)
        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            mean_hue = self.calculate_mean_hue(frame, x1, y1, x2, y2)

            status = self.analyze_health(mean_hue, self.moisture)
            cv.putText(frame, f"Status: {status}", (x1, y2 + 40), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            logger.debug(f"Detected box: ({x1}, {y1}, {x2}, {y2}), Mean Hue: {mean_hue}, Status: {status}")

        cv.putText(frame, f"FPS: {self.fps:.2f}", (20, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        return frame

    def calculate_mean_hue(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> float:
        detected_area = frame[y1:y2, x1:x2]
        hsv_image = cv.cvtColor(detected_area, cv.COLOR_BGR2HSV)
        mean_hue = np.mean(hsv_image[:, :, 0])
        return mean_hue

    def run(self) -> None:
        while True:
            frame = self.get_frame()
            if frame is None:
                break
            if self.debug:
                cv.imshow('YOLOv8 Inference', frame)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    self.cap.release()
                    cv.destroyAllWindows()
                    sys.exit()
            logger.debug("Frame processed.")
        self.cap.release()
        cv.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Chicken Comb Detector.')
    parser.add_argument('--debug', action='store_true', help='Enable debugging mode.')
    args = parser.parse_args()
    detector = ChickenCombDetector('model/best.pt', debug=args.debug)
    detector.run()
