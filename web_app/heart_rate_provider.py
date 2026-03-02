import requests
import threading
import time

class HeartRateProvider:
    def __init__(self, ip_address):
        self.url = f"http://{ip_address}/data"
        self.bpm = 0
        self.status = "Initializing..."
        self.connected = False
        self.running = True
        self.lock = threading.Lock()
        
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        """Polls ESP32 at 1Hz with non-blocking timeouts."""
        while self.running:
            try:
                # Tight timeout ensures thread remains responsive to stop()
                response = requests.get(self.url, timeout=0.5)
                
                if response.status_code == 200:
                    data = response.json()
                    with self.lock:
                        self.bpm = data.get("bpm", 0)
                        self.status = data.get("status", "Unknown")
                        self.connected = True
                else:
                    with self.lock:
                        self.bpm = 0
                        self.status = f"HTTP Error {response.status_code}"
                        self.connected = False
                        
            except (requests.exceptions.RequestException, ValueError):
                with self.lock:
                    self.bpm = 0
                    self.status = "ESP32 Offline"
                    self.connected = False
            
            time.sleep(1)

    def get_heart_rate_data(self):
        """Returns snapshot of current biometric state."""
        with self.lock:
            return {
                "bpm": self.bpm,
                "status": self.status,
                "connected": self.connected
            }

    def stop(self):
        """Signals thread to terminate."""
        self.running = False

# --- GLOBAL SINGLETON HELPERS ---
_provider = None

def initialize_hr_provider(ip):
    global _provider
    if _provider is None:
        _provider = HeartRateProvider(ip)
    return _provider

def get_current_hr():
    if _provider:
        return _provider.get_heart_rate_data()
    return {"bpm": 0, "status": "Not Initialized", "connected": False}

def stop_hr_provider():
    global _provider
    if _provider:
        _provider.stop()
        _provider = None