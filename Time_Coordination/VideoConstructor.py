from Modules import sys, cv2, np, csv, pytesseract, t, plt

from pytesseract_configs import speed_config, km_config, time_config, date_config
from segmentation_settings import (
    width_marker_start, width_marker_end, height_marker,
    width_time_start, width_time_end, height_time,
    width_date_start, width_date_end, height_date,
    width_speed, height_speed,
    bar_length,
    speed_threshold, time_threshold, marker_threshold, date_threshold
)
from Base import mess


class VideoProcessor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.capture = None
        self.frame_id = 0
        self.total_frames = 0
        self.data_output = []
        self.prev_data = {}
        self.timings = {
            'opening': 0,
            'info': 0,
            'extraction_speed': 0,
            'extraction_marker': 0,
            'extraction_time': 0,
            'extraction_date': 0,
            'extraction_total': 0,
            'saving': 0,
            'closing': 0,
            'others': 0,
        }
        self.change_log = {'speed': [], 'marker': [], 'time': [],'date': []}
        self.diff_log = {'speed': [], 'marker': [], 'time': [], 'date': []}
    
    def rewrite_marker_format(self, km_marker):
        km_marker_list = list(km_marker)
        km_marker_list[3] = '+'
        km_marker_new = ''.join(km_marker_list)
        return km_marker_new

    @staticmethod
    def convert_ms_to_time_format(ms):
        """
        Converts milliseconds to time format
        Input : Time in ms
        Output : Time in HH:MM:SS:XXXX
        """
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        seconds, ms = divmod(ms, 1000)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}:{int(ms):03}"
    
    def progress_bar(self, start_time):
        """
        Prints the progress of the analysis in % and the estimated time left
        Input : start_time in ms
        Output : Progres bar with % and estimated time left
        """
        current_time = t.time()
        elapsed_time = current_time - start_time
        progress = self.frame_id / self.total_frames
        time_left_formatted = self.convert_ms_to_time_format((elapsed_time / progress - elapsed_time) * 1000) if self.frame_id > 0 else "Calculating..."

        block = int(round(bar_length * progress))
        progress_text = f"\rProgress: [{'#' * block + '-' * (bar_length - block)}] {progress * 100:.2f}% ({self.frame_id}/{self.total_frames} frames). Estimated Time Left: {time_left_formatted}"
        sys.stdout.write(progress_text)
        sys.stdout.flush()
    
    def convert_time_format_to_ms(time_format):
        """
        Converts milliseconds to time format
        Input : Time in HH:MM:SS
        Output : Time in ms (ending with 3 zeros)
        """
        heures, minutes, secondes = map(int, time_format.split(':'))
        ms_heures = heures * 3600 * 1000
        ms_minutes = minutes * 60 * 1000
        ms_secondes = secondes * 1000
        time_in_ms = ms_heures + ms_minutes + ms_secondes
        return time_in_ms

    def measure_time(method):
        """
        Wrapped method to calculate the time of execution of the method in entry
        Input : The method we want to time
        Output : The output of the method; but it added to a self dict the running time of the entry
        """
        def wrapper(self, *args, **kwargs):
            start_time = t.time()
            result = method(self, *args, **kwargs)
            end_time = t.time()
            self.timings[method.__name__] = end_time - start_time
            return result
        return wrapper

    @measure_time
    def open_video(self):
        """
        Opens a video
        Input : None
        Output : True if the Video is correctly opened; False otherwise
        """
        self.capture = cv2.VideoCapture(self.video_path)
        if not self.capture.isOpened():
            print(mess.P_open, end='')
            return False
        return True

    @measure_time
    def get_video_info(self):
        """
        Gets the FPS, Dimensions and Total Frames of a Video
        Input : None
        Output : None
        """
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.frame_dimensions = [int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                                 int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))]
        self.total_frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        return None

    def read_frame(self):
        """
        Reads a single frame from the video capture object.
        Input : None
        Output:
        - frame: The next frame in the video or None if no more frames are available.
        """
        success, frame = self.capture.read()
        return frame if success else None

    def detect_change(self, current_zone, prev_zone, threshold):
        """
        Detects changes between two images (zones) using simple image processing techniques.
        Inputs:
        - current_zone: The current frame zone to analyze.
        - prev_zone: The previous frame zone for comparison.
        - threshold: The threshold for change detection sensitivity.
        Output:
        - Boolean indicating whether a change was detected based on the threshold.
        """
        if prev_zone is None:
            return (0,True)
        current_gray = cv2.cvtColor(current_zone, cv2.COLOR_BGR2GRAY)
        previous_gray = cv2.cvtColor(prev_zone, cv2.COLOR_BGR2GRAY)
        _, current_bw = cv2.threshold(current_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 
        _, previous_bw = cv2.threshold(previous_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        diff = np.sum(np.abs(current_bw.astype(int) - previous_bw.astype(int)))
        sum_of_pixel_values = np.sum(current_bw.astype(int))
        return (diff/sum_of_pixel_values, diff/sum_of_pixel_values > threshold)
    

    def extract_data_from_frame(self, frame):
        """
    Processes a single frame to extract relevant information based on predefined zones for speed, marker data, and time. 
    Also logs changes detected between the current frame and previous frames for each zone.
    
    Inputs:
    - frame: The current video frame to process.
    
    Outputs:
    - data: Dictionary containing extracted information for the current frame including speed, markers, and time.
    
    Operations:
    - For each zone defined (speed, km marker, meters, hours, minutes, seconds), the method:
      * Detects changes from the previous frame using the detect_change method.
      * Extracts text using OCR if a change is detected or reuses text from the previous frame if no change is detected.
      * Logs change detections for each zone to analyze how often changes occur.
    - Calculates and records the time taken to process each zone and the total extraction time for performance analysis.
    """
        T_extraction_start = t.time()
        data = {}
        zones = {
            'speed': (frame[-height_speed:, :width_speed], speed_config, speed_threshold),
            'marker': (frame[:height_marker, width_marker_start:width_marker_end], km_config, marker_threshold),  
            'time': (frame[:height_time, width_time_start:width_time_end], time_config, time_threshold),    
            'date': (frame[:height_date, width_date_start:width_date_end], date_config, date_threshold)  
        }
    
        for key, (zone, config, threshold) in zones.items():
            start_extraction = t.time()
            prev_zone = self.prev_data.get(key, (None, None))[0]
            change_detected = self.detect_change(zone, prev_zone, threshold)[1]
            self.change_log[key].append(change_detected)
            self.diff_log[key].append(self.detect_change(zone, prev_zone, threshold)[0])
            if prev_zone is None or change_detected:
                text = self.get_text(zone, config=config)
                if key=='marker':
                    text=self.rewrite_marker_format(text)
                self.prev_data[key] = (zone, text)
            else:
                text = self.prev_data[key][1]
            data[key] = text
            self.timings['extraction_' + key] += t.time() - start_extraction

        T_extraction_end = t.time()
        self.timings['extraction_total'] += T_extraction_end - T_extraction_start
        return data

    def get_text(self, zone, config):
        """
        Extracts text from a given image zone using OCR configured by the specified configuration.
        Inputs:
        - zone: Image region from which to extract text.
        - config: Configuration parameters for pytesseract.
        Output:
        - Extracted text as a string.
        """
        gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return pytesseract.image_to_string(bw, config=config).strip()

    def save_data(self, data, format_type):
        """
        Saves processed data into the specified format (CSV, dict, or list).
        Inputs:
        - data: The processed data to save.
        - format_type: The format in which to save the data ('csv', 'dict', 'list').
        """
        T_saving_start = t.time()
        if format_type == 'csv':
            if 'file' not in self.prev_data:  #
                self.prev_data['file'] = open('videotreatment.csv', 'w', newline='')
                self.prev_data['writer'] = csv.writer(self.prev_data['file'])
                self.prev_data['writer'].writerow(['Frame', 'Speed', 'Date', 'Time', 'Km marker'])
            self.prev_data['writer'].writerow([self.frame_id, data['speed'],data['date'], data['time'], data['marker']])

        elif format_type in ['dict', 'list']:
            if 'file' not in self.prev_data: 
                self.prev_data['file'] = open('videotreatment.txt', 'w')  
            if format_type == 'dict':
                self.prev_data['file'].write(str({self.frame_id: data}) + '\n')
            elif format_type == 'list':
                self.prev_data['file'].write(str([data['speed'],data['date'], data['time'], data['marker']]) + '\n')
        self.timings['saving'] += t.time() - T_saving_start

    def process_video(self):
        """
    Processes the entire video, extracting data from each frame and saving it in the selected format.
    It also manages the workflow for opening the video, reading frames, handling data extraction, 
    saving data, and cleaning up resources after processing.
    
    Inputs:
    - None directly, but relies on user input to select the output format (csv, dict, or list).
    
    Operations:
    - Opens the video file and retrieves video info.
    - Reads frames in a loop until the video ends.
    - For each frame, it extracts data, saves it, logs change detections, and updates the progress bar.
    - After all frames are processed, it cleans up resources and displays the results.
    
    Side effects:
    - Depending on the selected format, data is written to a CSV file or a text file, or simply stored in memory.
    - Generates a pie chart showing the proportion of time spent on various operations.
    - Outputs a change detection plot to visualize changes across frames.
    """
        format_type = input("Choose output format (csv, dict, list): ")
        start_time = t.time()
        if not self.open_video():
            print(mess.P_gettype, end='')
        self.get_video_info()

        while True:
            frame = self.read_frame()
            if frame is None:
                break

            data = self.extract_data_from_frame(frame)
            self.save_data(data, format_type)
            self.progress_bar(start_time)
            self.frame_id += 1

        self.cleanup()
        self.display_changes(self.change_log)
        self.display_changes(self.diff_log)
        self.display_results(format_type)

    @measure_time
    def cleanup(self):
        """
        Closes any resources held by the VideoProcessor, specifically the video file and any open file handles.
        """
        if 'file' in self.prev_data:
            self.prev_data['file'].close()
        self.capture.release()
        cv2.destroyAllWindows()

    def display_results(self, format_type):
        print("\nFinished processing. Data stored as:", format_type)
        print("Timing Summary:")
        for key, value in self.timings.items():
            print(f"{key}: {self.convert_ms_to_time_format(value * 1000)}")

        labels = []
        sizes = []
        explode = []
        self.timings.pop('extraction_total', None)
        for key, value in self.timings.items():
            if value > 0:
                labels.append(key)
                sizes.append(value)
                explode.append(0.1)

        explode = tuple(explode) # Ensure the size of explode matches the number of labels
        _, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=None, autopct='%1.1f%%', shadow=False, startangle=90, labeldistance=1.2)
        ax1.axis('equal')  # Draw a circle
        plt.legend(labels, loc="best")
        plt.title('Execution Time Breakdown')
        plt.show()
    
    def display_changes (self, results):
        """
        Displays individual plots of detected changes over the course of the video processing for each type of data extracted.
        Inputs:
        - results: Dictionary containing lists of change detection results for each label.
        """
        for key, changes in results.items():
            plt.figure(figsize=(10, 6))  # Create a new figure for each key
            plt.plot(changes, label=key, marker='o', linestyle='-')  # Mark each change point
            plt.title(f'Change Detection: {key}')
            plt.xlabel('Frame Number')
            plt.ylabel('Change Detected (True/False)')
            plt.legend()
            plt.grid(True)  # Optionally add grid for better visibility
            plt.show()