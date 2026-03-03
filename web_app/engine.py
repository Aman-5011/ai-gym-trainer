import cv2
import time
import sys
import json
import pose_module as pm
import squat_logic as squat
import pushup_logic as pushup
import bicep_logic as bicep
# Import specific singleton helpers from your refined provider
from heart_rate_provider import initialize_hr_provider, get_current_hr, stop_hr_provider

def main():
    # A. ARGUMENT PARSING
    if len(sys.argv) < 3:
        print("Usage: python engine.py <exercise> <fitness_level>")
        return

    exercise_choice = sys.argv[1].lower()
    fitness_level = sys.argv[2].lower()

    if exercise_choice not in ['squats', 'pushups', 'biceps']:
        print(f"Invalid exercise: {exercise_choice}")
        return

    # B. BIOMETRIC SETUP
    esp32_ip = "192.168.1.100" 
    initialize_hr_provider(esp32_ip)

    # Create simple profile dict instead of DB fetch
    profile = {
        "fitness_level": fitness_level
    }

    cap = cv2.VideoCapture('p3.mp4') 
    detector = pm.poseDetector()
    p_time = 0
    
    # Session tracking
    final_reps = 0
    final_accuracy = 0.0

    try:
        while True:
            success, img = cap.read()
            if not success:
                break

            # UI Frame Normalization
            h, w, _ = img.shape
            display_h = 720
            display_w = int(w * (display_h / h))
            img = cv2.resize(img, (display_w, display_h))

            # D. POSE DETECTION
            img = detector.findPose(img, draw=True)
            lm_list = detector.getPosition(img, draw=False)

            if len(lm_list) != 0:
                # Extract angles for rule-based logic
                angles = {
                    "knee": detector.findAngle(img, 23, 25, 27, draw=False),
                    "hip": detector.findAngle(img, 11, 23, 25, draw=False),
                    "elbow": detector.findAngle(img, 12, 14, 16, draw=False),
                    "shoulder": detector.findAngle(img, 14, 12, 24, draw=False),
                    "back": detector.findAngle(img, 12, 24, 26, draw=False)
                }

                # E. EXERCISE LOGIC ROUTING
                res = {}
                if exercise_choice == "squats":
                    res = squat.process_squat(angles, lm_list, profile)
                elif exercise_choice == "pushups":
                    res = pushup.process_pushup(angles, lm_list, profile)
                elif exercise_choice == "biceps":
                    res = bicep.process_bicep(angles, lm_list, profile)

                # Update session stats
                final_reps = res.get("rep_count", 0)
                final_accuracy = res.get("accuracy", 0.0)

                # F. UI OVERLAY (HUD)
                # Call the global helper to get latest thread data
                hr_data = get_current_hr()
                
                cv2.rectangle(img, (0, 0), (280, 200), (25, 25, 25), cv2.FILLED)
                
                cv2.putText(img, f"REPS: {int(final_reps)}", (20, 50), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f"ACC: {final_accuracy}%", (20, 90), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
                
                # Dynamic heart rate coloring
                hr_color = (0, 0, 255) if hr_data['connected'] else (100, 100, 100)
                cv2.putText(img, f"BPM: {hr_data['bpm']}", (20, 130), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, hr_color, 2)
                
                cv2.putText(img, f"STAGE: {res.get('stage', '').upper()}", (20, 175), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 0), 1)

            # Performance Metrics (FPS)
            c_time = time.time()
            fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
            p_time = c_time
            cv2.putText(img, f"FPS: {int(fps)}", (display_w - 100, 30), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (200, 0, 200), 1)

            cv2.imshow("AI Gym Trainer - Active Session", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # G. CLEANUP AND FINAL OUTPUT
        calories_burned = final_reps * 0.435
        
        # Terminal Output
        print(f"FINAL_REPS={int(final_reps)}")
        print(f"FINAL_ACCURACY={float(final_accuracy)}")
        print(f"CALORIES={float(calories_burned)}")

        # JSON Persistence
        session_data = {
            "exercise": exercise_choice,
            "reps": int(final_reps),
            "accuracy": float(final_accuracy),
            "calories": float(calories_burned)
        }

        with open("last_session.json", "w") as f:
            json.dump(session_data, f)
        
        cap.release()
        cv2.destroyAllWindows()
        # Ensure the background thread is terminated
        stop_hr_provider()

if __name__ == "__main__":
    main()