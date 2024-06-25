import cv2
import numpy as np

if __name__ == '__main__':
    img = cv2.imread(r'/home/sgm/jkk_ros/src/opencv_pkg/src/yun2.jpg')#600x600
    points = np.array([[200,50],[40,200],[120,100],[90,110],[50,50]],np.int32)# xy coord
    polylines = cv2.polylines(img,[points],True,(255,0,255),5)#picture XY (True or False --> close?)  color linewide
    while True:
        cv2.imshow("polylines",polylines)
        action = cv2.waitKey(10) & 0xFF
        if action == ord('q') or action == 113:
            break
    img.release()
    cv2.destroyAllWindows()