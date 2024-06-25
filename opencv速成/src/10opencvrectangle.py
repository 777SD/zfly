import cv2
import numpy as np

if __name__ == '__main__':
    img = cv2.imread(r'/home/sgm/jkk_ros/src/opencv_pkg/src/yun2.jpg')#600x600
    rect = cv2.rectangle(img,(200,200),(400,400),(255,0,255),10)#picture bingXY endXY colour linewide
    while True:
        cv2.imshow("rect",rect)
        action = cv2.waitKey(10) & 0xFF
        if action == ord('q') or action == 113:
            break
    img.release()
    cv2.destroyAllWindows()