import cv2
import HandModule as hm
import time
import gamefunctions2 as gf
import os
import numpy as np
from google.protobuf.json_format import MessageToDict


camw, camh = 640 *1.5, 720
vid = cv2.VideoCapture(0)
vid.set(3, camw)
#vid.set(4, camh)
detector = hm.handDetector(detectionCon=0.5, maxHands=1)
choice = stage = winRate = 0
path = "symbols"
mylist = os.listdir(path)
imglist = []
imgSize = [210, 211]
imgSize2 = [750,211]
for imgPath in mylist:
    image = cv2.imread(f'{path}/{imgPath}')
    imglist.append(image)
currentTime = time.time()
outcome = "none"
result = [0, 0, 0]
wordList = ["paper", "rock", "scissors", "", "select", "none"]
po = 1
detector1 = hm.HandGadgets()
while True:
    success, frame = vid.read()
    lmlist = detector.findPosition(frame, draw=False)[0]
    hand = detector.findPosition(frame, draw=False)[1]
    if len(lmlist) != 0 :
        detector1.DrawHandLandmarks(frame, lmlist, wordList[po])
    timenow = 0
    cv2.circle(frame, (int(frame.shape[1] / 2), 90), 90, (0, 255, 0),cv2.FILLED)
    print(po)
   # po = None
    if stage != 3:
        po = gf.pos(lmlist, hand, frame, imgSize, imglist, draw=True)
    else:
        po = gf.pos(lmlist,hand ,frame, imgSize, imglist, draw=False)

    if po == 4 and 390 < lmlist[8][1] < 570 and 0 < lmlist[8][2] < 180 and stage != 1:
        currentTime = time.time()
        stage = 1
    if stage == 0 :
        cv2.putText(frame, "PLAY", (int((frame.shape[1] / 2) - 80), 110), cv2.FONT_HERSHEY_COMPLEX, 2,
                    (255, 255, 255), 4)
    if stage == 1:
        cv2.circle(frame, (int(frame.shape[1] / 2), 90), 90, (0, 0, 255), cv2.FILLED)
        timenow = (currentTime - time.time()) * -1
        cv2.putText(frame, str(int(5 - timenow)), (int((frame.shape[1] / 2) - 25), 120), cv2.FONT_HERSHEY_COMPLEX, 3,
                    (255, 255, 255), 7)
    if timenow >= 5 and stage == 1:
        currentTime = time.time()
        stage = 2
    if stage == 2:
        results = gf.find(po)
        po1 = po
        if type(results) == tuple:
            if results[0] != "Empty":
                outcome = results[0]
                choice = results[1]
                outcome1 = results[2]
                Winrate1 = result[0]
                Winrate2 = result[1]
                totalPlays = result[2]
                if outcome1 == 0:
                    Winrate2 += 1
                elif outcome1 == 1:
                    Winrate1 += 1
                if outcome1 != 2:
                    totalPlays += 1
                result.clear()
                result.insert(0, Winrate1)
                result.insert(1, Winrate2)
                result.insert(2, totalPlays)

                stage = 3

    if stage == 3:
        cv2.circle(frame, (int(frame.shape[1] / 2), 90), 90, (255, 0, 0), cv2.FILLED)
        cv2.putText(frame, f'{outcome}', (int((frame.shape[1] / 2) - 70), 100), cv2.FONT_HERSHEY_COMPLEX, 1,
                    (255, 255, 255), 2)
    if stage == 3 or stage == 2:
        frame[0:imgSize[0], (960 - imgSize[1]):960] = imglist[choice]
        if po1 <= 2:
            frame[0:imgSize[0], 0:imgSize[1]] = imglist[po1]
    x1 = int(frame.shape[1] / 4)
    y1 = int(frame.shape[0] - 50)
    x2 = int((frame.shape[1] / 4 + (frame.shape[1] / 2)))
    y2 = int(frame.shape[0] - 10)
    if result[2] != 0:
        winRate = int((result[0] / result[2]) * 100)
        x3 = int(np.interp(winRate, [0, 100], [240, 720]))
        cv2.rectangle(img=frame, pt1=(240, y2), pt2=(int(x3), y1), color=(255, 0, 0), thickness=cv2.FILLED)
        cv2.rectangle(img=frame, pt1=(int(x3), y1), pt2=(x2, y2), color=(0, 0, 255), thickness=cv2.FILLED)

    cv2.putText(frame,f'{result[0]}:{result[1]}', (450, y1-10), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0, 0), 3 )
    cv2.rectangle(img=frame, pt1=(x2, y1), pt2=(240, y2), color=(0, 255, 0), thickness=10)
    cv2.imshow("video", frame)
    cv2.waitKey(1)