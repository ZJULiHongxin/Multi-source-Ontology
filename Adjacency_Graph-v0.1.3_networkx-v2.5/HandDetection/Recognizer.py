import cv2
import sys
import myImage
import HandStruc
from roi import myROI
import numpy as np

import time
# Hand segmentation
# fontFace = cv2.FONT_HERSHEY_PLAIN


class handDetector:
    __slots__ = 'square_len', 'roi_num', 'avgColor', 'color_lower', 'color_upper',\
                'textColor', 'numberOfDefects', 'iSinceKFInit', 'roi', 'cvtMode', \
                'cvtORGMode','img','hand', 'out', 'sample_time'

    def __init__(self, cameraNo, sample_time=50):
        self.square_len=20
        self.sample_time=sample_time
        self.roi_num = 0
        self.avgColor=[]
        self.color_lower=[]
        self.color_upper=[]
        self.textColor=tuple(map(int,(0,200,0)))
        self.numberOfDefects=0
        self.iSinceKFInit=0
        self.roi=[]
        self.cvtMode = cv2.COLOR_BGR2HLS
        self.cvtORGMode = cv2.COLOR_HLS2BGR
        self.img = myImage.myImage(cameraNo)
        self.hand = HandStruc.Hand()
        self.out = cv2.VideoWriter(
            filename="./demo.avi",
            fourcc=cv2.VideoWriter_fourcc(*'XVID'),
            fps=20,
            frameSize=(640, 480),
            isColor=1)



