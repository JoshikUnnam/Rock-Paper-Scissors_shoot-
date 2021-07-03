import random
import cv2
import HandModule as hm
detector = hm.HandGadgets()
def find(po):  # this function is used to generate a random move by the computer and compare it to our user
    # 0 = paper, 1 = rock, 2 = scissors
    choice = random.randint(0, 2)
    result = "Empty"
    no = 4
    if po == 4 or po == 5 :
        result = ("you lose")
        no = 0
        print(po)
    elif choice == po :
        result = ("  draw")
        no = 2
    else :
        if po == 0 :
            if choice == 2 :
                result = ("you lose ")
                no = 0
            if choice == 1 :
                result = ("you win")
                no = 1
        if po == 1:
            if choice == 0:
                result = ("you lose ")
                no = 0
            if choice == 2:
                result = ("you win")
                no = 1
        if po == 2:
            if choice == 1:
                result = ("you lose ")
                no = 0
            if choice == 0:
                result = ("you win")
                no = 1
    return result, choice, no

def findnumber(hand1, hand): # This function is used to find the status of the hand and returns a 5 element list with each element representing a finger
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
            status.append(1)
        if tx < tx1 and hand == "Left":
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
    if len(status) > 5:
        statusnew = []
        for i in range(0, 5):
            statusnew.append(status[i])
        status = statusnew
    return status
def pos(lmlist,hand ,frame, imgSize, imglist, draw = True) : # this functions detects if you have chosen rock paper or scissors
    po = 0
    if len(lmlist) != 0:
        position = findnumber(lmlist, hand)
        print(position)
        if position == [0, 1, 1, 0, 0]:
            po = 2
            if draw == True:
                frame[0:imgSize[0], 0:imgSize[1]] = imglist[2]
        elif position == [1, 1, 1, 1, 1]:
            po = 0
            if draw == True:
                frame[0:imgSize[0], 0:imgSize[1]] = imglist[0]
        elif position == [0, 0, 0, 0, 0]:
            po = 1
            if draw == True:
                frame[0:imgSize[0], 0:imgSize[1]] = imglist[1]
        elif position == [0, 1, 0, 0, 0]:
            po = 4
            if draw == True:
                cv2.putText(frame, "select", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, color=(0, 0, 0), thickness=7)
        else:
            po = 5
            if draw == True:
                cv2.putText(frame, "None", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, color=(0, 0, 0), thickness=7)
    else:
        po = 5
        if draw == True:
            cv2.putText(frame, "None", (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, color=(0, 0, 0), thickness=7)
    return po
