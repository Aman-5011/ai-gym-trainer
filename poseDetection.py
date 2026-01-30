import cv2
import mediapipe as mp
import time

mpPose=mp.solutions.pose
pose=mpPose.Pose()
mpDraw = mp.solutions.drawing_utils
cap = cv2.VideoCapture('bicep3.mp4')
pTime=0
cTime=0

while True:
    success , img = cap.read()
    imgRGB = cv2.cvtColor(img , cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)

    if results.pose_landmarks:
        mpDraw.draw_landmarks(img , results.pose_landmarks , mpPose.POSE_CONNECTIONS)
        for id , lm in enumerate(results.pose_landmarks.landmark):
            h,w,c=img.shape
            # print(id,lm)
            cx , cy = int(lm.x*w),int(lm.y*h)
            cv2.circle(img ,(cx,cy) , 10 , (0,0,255) , cv2.FILLED)

    if not success:
        print("Video ended or cannot read frame")
        break
    img=cv2.resize(img , (1240,640))

    cTime=time.time()
    fps=1/(cTime-pTime)
    pTime=cTime

    cv2.putText(img , str(int(fps)) , (70,70) , cv2.FONT_HERSHEY_COMPLEX , 3 , (255,0,255) , 3)
    cv2.imshow("bicep_curls",img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()