# # Sppech Recording
# CHUNK = 1024
# FORMAT = pyaudio.paInt16
# CHANNELS = 2
# RATE = 16000
# RECORD_SECONDS = 5
# WAVE_OUTPUT_FILENAME = "test.wav"
# inputStream=0
# OutputStream=0
# p=0

    def getHandReady(self):
        """
        Sampling the color features of users hands,
        in order to adjust to the environment in which  users' hands are
        """
        _, self.img.src=self.img.cap.read()
        #cv2.flip(self.img.src, 1)

        col = self.img.src.shape[1]
        row = self.img.src.shape[0]
        s_len=self.square_len
        self.roi.append(myROI(self.img.src,(col // 3, row // 6),    (col // 3 + s_len, row // 6 + s_len)))
        self.roi.append(myROI(self.img.src,(col // 4, row // 2),    (col // 4 + s_len, row // 2 + s_len)))
        self.roi.append(myROI(self.img.src,(col // 3, row // 1.5),  (col // 3 + s_len, row // 1.5 + s_len)))
        self.roi.append(myROI(self.img.src,(col // 2, row // 2),    (col // 2 + s_len, row // 2 + s_len)))
        self.roi.append(myROI(self.img.src,(col // 2.5, row // 2.5),(col // 2.5 + s_len, row // 2.5 + s_len)))
        self.roi.append(myROI(self.img.src,(col // 2, row // 1.5),  (col // 2 + s_len, row // 1.5 + s_len)))
        self.roi.append(myROI(self.img.src,(col // 2.5, row // 1.8),(col // 2.5 + s_len, row // 1.8 + s_len)))

        self.roi_num=len(self.roi)
        self.avgColor=[[0,0,0] for i in range(self.roi_num)]
        self.color_lower=[[] for i in range(self.roi_num)]
        self.color_upper=[[] for i in range(self.roi_num)]

        # sampling hand color
        for i in range(self.sample_time):
            _, self.img.src=self.img.cap.read()
            for j in range(self.roi_num):
                self.roi[j].drawRect(self.img.src)

            fontFace = cv2.FONT_HERSHEY_PLAIN
            note='Sampling the color features of your hands \n please cover rectangles with your hand'
            cv2.putText(img=self.img.src, text=note, org=(round(col/3), round(row/10)),fontFace=fontFace, fontScale=1.2, color=(100, 250, 100))
            cv2.imshow("image", self.img.src)
            if cv2.waitKey(20) >=0:
                break

    def getAverageHandColor(self):
        sample_num=50
        for i in range(sample_num):
            _, self.img.src=self.img.cap.read()
            # The image is originally BGR, and now will be converted to HSL
            self.img.src = cv2.cvtColor(self.img.src, self.cvtMode)

            for j in range(self.roi_num):
                tl_row = self.roi[j].topleft[1]
                tl_col = self.roi[j].topleft[0]
                br_row = self.roi[j].bottomright[1]
                br_col = self.roi[j].bottomright[0]
                h_med=np.median(self.img.src[tl_row:br_row, tl_col:br_col, 0])
                s_med=np.median(self.img.src[tl_row:br_row, tl_col:br_col, 1])
                l_med=np.median(self.img.src[tl_row:br_row, tl_col:br_col, 2])
                self.avgColor[j][0] += h_med
                self.avgColor[j][1] += s_med
                self.avgColor[j][2] += l_med
                self.roi[j].drawRect(self.img.src)

            # HSL to BGR
            self.img.src = cv2.cvtColor(self.img.src, self.cvtORGMode)
            note='Calibrating average color of hand...'
            cv2.putText(img=self.img.src, text=note,
                        org=(round(self.img.src.shape[0]/2), round(self.img.src.shape[1]/10)),
                        fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1.2, color=(100, 250, 100))
            cv2.imshow("image", self.img.src)
            if cv2.waitKey(10) >=0:
                break
        for j in range(self.roi_num):
            self.avgColor[j][0]/=sample_num
            self.avgColor[j][1]/=sample_num
            self.avgColor[j][2] /= sample_num


    def normalizeColors(self):
        """ 
        Copy all boundries read from trackbars to all of the different boundries
        """
        
        
        for i in range(self.roi_num):
            for j in range(3):
                self.color_lower[i][j] = self.color_lower[0][j]
                self.color_upper[i][j] = self.color_upper[0][j]

        for i in range(self.roi_num):
            if (self.avgColor[i][0] - self.color_lower[i][0]) < 0:
                self.color_lower[i][0] = self.avgColor[i][0]
            if (self.avgColor[i][1] - self.color_lower[i][1]) < 0:
                self.color_lower[i][1] = self.avgColor[i][1]
            if (self.avgColor[i][2] - self.color_lower[i][2]) < 0:
                self.color_lower[i][2] = self.avgColor[i][2]

            if (self.avgColor[i][0] + self.color_upper[i][0]) > 255:
                self.color_upper[i][0] = 255 - self.avgColor[i][0]
            if (self.avgColor[i][1] + self.color_upper[i][1]) > 255:
                self.color_upper[i][1] = 255 - self.avgColor[i][1]
            if (self.avgColor[i][2] + self.color_upper[i][2]) > 255:
                self.color_upper[i][2] = 255 - self.avgColor[i][2]

    def produceBinary(self):
        """
        set pixels that are believed to be part of hand to 1, while others to zeros.
        In order to segment hands from original image in HSL space
        :param img: an instance of myImage class
        """
        self.img.bwList.clear() # Prevent memory leakage
        self.normalizeColors()
        for i in range(self.roi_num):
            lowerBound = (self.avgColor[i][0] - self.color_lower[i][0], self.avgColor[i][1] - self.color_lower[i][1], self.avgColor[i][2] - self.color_lower[i][2])
            upperBound = (self.avgColor[i][0] + self.color_upper[i][0], self.avgColor[i][1] + self.color_upper[i][1], self.avgColor[i][2] + self.color_upper[i][2])
            self.img.bwList.append(self.img.srcLR)
            self.img.bwList[i] = cv2.inRange(self.img.srcLR, lowerBound, upperBound)

        self.img.bw = self.img.bwList[0].copy()
        for i in range(self.roi_num):
            self.img.bw += self.img.bwList[i]

        self.img.bw = cv2.medianBlur(self.img.bw, 7)

    def findLargestContour(self, contours):
        """
        find out the largest and the second largest contour in property 'contours',
        because they stand for the two hands of human
        :param contours: 
        :return: 
        """
        largest_idx=-1
        size=0
        for i in range(len(contours)):
            if len(contours[i]) > size:
                size = len(contours[i])
                largest_idx = i

        secLargest_idx=-1
        size=0
        for i in range(len(contours)):
            if len(contours[i]) > size and len(contours[i]) != len(contours[largest_idx]) and len(contours[i]) > len(contours[largest_idx]) / 2:
                size = len(contours[i])
                secLargest_idx = i

        return largest_idx, secLargest_idx

    def extractContours(self):
        self.img.bw = cv2.pyrUp(self.img.bw)
        temp_bw = self.img.bw.copy()

        _, self.hand.contours, _ = cv2.findContours(temp_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        self.hand.initVectors()
        hands = self.findLargestContour(self.hand.contours)

        # Extract contours of left and right hands
        result=[]
        for i in range(2):
            cIdx = hands[i]
            self.hand.contourIdx = hands[i]
            if cIdx != -1:
                # Calculates the up-right bounding rectangle of the point set which represents hands
                # bRect stands for the rectangle enclosing hand
                x, y, w, h = cv2.boundingRect(self.hand.contours[cIdx])
                self.hand.bRect = (x, y, w, h)
                result.append((x, y, w, h))
                # Calculate and store the points of the found convex hull
                self.hand.hullPoints[cIdx] = cv2.convexHull(
                    points=self.hand.contours[cIdx],
                    clockwise=False,
                    returnPoints=True)
                # Calculate and store the indices of the points of the found convex hull
                self.hand.hullIdx[cIdx] = cv2.convexHull(
                    points=self.hand.contours[cIdx],
                    clockwise=False,
                    returnPoints=False)
                self.hand.hullPoints[cIdx]=cv2.approxPolyDP(self.hand.hullPoints[cIdx], 18, True)

                if len(self.hand.contours[cIdx]) > 3:
                    self.hand.defects[cIdx] = cv2.convexityDefects( \
                        self.hand.contours[cIdx], \
                        self.hand.hullIdx[cIdx])

                    self.hand.removeDefects(self.img)

                isHand = self.hand.detectHands()
                self.hand.printGestureInfo(self.img.src)

                if isHand:
                    self.hand.getFingerTips(self.img)
                    #self.hand.drawFingerTips(self.img)
                    self.drawHandContours()
        return result

    def showWindows(self):
        '''
        Show the HSL space at top right
        :param img: 
        :return: 
        '''
        self.img.bw=cv2.pyrDown(self.img.bw)
        self.img.bw=cv2.pyrDown(self.img.bw)

        channels=[]
        for i in range(3):
            channels.append(self.img.bw)
        merged = cv2.merge(channels)

        x1=int(3 * self.img.src.shape[1] / 4)
        y1=0
        x2=self.img.bw.shape[1] + x1
        y2=self.img.bw.shape[0] + y1
        self.img.src[y1:y2,x1:x2,:]=merged.copy()
        cv2.imshow("image", self.img.src)

    def drawHandContours(self):

        cIdx = self.hand.contourIdx
        cnt = self.hand.hullPoints[cIdx]
        cv2.drawContours(self.img.src, [cnt], 0, (0,200,0), 2, 8)
        cv2.rectangle(img=self.img.src, pt1=self.hand.bRect[0:2],
                      pt2=(self.hand.bRect[0]+self.hand.bRect[2], \
                           self.hand.bRect[1]+self.hand.bRect[3]),
                      color=(0,0,200),
                      thickness=1)
        # tl=self.hand.bRect[0:2]
        # br=(tl[0]+self.hand.bRect[2], tl[1]+self.hand.bRect[3])
        # cv2.rectangle(self.img.src, tl, br, (200,0,0))
        # d=0
        # channels=[]
        # for i in range(3):
        #     channels.append(self.img.bw)
        # merged=cv2.merge(channels)
        #
        # cnt = self.hand.hullPoints[cIdx]
        # cv2.drawContours(merged, cnt, 0, (0,0,250), 10, 8)
        #
        # while d != len(self.hand.defects[cIdx]):
        #     vec4 = self.hand.defects[cIdx][d]
        #     farIdx = vec4[2]
        #     pFar = self.hand.contours[cIdx][farIdx][0]
        #
        #     cv2.circle(merged, tuple(pFar), 9, (0,205,0), 5)
        #     d+=1
        # cv2.imwrite('./before_ede.jpg',merged)

    # callback functions of the track bar
    def getHmin(self,x):
        self.color_lower[0][0] = x  # cv2.getTrackbarPos("Min of H", "Control Panel")
    def getHmax(self,x):
        self.color_upper[0][0] = x  # cv2.getTrackbarPos("Max of H", "Control Panel")
    def getSmin(self,x):
        self.color_lower[0][1] = x  # cv2.getTrackbarPos("Min of S", "Control Panel")
    def getSmax(self,x):
        self.color_upper[0][1] = x  # cv2.getTrackbarPos("Max of S", "Control Panel")
    def getLmin(self,x):
        self.color_lower[0][2] = x  # cv2.getTrackbarPos("Min of L", "Control Panel")
    def getLmax(self,x):
        self.color_upper[0][2] = x  # cv2.getTrackbarPos("Max of L", "Control Panel")

    def initTrackbars(self):
        for i in range(self.roi_num):
            self.color_lower[i]=[71, 80, 18]
            self.color_upper[i]=[3, 255, 133]

        cv2.createTrackbar("Min of H", "Control Panel" , self.color_lower[0][0], 255, self.getHmin)
        cv2.createTrackbar("Max of H", "Control Panel" , self.color_upper[0][0], 255, self.getHmax)
        cv2.createTrackbar("Min of S", "Control Panel" , self.color_lower[0][1], 255, self.getSmin)
        cv2.createTrackbar("Max of S", "Control Panel" , self.color_upper[0][1], 255, self.getSmax)
        cv2.createTrackbar("Min of L", "Control Panel" , self.color_lower[0][2], 255, self.getLmin)
        cv2.createTrackbar("Max of L", "Control Panel" , self.color_upper[0][2], 255, self.getLmax)

    def initDetector(self):
        try:
            self.getHandReady()
            self.getAverageHandColor()
            cv2.destroyWindow('image')
            cv2.namedWindow('Control Panel', cv2.WINDOW_KEEPRATIO)
            self.initTrackbars()
        except AttributeError:
            print("Camera not found or disabled.")
            exit()

    def detectHand(self):

        # Calibrate the color of user's hands, in case of variatrion of surroundings

        # initAudio()

        # x = threading.Thread(target=speechRecording, args=())
        # x.start()
        self.hand.frameNumber+=1
        self.hand.count+=1

        _, self.img.src = self.img.cap.read()
        self.img.plainImg = self.img.src.copy()
        self.img.srcLR = cv2.pyrDown(self.img.src)
        self.img.srcLR = cv2.blur(self.img.srcLR, ksize=(3,3))
        self.img.srcLR = cv2.cvtColor(self.img.srcLR, self.cvtMode)
        self.produceBinary()
        self.img.srcLR = cv2.cvtColor(self.img.srcLR, self.cvtORGMode)
        result = self.extractContours()
        # #hand.getFingerNumbers(img)
        self.showWindows()
        return result


    


if __name__ == '__main__':

    hd = handDetector(0)
    hd.initDetector()
    while True:
        hd.detectHand()
        hd.out.write(hd.img.src)
        if cv2.waitKey(20) > 48 :
            break
    hd.out.release()
    cv2.destroyAllWindows()
