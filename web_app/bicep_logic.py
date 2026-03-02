import numpy as np
import time

class BicepAnalyzer:
    """
    Fixed logic for bicep curl analysis. 
    Implements state-based rep counting using 'extended' and 'flexed' states.
    """

    def __init__(self):
        # State tracking: replaces up/down with biceps-specific terminology
        self.state = "extended" 
        self.flexion_achieved = False
        
        # Repetition and Accuracy counters
        self.rep_count = 0
        self.total_attempts = 0
        self.correct_reps = 0
        
        # Thresholds (Angles in degrees)
        self.EXTENSION_THRESHOLD = 155  # Arm is straight
        self.FLEXION_THRESHOLD = 45     # Arm is fully curled
        
        # Performance monitoring
        self.warnings = []
        self.shoulder_warning_counter = 0
        self.STABILITY_FRAMES = 10
        self.rep_has_error = False

    def analyze_frame(self, angles, landmarks, user_profile):
        """
        Processes bicep curl logic. Logic is now state-driven to prevent partial rep counting.
        """
        elbow_angle = angles.get("elbow", 180)
        shoulder_angle = angles.get("shoulder", 0) # Angle of upper arm relative to torso
        
        current_frame_warnings = []

        # 1. SHOULDER STABILITY (Soft Check Only)
        # Using shoulder angle to detect excessive upper arm swinging
        # Standard curls keep the upper arm nearly parallel to the torso (small angle)
        if shoulder_angle > 35: 
            self.shoulder_warning_counter += 1
            if self.shoulder_warning_counter > self.STABILITY_FRAMES:
                current_frame_warnings.append("Keep your upper arm stable")
                self.rep_has_error = True
        else:
            self.shoulder_warning_counter = 0

        # 2. STATE-BASED REP DETECTION (EXTENDED -> FLEXED -> EXTENDED)
        # Transition 1: Achieving full flexion (curl)
        if elbow_angle < self.FLEXION_THRESHOLD:
            if self.state == "extended":
                self.flexion_achieved = True
                self.state = "flexed"

        # Transition 2: Returning to full extension (straight arm)
        if elbow_angle > self.EXTENSION_THRESHOLD:
            if self.state == "flexed":
                # A full cycle is complete
                self.total_attempts += 1
                
                # Check if the rep was full-range and stable
                if self.flexion_achieved and not self.rep_has_error:
                    self.correct_reps += 1
                    self.rep_count += 1
                elif self.flexion_achieved:
                    # Count as a rep even with minor shoulder movement, but don't mark as 'correct' for accuracy
                    self.rep_count += 1
                
                # Reset for next repetition
                self.state = "extended"
                self.flexion_achieved = False
                self.rep_has_error = False

        # 3. ACCURACY CALCULATION
        # accuracy = (correct_reps / total_attempts) * 100
        accuracy = (self.correct_reps / self.total_attempts * 100) if self.total_attempts > 0 else 0.0

        self.warnings = current_frame_warnings

        return {
            "rep_count": self.rep_count,
            "stage": self.state, # Returns 'extended' or 'flexed'
            "accuracy": round(accuracy, 2),
            "warnings": self.warnings
        }

# --- PUBLIC API ---
_analyzer = BicepAnalyzer()

def process_bicep(angles, landmarks, user_profile):
    """
    Main entry point for bicep logic. 
    Maintains persistent state across frames for accurate rep counting.
    """
    return _analyzer.analyze_frame(angles, landmarks, user_profile)