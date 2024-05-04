import cv2
from pyzbar import pyzbar
import numpy as np
import threading
import struct
import serial
import time
a='@'  #包头
b='rn' #包尾

text=0
data=None  #二维码的数据


order=0   #顺序排列 取第一次
order1=0   #放第一次
order2=0  #取第二次
order3=0  #放第二次


nember=1   #第一次取料
nember1=1  #第一次放料
nember2=1  #第二次取料
nember3=1  #第二次放料

promise='1'  #抓区允许标志位
promise=a+promise+b
put='2'     #圆环投放标志位
put=a+put+b
print('ok')


ser = serial.Serial("/dev/ttyAMA0",115200)
# 定义串口接收函数
def receive_data():
    while True:
        # 获得接收缓冲区字符
        date_read = ser.inWaiting()
        if date_read != 0:
            # 读取内容并回显
            date_read = ser.read(date_read)  #树莓派串口接收数据       从bytes类型转成str类型
            
            print(date_read)
            # 清空接收缓冲区
            ser.flushInput()
            # 必要的软件延时
            time.sleep(0.1)
            
receive_thread=threading.Thread(target=receive_data,name="fun_thread1",daemon=True)
receive_thread.start()



# 打开摄像头
cap = cv2.VideoCapture(0)


# 设置摄像头的分辨率和帧率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 30)

# 获取默认分辨率
default_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
default_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
center_x=default_width/2
center_y=default_height/2   #获得图像中心点



