from __future__ import print_function
import cv2  # Open webcam to capture images and store them.

import numpy as np
import argparse
import matplotlib.pyplot as plt
import pickle


def bgr_rgb(img):
    (r, g, b) = cv2.split(img)
    return cv2.merge([b, g, r])

def surf_detect(img1, img2, detector='surf'):
    if detector.startswith('si'):
        print
        "sift detector......"
        sift = cv2.xfeatures2d.SURF_create()
    else:
        print
        "surf detector......"
        sift = cv2.xfeatures2d.SURF_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # # BFMatcher with default params
    # bf = cv2.BFMatcher()
    # matches = bf.knnMatch(des1, des2, k=2)

    # Apply ratio test
    good = [[m] for m, n in matches if m.distance < 0.6 * n.distance]

    # cv2.drawMatchesKnn expects list of lists as matches.
    img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags=2)

    return [bgr_rgb(img3),len(good)]

def saveKpAndDes(imgpath,dir):
    dot = imgpath[1:-1].index('.')
    kppath = dir + '/' + imgpath[0:dot] + '.kp'
    despath = dir + '/' + imgpath[0:dot] + '.des'
    print(kppath,despath)
    img = cv2.imread(imgpath)

    detector = cv2.xfeatures2d.SURF_create()
    kp, des = detector.detectAndCompute(img, None)

    # new_k = []
    # for i in range(len(kp)):
    #     temp = {'pt': kp[i].pt, 'size': kp[i].size, 'angle': kp[i].angle, 'octave': kp[i].octave,
    #             'class_id': kp[i].class_id, 'response':kp[i].response}  # 把这些信息写入到字典中
    #     new_k.append(temp)
    #
    # with open(kppath,'wb') as f:
    #     pickle.dump(new_k,f)
    # with open(despath,'wb') as f:
    #     pickle.dump(des,f)

import os
import re
dir='./testImg'
filelist=os.listdir(dir)

for i in range(len(filelist)):
    saveKpAndDes(dir+'/'+filelist[i],dir)

# for i in range(len(filelist)-1):
#     img2=cv2.imread(dir+'/'+filelist[i+1],0)
#     print(filelist[i])
#     img3,good=surf_detect(img1,img2)
#     cv2.imshow("result",img3)
#     print("The number of good matching: %d" % good)
#     cv2.waitKey(0)



