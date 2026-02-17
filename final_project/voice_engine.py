import pyttsx3
import threading
import time

class VoiceEngine:
    """
    Provides a non-blocking text-to-speech interface using pyttsx3 and threading.
    Implements cooldown logic to prevent overlapping or redundant audio feedback.
    """

    def __init__(self, rate=150):
        # Initialize the pyttsx3 engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        
        # Dictionary to track the last timestamp of specific spoken messages
        self.last_spoken_time = {}
        
        # Cooldown settings for different feedback categories (in seconds)
        self.cooldowns = {
            "default": 2.0,
            "warning": 3.0,
            "motivation": 15.0,
            "rep": 0.0  # Rep counts should never be skipped due to cooldown
        }

    def _execute_speech(self, text):
        """
        Internal target for the thread. 
        Initializes a local engine instance per thread to avoid COM/Global state issues.
        """
        try:
            # Re-initializing locally inside the thread is safer for non-blocking calls
            temp_engine = pyttsx3.init()
            temp_engine.setProperty('rate', 150)
            temp_engine.say(text)
            temp_engine.runAndWait()
            temp_engine.stop()
        except Exception:
            pass # Suppress thread-specific errors to keep main loop running

    def _speak_non_blocking(self, text, category="default"):
        """
        Checks cooldowns and spawns a daemon thread for speech.
        """
        current_time = time.time()
        cooldown_time = self.cooldowns.get(category, self.cooldowns["default"])

        # Check if the exact same text has been spoken recently within the category's cooldown
        last_time = self.last_spoken_time.get(text, 0)
        
        if (current_time - last_time) >= cooldown_time:
            self.last_spoken_time[text] = current_time
            # Spawn daemon thread so it doesn't block the computer vision loop
            speech_thread = threading.Thread(target=self._execute_speech, args=(text,), daemon=True)
            speech_thread.start()

    def speak(self, text):
        """Standard general-purpose speech."""
        self._speak_non_blocking(text, category="default")

    def speak_rep_count(self, number):
        """Speaks the current repetition number. Cooldown is 0 for precision."""
        self._speak_non_blocking(str(number), category="rep")

    def speak_warning(self, text):
        """Speaks posture warnings with a moderate cooldown to avoid annoyance."""
        self._speak_non_blocking(text, category="warning")

    def speak_motivation(self, text):
        """Speaks encouraging phrases with a high cooldown."""
        self._speak_non_blocking(text, category="motivation")


# --- GLOBAL INSTANCE FOR EXTERNAL USE ---
# This allows other modules to import 'engine' and use it immediately
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
    # Internal test logic
    print("Testing Voice Engine (Non-blocking)...")
    speak_motivation("Welcome to your workout. Let's get started!")
    time.sleep(1)
    speak_rep_count(1)
    time.sleep(0.5)
    speak_warning("Keep your back straight")
    # This identical warning should be blocked by cooldown:
    speak_warning("Keep your back straight") 
    time.sleep(4)
    # Now it should speak again after cooldown:
    speak_warning("Keep your back straight")
    print("Test complete.")