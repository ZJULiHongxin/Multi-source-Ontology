import cv2

class myImage:
    """ 
    @ Members: 
    """

    __slots__='srcLR','src','bw','bwList','cap','cameraSrc','plainImg'
    def __init__(self, cameraNo=0):
        self.cameraSrc=cameraNo
        try:
            self.cap=cv2.VideoCapture(cameraNo)
        except:
            print('Camera opened failure!')
        self.bwList=[]
        self.src=None
        self.srcLR=None
    
