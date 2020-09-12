import cv2
from math import acos, pi
import time
# img.shape = [rows, cols]


class Hand:
    __slots__ = 'Img', 'contours', 'hullIdx', 'hullPoints', 'defects', \
    'fingerTips', 'rect', 'contourIdx', 'frameNumber', 'mostFrequentFingerIndex', \
    'numberOfDefects', 'bRect', 'bRect_width', 'bRect_height', \
    'isHand', 'fontFace','colourScalar', 'previousNrFingerTips', 'checkForOneFinger', \
    'fingerNumbers', 'numbersToDisplay', 'numberColor', 'nrNofinger', 'fps', 't', 'count'
    # hand.bRect=(x,y,w,h)

    def __init__(self):
        self.frameNumber = 0
        self.nrNofinger = 0
        self.colourScalar=(0,200,0)
        self.bRect_width=0
        self.bRect_height=0
        self.fingerTips=[]
        self.isHand = True
        self.fps=0
        self.count=0
        self.t=time.clock()

    def initVectors(self):
        self.hullIdx = [[] for i in range(len(self.contours))]
        self.hullPoints = [[] for i in range(len(self.contours))]
        self.defects = [[] for i in range(len(self.contours))]
    
    def parseContours(self):
        self.bRect_height = self.bRect[3]
        self.bRect_width = self.bRect[2]


    def printGestureInfo(self, src):
        fontFace = cv2.FONT_HERSHEY_TRIPLEX
        fontColor = tuple(map(int,(245, 200, 200)))
        fontSize = 0.5
        linelength = 14

        xpos = int(src.shape[1] / 1.5)
        ypos = int(src.shape[0] / 1.8)

        if time.clock() - self.t >= 1.0:
            self.t=time.clock()
            self.fps = self.count
            self.count = 0

        txt = 'FPS: %d, Number of frame: %d' % (self.fps, self.frameNumber)
        cv2.putText(src, txt, (10, 20), fontFace, fontSize, fontColor)

        txt = 'Figure info:'
        cv2.putText(src, txt, (ypos, xpos), fontFace, fontSize, fontColor)
        xpos += linelength

        txt = 'Number of deftecs: %d' % self.numberOfDefects
        cv2.putText(src, txt, (ypos, xpos), fontFace, fontSize, fontColor)
        xpos += linelength

        txt = 'Bounding box height: %d, width: %d' % (self.bRect_height, self.bRect_width)
        cv2.putText(src, txt, (ypos, xpos), fontFace, fontSize, fontColor)
        xpos += linelength

        txt = 'Detected Hand: %d' % self.isHand
        cv2.putText(src, txt, (ypos, xpos), fontFace, fontSize, fontColor)

    def detectHands(self):
        self.parseContours()
        self.isHand = True
        h = self.bRect_height
        w = self.bRect_width
        if len(self.fingerTips) > 5:
            self.isHand = False
        elif h == 0 or w == 0:
            self.isHand = False
        elif h / w > 4 or w / h > 4:
            self.isHand = False
        elif self.bRect[0] < 20:
            self.isHand = False
        return self.isHand
    
    def calcPointDist(self,a,b):
        return ((a[0]-b[0])**2+(a[1]-b[1])**2) ** 0.5
    
    # remove fingertips that are too close to each other
    def removeInvalidFingers(self):
        foundFingers=[]
        for i in range(self.fingerTips.size()):
            for j in range(self.fingerTips.size()):
                if self.calcPointDist(self.fingerTips[i],self.fingerTips[j]) >= 10 or i == j:
                    foundFingers.append(fingerTinps[i])
                    break
        self.fingerTips=fountFingers

    def computeFingerNumber(self):
        self,fingerNUmbers.sort()
        fingerIndex=self.fingerNumbers[0]
        temp_freq = 1
        highestFreq = 1
        for i in range(self.fingerNumbers.size()):
            if self.fingerNumbers[i-1] != fingerNUmbers[i]:
                if temp_freq > highestFreq:
                    fingerIndex = self.fingerNumbers[i-1]
                    highestFreq =  temp_freq
                temp_freq = 0
            temp_freq += 1
        
        if temp_freq > highestFreq:
            fingerIndex = self.fingerNumbers[self.fingerNumbers.size()-1]
        
        self.mostFrequentFingerIndex = fingerIndex

    
    def printNumberToImage(self, img):
        x=10
        y=10
        offset=30
        fontSize=1.5
        fontFace= cv2.FONT_HERSHEY_PLAIN
        for i in range(self.numbers_to_Display.size()):
            cv2.rectangle(img = img.src, pt1=(x,y), pt2=(x+offset, y+offset), color=self.colorScalar, thickness=2)
            cv2.putText(img=img.src, text=str(self.numbersToDisplay[i]), org=(xPos + 7, yPos + offset - 3), fontFace=fontFace, fontScale=fontSize, color=self.colorscalar)
            x+=40
            if x > (img.src.shape[1] - img.src.shape[1]/3.2) :
                x=10
                y+=40
        
    def getFingerNumber(self, img):
        self.removeInvalidFingers()
        if self.bRect[2] > img.src.shape[0] / 2 and self.nrNoFinger > 12 and self.isHand:
            self.fingerNumbers.append(self.fingerTips.size())
            if self.frameNumber > 12:
                self.nrNoFinger = 0
                self.frameNumber = 0
                self.computeFingerNumber()
                self.numbersToDisplay.append(self.mostFrequentFingerIndex)
                self.fingerNumbers.clear()
            else:
                frameNumber+=1
        else:
            self.nrNoFinger+=1

    
    def getAngle(self, s,f,e):
        l1=self.calcPointDist(f,s)
        l2=self.calcPointDist(f,e)
        dot=(s[0]-f[0])*(e[0]-f[0]) + (s[1]-f[1])*(e[1]-f[1])
        angle=acos(dot / (l1*l2))
        angle = angle *180/ pi
        return angle
    
    def removeDefects(self, img):
        tolerance = self.bRect_height / 5
        angleTolerance = 95
        foundDefects=[]

        d=0

        if self.defects[self.contourIdx] is not None:
            while d != len(self.defects[self.contourIdx]):
                vec4 = self.defects[self.contourIdx][d][0]
                startIdx, endIdx, farIdx = vec4[0:3]
                pStart=self.contours[self.contourIdx][startIdx][0]
                pEnd = self.contours[self.contourIdx][endIdx][0]
                pFar = self.contours[self.contourIdx][farIdx][0]
                if self.calcPointDist(pStart, pFar) > tolerance \
                 and self.calcPointDist(pEnd, pFar) > tolerance  \
                 and self.getAngle(pStart, pFar, pEnd) < angleTolerance:
                    cond1=pEnd[1] > (self.bRect[1] + self.bRect[3] * 3 / 4)
                    cond2=pStart[1] > (self.bRect[1] + self.bRect[3] * 3 / 4)
                    if not cond1 and not cond2:
                        foundDefects.append(vec4)

                d+=1

        
        self.numberOfDefects = len(foundDefects)
        self.defects[self.contourIdx] = foundDefects
        self.removeRedundantEndPoints(foundDefects, img)

    def removeRedundantEndPoints(self, foundDefects, img):
        tolerance = self.bRect_width / 6

        for i in range(len(foundDefects)):
            for j in range(len(foundDefects)):
                startIdx, endIdx = foundDefects[i][0:2]
                pStart=self.contours[self.contourIdx][startIdx][0]
                pEnd = self.contours[self.contourIdx][endIdx][0]

                startIdx2, endIdx2 = foundDefects[j][0:2]
                pStart2=self.contours[self.contourIdx][startIdx2][0]
                pEnd2 = self.contours[self.contourIdx][endIdx2][0]

                if self.calcPointDist(pStart, pEnd2) < tolerance:
                    self.contours[self.contourIdx][startIdx] = pEnd2
                    break
                
                if self.calcPointDist(pEnd, pStart2) < tolerance:
                    self.contours[self.contourIdx][startIdx2] = pEnd

    def checkForOneFInger(self, img):
        yTolerance = self.bRect[3] / 6

        # point=(x, y) img.shape=(rows, cols)
        highestP = (0,img.src.shape[0])

        d = 0
        while d != len(self.contours[self.contourIdx]):
            v=self.contours[self.contourIdx][d][0]
            if v[1] < highestP[1]:
                highestP = v
            
            d+=1
        
        n=0
        d=0
        while d != len(self.hullPoints[self.contourIdx]):
            v = self.hullPoints[self.contourIdx][d][0]
            if v[1] < highestP[1] + yTolerance and v[1] != highestP[1] and v[0] != highestP[0]:
                n+=1
            d+=1
        
        if n==0:
            self.fingerTips.append(highestP)
    
    def drawFingerTips(self, img):
        for i in range(len(self.fingerTips)):
            p = self.fingerTips[i]
            cv2.putText(img.src, str(i), (p[0], p[1]-30), cv2.FONT_HERSHEY_PLAIN, 1.2, (200,0,0), 2)
            cv2.circle(img.src, tuple(p), 5, (100,255,100), 3)
    
    def getFingerTips(self, img):
        self.fingerTips.clear()
        i=0
        d=0
        
        while d != len(self.defects[self.contourIdx]):
            v = self.defects[self.contourIdx][d]
            startIdx, endIdx, farIdx = v[0:3]
            pStart=self.contours[self.contourIdx][startIdx][0]
            pEnd = self.contours[self.contourIdx][endIdx][0]
            pFar = self.contours[self.contourIdx][farIdx][0]

            if i==0:
                self.fingerTips.append(pStart)
                i+=1
            
            self.fingerTips.append(pEnd)
            d+=1
            i+=1

        if len(self.fingerTips) == 0:
            self.checkForOneFInger(img)

