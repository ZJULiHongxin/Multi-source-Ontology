import cv2

class myROI:
    __slots__ = 'topleft','bottomright','colorScalar','borderThickness','region'
    def __init__(self, src, tl=(0,0), br=(0,0)):
        self.topleft=tuple(map(int,tl))
        self.bottomright=tuple(map(int,br))
        self.colorScalar=(0,255,0)
        self.borderThickness=2
        self.region = src[round(tl[1]):round(br[1]), round(tl[0]):round(br[0]), :] # row range: tl.y ~ br.y; col range: tl.x ~ br.x

    def drawRect(self,src):
        cv2.rectangle(img=src, pt1=self.topleft, pt2=self.bottomright, color= self.colorScalar,
        thickness=self.borderThickness)


