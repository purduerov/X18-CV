from otsu import RollingAverage, find_rects, max_area, order_points
from ratio import calculate_wh_ratio
import cv2
import math

ratio = RollingAverage(60)
prev_x = RollingAverage(60)
prev_y = RollingAverage(60)

# obj_height = 8.5 * 2.54
obj_height = 36

cap = cv2.VideoCapture("data/camera_roll/video1.avi")
# cap = cv2.VideoCapture(1)

while cap.isOpened():
# if True:
    # ret, frame = [True, cv2.imread("data/struct.jpg")]
    ret, frame = cap.read()
    
    if ret:
        image, rects = find_rects(frame)
        
        height, width, channels = image.shape;
        
        rect = max_area(rects)
        # print("\n\n")
        
        if len(rect) != 0:
        # for rect in rects:
            cv2.polylines(image, pts=[rect], isClosed=True, color=(0, 255, 0), thickness=6)
            points = [
                rect[0][0],
                rect[1][0],
                rect[2][0],
                rect[3][0],
            ]
            points = order_points(points)
            print(points)
            prev_x.add(points[0][0])
            prev_y.add(points[0][1])
            
            dist_from_prev = math.sqrt((points[0][0] - prev_x.get_average())**2 + (points[0][1] - prev_y.get_average())**2)
            
            # if dist_from_prev < min(height, width) / 4:
            if True:
                ratio.add(calculate_wh_ratio.get_wh_ratio(
                    points[0],
                    points[1],
                    points[2],
                    points[3],
                    width,
                    height
                ))
                # ratio = (calculate_wh_ratio.get_wh_ratio(
                #     points[0],
                #     points[1],
                #     points[2],
                #     points[3],
                #     width,
                #     height
                # ))
                ratio_avg = ratio.get_average()
                calculated_width = obj_height / ratio_avg
                
                cv2.putText(image, f'ratio: {round(ratio_avg, 3)}\nwidth: {round(calculated_width, 3)}\nerror: {round((abs(55 - calculated_width)), 3)}', tuple(points[2]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3, cv2.LINE_AA)
                # cv2.putText(image, f'width: {round(calculated_width, 3)}', (points[2][0], points[2][0] + 4), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_AA)
                # cv2.putText(image, f'error: {round((abs(11.5 * 2.54 - calculated_width)), 3)}', (points[2][0], points[2][0] + 4), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_AA)
        
        cv2.imshow("res", image)
        cv2.waitKey()
    # if cv2.waitKey(1) & 0xFF == ord('q'): 
    #     break

# cap.release()
cv2.destroyAllWindows()