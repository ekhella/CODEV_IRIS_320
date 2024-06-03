from Modules import plt
from Modules import np

class VideoDataAnalyzer:
    def __init__(self, file_path, video_path):
        self.file_path = file_path
        self.video_path = video_path
        self.data = self.read_data_from_file()
        self.frames = list(self.data.keys())
        self.markers_meters = [self.convert_marker_to_meters(self.data[frame]['marker']) for frame in self.frames]
        self.time_seconds = [self.convert_time_to_seconds(self.data[frame]['time']) for frame in self.frames]
        self.speeds = [float(self.data[frame]['speed']) for frame in self.frames]
        self.slope, self.intercept = self.calculate_regression()

    def convert_time_to_seconds(self, time_str):
        hours, minutes, seconds = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds

    def convert_marker_to_meters(self, marker_str):
        km, meters = marker_str.split('+')
        return float(km) * 1000 + float(meters)

    def read_data_from_file(self):
        data = {}
        with open(self.file_path, 'r') as file:
            for line in file:
                frame_data = eval(line)
                frame_num = list(frame_data.keys())[0]
                data[frame_num] = frame_data[frame_num]
        return data

    def calculate_regression(self):
        """Create dictionaries with frame numbers as keys and time or marker meters as values
        Only include frames where delta time is not zero to avoid division by zero in regression calculation"""
        valid_frames = {index: self.time_seconds[i] for i, index in enumerate(self.frames[1:]) 
                        if self.time_seconds[i] - self.time_seconds[i-1] != 0}
        if valid_frames:
            coefficients = np.polyfit(list(valid_frames.keys()), list(valid_frames.values()), 1)
            return coefficients[0], coefficients[1]  # slope, intercept
        return 0, 0  # Default if no valid frames for regression
    
    def get_frame_number(self, time_input):
        if self.slope != 0: 
            frame_number = (time_input - self.intercept) / self.slope
            return np.rint(frame_number).astype(int)
        return None  

    def plot_markers(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.frames, self.markers_meters, marker='.', linestyle='-', color='green')
        plt.xlabel('Frame Number')
        plt.ylabel('Distance (meters)')
        plt.title('Distance Traveled Over Frames')
        plt.grid(True)
        #plt.show()

    def plot_time_progression(self):
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
        plt.figure(figsize=(10, 6))
        plt.plot(self.frames, self.speeds, 'm-', marker='.')
        plt.xlabel('Frame Number')
        plt.ylabel('Speed (km/h)')
        plt.title('Speed Over Frames')
        plt.grid(True)
        #plt.show()