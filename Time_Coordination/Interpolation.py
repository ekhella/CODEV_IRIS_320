import math
from scipy.optimize import newton
import cv2
import numpy as np
import matplotlib.pyplot as plt
from LED_on_multiprocces import time_regr
from LED_on_multiprocces import regr
from LED_on_multiprocces import time_seconds_offset
from LED_on_multiprocces import offset
from LED_on_multiprocces import led_time_offset
from LED_on_multiprocces import led_status
import datetime
from math import *

def convert_to_hour_minute_second(seconds):
    """
    Converts a given time in seconds to a string in the format 
    hour:minute:second:decimal of the second.

    :param seconds: Time in seconds.
    :return: A string representing the time.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = seconds % 60
    whole_seconds = int(remaining_seconds)
    decimal_second = remaining_seconds - whole_seconds

    # Format the values to get the required format
    time_format = f"{hours:02}:{minutes:02}:{whole_seconds:02}.{int(decimal_second * 1000):03}"
    
    return time_format

def convert_to_seconds(time_str):
    """
    Converts a string representing a time in the format 
    hour:minute:second:decimal of the second to seconds.

    :param time_str: The string representing the time.
    :return: The total time in seconds.
    """
    try:
        hours, minutes, seconds = time_str.split(':')
        whole_seconds, decimal_second = seconds.split('.')
    except ValueError:
        raise ValueError("The time format must be hour:minute:second.decimal of the second")

    hours = int(hours)
    minutes = int(minutes)
    whole_seconds = int(whole_seconds)
    decimal_second = float("0." + decimal_second)

    total_seconds = (hours * 3600) + (minutes * 60) + whole_seconds + decimal_second
    return total_seconds

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

x = np.array(time_regr)
y = np.array([point[1] for point in regr])
coefficients = np.polyfit(x, y, 1)

slope = coefficients[0]
intercept = coefficients[1]

print(f"Slope (Directional Coefficient): {slope}")
print(f"Intercept: {intercept}")


def get_frame_and_timestamp(video_path, frame_number):
    # Open the video with OpenCV
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video opens correctly
    if not cap.isOpened():
        print(f"Error: Unable to open the video {video_path}")
        return None, None
    
    # Get the frame rate of the video
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    
    # Calculate the timestamp at which the frame appears
    timestamp = frame_number / fps
    
    # Read the specific frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    
    # Check if the frame is read correctly
    if not ret:
        print(f"Error: Unable to read frame number {frame_number}")
        return None, None
    
    # Release the resources
    cap.release()
    
    return frame, timestamp, fps

video_path = 'Data_confidential/video_vision_perif.mp4'
num1 = 500
num2 = 700

frame1 = get_frame_and_timestamp(video_path, num1)[0]
print('Cette frame correspond à la date '+
      convert_to_hour_minute_second(get_frame_and_timestamp(video_path, num1)[1]*0.25+convert_to_seconds('15:59:42.505')))
print(get_frame_and_timestamp(video_path, num1)[1])
if frame1 is not None:
    cv2.imshow('Frame', frame1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

frame2 = get_frame_and_timestamp(video_path, num2)[0]
print('Cette frame correspond à la date '+
      convert_to_hour_minute_second(get_frame_and_timestamp(video_path, num2)[1]*0.25+convert_to_seconds('15:59:42.505')))
print(get_frame_and_timestamp(video_path, num2)[1])
if frame2 is not None:
    cv2.imshow('Frame', frame2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def convert_video_time_to_led_time(Tbeginning, Twanted):
    Tbeginning_sec = convert_to_seconds(Tbeginning) 
    T_led = Twanted*slope 
    Twanted_according_led = Tbeginning_sec + T_led
    return convert_to_hour_minute_second(Twanted_according_led)

def convert_video_time_to_led_time_withoutbeginning(Twanted): 
    return  Twanted*slope 

print(convert_video_time_to_led_time('15:59:42.505', get_frame_and_timestamp(video_path, num1)[1]))
print(convert_video_time_to_led_time('15:59:42.505', get_frame_and_timestamp(video_path, num2)[1]))



def interpol(frame_num, video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Erreur lors de l'ouverture de la vidéo")
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        raise ValueError("Impossible d'obtenir le FPS de la vidéo")

    avg_frame_interval = 1 / fps
    T_frame_sec = frame_num/fps
    T_frame_according_led = convert_video_time_to_led_time('16:00:15.000',T_frame_sec)
    return T_frame_according_led,fps

time = interpol(1000,'Data_confidential/video_arriere.mp4')[0]
fps = interpol(1000,'Data_confidential/video_arriere.mp4')[1]
print(time)
print(fps)


cap = cv2.VideoCapture('Data_confidential/video_vision_perif.mp4')
if not cap.isOpened():
     raise ValueError("Erreur lors de l'ouverture de la vidéo")

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
duration = total_frames/fps
i=1
abs=[0]
time=[0]
while i/fps <duration/4:
    abs.append(i/fps)
    t=convert_video_time_to_led_time_withoutbeginning(abs[i])
    time.append(t)
    i+=1
    


# Check
plt.figure(figsize=(10, 6))
plt.plot(time_seconds_offset, led_time_offset, '-o', markersize=2, label='LED Time')
plt.plot(time_regr, [point[1] for point in regr], '-o', markersize=2, label="Linear Up regression", color="Red")
plt.step(abs, time, where= 'post', color='green', label='vod Time')
plt.title('Ministair')
plt.xlabel('Time_vodarrière (seconds)')
plt.ylabel('LED Time')
plt.grid(True)
plt.legend(loc="best")
plt.show()