import cv2
import numpy as np

if __name__ == '__main__':
    img = cv2.imread(r'/home/sgm/jkk_ros/src/opencv_pkg/src/yun2.jpg')#600x600
    imgInfo = img.shape
    height = imgInfo[0]
    width = imgInfo[1]
    matShift = np.float32([[1,0,100],[0,1,100]])#2*3
    dst = cv2.warpAffine(img,matShift,(width,height))
    while True :
        cv2.imshow("frame",img)
        cv2.imshow('dst',dst)
        action = cv2.waitKey(10) & 0xFF
        if action == ord('q') or action == 113:
            break
    img.release()
    cv2.destroyAllWindows()