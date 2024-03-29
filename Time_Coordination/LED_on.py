import cv2
import numpy as np
import matplotlib.pyplot as plt
from segmentation_settings import w_led_s, w_led_e, h_led_s, h_led_e

def is_led_on(frame, hsv_thresholds):
    roi = frame[h_led_s:h_led_e, w_led_s:w_led_e] # Region of Interest (HOI)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)  # Convert ROI to Hue Saturation Value(HSV) color space
    mask = cv2.inRange(hsv, hsv_thresholds[0], hsv_thresholds[1])  # Apply HSV threshold
    # Cleaning
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Check if there are any white pixels in the mask (indicating the presence of the LED)
    return cv2.countNonZero(mask) > 0

# HSV thresholds for red LED
hsv_thresholds = ((0, 74, 74), (15, 255, 255)), ((160, 79, 79), (180, 255, 255))  # Red HSV thresholds


video_path = 'Data_confidential/video_vision_perif.mp4'
cap = cv2.VideoCapture(video_path)

led_status = []  # List to keep track of LED status over time

if not cap.isOpened():
    print("Error opening video file")
else:
    frame_id = 0
    fps = cap.get(cv2.CAP_PROP_FPS) 
    while True:
        ret, frame = cap.read()
        if not ret:
            break 

        # Check if the LED is on for this frame and append the result to the list
        led_on = any(is_led_on(frame, threshold) for threshold in hsv_thresholds)
        led_status.append(1 if led_on else 0)

        frame_id += 1

    cap.release()

# Convert frame IDs to time in seconds
time_seconds = [frame_id / fps for frame_id in range(len(led_status))]

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(time_seconds, led_status, '-o', markersize=2, label='LED Status')
plt.title('LED Status Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('LED Status (ON=1, OFF=0)')
plt.grid(True)
plt.legend(loc = "best")
plt.show()
