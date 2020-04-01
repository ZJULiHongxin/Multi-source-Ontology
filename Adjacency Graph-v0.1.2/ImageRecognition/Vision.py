import cv2
import numpy as np
import scipy
import scipy.spatial
import pickle
import random
import os
import matplotlib.pyplot as plt

class ImageRecognizer:
    __slots__="data_path","training_data_path","training_data_feature_path",\
              "test_data_path","test_data_feature_path","class_names",\
              "data","names","matrix","color"
    def __init__(self,data_path):
        self.data_path=data_path
        self.training_data_path=os.path.join(data_path,"train")
        self.test_data_path=os.path.join(data_path,"test")
        self.training_data_feature_path=os.path.join(data_path,"training_features.feat")
        self.test_data_feature_path=os.path.join(data_path,"test_features.feat")
        self.names=[]
        self.matrix=[]
        self.data=[]
        self.class_names=[]

    def extract_features(self, img_path, vector_size=32):
        img = cv2.imread(img_path)

        if isinstance(img,np.ndarray)==False:
            return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        try:
            sift_extractor = cv2.xfeatures2d.SIFT_create()
            kps = sift_extractor.detect(gray)

            # Sort the response of all key points in decreasing order,
            # and select 0-31th vectors.
            kps = sorted(kps, key=lambda x: -x.response)[:vector_size]
            # Compute 32 descriptors, each of which is a 128-dimensioned vector.
            # kps is a list of 32 key points; dsc is list of 32 descriptors
            kps, dsc = sift_extractor.compute(gray, kps)

            # Flatten all descriptors and get a 4096-demensioned vector.
            dsc = dsc.flatten()
            # Ensure that all descriptors have the same size.
            needed_size = (vector_size * 128)

            if dsc.size < needed_size:
                dsc = np.concatenate([dsc, np.zeros(needed_size - dsc.size)])
        except cv2.error as e:
            print('Error: ', e)
            return None

        return dsc

    def batch_extract(self):
        self.class_names=os.listdir(self.training_data_path)
        result = {}
        try:
            for c in self.class_names:
                class_path=os.path.join(self.training_data_path,c)
                files = [os.path.join(class_path, p) for p in sorted(os.listdir(class_path))]
                for f in files:
                    print('Extracting features from image %s' % f)
                    name = c.lower()+'_'+f
                    dsc= self.extract_features(f)
                    if isinstance(dsc, np.ndarray):
                        result[name] = self.extract_features(f)
                    else:
                        print("Wrong format:",name)
                        input()

            # saving all our feature vectors in pickled file
            print('\n')
        except:
            pass



        with open(self.training_data_feature_path, 'wb') as f:
            pickle.dump(result, f)

    def init_matcher(self):
        with open(self.training_data_feature_path,'rb') as fp:
            self.data = pickle.load(fp)
        print(type(self.data),len(self.data))

        for k, v in self.data.items():
            self.names.append(k)
            self.matrix.append(v)
        self.matrix = np.array(self.matrix)
        self.names = np.array(self.names)

    def cos_cdist(self, vector):
        # Calculate the dot-product of two descriptor
        v = vector.reshape(1, -1)
        return scipy.spatial.distance.cdist(self.matrix, v, 'cosine').reshape(-1)

    def match(self, test_img_path, top_num=5):
        features = self.extract_features(test_img_path)
        img_distances = self.cos_cdist(features)
        # getting top 5 records
        # 获得前5个记录
        nearest_ids = np.argsort(img_distances)[:top_num].tolist()

        nearest_img_paths = self.names[nearest_ids].tolist()
        return nearest_img_paths, img_distances[nearest_ids].tolist()

    def test_accuracy(self):
        self.class_names = os.listdir(self.test_data_path)
        total_num=0
        for c in self.class_names:
            class_path=os.path.join(self.test_data_path,c)
            if os.path.exists(class_path)==False:
                continue

            files = [os.path.join(class_path, p) for p in sorted(os.listdir(class_path))]
            if len(files)==0:
                continue
            total_num+=len(files)
            correct_count=0
            for f in files:
                result,_=self.match(f)
                top1=result[0].split('_')
                pred_label=top1[0]

                if pred_label==c:
                    correct_count+=1

        print("""the total number of tested samples: {}, {} of which were matched correctly
    Accuracy:{:.2%}""".format(total_num,correct_count,correct_count/total_num))


if __name__ == "__main__":
    IR=ImageRecognizer('H:\\ImageNet\\fruit_and_vegetable\\practice')
    #IR.extract_features("H:\\ImageNet\\fruit_and_vegetable\\practice\\train\\banana_slices\\608.jpg")
    #IR.batch_extract()
    IR.init_matcher()
    r,l=IR.match('H:\\ImageNet\\fruit_and_vegetable\\practice\\test\\strawberry\\n07745940_530.JPEG')
    print(r,l)
    #IR.test_accuracy()