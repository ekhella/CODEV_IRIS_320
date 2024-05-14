from Modules import cv2 
Video_Path = 'Data_confidential/video_arriere.mp4'
cap = cv2.VideoCapture(Video_Path)
while True :
    frame_number = int(input("Which frame do you want to open ? "))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number-1)
    res, frame = cap.read()
    cv2.imshow('First Frame', frame)
    cv2.waitKey(0)