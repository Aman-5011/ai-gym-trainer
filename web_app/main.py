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
    Orchestrates the login and signup flow.
    Returns user_id if successful, else None.
    """
    print("\n" + "="*30)
    print("      AI GYM TRAINER")
    print("="*30)
    print("1. Login")
    print("2. Sign Up")
    choice = input("Select an option (1/2): ").strip()

    if choice == '2':
        # --- SIGN UP FLOW ---
        print("\n--- Create New Account ---")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        user_id = db.create_user(username, email, password)
        if not user_id:
            return None

        print("\n--- Complete Your Profile ---")
        try:
            age = int(input("Age: "))
            height = float(input("Height (cm): "))
            weight = float(input("Weight (kg): "))
            level = input("Fitness Level (beginner/intermediate/advanced): ").strip().lower()
            
            # Structured Goal Selection
            goal_map = {
                "1": "fat_loss",
                "2": "muscle_gain",
                "3": "endurance",
                "4": "general_training"
            }
            
            while True:
                print("\nSelect your primary goal:")
                print("1. Fat Loss")
                print("2. Muscle Gain")
                print("3. Endurance")
                print("4. General Training")
                goal_choice = input("Selection (1-4): ").strip()
                
                if goal_choice in goal_map:
                    goal = goal_map[goal_choice]
                    break
                print("Invalid selection. Please choose 1-4.")

            db.save_profile(user_id, age, height, weight, level, goal)
            print("\nAccount and Profile created successfully!")
            return user_id
            
        except ValueError:
            print("Invalid numeric data entered. Profile setup failed.")
            return None

    elif choice == '1':
        # --- LOGIN FLOW ---
        print("\n--- User Login ---")
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        user_id = db.login_user(email, password)
        if not user_id:
            print("Error: Invalid email or password.")
            return None
        
        # Display Profile Stats after Login
        profile = db.get_profile(user_id)
        if profile:
            print("\n" + "-"*30)
            print(f"Welcome back!")
            print(f"BMI: {profile.get('bmi', 'N/A')}")
            print(f"Goal: {profile.get('goal', 'N/A')}")
            print(f"Fitness Level: {profile.get('fitness_level', 'N/A')}")
            print("-" * 30)
            return user_id
    
    else:
        print("Invalid choice.")
    
    return None

def main():
    # A. INITIALIZATION
    db = auth.AuthSystem()
    db.init_db()
    
    # B. AUTHENTICATION
    user_id = handle_auth(db)
    if not user_id:
        print("Authentication failed. Exiting.")
        return

    # Fetch profile for logic modules
    profile = db.get_profile(user_id)

    # C. HARDWARE INTEGRATION (ESP32)
    # Ensure your ESP32 IP address is correct
    esp32_ip = "192.168.1.100" 
    hr_provider = hr.initialize_hr_provider(esp32_ip)

    # D. EXERCISE SELECTION
    print("\nAvailable Exercises: squats, pushups, biceps")
    exercise_choice = input("Select exercise to begin: ").strip().lower()
    
    if exercise_choice not in ['squats', 'pushups', 'biceps']:
        print("Invalid exercise selected. Exiting.")
        return

    # Pose Engine Setup
    cap = cv2.VideoCapture('vlog1.mp4')
    detector = pm.poseDetector()
    p_time = 0
    
    # Session tracking
    final_reps = 0
    final_accuracy = 0.0

    ve.speak_motivation(f"Starting {exercise_choice} session. Get into position.")

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

            # E. POSE DETECTION
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

                # F. EXERCISE LOGIC ROUTING
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
                
                # G. VOICE FEEDBACK
                if curr_reps > final_reps:
                    final_reps = curr_reps
                    ve.speak_rep_count(final_reps)
                    if final_reps % 5 == 0:
                        ve.speak_motivation("Excellent form, keep going!")

                for warning in res.get("warnings", []):
                    ve.speak_warning(warning)

                # H. UI OVERLAY (HUD)
                hr_data = hr_provider.get_heart_rate_data()
                
                cv2.rectangle(img, (0, 0), (280, 200), (25, 25, 25), cv2.FILLED)
                cv2.putText(img, f"REPS: {int(final_reps)}", (20, 50), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, f"ACC: {final_accuracy}%", (20, 90), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
                
                # Dynamic Heart Rate Display
                hr_color = (0, 0, 255) if hr_data['connected'] else (100, 100, 100)
                cv2.putText(img, f"BPM: {hr_data['bpm']}", (20, 130), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, hr_color, 2)
                
                cv2.putText(img, f"STAGE: {res.get('stage', '').upper()}", (20, 175), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 0), 1)

            # Performance Metrics
            c_time = time.time()
            fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
            p_time = c_time
            cv2.putText(img, f"FPS: {int(fps)}", (display_w - 100, 30), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (200, 0, 200), 1)

            cv2.imshow("AI Gym Trainer - Active Session", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # I. SESSION PERSISTENCE
        print(f"\nClosing session and saving data...")
        
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
        
        ve.speak_motivation("Workout session finalized. Great job today!")
        
        cap.release()
        cv2.destroyAllWindows()
        hr_provider.stop()

if __name__ == "__main__":
    main()