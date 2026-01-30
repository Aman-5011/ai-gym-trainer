import cv2
import mediapipe as mp
import time
import math

class poseDetector():
    def __init__(self, mode=False, smooth=True, detectioncon=0.5, trackcon=0.5):
        self.mode = mode
        self.smooth = smooth
        self.detectioncon = detectioncon
        self.trackcon = trackcon

        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=self.mode,
            smooth_landmarks=self.smooth,
            min_detection_confidence=self.detectioncon,
            min_tracking_confidence=self.trackcon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        if self.results.pose_landmarks and draw:
            self.mpDraw.draw_landmarks(
                img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS
            )
        return img

    def getPosition(self, img, draw=True):
        lmList = []
        if self.results.pose_landmarks:
            h, w, c = img.shape
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        return lmList


    def findAngle(self, img, p1, p2, p3, draw=True):
        """
        Calculates the angle at p2 between p1 and p3.
        p1, p2, p3 are landmark indices (e.g., 11, 13, 15).
        """
        # Get coordinates from lmList (assuming getPosition was called)
        # We need to get landmarks from the last results
        h, w, c = img.shape
        landmarks = self.results.pose_landmarks.landmark
        
        # Get coordinates for the three points
        x1, y1 = int(landmarks[p1].x * w), int(landmarks[p1].y * h)
        x2, y2 = int(landmarks[p2].x * w), int(landmarks[p2].y * h)
        x3, y3 = int(landmarks[p3].x * w), int(landmarks[p3].y * h)

        # Calculate the angle using atan2
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - 
                             math.atan2(y1 - y2, x1 - x2))
        
        if angle < 0:
            angle += 360
        if angle > 180:
            angle = 360 - angle

        # Draw the points and lines
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
            
        return angle

def main():
    cap = cv2.VideoCapture('bicep1.mp4')
    pTime = 0
    detector = poseDetector()

    while True:
        success, img = cap.read()
        if not success:
            break

        img = detector.findPose(img)
        lmList = detector.getPosition(img)
        if len(lmList)!=0:
            print(lmList[14])
            cv2.circle(img, (lmList[14][1], lmList[14][2]), 25, (255, 0, 255), cv2.FILLED)

        img = cv2.resize(img, (640, 640))

        cTime = time.time()
        fps = 1 / (cTime - pTime) if cTime != pTime else 0
        pTime = cTime

        cv2.putText(img, str(int(fps)), (70, 70),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 2)

        cv2.imshow("bicep_curls", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
