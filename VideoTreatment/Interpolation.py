import cv2
import numpy as np
import matplotlib.pyplot as plt
from LED_on_multiprocess import led_status
from math import *

class LEDVideoAnalysis:
    def __init__(self, video_path, led_status):
        self.video_path = video_path
        self.led_status = led_status
        self.slope = None
        self.intercept = None
        self.time_seconds = None
        self.time_seconds_offset = None
        self.led_time_offset = []
        self.regr = [[0, 0]]

        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError("Erreur lors de l'ouverture de la vidéo")
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    def convert_to_hour_minute_second(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        whole_seconds = int(remaining_seconds)
        decimal_second = remaining_seconds - whole_seconds
        return f"{hours:02}:{minutes:02}:{whole_seconds:02}.{int(decimal_second * 1000):03}"

    def convert_to_seconds(self, time_str):
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

    def calculate_offsets(self):
        indices = np.where(self.led_status == 1)[0]
        offset = indices[0]
        res_offset = 0
        for i in range(offset, len(self.led_status) - 1):
            self.led_time_offset.append(res_offset)
            if self.led_status[i + 1] - self.led_status[i] == 1:
                res_offset += 4
                self.regr.append([i - offset, res_offset])

    def calculate_time_seconds(self):
        self.time_seconds = [frame_id / self.fps for frame_id in range(len(self.led_status))]
        offset = np.where(self.led_status == 1)[0][0]
        self.time_seconds_offset = [t - self.time_seconds[offset] for t in self.time_seconds[offset:-1]]

    def perform_regression(self):
        time_regr = [self.time_seconds_offset[i] for i in [point[0] for point in self.regr]]
        x = np.array(time_regr)
        y = np.array([point[1] for point in self.regr])
        coefficients = np.polyfit(x, y, 1)
        self.slope = coefficients[0]
        self.intercept = coefficients[1]
        print(f"Slope (Directional Coefficient): {self.slope}")
        print(f"Intercept: {self.intercept}")

    def convert_video_time_to_led_time(self, Tbeginning, Twanted):
        Tbeginning_sec = self.convert_to_seconds(Tbeginning)
        T_led = Twanted * self.slope + self.intercept
        Twanted_according_led = Tbeginning_sec + T_led
        return self.convert_to_hour_minute_second(Twanted_according_led)

    def convert_video_time_to_led_time_withoutbeginning(self, Twanted):
        return Twanted * self.slope + self.intercept

    def plot_interpolation(self):
        duration = self.total_frames / self.fps
        abs = [i / self.fps for i in range(self.total_frames)]
        time = [self.convert_video_time_to_led_time_withoutbeginning(t) for t in abs]

        plt.figure(figsize=(10, 6))
        plt.plot(self.time_seconds_offset, self.led_time_offset, '-o', markersize=2, label='LED Time')
        time_regr = [self.time_seconds_offset[i] for i in [point[0] for point in self.regr]]
        plt.plot(time_regr, [point[1] for point in self.regr], '-o', markersize=2, label="Linear Up regression", color="Red")
        plt.step(abs, time, where='post', color='green', label='Calcul of convert_video_time_to_led_time for each frame')
        plt.title('Interpolation for each video frames')
        plt.xlabel('Time (seconds)')
        plt.ylabel('LED Time')
        plt.grid(True)
        plt.legend(loc="best")
        plt.show()

    def run_analysis(self):
        self.calculate_offsets()
        self.calculate_time_seconds()
        self.perform_regression()
        self.plot_interpolation()

# Example usage:
analysis = LEDVideoAnalysis('Data_confidential/video_vision_perif.mp4', led_status)
analysis.run_analysis()