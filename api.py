from flask import Flask, request, jsonify
import requests

class DSPS_API:
    def __init__(self, data_callback):
        self.app = Flask(__name__)
        self.data_callback = data_callback
        self.should_reset = False
        self.setup_routes()

    def setup_routes(self):
        self.app.route('/sensor-data', methods=['POST'])(self.receive_data)
        self.app.route('/reset', methods=['POST'])(self.trigger_reset)

    def receive_data(self):
        if not self.data_callback:
            return jsonify({"status": "Callback not configured"}), 500
        
        try:
            data = request.json
            if all(k in data for k in ["temperature", "humidity", "altitude", "pressure"]):
                self.data_callback(data)
                if self.should_reset:
                    self.should_reset = False
                    return jsonify("reset"), 200
                return jsonify({"status": "Data received"}), 200
            return jsonify({"error": "Missing sensor data"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def trigger_reset(self):
        self.should_reset = True
        return jsonify({"status": "Reset signal queued"}), 200
    
    def send_reset(self):
        try:
            requests.post('http://localhost:5000/reset')
        except requests.exceptions.RequestException as e:
            print(f"Failed to send reset command: {e}")

    def run(self):
        self.app.run(host='0.0.0.0', port=5000)
