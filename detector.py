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
    """
    A class to detect chicken combs using YOLOv8 and analyze their health based on hue and moisture levels.

    Attributes:
        model_path (str): Path to the YOLO model.
        camera_index (int): Index of the camera for video capture.
        debug (bool): Flag to enable debug mode.
        model (YOLO): YOLOv8 model instance.
        cap (cv.VideoCapture): Video capture object.
        prev_time (float): Timestamp of the previous frame for FPS calculation.
        fps (float): Frames per second.
    """
    
    def __init__(self, model_path: str, camera_index: int = 0, debug: bool = False):
        """
        Initializes the ChickenCombDetector with model path, camera index, and debug mode.

        Args:
            model_path (str): Path to the YOLO model.
            camera_index (int, optional): Camera index for video capture. Defaults to 0.
            debug (bool, optional): Enable debug mode. Defaults to False.
        """
        logger.remove()
        logger.add(sys.stdout, level="DEBUG" if debug else "CRITICAL", format="{time} - {level} - {message}")
        logger.add(sys.stderr, format="<red>{level}</red> | <green>{message}</green>", colorize=True)
        logging.getLogger("ultralytics").setLevel(logging.CRITICAL)

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
        """
        Calculates and updates the frames per second (FPS) value.
        """
        current_time = time.time()
        self.fps = 1.0 / (current_time - self.prev_time)
        self.prev_time = current_time

    def get_frame(self):
        """
        Captures a frame from the video feed, processes it, and calculates FPS.

        Returns:
            np.ndarray: The processed frame.
        """
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to capture image.")
            return None
        frame = cv.resize(frame, (640, 480))
        frame = self.process_frame(frame)
        self.calculate_fps()
        return frame

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Processes the captured frame by detecting chicken combs and analyzing their health.

        Args:
            frame (np.ndarray): The frame to process.

        Returns:
            np.ndarray: The processed frame with annotations.
        """
        results = self.model(frame)
        self.chickens_detected = len(results[0].boxes)
        for result in results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            mean_hue = self.calculate_mean_hue(frame, x1, y1, x2, y2)
            status = self.analyze_health(mean_hue, self.moisture)

            if status == "Sick":
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                cv.putText(frame, f"Status: {status}", (center_x, center_y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv.LINE_AA)

            if self.debug:
                class_id = int(result.cls[0])
                confidence = result.conf[0]
                label = f"{self.model.names[class_id]}: {confidence:.2f}"
                cv.putText(frame, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                mean_hue_text = f"Mean Hue: {mean_hue:.2f}"
                cv.putText(frame, mean_hue_text, (x1, y2 + 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                logger.debug(f"Detected box: ({x1}, {y1}), {mean_hue_text}, Status: {status}")

        cv.putText(frame, f"FPS: {self.fps:.2f}", (20, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        return frame 

    def calculate_mean_hue(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calculates the mean hue of the detected area in the frame.

        Args:
            frame (np.ndarray): The frame containing the detected area.
            x1 (int): The x-coordinate of the top-left corner of the bounding box.
            y1 (int): The y-coordinate of the top-left corner of the bounding box.
            x2 (int): The x-coordinate of the bottom-right corner of the bounding box.
            y2 (int): The y-coordinate of the bottom-right corner of the bounding box.

        Returns:
            float: The mean hue value.
        """
        detected_area = frame[y1:y2, x1:x2]
        hsv_image = cv.cvtColor(detected_area, cv.COLOR_BGR2HSV)
        mean_hue = np.mean(hsv_image[:, :, 0])
        return mean_hue

    def run(self) -> None:
        """
        Starts capturing and processing video frames.
        """
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
