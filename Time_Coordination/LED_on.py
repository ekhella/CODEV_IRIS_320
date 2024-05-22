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

# Sample data points for linear regression
x = time_regr
y = [point[1] for point in regr]  # Extract y values (res_offsets)

# Perform linear regression
coefficients = np.polyfit(x, y, 1)  # '1' represents the degree of the polynomial, linear in this case

# Coefficients
slope = coefficients[0]
intercept = coefficients[1]

print(f"Slope (Directional Coefficient): {slope}")
print(f"Intercept: {intercept}")


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
    
video_path = 'Data_confidential/video_vision_perif.mp4'
cap = cv2.VideoCapture(video_path)
R_values, G_values, B_values = [], [], []


if not cap.isOpened():
    print("Error opening video file")

frame_id=0
while True:
    ret, frame = cap.read()
    if not ret:
        break 

    led_zone = frame[h_led_s:h_led_e, w_led_s:w_led_e]
    new_size = np.shape(led_zone)[0]*np.shape(led_zone)[1] #New size is just the total number of pixels of the wanted zone
    led_zone_list = np.reshape(led_zone,(new_size,3)) #We have now the wanted zone, it's a list of pixels (a pixel is a list of 3 int)
    mean_blue = np.mean(led_zone_list[:,0])
    mean_green = np.mean(led_zone_list[:,1])
    mean_red = np.mean(led_zone_list[:,2])
    R_values.append(mean_red)
    G_values.append(mean_green)
    B_values.append(mean_blue)

    frame_id += 1

cap.release() 


# Plotting 
fig, axes = plt.subplots(3, 1, figsize=(10, 18))  # Three rows, one column

# Plot Red values
axes[0].plot(time_seconds, R_values, '-o', markersize=2, label='Red Values')
axes[0].set_title('Red Values Over Time')
axes[0].set_xlabel('Time (seconds)')
axes[0].set_ylabel('Red values (from 0 to 255)')
axes[0].grid(True)
axes[0].legend(loc='best')

# Plot Green values
axes[1].plot(time_seconds, G_values, '-o', markersize=2, label='Green Values')
axes[1].set_title('Green Values Over Time')
axes[1].set_xlabel('Time (seconds)')
axes[1].set_ylabel('Green values (from 0 to 255)')
axes[1].grid(True)
axes[1].legend(loc='best')

# Plot Blue values
axes[2].plot(time_seconds, B_values, '-o', markersize=2, label='Blue Values')
axes[2].set_title('Blue Values Over Time')
axes[2].set_xlabel('Time (seconds)')
axes[2].set_ylabel('Blue values (from 0 to 255)')
axes[2].grid(True)
axes[2].legend(loc='best')

# Adjust layout to prevent overlap
plt.tight_layout()
plt.show()