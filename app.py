import sys
import argparse
import threading
import cv2 as cv

import logging
from loguru import logger
from flask import Flask, render_template, Response, request, jsonify


from detector import ChickenCombDetector

class ChickenMonitoringApp(ChickenCombDetector):
    """
    A Flask application for monitoring chickens using the ChickenCombDetector.

    Attributes:
        port (int): The port number for the Flask application.
        app (Flask): Flask application instance.
    """
    
    def __init__(self, model_path: str, port: int = 5001, debug: bool = False):
        """
        Initializes the ChickenMonitoringApp with model path, port, and debug mode.

        Args:
            model_path (str): Path to the YOLO model.
            port (int, optional): Port number for the Flask application. Defaults to 5001.
            debug (bool, optional): Enable debug mode. Defaults to False.
        """
        super().__init__(model_path, debug=debug)
        self.port = port
        self.app = Flask(__name__)
        self.define_routes()
        logger.remove()
        logger.add(sys.stdout, level="DEBUG" if debug else "CRITICAL", format="{time} - {level} - {message}")
        logger.add(sys.stderr, format="<red>{level}</red> | <green>{message}</green>", colorize=True)
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)

    def define_routes(self):
        """
        Defines the routes for the Flask application.
        """
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/update_moisture', methods=['POST'])
        def update_moisture():
            data = request.json
            self.update_moisture(data['moisture'])
            logger.info(f"Moisture updated: {data['moisture']}")
            return jsonify(success=True)

        @self.app.route('/sensor_data')
        def sensor_data():
            data = self.get_sensor_data()
            health_data = self.get_health_data()
            data.update(health_data)
            logger.debug(f"Sensor data requested: {data}")
            return jsonify(data)

        @self.app.route('/chicken_status')
        def chicken_status():
            health_data = self.get_health_data()
            logger.debug(f"Chicken status requested: {health_data}")
            return jsonify(health_data)

    def generate_frames(self):
        """
        Generates video frames for the video feed.

        Yields:
            bytes: The JPEG-encoded frame.
        """
        while True:
            frame = self.get_frame()
            if frame is None:
                continue
            ret, buffer = cv.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    def run(self, debug):
        """
        Starts the Flask application and attempts to use an alternative port if the desired port is in use.
        """
        import socket

        def find_free_port(starting_port):
            port = starting_port
            while True:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        s.bind(('0.0.0.0', port))
                        return port
                    except OSError:
                        port += 1

        try:
            logger.info(f"Starting Flask app on port {self.port}.")
            self.app.run(host='0.0.0.0', port=self.port, threaded=True, use_reloader=debug, debug=debug)
        except OSError as e:
            logger.error(f"Port {self.port} is in use. Trying a different port.")
            free_port = find_free_port(self.port)
            logger.info(f"Starting Flask app on port {free_port}.")
            self.app.run(host='0.0.0.0', port=free_port, threaded=True, use_reloader=debug, debug=debug)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Chicken Monitoring App.')
    parser.add_argument('--debug', action='store_true', help='Enable debugging mode.')
    parser.add_argument('--port', type=int, default=5001, help='Port number for the Flask application.')
    args = parser.parse_args()

    app = ChickenMonitoringApp('model/best.pt', port=args.port, debug=args.debug)
    threading.Thread(target=app.run(debug=args.debug)).start()
