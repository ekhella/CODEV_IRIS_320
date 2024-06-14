import csv
import numpy as np
import matplotlib.pyplot as plt

class VideoDataAnalyzer:
    def __init__(self, file_path, video_path):
        self.file_path = file_path
        self.video_path = video_path
        self.data = self.read_data_from_file()
        self.frames = list(self.data.keys())
        # Ensure default values are properly set to avoid missing data issues
        self.markers_meters = [self.convert_marker_to_meters(self.data[frame].get('marker', '0+0')) for frame in self.frames]
        self.time_seconds = [self.convert_time_to_seconds(self.data[frame].get('time', '00:00:00')) for frame in self.frames]
        self.speeds = [float(self.data[frame].get('speed', 0)) for frame in self.frames]
        self.slope, self.intercept = self.calculate_regression()
        self.interpolated_times = self.calculate_interpolated_times()

    def convert_time_to_seconds(self, time_str):
        hours, minutes, seconds = map(float, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    
    def convert_seconds_to_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:06.3f}"

    def convert_marker_to_meters(self, marker_str):
        km, meters = marker_str.split('+')
        return float(km) * 1000 + float(meters)

    def read_data_from_file(self):
        data = {}
        with open(self.file_path, mode='r', newline='') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Use the frame number as the key in the dictionary
                frame_number = int(row['frame'])
                data[frame_number] = row
        return data

    def calculate_regression(self):
        """Calculates a linear regression from the time data to estimate frame numbers."""
        valid_frames = {index: self.time_seconds[index] for index in self.frames
                if index > 1 and self.time_seconds[index] - self.time_seconds[index-1] != 0}

        if valid_frames:
            x = list(valid_frames.keys())
            y = list(valid_frames.values())
            coefficients = np.polyfit(x, y, 1)
            return coefficients[0], coefficients[1]  # slope, intercept
        else:
            print("Insufficient data for a meaningful regression.")
            return 0, 0  # Default if no valid data for regression
    
    def calculate_interpolated_times(self):
        """Calculates interpolated times for all frames."""
        interpolated_times = {}
        for frame in self.frames:
            interpolated_time_seconds = self.slope * frame + self.intercept
            interpolated_times[frame] = self.convert_seconds_to_time(interpolated_time_seconds)
        return interpolated_times

    def get_frame_number(self, time_input):
        """Estimates frame number based on input time using the regression line."""
        if self.slope != 0:
            frame_number = (self.convert_time_to_seconds(time_input) - self.intercept) / self.slope
            return int(np.rint(frame_number))
        else:
            print("Slope is zero, cannot calculate frame number.")
            return None
        
    def add_interpolated_times_to_data(self):
        """Adds the interpolated times to the data."""
        for frame in self.frames:
            self.data[frame]['Interpolated Time'] = self.interpolated_times[frame]

    def save_data_with_interpolated_times(self, output_file_path):
        """Saves the data with interpolated times to a new CSV file."""
        self.add_interpolated_times_to_data()
        fieldnames = list(self.data[self.frames[0]].keys())
        with open(output_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for frame in self.frames:
                writer.writerow(self.data[frame])

    def plot_markers(self):
        """Plots markers over frames."""
        plt.figure(figsize=(10, 6))
        plt.plot(self.frames, self.markers_meters, marker='.', linestyle='-', color='green')
        plt.xlabel('Frame Number')
        plt.ylabel('Distance (meters)')
        plt.title('Distance Traveled Over Frames')
        plt.grid(True)
        #plt.show()

    def plot_time_progression(self):
        """Plots time progression over frames."""
        plt.figure(figsize=(10, 6))
        actual_time = [self.time_seconds[int(frame)] for frame in self.frames]
        predicted_time = [self.slope * float(frame) + self.intercept for frame in self.frames]
        plt.plot(self.frames, actual_time, 'b-', label='Actual Time')
        plt.plot(self.frames, predicted_time, 'r--', label='Predicted Time')
        plt.xlabel('Frame Number')
        plt.ylabel('Time (seconds)')
        plt.title('Time Progression Over Frames')
        plt.legend()
        plt.grid(True)
        #plt.show()

    def plot_speeds(self):
        """Plots speed over frames."""
        plt.figure(figsize=(10, 6))
        plt.plot(self.frames, self.speeds, 'm-', marker='.')
        plt.xlabel('Frame Number')
        plt.ylabel('Speed (km/h)')
        plt.title('Speed Over Frames')
        plt.grid(True)
        #plt.show()