# 检查摄像头是否已成功打开
if cap.isOpened():
    while True:
        ret, frame = cap.read()     

        if text==0:    #情况0扫描二维码
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded = pyzbar.decode(gray)

            for obj in decoded:
                data = obj.data.decode("utf-8")

            if data!=None:
                data1=a+data+b             #将发送的数据加包头包尾
                print("二维码内容:", data1)
                print("完成了二维码扫描")
                ser.write(data1.encode())          #自己本身解析二维码内容 date[order]
                text=1


                

        
        if text==1: #形况1识别三小料顺序
            # 清理因为相同命名而可能出现的误差
            x_red, y_red, w_red, h_red=0,0,0,0
            x_blue, y_blue, w_blue, h_blue=0,0,0,0
            x_green, y_green, w_green, h_green=0,0,0,0



            # 定义红色范围（在HSV颜色空间中）
            lower_red = np.array([0, 45, 45])
            upper_red = np.array([10, 255, 255])
            lower_red1 = np.array([170, 45, 45])
            upper_red1 = np.array([180, 255, 255])

            # 定义蓝色范围（在HSV颜色空间中）
            lower_blue = np.array([100, 45, 45])
            upper_blue = np.array([130, 255, 255])
            # 定义绿色范围（在HSV颜色空间中）
            lower_green = np.array([45, 45, 45])
            upper_green = np.array([100, 255, 255])

            max_area_red = 0
            max_rect_red = None
            max_area_blue = 0
            max_rect_blue = None
            max_area_green = 0
            max_rect_green = None
            area_red=0
            area_blue=0
            area_green=0
            red=0
            blue=0
            green=0

    
            #进行滤波选择
            # 中值滤波
            filtered_image = cv2.medianBlur(frame, 5)
            # 均值滤波
            # filtered_image = cv2.blur(balanced_image, (7, 7))
            # 进行高斯滤波
            # filtered_image = cv2.GaussianBlur(balanced_image, (5, 5), 0)

            # 将图像转换到HSV颜色空间
            hsv = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2HSV)
            # 根据红色范围，提取红色区域
            red_mask1 = cv2.inRange(hsv, lower_red, upper_red)
            red_mask2 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_red = cv2.bitwise_or(red_mask1, red_mask2)

            # mask_red = cv2.inRange(hsv, lower_red,upper_red)
            # 根据蓝色范围，提取蓝色区域
            mask_blue = cv2.inRange(hsv,lower_blue ,upper_blue)
            # 根据绿色范围，提取绿色区域
            mask_green = cv2.inRange(hsv,lower_green ,upper_green)

            # 创建结构元素
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
            # 进行闭运算
            for i in range(1):
                closed_image_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
                closed_image_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)
                closed_image_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)

            for i in range(5):
                closed_image_red = cv2.morphologyEx(closed_image_red, cv2.MORPH_CLOSE, kernel)
                closed_image_blue = cv2.morphologyEx(closed_image_blue, cv2.MORPH_CLOSE, kernel)
                closed_image_green = cv2.morphologyEx(closed_image_green, cv2.MORPH_CLOSE, kernel)                

            # 红色 
            contours, _ = cv2.findContours( closed_image_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # 检查是否找到了轮廓
            if len(contours) > 0:
                red=1
                # 找到最大矩形框
                for contour in contours:
                    x_red, y_red, w_red, h_red = cv2.boundingRect(contour)
                    area_red = w_red * h_red
                    if  area_red > max_area_red:
                        max_area_red = area_red
                        max_rect_red = (x_red, y_red, w_red, h_red)

                # 在原始图像上绘制最大矩形框
                x_red, y_red, w_red, h_red = max_rect_red  #得到左上角的坐标  待修改
                cv2.rectangle(frame, (x_red, y_red), (x_red+w_red, y_red+h_red), (255,0 , 0), 3)
                
          

            # 蓝色 
            contours, _ = cv2.findContours( closed_image_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                blue=1
                for contour in contours:
                    x_blue, y_blue, w_blue, h_blue = cv2.boundingRect(contour)
                    area_blue = w_blue * h_blue
                    if  area_blue > max_area_blue:
                        max_area_blue = area_blue
                        max_rect_blue = (x_blue, y_blue, w_blue, h_blue)

                # 在原始图像上绘制最大矩形框
                x_blue, y_blue, w_blue, h_blue = max_rect_blue
                # cv2.rectangle(frame, (x_blue, y_blue), (x_blue+w_blue, y_blue+h_blue), (0, 255, 0), 3)
        

            # 绿色 
            contours, _ = cv2.findContours( closed_image_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                green=1
                for contour in contours:
                    x_green, y_green, w_green, h_green = cv2.boundingRect(contour)
                    area_green= w_green * h_green
                    if  area_green > max_area_green:
                        max_area_green = area_green
                        max_rect_green = (x_green, y_green, w_green, h_green)

                # 在原始图像上绘制最大矩形框
                x_green, y_green, w_green, h_green = max_rect_green
                #cv2.rectangle(frame, (x_green, y_green), (x_green+w_green, y_green+h_green), (0, 255, 0), 3)


    
            if red or blue or green:  #红1 绿2 蓝3                   所以参数待修改
                if data[order]=='1' and nember==1 :
                    if max_area_red>=5000:
                        if  (2*x_red+w_red)/2 > center_x*0.8 and (2*x_red+w_red)/2 < center_x*1.2 :
                            if  (2*y_red+h_red)/2 > center_y*0.8 and (2*y_red+h_red)/2  < center_y*1.2 :    
                                ser.write(promise.encode()) 
                                order+=1
                                nember+=1

                                print('1')
                                
                if data[order]=='2' and nember==1 :
                    if max_area_green>=5000:
                        if  (2*x_green+w_green)/2 > center_x*0.8 and (2*x_green+w_green)/2 < center_x*1.5 :
                            if  (2*y_green+h_green)/2 > center_y*0.8 and (2*y_green+h_green)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order+=1   
                                nember+=1  

                if data[order]=='3' and nember==1 :
                    if max_area_blue>=5000:
                        if  (2*x_blue+w_blue)/2 > center_x*0.8 and (2*x_blue+w_blue)/2 < center_x*1.2 :
                            if  (2*y_blue+h_blue)/2 > center_y*0.8 and (2*y_blue+h_blue)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order+=1
                                nember+=1                                


                #抓第二个                   #红1 绿2 蓝3 
                if data[order]=='1' and nember==2 :
                    if max_area_red>=5000:
                        if  (2*x_red+w_red)/2 > center_x*0.8 and (2*x_red+w_red)/2 < center_x*1.2 :
                            if  (2*y_red+h_red)/2 > center_y*0.8 and (2*y_red+h_red)/2  < center_y*1.2 :    
                                ser.write(promise.encode()) 
                                order+=1
                                nember+=1

                if data[order]=='2' and nember==2 :
                    if max_area_green>=5000:
                        if  (2*x_green+w_green)/2 > center_x*0.8 and (2*x_green+w_green)/2 < center_x*1.2 :
                            if  (2*y_green+h_green)/2 > center_y*0.8 and (2*y_green+h_green)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order+=1   
                                nember+=1
                                print('2')  


                if data[order]=='3' and nember==2 :
                    if max_area_blue>=5000:
                        if  (2*x_blue+w_blue)/2 > center_x*0.8 and (2*x_blue+w_blue)/2 < center_x*1.2 :
                            if  (2*y_blue+h_blue)/2 > center_y*0.8 and (2*y_blue+h_blue)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order+=1
                                nember+=1    




                #抓第三个
                if data[order]=='1' and nember==3 :
                    if max_area_red>=5000:
                        if  (2*x_red+w_red)/2 > center_x*0.8 and (2*x_red+w_red)/2 < center_x*1.2 :
                            if  (2*y_red+h_red)/2 > center_y*0.8 and (2*y_red+h_red)/2  < center_y*1.2 :    
                                ser.write(promise.encode()) 
                                order+=1
                                nember+=1
                                text=2  #更新text到下一个任务

                if data[order]=='2' and nember==3 :
                    if max_area_green>=5000:
                        if  (2*x_green+w_green)/2 > center_x*0.8 and (2*x_green+w_green)/2 < center_x*1.5 :
                            if  (2*y_green+h_green)/2 > center_y*0.8 and (2*y_green+h_green)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order+=1   
                                nember+=1  
                                text=2


                if data[order]=='3' and nember==3 :
                    if max_area_blue>=5000:
                        if  (2*x_blue+w_blue)/2 > center_x*0.8 and (2*x_blue+w_blue)/2 < center_x*1.2 :
                            if  (2*y_blue+h_blue)/2 > center_y*0.8 and (2*y_blue+h_blue)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order+=1
                                nember+=1    
                                text=2
                                print('3')


                  
        



        if text==2: #扫描圆环
            # 清理因为相同命名而可能出现的误差
            x_red, y_red, w_red, h_red=0,0,0,0
            x_blue, y_blue, w_blue, h_blue=0,0,0,0
            x_green, y_green, w_green, h_green=0,0,0,0


            # 定义红色范围（在HSV颜色空间中）
            lower_red = np.array([0, 45, 45])
            upper_red = np.array([10, 255, 255])
            lower_red1 = np.array([170, 45, 45])
            upper_red1 = np.array([180, 255, 255])

            # 定义蓝色范围（在HSV颜色空间中）
            lower_blue = np.array([100, 45, 45])
            upper_blue = np.array([130, 255, 255])
            # 定义绿色范围（在HSV颜色空间中）
            lower_green = np.array([45, 45, 45])
            upper_green = np.array([90, 255, 255])


            # 将图像转换到HSV颜色空间
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # 根据红色范围，提取红色区域
            # mask_red = cv2.inRange(hsv, lower_red,upper_red)
            
            red_mask1 = cv2.inRange(hsv, lower_red, upper_red)
            red_mask2 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_red = cv2.bitwise_or(red_mask1, red_mask2)
            
            # 根据蓝色范围，提取蓝色区域
            mask_blue = cv2.inRange(hsv,lower_blue ,upper_blue)
            # 根据绿色范围，提取绿色区域
            mask_green = cv2.inRange(hsv,lower_green ,upper_green)
            # 创建结构元素
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
            # 进行闭运算
            for i in range(1):
                closed_image_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
                closed_image_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)
                closed_image_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
            for i in range(3):
                closed_image_red = cv2.morphologyEx(closed_image_red, cv2.MORPH_CLOSE, kernel)
                closed_image_blue = cv2.morphologyEx(closed_image_blue, cv2.MORPH_CLOSE, kernel)  
                closed_image_green = cv2.morphologyEx(closed_image_green, cv2.MORPH_CLOSE, kernel)  
            #边缘检测
            edges_red = cv2.Canny(closed_image_red, 50, 100)    
            edges_blue= cv2.Canny(closed_image_blue, 50, 100) 
            edges_green = cv2.Canny(closed_image_green, 50, 100) 


            # 进行红圆检测
            circles_red = cv2.HoughCircles(edges_red, cv2.HOUGH_GRADIENT, 1, 50, param1=150, param2=55, minRadius=0, maxRadius=0)
            if circles_red is not None:
                circles_red = np.round(circles_red[0, :]).astype("int")
                max_radius_red = 0
                max_circle_red = None
                for (x_red, y_red, r_red) in circles_red:
                    if r_red > max_radius_red:
                        max_radius_red = r_red
                        max_circle_red = (x_red, y_red, r_red)
                (x_red, y_red, r_red) = max_circle_red
                # cv2.circle(frame, (x_red, y_red), r_red, (0, 255, 0), 4)
                # cv2.circle(frame, (x_red, y_red), 3, (0, 255, 0), -1)

            # 进行蓝圆检测
            circles_blue = cv2.HoughCircles(edges_blue, cv2.HOUGH_GRADIENT, 1, 50, param1=150, param2=55, minRadius=0, maxRadius=0)
            if circles_blue is not None:
                circles_blue = np.round(circles_blue[0, :]).astype("int")
                max_radius_blue = 0
                max_circle_blue = None
                for (x_blue, y_blue, r_blue) in circles_blue:
                    if r_blue > max_radius_blue:
                        max_radius_blue = r_blue
                        max_circle_blue = (x_blue, y_blue, r_blue)
                (x_blue, y_blue, r_blue) = max_circle_blue
                #cv2.circle(frame, (x_blue, y_blue), r_blue, (0, 255, 0), 4)
                #cv2.circle(frame, (x_blue, y_blue), 3, (0, 255, 0), -1)


            # 进行绿圆检测
            circles_green = cv2.HoughCircles(edges_green, cv2.HOUGH_GRADIENT, 1, 50, param1=150, param2=55, minRadius=0, maxRadius=0)
            if circles_green is not None:
                circles_green = np.round(circles_green[0, :]).astype("int")
                max_radius_green = 0
                max_circle_green = None
                for (x_green, y_green, r_green) in circles_green:
                    if r_green > max_radius_green:
                        max_radius_green = r_green
                        max_circle_green = (x_green, y_green, r_green)
                (x_green, y_green, r_green) = max_circle_green
                #cv2.circle(frame, (x_green, y_green), r_green, (0, 255, 0), 4)
                #cv2.circle(frame, (x_green, y_green), 3, (0, 255, 0), -1)

            #第一次放
            if data[order1]=='1' and nember1==1 :  #红1 绿2 蓝3   
                if  x_red > center_x*0.8 and x_red < center_x*1.2 : 
                    if y_red> center_y*0.8 and y_red <center_y*1.2:   
                        ser.write(put.encode()) 
                        order1+=1
                        nember1+=1
                        print('放1')           

            if data[order1]=='2' and nember1==1 :  #红1 绿2 蓝3   
                if  x_green > center_y*0.8 and x_green < center_y*1.2 :
                    if y_green > center_y*0.8 and y_green < center_y*1.2:   
                        ser.write(put.encode()) 
                        order1+=1
                        nember1+=1   

            if data[order1]=='3' and nember1==1 :  #红1 绿2 蓝3   
                if  x_blue > center_x*0.8 and x_blue < center_x*1.2 :
                    if  y_blue > center_y*0.8 and y_blue < center_y*1.2 :        
                        ser.write(put.encode()) 
                        order1+=1
                        nember1+=1         


            #第二次放
            if data[order1]=='1' and nember1==2 :  
                if  x_red > center_x*0.8 and x_red < center_x*1.2 : 
                    if y_red> center_y*0.8 and y_red <center_y*1.2:   
                        ser.write(put.encode()) 
                        order1+=1
                        nember1+=1

            if data[order1]=='2' and nember1==2 :  
                if  x_green > center_x*0.8 and x_green < center_x*1.2 :
                    if y_green > center_y*0.8 and y_green < center_y*1.2:   
                        ser.write(put.encode()) 
                        order1+=1
                        nember1+=1   
                        print('放2')                       

            if data[order1]=='3' and nember1==2 :  
                if  x_blue > center_x*0.8 and x_blue < center_x*1.2 :
                    if  y_blue > center_y*0.8 and y_blue < center_y*1.2 :        
                        ser.write(put.encode()) 
                        order1+=1
                        nember1+=1                        

            #第三次放
            if data[order1]=='1' and nember1==3 :  
                if  x_red > center_x*0.8 and x_red < center_x*1.2 : 
                    if y_red> center_y*0.8 and y_red <center_y*1.2:   
                        ser.write(put.encode()) 
                        order1+=1
                        nember1+=1
                        text=3                #更新text到下一个任务       

            if data[order1]=='2' and nember1==3 :  
                if  x_green > center_x*0.8 and x_green < center_x*1.2 :
                    if y_green > center_y*0.8 and y_green < center_y*1.2:   
                        ser.write(put.encode()) 
                        order1+=1
                        nember1+=1   
                        text=3                     

            if data[order1]=='3' and nember1==3 :  
                if  x_blue > center_x*0.8 and x_blue < center_x*1.2 :
                    if  y_blue > center_y*0.8 and y_blue < center_y*1.2 :        
                        ser.write(put.encode()) 
                        order1+=1
                        nember1+=1   
                        text=3 
                        print('放3')





        if text==3:   #第二次抓物料   按照从原料区运算的顺序来抓
            # 清理因为相同命名而可能出现的误差
            x_red, y_red, w_red, h_red=0,0,0,0
            x_blue, y_blue, w_blue, h_blue=0,0,0,0
            x_green, y_green, w_green, h_green=0,0,0,0

            # 定义红色范围（在HSV颜色空间中）
            lower_red = np.array([0, 45, 45])
            upper_red = np.array([10, 255, 255])
            lower_red1 = np.array([170, 45, 45])
            upper_red1 = np.array([180, 255, 255])

            # 定义蓝色范围（在HSV颜色空间中）
            lower_blue = np.array([100, 45, 45])
            upper_blue = np.array([130, 255, 255])
            # 定义绿色范围（在HSV颜色空间中）
            lower_green = np.array([45, 45, 45])
            upper_green = np.array([90, 255, 255])

            max_area_red = 0
            max_rect_red = None
            max_area_blue = 0
            max_rect_blue = None
            max_area_green = 0
            max_rect_green = None
            area_red=0
            area_blue=0
            area_green=0
            red=0
            blue=0
            green=0

    
            #进行滤波选择
            # 中值滤波
            filtered_image = cv2.medianBlur(frame, 5)
            # 均值滤波
            # filtered_image = cv2.blur(balanced_image, (7, 7))
            # 进行高斯滤波
            # filtered_image = cv2.GaussianBlur(balanced_image, (5, 5), 0)

            # 将图像转换到HSV颜色空间
            hsv = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2HSV)
            # 根据红色范围，提取红色区域
            
            # mask_red = cv2.inRange(hsv, lower_red,upper_red)
            red_mask1 = cv2.inRange(hsv, lower_red, upper_red)
            red_mask2 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_red = cv2.bitwise_or(red_mask1, red_mask2)

            # 根据蓝色范围，提取蓝色区域
            mask_blue = cv2.inRange(hsv,lower_blue ,upper_blue)
            # 根据绿色范围，提取绿色区域
            mask_green = cv2.inRange(hsv,lower_green ,upper_green)

            # 创建结构元素
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
            # 进行闭运算
            for i in range(1):
                closed_image_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
                closed_image_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)
                closed_image_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)

            for i in range(5):
                closed_image_red = cv2.morphologyEx(closed_image_red, cv2.MORPH_CLOSE, kernel)
                closed_image_blue = cv2.morphologyEx(closed_image_blue, cv2.MORPH_CLOSE, kernel)
                closed_image_green = cv2.morphologyEx(closed_image_green, cv2.MORPH_CLOSE, kernel)                

            # 红色 
            contours, _ = cv2.findContours( closed_image_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # 检查是否找到了轮廓
            if len(contours) > 0:
                red=1
                # 找到最大矩形框
                for contour in contours:
                    x_red, y_red, w_red, h_red = cv2.boundingRect(contour)
                    area_red = w_red * h_red
                    if  area_red > max_area_red:
                        max_area_red = area_red
                        max_rect_red = (x_red, y_red, w_red, h_red)

                # 在原始图像上绘制最大矩形框
                x_red, y_red, w_red, h_red = max_rect_red
                # cv2.rectangle(frame, (x_red, y_red), (x_red+w_red, y_red+h_red), (0, 255, 0), 3)
                
          

            # 蓝色 
            contours, _ = cv2.findContours( closed_image_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                blue=1
                for contour in contours:
                    x_blue, y_blue, w_blue, h_blue = cv2.boundingRect(contour)
                    area_blue = w_blue * h_blue
                    if  area_blue > max_area_blue:
                        max_area_blue = area_blue
                        max_rect_blue = (x_blue, y_blue, w_blue, h_blue)

                # 在原始图像上绘制最大矩形框
                x_blue, y_blue, w_blue, h_blue = max_rect_blue
                # cv2.rectangle(frame, (x_blue, y_blue), (x_blue+w_blue, y_blue+h_blue), (0, 255, 0), 3)
        

            # 绿色 
            contours, _ = cv2.findContours( closed_image_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                green=1
                for contour in contours:
                    x_green, y_green, w_green, h_green = cv2.boundingRect(contour)
                    area_green= w_green * h_green
                    if  area_green > max_area_green:
                        max_area_green = area_green
                        max_rect_green = (x_green, y_green, w_green, h_green)

                # 在原始图像上绘制最大矩形框
                x_green, y_green, w_green, h_green = max_rect_green
                # cv2.rectangle(frame, (x_green, y_green), (x_green+w_green, y_green+h_green), (0, 255, 0), 3)

    
            if red or blue or green:  #红1 绿2 蓝3                   所以参数待修改
                
                if data[order2]=='1' and nember2==1 :
                    if max_area_red>=5000:
                        if  (2*x_red+w_red)/2 > center_x*0.8 and (2*x_red+w_red)/2 < center_x*1.2 :
                            if  (2*y_red+h_red)/2 > center_y*0.8 and (2*y_red+h_red)/2  < center_y*1.2 :    
                                ser.write(promise.encode()) 
                                order2+=1
                                nember2+=1
                                print('抓1')

                if data[order2]=='2' and nember2==1 :
                    if max_area_green>=5000:
                        if  (2*x_green+w_green)/2 > center_x*0.8 and (2*x_green+w_green)/2 < center_x*1.2 :
                            if  (2*y_green+h_green)/2 > center_y*0.8 and (y_green+h_green)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order2+=1   
                                nember2+=1  


                if data[order2]=='3' and nember2==1 :
                    if max_area_blue>=5000:
                        if  (2*x_blue+w_blue)/2 > center_x*0.8 and (2*x_blue+w_blue)/2 < center_x*1.2 :
                            if  (2*y_blue+h_blue)/2 > center_y*0.8 and (2*y_blue+h_blue)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order2+=1
                                nember2+=1


                #抓第二个
                if data[order2]=='1' and nember2==2 :
                    if max_area_red>=5000:
                        if  (2*x_red+w_red)/2 > center_x*0.8 and (2*x_red+w_red)/2 < center_x*1.2 :
                            if  (2*y_red+h_red)/2 > center_y*0.8 and (2*y_red+h_red)/2  < center_y*1.2 :    
                                ser.write(promise.encode()) 
                                order2+=1
                                nember2+=1


                if data[order2]=='2' and nember2==2 :
                    if max_area_green>=5000:
                        if  (2*x_green+w_green)/2 > center_x*0.8 and (2*x_green+w_green)/2 < center_x*1.2 :
                            if  (2*y_green+h_green)/2 > center_y*0.8 and (y_green+h_green)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order2+=1   
                                nember2+=1  
                                print('抓2')

                if data[order2]=='3' and nember2==2 :
                    if max_area_blue>=5000:
                        if  (2*x_blue+w_blue)/2 > center_x*0.8 and (2*x_blue+w_blue)/2 < center_x*1.2 :
                            if  (2*y_blue+h_blue)/2 > center_y*0.8 and (2*y_blue+h_blue)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order2+=1
                                nember2+=1


                #抓第三个
                if data[order2]=='1' and nember2==3 :
                    if max_area_red>=5000:
                        if  (2*x_red+w_red)/2 > center_x*0.8 and (2*x_red+w_red)/2 < center_x*1.2 :
                            if  (2*y_red+h_red)/2 > center_y*0.8 and (2*y_red+h_red)/2  < center_y*1.2 :    
                                ser.write(promise.encode()) 
                                order2+=1
                                nember2+=1
                                text=4  #更新text到下一个任务


                if data[order2]=='2' and nember2==3 :
                    if max_area_green>=5000:
                        if  (2*x_green+w_green)/2 > center_x*0.8 and (2*x_green+w_green)/2 < center_x*1.2 :
                            if  (2*y_green+h_green)/2 > center_y*0.8 and (y_green+h_green)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order2+=1   
                                nember2+=1  
                                text=4

                if data[order2]=='3' and nember2==3 :
                    if max_area_blue>=5000:
                        if  (2*x_blue+w_blue)/2 > center_x*0.8 and (2*x_blue+w_blue)/2 < center_x*1.2 :
                            if  (2*y_blue+h_blue)/2 > center_y*0.8 and (2*y_blue+h_blue)/2 < center_y*1.2 :  
                                ser.write(promise.encode()) 
                                order2+=1
                                nember2+=1
                                text=4    
                                print('抓3')




        if text==4:  #第二次寻找圆环
            # 清理因为相同命名而可能出现的误差
            x_red, y_red, w_red, h_red=0,0,0,0
            x_blue, y_blue, w_blue, h_blue=0,0,0,0
            x_green, y_green, w_green, h_green=0,0,0,0

            # 定义红色范围（在HSV颜色空间中）
            lower_red = np.array([0, 45, 45])
            upper_red = np.array([10, 255, 255])
            lower_red1 = np.array([170, 45, 45])
            upper_red1 = np.array([180, 255, 255])

            # 定义蓝色范围（在HSV颜色空间中）
            lower_blue = np.array([100, 45, 45])
            upper_blue = np.array([130, 255, 255])
            # 定义绿色范围（在HSV颜色空间中）
            lower_green = np.array([45, 45, 45])
            upper_green = np.array([90, 255, 255])


            # 将图像转换到HSV颜色空间
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            # 根据红色范围，提取红色区域
            # mask_red = cv2.inRange(hsv, lower_red,upper_red)
            red_mask1 = cv2.inRange(hsv, lower_red, upper_red)
            red_mask2 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_red = cv2.bitwise_or(red_mask1, red_mask2)
            # 根据蓝色范围，提取蓝色区域
            mask_blue = cv2.inRange(hsv,lower_blue ,upper_blue)
            # 根据绿色范围，提取绿色区域
            mask_green = cv2.inRange(hsv,lower_green ,upper_green)
            # 创建结构元素
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
            # 进行闭运算
            for i in range(1):
                closed_image_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
                closed_image_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)
                closed_image_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
            for i in range(5):
                closed_image_red = cv2.morphologyEx(closed_image_red, cv2.MORPH_CLOSE, kernel)
                closed_image_blue = cv2.morphologyEx(closed_image_blue, cv2.MORPH_CLOSE, kernel)  
                closed_image_green = cv2.morphologyEx(closed_image_green, cv2.MORPH_CLOSE, kernel)  
            #边缘检测
            edges_red = cv2.Canny(closed_image_red, 50, 100)    
            edges_blue= cv2.Canny(closed_image_blue, 50, 100) 
            edges_green = cv2.Canny(closed_image_green, 50, 100) 


            # 进行红圆检测
            circles_red = cv2.HoughCircles(edges_red, cv2.HOUGH_GRADIENT, 1, 50, param1=150, param2=55, minRadius=0, maxRadius=0)
            if circles_red is not None:
                circles_red = np.round(circles_red[0, :]).astype("int")
                max_radius_red = 0
                max_circle_red = None
                for (x_red, y_red, r_red) in circles_red:
                    if r_red > max_radius_red:
                        max_radius_red = r_red
                        max_circle_red = (x_red, y_red, r_red)
                (x_red, y_red, r_red) = max_circle_red
                # cv2.circle(frame, (x_red, y_red), r_red, (0, 255, 0), 4)
                # cv2.circle(frame, (x_red, y_red), 3, (0, 255, 0), -1)

            # 进行蓝圆检测
            circles_blue = cv2.HoughCircles(edges_blue, cv2.HOUGH_GRADIENT, 1, 50, param1=150, param2=55, minRadius=0, maxRadius=0)
            if circles_blue is not None:
                circles_blue = np.round(circles_blue[0, :]).astype("int")
                max_radius_blue = 0
                max_circle_blue = None
                for (x_blue, y_blue, r_blue) in circles_blue:
                    if r_blue > max_radius_blue:
                        max_radius_blue = r_blue
                        max_circle_blue = (x_blue, y_blue, r_blue)
                (x_blue, y_blue, r_blue) = max_circle_blue
                #cv2.circle(frame, (x_blue, y_blue), r_blue, (0, 255, 0), 4)
                #cv2.circle(frame, (x_blue, y_blue), 3, (0, 255, 0), -1)


            # 进行绿圆检测
            circles_green = cv2.HoughCircles(edges_green, cv2.HOUGH_GRADIENT, 1, 50, param1=150, param2=55, minRadius=0, maxRadius=0)
            if circles_green is not None:
                circles_green = np.round(circles_green[0, :]).astype("int")
                max_radius_green = 0
                max_circle_green = None
                for (x_green, y_green, r_green) in circles_green:
                    if r_green > max_radius_green:
                        max_radius_green = r_green
                        max_circle_green = (x_green, y_green, r_green)
                (x_green, y_green, r_green) = max_circle_green
                #cv2.circle(frame, (x_green, y_green), r_green, (0, 255, 0), 4)
                #cv2.circle(frame, (x_green, y_green), 3, (0, 255, 0), -1)

            #第一次放
            if data[order3]=='1' and nember3==1 :  #红1 绿2 蓝3   
                if  x_red > center_x*0.8 and x_red < center_x*1.2 :
                    if y_red > center_y*0.8 and y_red <center_y*1.2:    
                        ser.write(put.encode()) 
                        order3+=1
                        nember3+=1
                        print('放1')           

            if data[order3]=='2' and nember3==1 :  #红1 绿2 蓝3   
                if  x_green > center_x*0.8 and x_green < center_x*1.2 :
                    if y_green > center_y*0.8 and y_green <center_y*1.2 :    
                        ser.write(put.encode()) 
                        order3+=1
                        nember3+=1        

            if data[order3]=='3' and nember3==1 :  #红1 绿2 蓝3   
                if  x_blue > center_x*0.8 and x_blue < center_x*1.2 :
                    if y_blue > center_y*0.8 and y_blue <center_y*1.2:    
                        ser.write(put.encode()) 
                        order3+=1
                        nember3+=1    

            #第二次放
            if data[order3]=='1' and nember3==2 :  
                if  x_red > center_x*0.8 and x_red < center_x*1.2 :
                    if y_red > center_y*0.8 and y_red <center_y*1.2:    
                        ser.write(put.encode()) 
                        order3+=1
                        nember3+=1

            if data[order3]=='2' and nember3==2 :  
                if  x_green > center_x*0.8 and x_green < center_x*1.2 :
                    if y_green > center_y*0.8 and y_green <center_y*1.2 :    
                        ser.write(put.encode()) 
                        order3+=1
                        nember3+=1       
                        print('放2')              

            if data[order3]=='3' and nember3==2 :  
                if  x_blue > center_x*0.8 and x_blue < center_x*1.2 :
                    if y_blue > center_y*0.8 and y_blue <center_y*1.2:    
                        ser.write(put.encode()) 
                        order3+=1
                        nember3+=1                        

            #第三次放
            if data[order3]=='1' and nember3==3 :  
                if  x_red > center_x*0.8 and x_red < center_x*1.2 :
                    if y_red > center_y*0.8 and y_red <center_y*1.2:    
                        ser.write(put.encode()) 
                        order3+=1
                        nember3+=1
                        text=5                #更新text到下一个任务       

            if data[order3]=='2' and nember3==3 :  
                if  x_green > center_x*0.8 and x_green < center_x*1.2 :
                    if y_green > center_y*0.8 and y_green <center_y*1.2 :    
                        ser.write(put.encode()) 
                        order3+=1
                        nember3+=1 
                        text=5                     

            if data[order3]=='3' and nember3==3 :  
                if  x_blue > center_x*0.8 and x_blue < center_x*1.2 :
                    if y_blue > center_y*0.8 and y_blue <center_y*1.2:    
                        ser.write(put.encode()) 
                        order3+=1
                        nember3+=1     
                        text=5        
                        print('放3')




        if text==5 :
            text=6
            print('已经完成第一阶段')    


        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()  






                                
                                       


 
else:
    print("摄像头无法打开")
