import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from concurrent.futures import ThreadPoolExecutor
from segmentation_settings import radius, center
from segmentation_settings import w_led_s, w_led_e, h_led_s, h_led_e

def is_led_on(frame, hsv_thresholds):
    roi = frame[h_led_s:h_led_e, w_led_s:w_led_e]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_thresholds[0], hsv_thresholds[1])
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    return cv2.countNonZero(mask) > 0

# Constants
video_path = 'Data_confidential/video_vision_perif.mp4'
hsv_thresholds = [(0, 90, 90), (15, 255, 255), (160, 110, 110), (180, 255, 255)]
frame_interval = 1

# Start time measurement for video loading
start_load_time = time.time()
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error opening video file")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
h, w = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
end_load_time = time.time()
load_time = end_load_time - start_load_time
print(f"Video loading time: {load_time:.2f} seconds")

# Start time measurement for mask computation
start_mask_time = time.time()
Y, X = np.ogrid[:h, :w]
r_squared = (X - center[0]) ** 2 + (Y - center[1]) ** 2
mask_circle = r_squared <= radius ** 2
end_mask_time = time.time()
mask_time = end_mask_time - start_mask_time
print(f"Mask computation time: {mask_time:.2f} seconds")

# Start time measurement for data arrays creation
start_array_time = time.time()
num_frames_to_process = total_frames // frame_interval
mean_colors = np.zeros((num_frames_to_process, 3), dtype=np.float64)
led_status = np.zeros(num_frames_to_process, dtype=np.uint8)
end_array_time = time.time()
array_time = end_array_time - start_array_time
print(f"Data arrays creation time: {array_time:.2f} seconds")

# Start time measurement for main processing
start_main_time = time.time()

def process_frame(frame_info):
    frame_id, frame = frame_info
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    led_on = is_led_on(frame_hsv, hsv_thresholds)
    led_status[frame_id] = 1 if led_on else 0
    led_zone = frame[mask_circle]
    if len(led_zone) > 0:
        mean_colors[frame_id] = np.mean(led_zone, axis=0)

# Using ThreadPoolExecutor to process frames in parallel
with ThreadPoolExecutor() as executor:
    frame_id = 0
    processed_frames = 0
    while cap.isOpened() and processed_frames < num_frames_to_process:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_id % frame_interval == 0:
            executor.submit(process_frame, (processed_frames, frame))
            processed_frames += 1
        frame_id += 1

end_main_time = time.time()
main_time = end_main_time - start_main_time
print(f"Main processing time: {main_time:.2f} seconds")

cap.release()

# Convert frame IDs to time in seconds
time_seconds = np.arange(num_frames_to_process) * frame_interval / fps

# Plotting
fig, axes = plt.subplots(3, 1, figsize=(10, 18))  # Three rows, one column

# Plot color values
labels = ['Blue', 'Green', 'Red']
for i, color_channel in enumerate(labels):
    axes[i].plot(time_seconds, mean_colors[:, i], '-o', markersize=2, label=f'{color_channel} Values')
    axes[i].set_title(f'{color_channel} Values Over Time')
    axes[i].set_xlabel('Time (seconds)')
    axes[i].set_ylabel(f'{color_channel} values (from 0 to 255)')
    axes[i].grid(True)
    axes[i].legend(loc='best')

# Adjust layout to prevent overlap
plt.tight_layout()
plt.show()

indices = np.where(led_status == 1)[0]
offset = indices[0]

led_time_offset = []
res_offset = 0
regr = [[0, 0]]
for i in range(offset, len(led_status) - 1):
    led_time_offset.append(res_offset)
    if led_status[i + 1] - led_status[i] == 1:
        res_offset += 4
        regr.append([i - offset, res_offset])

led_time = []
res = 0
for i in range(len(led_status) - 1):
    led_time.append(res)
    if led_status[i + 1] - led_status[i] == 1:
        res += 4

time_seconds = [frame_id / fps for frame_id in range(len(led_status))]
time_seconds_offset = [t - time_seconds[offset] for t in time_seconds[offset:-1]]
time_regr = [time_seconds_offset[i] for i in [point[0] for point in regr]]

plt.figure(figsize=(10, 6))
plt.plot(time_seconds_offset, led_time_offset, '-o', markersize=2, label='LED Time')
plt.plot(time_regr, [point[1] for point in regr], '-o', markersize=2, label="Linear Up regression", color="Red")
plt.title('LED Time Over Time after Offset')
plt.xlabel('Time (seconds)')
plt.ylabel('LED Time')
plt.grid(True)
plt.legend(loc="best")
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(time_seconds[:-1], led_time, '-o', markersize=2, label='LED Time')
plt.title('LED Time Over Time before Offset')
plt.xlabel('Time (seconds)')
plt.ylabel('LED Time')
plt.grid(True)
plt.legend(loc="best")

total_execution_time = load_time + mask_time + array_time + main_time
print(f"Total execution time (excluding plotting): {total_execution_time:.2f} seconds")
video_duration = total_frames / fps
execution_percentage = (total_execution_time / video_duration) * 100
print(f"Execution time as percentage of video duration: {execution_percentage:.2f}%")