import numpy as np
import time

class PushupAnalyzer:
    """
    Revised logic for push-up analysis focusing on strict depth requirements.
    Ensures reps are only counted if the user reaches the required elbow flexion.
    """

    def __init__(self):
        # Repetition State Machine
        self.state = "extended" 
        # BUG FIX: Initialize depth_reached flag to False
        self.depth_reached = False
        
        # Repetition and Accuracy counters
        self.rep_count = 0
        self.total_completed_reps = 0
        self.correct_reps = 0
        
        # Base Thresholds (Angles in degrees)
        self.EXTENDED_THRESHOLD = 160  # Arms straight
        self.HIP_EXTREME_BEND = 140    # Posture penalty threshold
        
        # Stability and Warning tracking
        self.warnings = []
        self.posture_warning_counter = 0
        self.STABILITY_FRAMES = 10
        self.current_rep_is_valid = True

    def _get_leniency_config(self, user_profile):
        """
        Determines the required elbow depth based on user profile.
        Leniency only shifts the threshold; it does not bypass the depth requirement.
        """
        age = user_profile.get("age", 25)
        bmi = user_profile.get("bmi", 22.0)
        level = user_profile.get("fitness_level", "intermediate").lower()

        # Priority-based Leniency Check
        if bmi >= 30:
            return 110, "Keeping conditions relaxed due to obesity"
        if level == "beginner":
            return 110, "Keeping conditions relaxed for beginners"
        if age < 14:
            return 110, "Keeping conditions relaxed for children"
        
        # Default Strict Conditions
        return 90, None

    def analyze_frame(self, angles, landmarks, user_profile):
        """
        Processes push-up frame with strict depth-reached validation.
        """
        elbow_angle = angles.get("elbow", 180)
        hip_angle = angles.get("hip", 180)
        
        # Determine Leniency Decision & Depth Threshold
        bent_threshold, leniency_msg = self._get_leniency_config(user_profile)
        
        current_frame_warnings = []
        if leniency_msg:
            current_frame_warnings.append(leniency_msg)

        # 1. BODY STRAIGHTNESS CHECK
        if hip_angle < self.HIP_EXTREME_BEND:
            self.posture_warning_counter += 1
            if self.posture_warning_counter > self.STABILITY_FRAMES:
                current_frame_warnings.append("Keep your body straight")
                self.current_rep_is_valid = False
        else:
            self.posture_warning_counter = 0

        # 2. STATE-BASED REP DETECTION (EXTENDED -> BENT -> EXTENDED)
        
        # Transition 1: Moving from extension to flexion
        if elbow_angle < bent_threshold:
            if self.state == "extended":
                # MANDATORY FIX: Set depth_reached ONLY when threshold is passed
                self.depth_reached = True
                self.state = "bent"

        # Transition 2: Returning to full extension
        if elbow_angle > self.EXTENDED_THRESHOLD:
            if self.state == "bent":
                # A cycle is complete
                self.total_completed_reps += 1
                
                # STRICT RULE: Count rep ONLY if depth_reached was True during cycle
                if self.depth_reached:
                    self.rep_count += 1
                    if self.current_rep_is_valid:
                        self.correct_reps += 1
                
                # MANDATORY RESET: Reset flags for the next rep cycle
                self.state = "extended"
                self.depth_reached = False
                self.current_rep_is_valid = True

        # 3. ACCURACY CALCULATION
        accuracy = (self.correct_reps / self.total_completed_reps * 100) if self.total_completed_reps > 0 else 0.0

        self.warnings = current_frame_warnings

        return {
            "rep_count": self.rep_count,
            "stage": self.state,
            "accuracy": round(accuracy, 2),
            "warnings": self.warnings
        }

# --- PUBLIC API ---
_analyzer = PushupAnalyzer()

def process_pushup(angles, landmarks, user_profile):
    """
    Main entry point for push-up logic with strict depth validation.
    """
    return _analyzer.analyze_frame(angles, landmarks, user_profile)