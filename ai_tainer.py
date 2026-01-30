import cv2
import time
import numpy as np
import poseModule as pm


def process_biceps(detector, img, lmList, count, dir, feedback):
    """Logic for Bicep Curls: Uses Elbow Angle (11, 13, 15) or (12, 14, 16)"""
    # Calculate angle for the right arm
    angle = detector.findAngle(img, 12, 14, 16)
    
    # Calculate percentage and bar for visual feedback
    per = np.interp(angle, (30, 160), (100, 0))
    
    # Repetition Counter Logic
    if per == 100:
        if dir == 0:
            count += 0.5
            dir = 1
    if per == 0:
        if dir == 1:
            count += 0.5
            dir = 0
            
    # Accuracy/Feedback
    if angle > 160:
        feedback = "Good Extension"
    elif angle < 30:
        feedback = "Great Contraction"
        
    return count, dir, per, feedback

def process_pushups(detector, img, lmList, count, dir, feedback):
    """Logic for Push-ups: Uses Elbow (11,13,15) and Hip stability (11,23,25)"""
    elbow = detector.findAngle(img, 11, 13, 15)
    hip = detector.findAngle(img, 11, 23, 25) # Body straightness
    
    per = np.interp(elbow, (70, 160), (100, 0))
    
    # Repetition Counter Logic
    if per == 100:
        if dir == 0:
            count += 0.5
            dir = 1
    if per == 0:
        if dir == 1:
            count += 0.5
            dir = 0

    # Accuracy/Feedback
    if hip < 150:
        feedback = "Keep your back straight!"
    elif elbow > 150:
        feedback = "Go Down Lower"
    else:
        feedback = "Good Form"
        
    return count, dir, per, feedback

def process_squats(detector, img, lmList, count, dir, feedback):
    """Logic for Squats: Uses Knee (23,25,27) and Hip (11,23,25)"""
    knee = detector.findAngle(img, 23, 25, 27)
    hip = detector.findAngle(img, 11, 23, 25)
    
    # Mapping knee angle to percentage (Standing ~170, Deep Squat ~70)
    per = np.interp(knee, (75, 160), (100, 0))
    
    # Repetition Counter Logic
    if per == 100:
        if dir == 0:
            count += 0.5
            dir = 1
    if per == 0:
        if dir == 1:
            count += 0.5
            dir = 0
            
    # Accuracy/Feedback: Depth and Back posture
    if hip < 80:
        feedback = "Don't lean too far forward"
    elif knee > 160:
        feedback = "Stand Tall"
    elif knee < 100:
        feedback = "Good Depth"
    else:
        feedback = "Squat Deeper"
        
    return count, dir, per, feedback

# --------------------------------------------------------------------------
# MAIN SYSTEM
# --------------------------------------------------------------------------

def main():
    # 1. User Input for Exercise Selection
    print("--- AI Gym Trainer Activated ---")
    print("Select Exercise: squats / pushups / biceps")
    choice = input("Enter choice: ").strip().lower()

    if choice not in ['squats', 'pushups', 'biceps']:
        print("Invalid choice. Exiting.")
        return

    # 2. Initialization
    cap = cv2.VideoCapture('squats.mp4')
    detector = pm.poseDetector()
    count = 0
    dir = 0 # 0 is going down/extending, 1 is coming up/contracting
    feedback = "Fix your posture"
    pTime = 0

    while True:
        success, img = cap.read()
        if not success: break
        
        img = detector.findPose(img, draw=False)
        lmList = detector.getPosition(img, draw=False)

        if len(lmList) != 0:
            # 3. Route to specific exercise logic
            if choice == "biceps":
                count, dir, per, feedback = process_biceps(detector, img, lmList, count, dir, feedback)
            elif choice == "pushups":
                count, dir, per, feedback = process_pushups(detector, img, lmList, count, dir, feedback)
            elif choice == "squats":
                count, dir, per, feedback = process_squats(detector, img, lmList, count, dir, feedback)

            # 4. Draw Visual UI
            # Progress Bar
            cv2.rectangle(img, (580, 100), (610, 400), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(400 - (per * 3))), (610, 400), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (565, 90), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            # Rep Counter
            cv2.rectangle(img, (0, 450), (250, 720), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, str(int(count)), (45, 670), cv2.FONT_HERSHEY_PLAIN, 15, (255, 0, 0), 25)
            
            # Feedback text
            cv2.rectangle(img, (500, 0), (1280, 50), (255, 255, 255), cv2.FILLED)
            cv2.putText(img, feedback, (520, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
            
            # Exercise Stage (Up/Down)
            stage = "DOWN" if dir == 0 else "UP"
            cv2.putText(img, f"STAGE: {stage}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

   
        cTime = time.time()       # FPS Calculation
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f"FPS: {int(fps)}", (10, 90), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        img = cv2.resize(img, (1240, 600))
        cv2.imshow("AI Gym Trainer", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()