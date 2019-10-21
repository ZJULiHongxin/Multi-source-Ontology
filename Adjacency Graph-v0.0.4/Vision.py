import cv2  # Open webcam to capture images and store them.

import keras
from keras.preprocessing import image
import numpy as np
from keras import backend as K
import keras.applications
from keras.applications import resnet50

K.clear_session()

model = keras.applications.resnet50.ResNet50(include_top=True, weights='imagenet', input_tensor=None, input_shape=None,
                                             pooling=None, classes=1000)