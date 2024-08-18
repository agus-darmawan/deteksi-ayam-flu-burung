import threading
import argparse
import sys
from loguru import logger
import cv2 as cv
from flask import Flask, render_template, Response, request, jsonify

from detector import ChickenCombDetector

class ChickenMonitoringApp(ChickenCombDetector):
    def __init__(self, model_path, port=5001, debug: bool = False):
        super().__init__(model_path, debug=debug)
        self.port = port
        self.app = Flask(__name__)
        self.define_routes()

        logger.remove()
        logger.add(sys.stdout, level="DEBUG" if debug else "CRITICAL", format="{time} - {level} - {message}")

    def define_routes(self):
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
            return jsonify(success=True)

        @self.app.route('/sensor_data')
        def sensor_data():
            data = self.get_sensor_data()
            health_data = self.get_health_data()
            data.update(health_data)
            return jsonify(data)

        @self.app.route('/chicken_status')
        def chicken_status():
            health_data = self.get_health_data()
            return jsonify(health_data)

    def generate_frames(self):
        while True:
            frame = self.get_frame()
            if frame is None:
                continue
            ret, buffer = cv.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    def run(self):
        logger.info(f"Starting Flask app on port {self.port}.")
        self.app.run(host='0.0.0.0', port=self.port, threaded=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Chicken Monitoring App.')
    parser.add_argument('--debug', action='store_true', help='Enable debugging mode.')
    args = parser.parse_args()

    app = ChickenMonitoringApp('model/best.pt', debug=args.debug)
    threading.Thread(target=app.run).start()
    app.run()
