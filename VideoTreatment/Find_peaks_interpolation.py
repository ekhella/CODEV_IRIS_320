import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from LED_on import time_seconds
from LED_on_multiprocess import mean_colors

class LEDAnalysis:
    def __init__(self, mean_colors, time_seconds):
        self.mean_colors = mean_colors
        self.time_seconds = time_seconds
        self.red_channel = mean_colors[:, 2]
        self.diff_red_channel = np.diff(self.red_channel)
        self.peaks, _ = find_peaks(self.diff_red_channel, height=60)
        self.stairs_frames = [0]
        self.stairs_times = [0]
        self.res = -4

    def detect_peaks(self):
        for peak in self.peaks:
            self.stairs_frames.append(peak)
            self.stairs_times.append(self.time_seconds[peak])
            self.res += 4

    def plot_staircase(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.stairs_frames, self.stairs_times, drawstyle='steps-post', label='Staircase Values')
        plt.xlabel('Frame Number')
        plt.ylabel('Time (seconds)')
        plt.title('LED Activation Over Frames')
        plt.grid(True)
        plt.legend()
        plt.show()

    def linear_regression(self):
        coefficients = np.polyfit(self.stairs_frames[1:], self.stairs_times[1:], 1)
        self.slope = coefficients[0]
        self.intercept = coefficients[1]
        self.regression_values = [self.slope * frame + self.intercept for frame in self.stairs_frames[1:]]
        print(f"Slope (Directional Coefficient): {self.slope}")
        print(f"Intercept: {self.intercept}")

    def plot_regression(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.stairs_frames[1:], self.stairs_times[1:], drawstyle='steps-post', label='LED Frames')
        plt.plot(self.stairs_frames[1:], self.regression_values, '-o', markersize=2, label='Linear Up Regression', color='Red')
        plt.xlabel('Frame Number')
        plt.ylabel('Time (seconds)')
        plt.title('LED Activation Over Frames')
        plt.grid(True)
        plt.xlim(0, None)
        plt.ylim(0, None)
        plt.legend()
        plt.show()

    def associate_time_to_frame(self): #To be continued, not finished
        time_min = min(self.stairs_times)
        time_max = max(self.stairs_times)
        time_interp = np.arange(time_min, time_max, 0.001)  #Interpolate every millisecond

        frames_interpolated = np.round((time_interp - self.intercept) / self.slope).astype(int) #Using the slope and intercept to calculate the corresponding frame numbers

        for time, frame in zip(time_interp, frames_interpolated): #To print what we'll want to have in the csv (even if it'll be HH:MM:SS.xxx and note just SS.xxx)
            print(f"Time: {time:.3f} s, Frame: {frame:.0f}")

    def run_analysis(self):
        self.detect_peaks()
        self.plot_staircase()
        self.linear_regression()
        self.plot_regression()
        self.associate_time_to_frame() 

analysis = LEDAnalysis(mean_colors, time_seconds)
analysis.run_analysis()

