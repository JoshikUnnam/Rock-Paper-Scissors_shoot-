import cv2
import mediapipe as mp
import math
from google.protobuf.json_format import MessageToDict
import numpy as np
import pyrebase
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class handDetector():
    def __init__(self, mode=False, maxHands=1, detectionCon=0.7, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.barvol = 0
        self.barpercentange = 0
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img,
                    handLms,
                    self.mpHands.HAND_CONNECTIONS,
                    self.mpDraw.DrawingSpec(color = (0, 0, 255), circle_radius= 3, thickness= cv2.FILLED),
                    self.mpDraw.DrawingSpec(color = (0, 255, 0), thickness=3)
                    )

        return img

    def draw(self, img1, img2, draw=True):
        imgRGB = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img2,
                                               handLms,
                                               self.mpHands.HAND_CONNECTIONS,
                                               self.mpDraw.DrawingSpec(color=(0, 0, 255), circle_radius=3,
                                                                       thickness=cv2.FILLED),
                                               self.mpDraw.DrawingSpec(color=(0, 255, 0), thickness=3)
                                               )

        return img2
    def findPosition(self, img, handNo=0, draw = False ):
        hand = []
        lmlist = []
        length = 0
        l = 0
        imgRGB  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        x1, x2, y1, y2 = 0, 0, 0, 0
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
                handlm = self.results.multi_hand_landmarks[handNo]
                for id, lm in enumerate(handlm.landmark):
                    h, w, c = img.shape
                    cx, cy, cd = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                   # print(id, cy, cx)
                    lmlist.append([id, cx, cy])
                    if draw :
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        go = "unknown"
        if self.results.multi_hand_landmarks:
            for idx, hand_handedness in enumerate(self.results.multi_handedness):
                handedness_dict = MessageToDict(hand_handedness)
                go = (handedness_dict.get('classification')[0].get('label'))
                if go == "Left":
                    go = "Right"
                else :
                    go = "Left"


        return lmlist, go

