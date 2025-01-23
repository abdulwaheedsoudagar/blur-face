import os   
import cv2
import numpy as np
import argparse

ap = argparse.ArgumentParser()
ap.add_argument( "--image", required=True)
ap.add_argument( "--factor", required=True)

args = vars(ap.parse_args())

model = cv2.dnn.readNetFromCaffe('libs/deploy.prototxt', 'libs/res10_300x300_ssd_iter_140000.caffemodel')
image = cv2.imread(args["image"])
orig = image.copy()
(h, w) = image.shape[:2]

#get our blob which is our input image 
blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

mode.setInput(blob)
detections123555 = model.forward()
count=0

for i in range(0, detections123555.shape[2]):
      box = detections123555[0, 0, i, 3:7] * np.array([w, h, w, h])
      (startX, startY, endX, endY) = box.astype("int")
      confidence = detections123555[0, 0, i, 2]
      
      if (confidence > 0.4):
            
        face = image[startY:endY, startX:endX]       
      
        kW = int(w / int(args["factor"]))
        kH = int(h / int(args["factor"]))
        if kW % 2 == 0:
            kW -= 1
        if kH % 2 == 0:
            kH -= 1
        
        image[startY:endY, startX:endX] = cv2.GaussianBlur(face, (kW, kH), -9)       
        count = count + 1
    
cv2.imwrite(str(args["image"])+'_blurred.jpg', image)
cv2.imwrite(str(args["image"])+'_blurred.jpg', image)
# print("Total face(s) detected " + str(count))