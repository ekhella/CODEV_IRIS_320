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
        self.stairs_time = [0]
        self.stairs_values = [0]
        self.res = -4

    def detect_peaks(self):
        for peak in self.peaks:
            self.stairs_time.append(self.time_seconds[peak] - self.time_seconds[self.peaks[0]])  # Adjust to start from zero
            self.res += 4
            self.stairs_values.append(self.res)

    def plot_staircase(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.stairs_time, self.stairs_values, drawstyle='steps-post', label='Staircase Values')
        plt.xlabel('Time (seconds)')
        plt.ylabel('LED Activation Time')
        plt.title('LED Activation Over Time')
        plt.grid(True)
        plt.legend()
        plt.show()

    def shift_times(self):
        first_step_time = self.stairs_time[1]
        self.stairs_time_shifted = [time - first_step_time for time in self.stairs_time]
        self.stairs_time_shifted_positive = [time for time in self.stairs_time_shifted if time >= 0]
        self.stairs_values_positive = [self.stairs_values[i] for i in range(len(self.stairs_time_shifted)) if self.stairs_time_shifted[i] >= 0]

    def linear_regression(self):
        coefficients = np.polyfit(self.stairs_time_shifted_positive, self.stairs_values_positive, 1)
        self.slope = coefficients[0]
        self.intercept = coefficients[1]
        self.regression_values = [self.slope * time + self.intercept for time in self.stairs_time_shifted_positive]
        print(f"Slope (Directional Coefficient): {self.slope}")
        print(f"Intercept: {self.intercept}")

    def plot_regression(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.stairs_time_shifted_positive, self.stairs_values_positive, drawstyle='steps-post', label='LED Time')
        plt.plot(self.stairs_time_shifted_positive, self.regression_values, '-o', markersize=2, label='Linear Up Regression', color='Red')
        plt.xlabel('Time (seconds)')
        plt.ylabel('LED Activation Time')
        plt.title('LED Activation Over Time ')
        plt.grid(True)
        plt.xlim(0, None)
        plt.ylim(0, None)
        plt.legend()
        plt.show()

    def run_analysis(self):
        self.detect_peaks()
        self.plot_staircase()
        self.shift_times()
        self.linear_regression()
        self.plot_regression()

# Example usage:
# mean_colors and time_seconds should be defined or imported from LED_on_multiprocess
# mean_colors = ...
# time_seconds = ...
analysis = LEDAnalysis(mean_colors, time_seconds)
analysis.run_analysis()