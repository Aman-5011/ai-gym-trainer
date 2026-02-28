import requests
import threading
import time

class HeartRateProvider:

    def __init__(self, ip_address):
        self.url = f"http://{ip_address}/data"
        self.bpm = 0
        self.status = "Initializing..."
        self.running = True
        self.last_fetch_time = 0
        self.connection_error_count = 0
        
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        """
        Polls the ESP32 for BPM data. 
        Uses a tight timeout to prevent blocking the thread if the ESP32 drops.
        """
        while self.running:
            try:
                response = requests.get(self.url, timeout=0.5)
             
                if response.status_code == 200:
                    data = response.json()
                    self.bpm = data.get("bpm", 0)
                    self.status = data.get("status", "Unknown")
                    self.connection_error_count = 0
                else:
                    self.status = f"Server Error: {response.status_code}"
                    
            except requests.exceptions.RequestException:
                self.bpm = 0
                self.status = "ESP32 Offline"
                self.connection_error_count += 1
            
            except Exception as e:
                self.status = f"Error: {str(e)}"
            time.sleep(1)

    def get_heart_rate_data(self):
        """
        Returns the most recent heart rate data as a dictionary.
        This follows the return pattern of the exercise logic modules.
        """
        return {
            "bpm": self.bpm,
            "status": self.status,
            "connected": self.connection_error_count < 5
        }

    def stop(self):
        """Safely stops the background thread."""
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
_provider = None

def initialize_hr_provider(ip):
    global _provider
    _provider = HeartRateProvider(ip)
    return _provider

def get_current_hr():
    if _provider:
        return _provider.get_heart_rate_data()
    return {"bpm": 0, "status": "Not Initialized", "connected": False}
