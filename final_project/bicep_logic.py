import numpy as np
import time

class PushupAnalyzer:
    """
    Revised logic for push-up analysis focusing on rep-level accuracy and state-based detection.
    Corrects issues where frame-level penalties were inaccurately reducing session scores.
    """

    def __init__(self):
        # Repetition State Machine: Replaced up/down with extended/bent states
        self.state = "extended" 
        self.depth_reached = False
        
        # Repetition and Accuracy counters
        self.rep_count = 0
        self.total_completed_reps = 0
        self.correct_reps = 0
        
        # Thresholds (Angles in degrees)
        self.EXTENDED_THRESHOLD = 160  # Arms straight
        self.BENT_THRESHOLD = 90      # Sufficient depth for push-up
        
        # Posture threshold (Shoulder-Hip-Knee/Ankle)
        self.HIP_EXTREME_BEND = 140    # Only angles below this are considered "extreme"
        
        # Stability and Warning tracking
        self.warnings = []
        self.posture_warning_counter = 0
        self.STABILITY_FRAMES = 10
        self.current_rep_is_valid = True # Resets every rep cycle

    def analyze_frame(self, angles, landmarks, user_profile):
        """
        Processes push-up logic frame-by-frame. 
        Accuracy is calculated only upon completion of a full rep cycle.
        """
        elbow_angle = angles.get("elbow", 180)
        hip_angle = angles.get("hip", 180)
        
        current_frame_warnings = []

        # 1. BODY STRAIGHTNESS (Soft Check)
        # We only flag extreme bends and only penalize accuracy at the rep level
        if hip_angle < self.HIP_EXTREME_BEND:
            self.posture_warning_counter += 1
            if self.posture_warning_counter > self.STABILITY_FRAMES:
                current_frame_warnings.append("Keep your body straight")
                self.current_rep_is_valid = False # Mark the current rep attempt as flawed
        else:
            self.posture_warning_counter = 0

        # 2. STATE-BASED REP DETECTION (EXTENDED -> BENT -> EXTENDED)
        # Transition 1: Achieving sufficient depth
        if elbow_angle < self.BENT_THRESHOLD:
            if self.state == "extended":
                self.depth_reached = True
                self.state = "bent"

        # Transition 2: Returning to full extension
        if elbow_angle > self.EXTENDED_THRESHOLD:
            if self.state == "bent":
                # A full rep cycle is completed here
                self.total_completed_reps += 1
                
                # Accuracy logic: rep is correct if sufficient depth was reached 
                # and no extreme posture violations occurred during the cycle.
                if self.depth_reached:
                    self.rep_count += 1
                    if self.current_rep_is_valid:
                        self.correct_reps += 1
                
                # Reset rep-specific flags for the next cycle
                self.state = "extended"
                self.depth_reached = False
                self.current_rep_is_valid = True

        # 3. REP-LEVEL ACCURACY CALCULATION
        # Fixed: Accuracy = (correct_reps / total_completed_reps) * 100
        # This prevents mid-rep frame noise from zeroing out the score.
        accuracy = (self.correct_reps / self.total_completed_reps * 100) if self.total_completed_reps > 0 else 0.0

        self.warnings = current_frame_warnings

        return {
            "rep_count": self.rep_count,
            "stage": self.state, # Returns 'extended' or 'bent'
            "accuracy": round(accuracy, 2),
            "warnings": self.warnings
        }

# --- PUBLIC API ---
_analyzer = PushupAnalyzer()

def process_pushup(angles, landmarks, user_profile):
    """
    Main entry point for push-up logic.
    Ensures modularity and state persistence across the session.
    """
    return _analyzer.analyze_frame(angles, landmarks, user_profile)