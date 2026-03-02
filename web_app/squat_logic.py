import numpy as np
import time

class SquatAnalyzer:
    """
    Modular squat analysis logic.
    Fixed to ensure reps are only counted when the required depth is reached.
    """

    def __init__(self):
        # Repetition State Machine
        self.rep_count = 0
        self.total_attempts = 0
        self.correct_reps = 0
        self.stage = "up"
        
        # CRITICAL BUG FIX: Explicit depth flag tracking
        self.depth_reached = False
        
        # Stability and performance tracking
        self.warnings = []
        self.warning_counters = {"too_close": 0, "too_wide": 0, "lean": 0, "depth": 0}
        self.STABILITY_FRAMES = 8
        self.prev_knee_angle = 180
        self.last_time = time.time()
        
        # Base thresholds
        self.UP_THRESHOLD = 150
        self.SIDE_VIEW_X_LIMIT = 45

    def _get_user_category(self, user_profile):
        """Classifies user for group-based depth leniency."""
        age = user_profile.get("age", 25)
        bmi = user_profile.get("bmi", 22.0)

        if age < 14: return "CHILD"
        if age > 55: return "SENIOR"
        if bmi >= 27: return "OVERWEIGHT"
        return "NORMAL"

    def _get_depth_threshold(self, category):
        """Returns the specific depth_threshold based on the user category."""
        thresholds = {
            "NORMAL": 90,
            "OVERWEIGHT": 100,
            "SENIOR": 105,
            "CHILD": 100
        }
        return thresholds.get(category, 90)

    def is_side_view(self, landmarks):
        """Detects profile view via shoulder horizontal overlap."""
        shoulder_dist_x = abs(landmarks[11][1] - landmarks[12][1])
        return shoulder_dist_x < self.SIDE_VIEW_X_LIMIT

    def get_leg_ratio(self, landmarks):
        """Calculates normalized leg width relative to hip width."""
        hip_width = abs(landmarks[23][1] - landmarks[24][1])
        ankle_dist = abs(landmarks[27][1] - landmarks[28][1])
        if hip_width < 10: return None
        return ankle_dist / hip_width

    def analyze_frame(self, angles, landmarks, user_profile):
        """
        Processes squat frame with strict depth-reached validation.
        """
        curr_time = time.time()
        knee_angle = angles.get("knee", 180)
        
        # Determine specific depth threshold for this user
        user_cat = self._get_user_category(user_profile)
        depth_threshold = self._get_depth_threshold(user_cat)
        
        current_frame_warnings = []
        side_view = self.is_side_view(landmarks)
        leg_ratio = self.get_leg_ratio(landmarks)

        # 1. POSTURE VALIDATION
        rep_is_valid = True
        if not side_view and leg_ratio is not None:
            if leg_ratio < 0.8:
                self.warning_counters["too_close"] += 1
                if self.warning_counters["too_close"] > self.STABILITY_FRAMES:
                    current_frame_warnings.append("Legs too close")
                    rep_is_valid = False
            elif leg_ratio > 1.8:
                self.warning_counters["too_wide"] += 1
                if self.warning_counters["too_wide"] > self.STABILITY_FRAMES:
                    current_frame_warnings.append("Legs too wide")
                    rep_is_valid = False
            else:
                self.warning_counters["too_close"] = 0
                self.warning_counters["too_wide"] = 0

        self.warnings = current_frame_warnings

        # 2. STATE MACHINE & STRICT REP COUNTING
        
        # Monitor for Depth Reached
        if knee_angle < depth_threshold:
            self.depth_reached = True
            
        # Transition to DOWN state
        if self.depth_reached and self.stage == "up":
            self.stage = "down"

        # Transition to UP (Completion Phase)
        if knee_angle > self.UP_THRESHOLD:
            if self.stage == "down":
                # Cycle complete attempt
                self.total_attempts += 1
                
                # STRICT RULE: Rep counted ONLY if depth was reached
                if self.depth_reached:
                    if rep_is_valid:
                        self.rep_count += 1
                        self.correct_reps += 1
                
                # MANDATORY RESET: Reset depth flag and stage for next cycle
                self.stage = "up"
                self.depth_reached = False
            else:
                # Reset depth flag if user stood up without completing a 'down' cycle
                self.depth_reached = False

        # 3. ACCURACY CALCULATION
        accuracy = (self.correct_reps / self.total_attempts * 100) if self.total_attempts > 0 else 0.0

        self.prev_knee_angle = knee_angle
        self.last_time = curr_time

        return {
            "rep_count": self.rep_count,
            "stage": self.stage,
            "accuracy": round(accuracy, 2),
            "warnings": self.warnings
        }

# --- PUBLIC API ---
_analyzer = SquatAnalyzer()

def process_squat(angles, landmarks, user_profile):
    """
    Processes a squat frame ensuring depth thresholds are strictly enforced.
    """
    return _analyzer.analyze_frame(angles, landmarks, user_profile)