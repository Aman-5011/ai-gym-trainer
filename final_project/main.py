import cv2
import time
import pose_module as pm
import user_profile as up
import voice_engine as ve
import squat_logic as squat
import pushup_logic as pushup
import bicep_logic as bicep

# ===== ADDED HEART RATE INTEGRATION START =====
import requests
import threading

current_bpm = 0
HEART_RATE_LIMIT = 120

def fetch_heart_rate():
    global current_bpm
    while True:
        try:
            # Fetch data from ESP32 with a short timeout to prevent hangs
            response = requests.get("http://10.178.10.14/data", timeout=0.5)
            if response.status_code == 200:
                data = response.json()
                current_bpm = data.get("bpm", 0)
        except Exception:
            # Fails silently in the background if connection drops
            pass
        time.sleep(1)

# Start the background thread
hr_thread = threading.Thread(target=fetch_heart_rate, daemon=True)
hr_thread.start()
# ===== ADDED HEART RATE INTEGRATION END =====

def main():
    """
    Main orchestration script for the AI Gym Trainer.
    Integrates user profiling, pose detection, exercise-specific logic, 
    and non-blocking voice feedback.
    """
    
    # 1. User Profile Initialization
    user_id = up.setup_user()
    if not user_id:
        print("Failed to initialize user profile. Exiting.")
        return
    
    profile = up.get_user_profile(user_id)
    
    # 2. Exercise Selection
    print("\n--- Exercise Selection ---")
    print("Available: squats, pushups, biceps")
    choice = input("Enter exercise to perform: ").strip().lower()
    
    if choice not in ['squats', 'pushups', 'biceps']:
        print("Invalid exercise selected. Exiting.")
        return

    # 3. Hardware & Pose Engine Setup
    cap = cv2.VideoCapture('vlog1.mp4')
    detector = pm.poseDetector()
    p_time = 0
    
    # Session tracking variables for database persistence
    final_reps = 0
    final_accuracy = 0.0

    ve.speak_motivation(f"Starting {choice} session. Get ready!")

    try:
        while True:
            success, img = cap.read()
            if not success:
                break

            # Standardize frame for portrait-style UI if necessary
            h, w, _ = img.shape
            display_h = 720
            display_w = int(w * (display_h / h))
            img = cv2.resize(img, (display_w, display_h))

            # 4. Pose Detection
            # Use PoseModule to detect landmarks and calculate angles
            img = detector.findPose(img, draw=True)
            lm_list = detector.getPosition(img, draw=False)

            if len(lm_list) != 0:
                # Prepare data structures for logic files
                # Extracting specific angles needed by logic modules
                angles = {
                    "knee": detector.findAngle(img, 23, 25, 27, draw=False),
                    "hip": detector.findAngle(img, 11, 23, 25, draw=False),
                    "elbow": detector.findAngle(img, 12, 14, 16, draw=False),
                    "shoulder": detector.findAngle(img, 14, 12, 24, draw=False),
                    "back": detector.findAngle(img, 12, 24, 26, draw=False) # Verticality reference
                }

                # 5. Modular Logic Routing
                res = {}
                if choice == "squats":
                    res = squat.process_squat(angles, lm_list, profile)
                elif choice == "pushups":
                    res = pushup.process_pushup(angles, lm_list, profile)
                elif choice == "biceps":
                    res = bicep.process_bicep(angles, lm_list, profile)

                # Update session stats
                curr_reps = res.get("rep_count", 0)
                final_accuracy = res.get("accuracy", 0.0)
                
                # 6. Voice Feedback Triggering
                # Trigger rep count on increment
                if curr_reps > final_reps:
                    final_reps = curr_reps
                    ve.speak_rep_count(final_reps)
                    if final_reps % 5 == 0:
                        ve.speak_motivation("Great work, keep it up!")

                # Trigger warnings if present
                for warning in res.get("warnings", []):
                    ve.speak_warning(warning)

                # 7. UI Rendering
                # Display Reps and Accuracy in the top corner
                cv2.rectangle(img, (0, 0), (250, 150), (20, 20, 20), cv2.FILLED)
                cv2.putText(img, f"REPS: {int(final_reps)}", (20, 50), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f"ACC: {final_accuracy}%", (20, 90), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
                cv2.putText(img, f"STAGE: {res.get('stage', '').upper()}", (20, 130), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 0), 1)

                # Display warnings on screen
                if res.get("warnings"):
                    cv2.rectangle(img, (display_w//2 - 150, 0), (display_w//2 + 150, 40), (0, 0, 255), cv2.FILLED)
                    cv2.putText(img, res["warnings"][0], (display_w//2 - 130, 30), 
                                cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

            # ===== ADDED HEART RATE INTEGRATION START =====
            if current_bpm > HEART_RATE_LIMIT:
                cv2.putText(img, "⚠ High Heart Rate!", (display_w//2 - 130, 70), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 255), 2)
            # ===== ADDED HEART RATE INTEGRATION END =====

            # FPS Display
            c_time = time.time()
            fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
            p_time = c_time
            cv2.putText(img, f"FPS: {int(fps)}", (display_w - 100, 30), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 0, 255), 1)

            cv2.imshow("AI Gym Trainer", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # 8. Session Persistence
        # Ensure session is saved even if user quits mid-workout
        print(f"\nSaving session for {profile['name']}...")
        up.save_workout_session(user_id, choice, final_reps, final_accuracy)
        ve.speak_motivation("Workout complete. Session saved to database.")
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()