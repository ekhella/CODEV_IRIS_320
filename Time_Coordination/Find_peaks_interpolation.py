import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from Time_Coordination.LED_on_multiprocess import mean_colors, time_seconds

# Detect rising edges in the red channel
red_channel = mean_colors[:, 2]
diff_red_channel = [red_channel[i] - red_channel[i - 1] for i in range(1, len(red_channel))]
peaks, _ = find_peaks(diff_red_channel, height=60) #Below a height of 60 certain peaks are not detected
stairs_time, stairs_values, res = [0], [0], -4

for peak in peaks:
    stairs_time.append(time_seconds[peak] - time_seconds[peaks[0]])  # Adjust to start from zero
    res += 4
    stairs_values.append(res)

# Plotting the staircase plot
plt.figure(figsize=(10, 6))
plt.plot(stairs_time, stairs_values, drawstyle='steps-post', label='Staircase Values')
plt.xlabel('Time (seconds)')
plt.ylabel('LED Activation Time')
plt.title('LED Activation Over Time')
plt.grid(True)
plt.legend()
plt.show()

# Determine the time of the first step
first_step_time = stairs_time[1]

# Shift all step times to start from the origin
stairs_time_shifted = [time - first_step_time for time in stairs_time]

# Remove the initial negative times and corresponding values
stairs_time_shifted_positive = [time for time in stairs_time_shifted if time >= 0]
stairs_values_positive = [stairs_values[i] for i in range(len(stairs_time_shifted)) if stairs_time_shifted[i] >= 0]

#Linear Regression
coefficients = np.polyfit(stairs_time_shifted_positive, stairs_values_positive, 1)
slope = coefficients[0]
intercept = coefficients[1]
regression_values = [slope * time + intercept for time in stairs_time_shifted_positive]

print(f"Slope (Directional Coefficient): {slope}")
print(f"Intercept: {intercept}")

# Plot the graph with shifted times and linear regression
plt.figure(figsize=(10, 6))
plt.plot(stairs_time_shifted_positive, stairs_values_positive, drawstyle='steps-post', label='LED Time')
plt.plot(stairs_time_shifted_positive, regression_values, '-o', markersize=2, label='Linear Up Regression', color='Red')
plt.xlabel('Time (seconds)')
plt.ylabel('LED Activation Time')
plt.title('LED Activation Over Time ')
plt.grid(True)
plt.xlim(0, None)
plt.ylim(0, None)
plt.legend()
plt.show()
