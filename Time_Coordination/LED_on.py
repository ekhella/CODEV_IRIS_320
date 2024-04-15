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
hsv_thresholds = ((0, 90, 90), (15, 255, 255)), ((160, 110, 110), (180, 255, 255))  # Red HSV thresholds


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

offset=1
while led_status[offset]-led_status[offset-1]!=1:
     offset+=1

led_time_offset=[]
res_offset=0
regr=[[0,0]]
for i in range(offset, len(led_status)-1):
    led_time_offset.append(res_offset)
    if led_status[i+1]-led_status[i]==1:
            res_offset+=4
            regr.append([i-offset,res_offset])

led_time=[]
res=0
for i in range(len(led_status)-1):
    led_time.append(res)
    if led_status[i+1]-led_status[i]==1:
            res+=4          

time_seconds = [frame_id / fps for frame_id in range(len(led_status))] # Convert frame IDs to time in seconds
time_seconds_offset = [t - time_seconds[offset] for t in time_seconds[offset:-1]]  # Setting the new origin of the time
time_regr = [time_seconds_offset[i] for i in[point[0] for point in regr]] # Taking the points of interest in the linear regression


# Plotting
plt.figure(figsize=(10, 6))
plt.plot(time_seconds, led_status, '-o', markersize=2, label='LED Status')
plt.title('LED Status Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('LED Status (ON=1, OFF=0)')
plt.grid(True)
plt.legend(loc = "best")
plt.show()

# Plotting
plt.figure(figsize=(10, 6))
plt.plot( time_seconds_offset, led_time_offset, '-o', markersize=2, label='LED Time')
plt.plot(time_regr, [point[1] for point in regr], '-o', markersize=2, label = "Linear Up regression", color="Red" )
plt.title('LED Time Over Time after Offset')
plt.xlabel('Time (seconds)')
plt.ylabel('LED Time')
plt.grid(True)
plt.legend(loc = "best")
plt.show()

# Plotting
plt.figure(figsize=(10, 6))
plt.plot( time_seconds[:-1], led_time, '-o', markersize=2, label='LED Time')
plt.title('LED Time Over Time before Offset')
plt.xlabel('Time (seconds)')
plt.ylabel('LED Time')
plt.grid(True)
plt.legend(loc = "best")
plt.show()


def get_color_redLED(): # Get the colors of all the pixels of one frame of the red LED

    LED_zone = frame[h_led_s:h_led_e, w_led_s:w_led_e]
    one_frame_LED_colors = [] #Initialize a list to stock colors of pixels

    for row in range(LED_zone.shape[0]):
        for col in range(LED_zone.shape[1]):
            blue, green, red = frame[row, col]

            one_frame_LED_colors.append((blue, green, red))
    return one_frame_LED_colors

def mean_color_redLED(colors): # Get the mean color of one frame of the red LED

    mean_R, mean_G, mean_B = 0,0,0

    for color in colors:
        mean_R += color[0]
        mean_G += color[1]
        mean_B += color[2]
    
    nb_pixels = len(colors)
    mean_R /= nb_pixels
    mean_G /= nb_pixels
    mean_B /= nb_pixels

    return (mean_R, mean_B, mean_G)

def get_RGB():
    video_path = 'Data_confidential/video_vision_perif.mp4'
    cap = cv2.VideoCapture(video_path)
    R_values, G_values, B_values = [], [], []

    if not cap.isOpened():
        print("Error opening video file")
    else:
        frame_id = 0
        fps = cap.get(cv2.CAP_PROP_FPS) 
        while True:
            ret, frame = cap.read()
            if not ret:
                break 
        
            R, G, B = mean_color_redLED(get_color_redLED())
            R_values.append(R)
            G_values.append(G)
            B_values.append(B)

            frame_id += 1

        cap.release()
    return R_values, G_values, B_values

R_values, G_values, B_values = get_RGB
time_seconds_bis = [frame_id / fps for frame_id in range(len(get_RGB()))]

# Plotting 

plt.figure(figsize=(10, 6))
plt.plot(time_seconds_bis,R_values,'-o', markersize=2, label='R_values')
plt.title('R values Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('R values (from 0 to 255)')
plt.grid(True)
plt.legend(loc = "best")
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(time_seconds_bis,G_values, '-o', markersize=2, label='G_values')
plt.title('G values Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('G values (from 0 to 255)')
plt.grid(True)
plt.legend(loc = "best")
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(time_seconds_bis,B_values, '-o', markersize=2, label='B_values')
plt.title('B values Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('B values (from 0 to 255)')
plt.grid(True)
plt.legend(loc = "best")
plt.show()