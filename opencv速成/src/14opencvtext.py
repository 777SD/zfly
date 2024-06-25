import cv2
import numpy as np

if __name__ == '__main__':
    img = cv2.imread(r'/home/sgm/jkk_ros/src/opencv_pkg/src/yun2.jpg')#600x600
    cv2.putText(img,'I am is jkk!',(50,50),cv2.FONT_HERSHEY_SIMPLEX,2,(200,0,200),2)#picture text bingXY typetext textsize color linewide
    while True:
        cv2.imshow("img",img)
        action = cv2.waitKey(10) & 0xFF
        if action == ord('q') or action == 113:
            break
    img.release()
    cv2.destroyAllWindows()