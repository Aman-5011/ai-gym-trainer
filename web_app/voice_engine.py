#we are not using this file in the project as the voice is breaking ..if you want you can consider it

import pyttsx3
import threading
import time

class VoiceEngine:
    def __init__(self, rate=150):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.last_spoken_time = {}
        
        self.cooldowns = {
            "default": 2.0,
            "warning": 3.0,
            "motivation": 15.0,
            "rep": 0.0 
        }

    def _execute_speech(self, text):
        try:
            temp_engine = pyttsx3.init()
            temp_engine.setProperty('rate', 150)
            temp_engine.say(text)
            temp_engine.runAndWait()
            temp_engine.stop()
        except Exception:
            pass 

    def _speak_non_blocking(self, text, category="default"):
        current_time = time.time()
        cooldown_time = self.cooldowns.get(category, self.cooldowns["default"])

        last_time = self.last_spoken_time.get(text, 0)
        
        if (current_time - last_time) >= cooldown_time:
            self.last_spoken_time[text] = current_time
            speech_thread = threading.Thread(target=self._execute_speech, args=(text,), daemon=True)
            speech_thread.start()

    def speak(self, text):
        self._speak_non_blocking(text, category="default")

    def speak_rep_count(self, number):
        self._speak_non_blocking(str(number), category="rep")

    def speak_warning(self, text):
        self._speak_non_blocking(text, category="warning")

    def speak_motivation(self, text):
        self._speak_non_blocking(text, category="motivation")


_voice_manager = VoiceEngine()

def speak(text):
    _voice_manager.speak(text)

def speak_rep_count(number):
    _voice_manager.speak_rep_count(number)

def speak_warning(text):
    _voice_manager.speak_warning(text)

def speak_motivation(text):
    _voice_manager.speak_motivation(text)


if __name__ == "__main__":
    print("Testing Voice Engine (Non-blocking)...")
    speak_motivation("Welcome to your workout. Let's get started!")
    time.sleep(1)
    speak_rep_count(1)
    time.sleep(0.5)
    speak_warning("Keep your back straight")
    speak_warning("Keep your back straight") 
    time.sleep(4)
    speak_warning("Keep your back straight")
    print("Test complete.")