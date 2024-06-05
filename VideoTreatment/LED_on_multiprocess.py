import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from concurrent.futures import ThreadPoolExecutor
from Settings import Settings  
class VideoAnalyzer:
    def __init__(self, video_path):
        self.settings = Settings()
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError("Error opening video file")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.h, self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_interval = 1
        self.hsv_thresholds = [(0, 90, 90), (15, 255, 255), (160, 110, 110), (180, 255, 255)]
        self.start_time = None

    def is_led_on(self, frame):
        roi = frame[self.settings.segmentation.led_bounds[2]:self.settings.segmentation.led_bounds[3], self.settings.segmentation.led_bounds[0]:self.settings.segmentation.led_bounds[1]]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.hsv_thresholds[0], self.hsv_thresholds[1])
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        return cv2.countNonZero(mask) > 0
    
    def stairs_with_red_value(self):
        threshold_stairs = 150 #empirical value
        new_status_led = []

        for mean_color_red in [triplet[2] for triplet in mean_colors]: # 2 because we are only interested in the mean value of the red component
            if mean_color_red < threshold_stairs:
                new_status_led.append(0)
            else:
                new_status_led.append(1)
        return new_status_led

    def process_frame(self, frame_info):
        frame_id, frame = frame_info
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        led_on = self.is_led_on(frame_hsv)
        led_zone = frame[self.mask_circle]
        if len(led_zone) > 0:
            return frame_id, 1 if led_on else 0, np.mean(led_zone, axis=0)
        return frame_id, 0, np.zeros(3)

    def generate_mask(self):
        Y, X = np.ogrid[:self.h, :self.w]
        r_squared = (X - self.settings.segmentation.center[0]) ** 2 + (Y - self.settings.segmentation.center[1]) ** 2
        self.mask_circle = r_squared <= self.settings.segmentation.radius ** 2

    def process_video(self):
        self.start_time = time.time()
        self.generate_mask()
        self.mean_colors = []
        self.led_status = []

        with ThreadPoolExecutor() as executor:
            frame_id = 0
            while frame_id < self.total_frames:
                ret, frame = self.cap.read()
                if not ret:
                    break
                if frame_id % self.frame_interval == 0:
                    future = executor.submit(self.process_frame, (frame_id, frame))
                    self.led_status.append(future.result()[1])
                    self.mean_colors.append(future.result()[2])
                frame_id += 1

        self.total_execution_time = time.time() - self.start_time
        video_duration = self.total_frames / self.fps
        execution_percentage = (self.total_execution_time / video_duration) * 100
        print(f"Total execution time: {self.total_execution_time:.2f} seconds")
        print(f"Execution time as percentage of video duration: {execution_percentage:.2f}%")
        #print(mean_colors)
        return np.array(self.mean_colors), np.array(self.led_status)

    def plot_results(self, mean_colors, led_status):
        time_seconds = np.arange(len(led_status)) * self.frame_interval / self.fps

        fig, axes = plt.subplots(3, 1, figsize=(10, 18))
        labels = ['Blue', 'Green', 'Red']
        for i, color_channel in enumerate(labels):
            axes[i].plot(time_seconds, mean_colors[:, i], '-o', markersize=2, label=f'{color_channel} Values')
            axes[i].set_title(f'{color_channel} Values Over Time')
            axes[i].set_xlabel('Time (seconds)')
            axes[i].set_ylabel(f'{color_channel} values (from 0 to 255)')
            axes[i].grid(True)
            axes[i].legend(loc='best')
        plt.tight_layout()
        plt.show()

    def plot_stairs(self, new_status_led):
        time_seconds = np.arange(len(new_status_led)) * self.frame_interval / self.fps

        plt.plot(time_seconds, new_status_led, '-o')
        plt.show()

    def release_resources(self):
        self.cap.release()

video_path = 'Data_confidential/video_vision_perif.mp4'
analyzer = VideoAnalyzer(video_path)
mean_colors, led_status = analyzer.process_video()
analyzer.plot_results(mean_colors, led_status)
new_status_led = analyzer.stairs_with_red_value()
analyzer.plot_stairs(new_status_led)
analyzer.release_resources()