import cv2
import numpy as np
import scipy
import scipy.spatial
import pickle
import random
import os
import matplotlib.pyplot as plt

class ImageRecognizer:
    __slots__="KBpath","feature_file_path","data","names","matrix","color","vector_size"
    def __init__(self,KBpath,title):
        self.KBpath=KBpath
        self.feature_file_path=os.path.join(KBpath,title,title+".fts")
        self.names=[]
        self.matrix=[]
        self.data=dict()
        self.vector_size=32

        if os.path.exists(self.feature_file_path):
            with open(self.feature_file_path,'rb') as fp:
                self.data = pickle.load(fp)
            for k, v in self.data.items():
                self.names.append(k)
                self.matrix.append(v)

    def extract_features(self, img):
        if isinstance(img,np.ndarray)==False:
            return None
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
        sift_extractor = cv2.xfeatures2d.SIFT_create()
        kps = sift_extractor.detect(gray)

        # Sort the response of all key points in decreasing order,
        # and select 0-31th vectors.
        kps = sorted(kps, key=lambda x: -x.response)[:self.vector_size]
        # Compute 32 descriptors, each of which is a 128-dimensioned vector.
        # kps is a list of 32 key points; dsc is list of 32 descriptors
        kps, dsc = sift_extractor.compute(gray, kps)

        # Flatten all descriptors and get a 4096-demensioned vector.
        dsc = dsc.flatten()
        # Ensure that all descriptors have the same size.
        needed_size = (self.vector_size * 128)

        if dsc.size < needed_size:
            dsc = np.concatenate([dsc, np.zeros(needed_size - dsc.size)])

        return dsc

    def append_feature(self,dsc,img_path):
        self.data[img_path] = dsc

    def save_feature_file(self):
        with open(self.feature_file_path, 'wb') as fp:
            pickle.dump(self.data,fp)


    def __cos_cdist(self, vector):
        # Calculate the dot-product of two descriptor
        v = vector.reshape(1, -1)
        return scipy.spatial.distance.cdist(self.matrix, v, 'cosine').reshape(-1)

    def match(self, test_img_path, top_num=5):
        self.matrix = np.array(self.matrix)
        self.names = np.array(self.names)

        features = self.extract_features(test_img_path)
        img_distances = self.cos_cdist(features)
        # getting top 5 records
        # 获得前5个记录
        nearest_ids = np.argsort(img_distances)[:top_num].tolist()

        nearest_img_paths = self.names[nearest_ids].tolist()
        return nearest_img_paths, img_distances[nearest_ids].tolist()

