import cv2
import numpy as np

if __name__ == '__main__':
    img = cv2.imread(r'/home/sgm/jkk_ros/src/opencv_pkg/src/yun2.jpg')#600x600
    print(img.shape)
    x, y = img.shape[0:2]
    img_test1 = cv2.resize(img,(int(y/2),int(x/2)))#shu chu chi cun she ding
    while True :
        cv2.imshow("frame",img)
        cv2.imshow('resize0',img_test1)
        action = cv2.waitKey(10) & 0xFF
        if action == ord('q') or action == 113:
            break
    img.release()
    cv2.destroyAllWindows()