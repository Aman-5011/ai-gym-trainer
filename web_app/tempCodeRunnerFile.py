import cv2
import time
import pose_module as pm
import voice_engine as ve
import squat_logic as squat
import pushup_logic as pushup
import bicep_logic as bicep
import heart_rate_provider as hr
import auth_system as auth

def handle_auth(db):
    """
    Orchestrates the login and signup flow using the AuthSystem.
    Returns the user_id and user_profile dictionary.
    """
    print("\n" + "="*30)
    print("      AI GYM TRAINER")
    print("="*30)
    print("1. Login")
    print("2. Sign Up")
    choice = input("Select an option (1/2): ").strip()

    user_id = None

    if choice == '2':
        # SIGN UP FLOW
        print("\n--- Create New Account ---")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        user_id = db.create_user(username, email, password)
        
        if user_id:
            print("\n--- Complete Your Profile ---")
            try:
                age = int(input("Age: "))
                height = float(input("Height (cm): "))
                weight = float(input("Weight (kg): "))
                level = input("Fitness Level (beginner/intermediate/advanced): ").strip().lower()
                goal = input("Primary Goal: ").strip()
                
                db.save_profile(user_id, age, height, weight, level, goal)
                print("\nProfile created successfully!")
            except ValueError:
                print("Invalid data entered. Using default profile values.")
                db.save_profile(user_id, 25, 170, 70, "beginner", "general fitness")
        else:
            print("Error: Username or Email already exists.")
            return None, None

    elif choice == '1':
        # LOGIN FLOW
        print("\n--- User Login ---")
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        user_id = db.login_user(email, password)
        
        if not user_id:
            print("Error: Invalid email or password.")
            return None, None
    else:
        print("Invalid choice.")
        return None, None

    # Fetch and display profile
    profile = db.get_profile(user_id)
    if profile:
        print("\n" + "-"*30)
        print(f"Welcome back!")
        print(f"BMI: {profile.get('bmi', 'N/A')}")
        print(f"Goal: {profile.get('goal', 'N/A')}")
        print(f"Level: {profile.get('fitness_level', 'N/A')}")
        print("-"*30)
        return user_id, profile
    
    return None, None

def main():
    # A. INITIALIZATION
    db = auth.AuthSystem()
    db.init_db()
    
    # B. LOGIN FLOW
    user_id, profile = handle_auth(db)
    if not user_id:
        return

    # Heart Rate Integration (Hardware bridge)
    # Replace with your ESP32 IP address
    esp32_ip = "192.168.1.100" 
    hr_provider = hr.initialize_hr_provider(esp32_ip)

    # C. EXERCISE SELECTION
    print("\nAvailable Exercises: squats, pushups, biceps")
    exercise_choice = input("Select exercise: ").strip().lower()
    
    if exercise_choice not in ['squats', 'pushups', 'biceps']:
        print("Invalid exercise selected.")
        return

    # Hardware & Pose Engine Setup
    cap = cv2.VideoCapture(0)
    detector = pm.poseDetector()
    p_time = 0
    
    # Session tracking
    final_reps = 0
    final_accuracy = 0.0

    ve.speak_motivation(f"Starting {exercise_choice} session. Position yourself.")

    try:
        while True:
            success, img = cap.read()
            if not success:
                break

            # Resize for consistent UI
            h, w, _ = img.shape
            display_h = 720
            display_w = int(w * (display_h / h))
            img = cv2.resize(img, (display_w, display_h))

            # D. POSE DETECTION
            img = detector.findPose(img, draw=True)
            lm_list = detector.getPosition(img, draw=False)

            if len(lm_list) != 0:
                # Extract joint angles for logic modules
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
                curr_reps = res.get("rep_count", 0)
                final_accuracy = res.get("accuracy", 0.0)
                
                # F. VOICE FEEDBACK
                if curr_reps > final_reps:
                    final_reps = curr_reps
                    ve.speak_rep_count(final_reps)
                    if final_reps % 5 == 0:
                        ve.speak_motivation("Keep pushing!")

                for warning in res.get("warnings", []):
                    ve.speak_warning(warning)

                # G. UI OVERLAY
                # Heart Rate Data
                hr_data = hr_provider.get_heart_rate_data()
                
                # Sidebar/Overlay Stats
                cv2.rectangle(img, (0, 0), (280, 200), (20, 20, 20), cv2.FILLED)
                cv2.putText(img, f"REPS: {int(final_reps)}", (20, 50), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f"ACC: {final_accuracy}%", (20, 90), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
                cv2.putText(img, f"BPM: {hr_data['bpm']}", (20, 130), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255) if hr_data['connected'] else (128, 128, 128), 2)
                cv2.putText(img, f"STAGE: {res.get('stage', '').upper()}", (20, 175), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 0), 1)

            # FPS Display
            c_time = time.time()
            fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
            p_time = c_time
            cv2.putText(img, f"FPS: {int(fps)}", (display_w - 100, 30), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 0, 255), 1)

            cv2.imshow("AI Gym Trainer - Session Active", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # H. SESSION SAVE
        print(f"\nFinalizing session...")
        
        # Simple estimated metrics
        calories_burned = final_reps * 0.5
        target_completed = 1 if final_reps >= 10 else 0
        
        db.save_workout(
            user_id=user_id,
            exercise=exercise_choice,
            reps=int(final_reps),
            accuracy=float(final_accuracy),
            calories_burned=float(calories_burned),
            target_completed=target_completed
        )
        
        ve.speak_motivation("Session complete. Data synced to your profile.")
        
        cap.release()
        cv2.destroyAllWindows()
        hr_provider.stop()

if __name__ == "__main__":
    main()