import cv2

cap = cv2.VideoCapture("rtsp://192.168.1.51:8554/cv_camera")


while True: 
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        filename = f"test.jpg"
        #filepath = os.path.join(SAVE_DIR, filename)

        cv2.imwrite(filename, frame)

        print("Saved locally:", filename)

    elif key == ord('q'):
        cap.release()

            
        cv2.destroyAllWindows()

        break

    
