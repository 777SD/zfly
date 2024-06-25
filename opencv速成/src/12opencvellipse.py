import cv2
import numpy as np

if __name__ == '__main__':
    img = cv2.imread(r'/home/sgm/jkk_ros/src/opencv_pkg/src/yun2.jpg')#600x600
    ellipse = cv2.ellipse(img,(300,300),(50,80),0,0,360,(255,0,255),5)#picture XY (longR,shortR) angle bingangle endangle color linewide
    while True:
        cv2.imshow("ellipse",ellipse)
        action = cv2.waitKey(10) & 0xFF
        if action == ord('q') or action == 113:
            break
    img.release()
    cv2.destroyAllWindows()