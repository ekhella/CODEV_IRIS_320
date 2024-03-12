from Modules import cv2

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  
        print(f"Position: (x={x}, y={y})") 


capture = cv2.VideoCapture('Data_confidential/video_arriere.mp4') 

if not capture.isOpened():
    print("Error: Could not open video.")
else:

    ret, frame = capture.read()
    if ret:
        cv2.namedWindow('First Frame')

        cv2.setMouseCallback('First Frame', mouse_callback)

        cv2.imshow('First Frame', frame)

        cv2.waitKey(0)

        cv2.destroyAllWindows()
    else:
        print("Error: Could not read the first frame.")
    capture.release()
