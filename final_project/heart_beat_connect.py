import requests
import threading
import time

class HeartRateProvider:
    def __init__(self, ip_address):
        self.url = f"http://{ip_address}/data"
        self.bpm = 0
        self.status = "Connecting..."
        self.running = True
        
        # Start a background thread so the AI loop doesn't lag
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        while self.running:
            try:
                # Fast timeout (0.5s) so it doesn't hang the AI if ESP32 disconnects
                response = requests.get(self.url, timeout=0.5)
                if response.status_code == 200:
                    data = response.json()
                    self.bpm = data["bpm"]
                    self.status = data["status"]
            except:
                self.status = "ESP32 Offline"
            time.sleep(1) # Get data once per second

    def stop(self):
        self.running = False