class HandGadgets :
    def __init__(self, detection = True, SendToFirebase = False, maxhands=1,  mode=False, maxHands=1, detectionCon=0.7, trackCon=0.5):
        self.detector = handDetector(detectionCon=detectionCon, maxHands=maxhands) #hand module used to detect and identify the points on the hand
        self.firebasevalue = SendToFirebase # firebase confermation
        self.barvol = 0
        self.barpercentage = 0
        self.mpHands = mp.solutions.hands
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.detectionCon, self.trackCon)
        self.devices = AudioUtilities.GetSpeakers()
        self.mpdraw = mp.solutions.drawing_utils
        interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def  DrawHandLandmarks(self, frame, lmlist, word):
        LilFrame = frame
        RGBframe = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(RGBframe)
        def x(x):
            return x[1]

        def y(y):
            return y[2]

        if result.multi_hand_landmarks:
            # print("hand found")

            print(lmlist)
            xlist = sorted(lmlist, key=x)
            ylist = sorted(lmlist, key=y)
            x1, x2 = xlist[0][1] - 20, xlist[len(xlist) - 1][1] + 20
            y1, y2 = ylist[0][2] - 20, ylist[len(ylist) - 1][2] + 20
            LilFrame = LilFrame[y1 : y2, x1 : x2]
            for handLm in result.multi_hand_landmarks:
                # print(handLm)
                self.mpdraw.draw_landmarks(frame,
                                           handLm,
                                           self.mpHands.HAND_CONNECTIONS,
                                           self.mpdraw.DrawingSpec(color=(0, 0, 255), circle_radius=6,
                                                                   thickness=cv2.FILLED),
                                           self.mpdraw.DrawingSpec(color=(0, 255, 0), thickness=6)
                                           )
            cv2.rectangle(frame, (x1, y2), (x2, y1), (0, 255, 0), 5)
            cv2.putText(frame, word, (x1, y1 - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        return frame
    def Distance(self, frame):
        dis = []
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)
        if results.multi_hand_landmarks:
            for handlms in results.multi_hand_landmarks:
                for id, lm in enumerate(handlms.landmark):
                    h, w, c = frame.shape
                    z = (lm.z * w)
                    z1 = np.interp(z, [-400, 100], [255, 0])
                    dis.append(z1)
        return dis

    def DrawFull(self, frame, draw = False, lmlist = None):
        img = frame.copy()

        if draw == True :
            self.detector.findHands(img)
            lmlist = self.detector.findPosition(img)[0]
        else :
            lmlist = lmlist
        x1 = x2 = y1 = y2 = 0

        def x(list):
            return list[1]

        def y(list):
            return list[2]
        if len(lmlist) != 0 :
            xlist = sorted(lmlist, key=x)
            ylist = sorted(lmlist, key=y)
            x1, x2 = xlist[0][1] - 10, xlist[len(xlist) - 1][1] + 10
            x1 -= 10
            x2 += 10
            y1, y2 = ylist[0][2] - 10, ylist[len(ylist) - 1][2] + 10
            y1 -= 10
            y2 += 10
           # cv2.rectangle(img=img, pt1=(x1, y1), pt2=(x2, y2), color=(255, 0, 255), thickness=5)
        return img, x1, x2, y1, y2
    def FindPos(self, frame):
        i = 0
        hand1 = self.detector.findPosition(frame)[0]
        hand = self.detector.findPosition(frame)[1]
        points = [8, 12, 16, 20]
        tippoints = []
        threshpoints = []
        status = []
        number = 0
        if len(hand1) != 0:
            tippoints.append(hand1[4])
            threshpoints.append(hand1[3])
            i, tx, ty = tippoints[0]
            i, tx1, ty1 = threshpoints[0]
            if tx > tx1 and hand == "Right":
                number += 1
                status.append(1)
            if tx < tx1 and hand == "Left":
                number += 1
                status.append(1)
            else:
                status.append(0)

            i = 1
            while i <= 4:
                j = i - 1
                tippoints.append(hand1[points[j]])
                threshpoints.append(hand1[points[j] - 3])
                id, cx, cy = tippoints[i][0], tippoints[i][1], tippoints[i][2]
                id, cx1, cy1 = threshpoints[i][0], threshpoints[i][1], threshpoints[i][2]
                # print(cy, cy1)
                if cy < cy1:
                    status.insert(i, 1)
                    number = number + 1
                else:
                    status.insert(i, 0)
                i = i + 1
        if len(status) > 5 :
            statusnew = []
            for i in range(0, 5) :
                statusnew.append(status[i])
            status = statusnew
        return status, number
    def FindDistance(self, p1, p2, frame, draw = True):
        x1, y1 = self.lmlist[4][1], self.lmlist[4][2]
        x2, y2 = self.lmlist[8][1], self.lmlist[8][2]
        x, y = (x1 + x2) // 2, (y1 + y2) // 2
        if draw == True :
            cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(frame, (x, y), 10, (255, 0, 255), cv2.FILLED)
        distance = math.hypot(x2 - x1, y2 - y1)
    def TiltBase(self, frame):
        firebaseConfig = { # firebase configaration to the firebase database
             "apiKey": "AIzaSyA1501tS1oe8YF-F7CCeFosUbCCovPrq9Q",
             "authDomain": "python1-f0771.firebaseapp.com",
             "databaseURL": "https://python1-f0771-default-rtdb.firebaseio.com",
             "projectId": "python1-f0771",
             "storageBucket": "python1-f0771.appspot.com",
             "messagingSenderId": "696223136031",
             "appId": "1:696223136031:web:8aa3053818556f79dfd82a",
             "measurementId": "G-VYSJV75J0R"
        }
        self.firebase = pyrebase.initialize_app(firebaseConfig)
        self.database = self.firebase.database()
        frame = self.detector.findHands(frame)
        location = self.detector.findPosition(frame)[0]
        if len(location) != 0:
            # getting the locations
            i, x, y = location[0]
            i, x1, y1 = location[9]
            i, indexX, indexY = location[12]
            x2, y2 = ((x + x1) // 2), ((y + y1) // 2)
            bx1, bx2 = x2 + 40, x2 - 40
            status = 0
            # checking
            # print(indexY)
            # 110, 850
            # checking cv2.line(frame, (0, indexY), (960, indexY), (255, 0, 0), 4)  # horizontal center line
            # h, w, c = frame.shape
            # print(h)
            cv2.line(frame, (0, 110), (960, 110), (255, 0, 0), 4)  # horizontal center line
            cv2.line(frame, (0, 430), (960, 430), (255, 0, 0), 4)  # horizontal center line
            cv2.line(frame, (x2, 0), (x2, 720), (255, 0, 0), 4)  # vertical center line
            cv2.line(frame, (x, y), (x1, y1), (0, 255, 0), 2)  # center line
            cv2.line(frame, (0, y2), (960, y2), (255, 0, 0), 4)  # horizontal center line
            detectionStatus = "hand detected"
            if self.firebasevalue == True:
                self.database.child("data").child("detection").update({"detectionStatus": detectionStatus})
            if indexX > bx1:
               # cv2.putText(frame, "status : right ", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                cv2.line(frame, (bx1, 0), (bx1, 720), (0, 255, 0), 2, )  # threshold 1
                cv2.line(frame, (bx2, 0), (bx2, 720), (0, 255, 0), 2, )  # threshold 2
                status = "right"
                if self.firebasevalue == True:
                    self.database.child("data").child("direction").update({"directionStatus": status})
            elif indexX < bx2:
               # cv2.putText(frame, "status : left ", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                cv2.line(frame, (bx1, 0), (bx1, 720), (0, 255, 0), 2, )  # threshold 1
                cv2.line(frame, (bx2, 0), (bx2, 720), (0, 255, 0), 2, )  # threshold 2
                status = "left"
                if self.firebasevalue == True:
                    self.database.child("data").child("direction").update({"directionStatus": status})
            elif indexY < 110:
                cv2.putText(frame, "status : up ", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                cv2.line(frame, (bx1, 0), (bx1, 720), (0, 255, 0), 2, )  # threshold 1
                cv2.line(frame, (bx2, 0), (bx2, 720), (0, 255, 0), 2, )  # threshold 2
                status = "up"
                if self.firebasevalue == True:
                    self.database.child("data").child("direction").update({"directionStatus": status})
            elif y > 430:
                cv2.putText(frame, "status : down ", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                cv2.line(frame, (bx1, 0), (bx1, 720), (0, 255, 0), 2, )  # threshold 1
                cv2.line(frame, (bx2, 0), (bx2, 720), (0, 255, 0), 2, )  # threshold 2
                status = "down"
                if self.firebasevalue == True:
                    self.database.child("data").child("direction").update({"directionStatus": status})
            else:
                cv2.putText(frame, "status : normal ", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
                cv2.line(frame, (bx1, 0), (bx1, 720), (0, 0, 255), 2, )  # threshold 1
                cv2.line(frame, (bx2, 0), (bx2, 720), (0, 0, 255), 2, )  # threshold 2
                status = "stationary"
                if self.firebasevalue == True:
                    self.database.child("data").child("direction").update({"directionStatus": status})
            cv2.circle(frame, (x2, y2), 8, (0, 255, 0), cv2.FILLED)  # center point
        else:
            detectionStatus = "hand not detected"
            status = "not detected"
            if self.firebasevalue == True:
                self.database.child("data").child("detection").update({"detectionStatus": detectionStatus})
                self.database.child("data").child("direction").update({"directionStatus": "null"})
            cv2.putText(frame, "status : not detected", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
        return frame, status

    def VolumeControl(self, frame, volrange, fingerset = False ):
        frame = self.detector.findHands(frame)
        lmlist = self.detector.findPosition(frame, draw=False)[0]
        volRange = volrange
        minVol = volRange[0]
        maxVol = volRange[1]
        distance = 0
        barpercentage = 0
        if len(lmlist) != 0:
            graph = self.FindPos(frame)[0]
            x1, y1 = lmlist[4][1], lmlist[4][2]
            x2, y2 = lmlist[8][1], lmlist[8][2]
            x, y = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(frame, (x, y), 10, (255, 0, 255), cv2.FILLED)
            distance = math.hypot(x2 - x1, y2 - y1)

            # print(distance)

            # hand volume range 15 - 300
            # volume range -65-0

            vol = np.interp(distance, [50, 300], [minVol, maxVol])
            barvol = np.interp(distance, [50, 300], [500, 100])
            barpercentage = np.interp(distance, [50, 300], [0, 100])

            if graph == [1, 1, 0, 0, 0] and fingerset == True :

                self.volume.SetMasterVolumeLevel(vol, None)

                if distance < 175:
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                    cv2.circle(frame, (x, y), 10, (255, 0, 0), cv2.FILLED)
                if distance > 175:
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.circle(frame, (x, y), 10, (0, 255, 0), cv2.FILLED)
                if distance > 300:
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.circle(frame, (x, y), 10, (0, 0, 255), cv2.FILLED)
            elif fingerset == False:
                self.volume.SetMasterVolumeLevel(vol, None)

                if distance < 175:
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                    cv2.circle(frame, (x, y), 10, (255, 0, 0), cv2.FILLED)
                if distance > 175:
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.circle(frame, (x, y), 10, (0, 255, 0), cv2.FILLED)
                if distance > 300:
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.circle(frame, (x, y), 10, (0, 0, 255), cv2.FILLED)
            cv2.rectangle(frame, (75, 100), (128, 500), (0, 255, 0), 3)
            cv2.rectangle(frame, (75, int(barvol)), (128, 500), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, f'{int(barpercentage)}%', (65, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
            if barpercentage < 50:
                cv2.rectangle(frame, (75, int(barvol)), (128, 500), (255, 0, 0), cv2.FILLED)
            if barpercentage > 50:
                cv2.rectangle(frame, (75, int(barvol)), (128, 500), (0, 255, 0), cv2.FILLED)
            if barpercentage >= 75:
                cv2.rectangle(frame, (75, int(barvol)), (128, 500), (0, 0, 255), cv2.FILLED)

        return frame, barpercentage, distance
def main() :
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()
    pTime = 0
    cTime = 0
    detector = HandGadgets()
    #############################
    camw, camh = 960, 720
    #############################

    vid = cv2.VideoCapture(0)
    vid.set(3, camw)
    vid.set(4, camh)
    while True:
        success, img = vid.read()
        frame, x1, x2, y1, y2 = detector.DrawFull(img, draw= True)
#        lmlist, go, x1, x2, y1, y2 = detector.findPosition(img)
#        cv2.rectangle(img=frame, pt1= (x1, y1),pt2= (x2, y2), color = (255, 0, 255), thickness=5)
       # cv2.putText(img, str(number), (10, 70), cv2.FONT_HERSHEY_COMPLEX, 3, (0, 255, 0), 4)
        cv2.imshow('video', frame)
        cv2.waitKey(1)

if __name__ == "__main__" :
    main()