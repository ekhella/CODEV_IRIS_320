from Modules import sys, cv2, np, csv, pytesseract, t, plt
from Base import mess
from segmentation_settings import (
    width_marker_start, width_marker_end, height_marker,
    width_time_start, width_time_end, height_time,
    width_date_start, width_date_end, height_date,
    width_speed, height_speed,
    )
from pytesseract_configs import speed_config, km_config, time_config
from segmentation_settings import bar_length, frame_decimation, explode
from FrameConstructor import Frame


def convert_ms_to_time_format(ms):
    """
    Convert milliseconds to a time format (hours:minutes:seconds:milliseconds).
    """
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}:{int(ms):03}"

def progress_bar(start_time, frame_id, total_frames):
    """
    Prints the progress bar of the video treatment with estimated time left.
    """
    current_time = t.time()
    elapsed_time = current_time - start_time
    progress = frame_id / total_frames

    if frame_id > 0:
        estimated_total_time = elapsed_time / progress
        estimated_time_left = estimated_total_time - elapsed_time
        time_left_formatted = convert_ms_to_time_format(estimated_time_left * 1000)  # Convert seconds to ms
    else:
        time_left_formatted = "Calculating..."

    block = int(round(bar_length * progress))
    progress_text = "\rProgress: [{0}] {1:.2f}% ({2}/{3} frames). Estimated Time Left: {4}".format(
        "#" * block + "-" * (bar_length - block), progress * 100, frame_id, total_frames, time_left_formatted
    )
    sys.stdout.write(progress_text)
    sys.stdout.flush()


class VideoProcessor:
    def __init__(self, video_path):
        self.id = None
        self.video_path = video_path
        self.frame_id = 0
        self.total_frames = 0
        self.frames = []
        self.fps = 0
        self.frame_dimensions = [0, 0]

    def get_attribute(self, zone, spec_config):
        zone_gray = cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
        _, zone_bw = cv2.threshold(zone_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        kernel= cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morphed_current= cv2.morphologyEx(zone_bw, cv2.MORPH_CLOSE, kernel)
        zone_text = pytesseract.image_to_string(morphed_current, config=spec_config)
        return str(zone_text.strip())

    def detect_change(self, zone_current, zone_previous, threshold=0):
        zone_current_gray = cv2.cvtColor(zone_current, cv2.COLOR_BGR2GRAY)
        zone_previous_gray = cv2.cvtColor(zone_previous, cv2.COLOR_BGR2GRAY)
        _, zone_current_bw = cv2.threshold(zone_current_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 
        _, zone_previous_bw = cv2.threshold(zone_previous_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        kernel= cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morphed_current= cv2.morphologyEx(zone_current_bw, cv2.MORPH_CLOSE, kernel)
        morphed_previous= cv2.morphologyEx(zone_previous_bw, cv2.MORPH_CLOSE, kernel)
        difference = np.sum(np.abs(morphed_current.astype(int) - morphed_previous.astype(int)))
        return difference, difference > threshold
    
    def open_video_timed(self):
        T_start_opening = t.time()
        self.capture = cv2.VideoCapture(self.video_path)
        file = open('videotreatment.csv', 'w', newline='')
        T_end_opening = t.time()
        T_opening = T_end_opening - T_start_opening
        print("\rOpening the video took {0} to execute".format(convert_ms_to_time_format(T_opening * 1000)))
        return file, T_opening
    
    def select_output_format(self):
        if True : 
            return None
    
    def get_video_info_timed(self):
        T_info_start = t.time()
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.frame_dimensions = [int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                                 int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))]
        self.total_frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        T_info_stop = t.time()
        T_info= T_info_stop-T_info_start
        print("\rGetting the FPS/dimensions took {0} to execute".format(convert_ms_to_time_format(T_info * 1000)))
        return T_info

    def process_video(self):
        """
        Returns frames, frame_number, fps, frame_size
        """
        T_start_process = t.time()
        self.file, T_opening = self.open_video_timed()
        self.select_output_format()
        writer = csv.writer(self.file)
        writer.writerow(['Frame', 'Speed', 'Time', 'Km marker'])
        difference_time = []
        difference_km = []
        difference_date = []
        difference_speed = []

        if not self.capture.isOpened():
            print(mess.P_open, end='')
            return None
        else:
            T_info = self.get_video_info_timed()

            T_speed, T_time, T_km, T_write = 0, 0, 0, 0
            prev_speed_zone, prev_km_zone, prev_time_zone, prev_date_zone = None, None, None, None
            last_speed, last_km, last_time, last_date = "", "", "", ""

            while True:
                success, frame = self.capture.read()
                if success:
                    speed_zone = frame[-height_speed:, :width_speed]
                    km_zone = frame[:height_marker, width_marker_start:width_marker_end]
                    time_zone = frame[:height_time, width_time_start:width_time_end]
                    date_zone = frame[:height_date, width_date_start:width_date_end]

                    self.frames.append(Frame(self.frame_id, np.array(frame)))  # For now, the Frame Class is Useless but let's keep it

                    if self.frame_id % frame_decimation == 0:
                        speed, km, time, date = last_speed, last_km, last_time, last_date

                        T_start_speed = t.time()
                        if prev_speed_zone is None or self.detect_change(speed_zone, prev_speed_zone)[1]:
                            speed = self.get_attribute(speed_zone, speed_config)
                            last_speed = speed
                        difference_speed.append(self.detect_change(speed_zone, prev_speed_zone)[0])
                        T_end_speed = t.time()
                        T_speed += T_end_speed - T_start_speed

                        T_start_time = t.time()
                        if prev_time_zone is None or self.detect_change(time_zone, prev_time_zone)[1]:
                            time = self.get_attribute(time_zone, time_config)
                            last_time = time
                        difference_time.append(self.detect_change(time_zone, prev_time_zone)[0])

                        if prev_date_zone is None or self.detect_change(date_zone, prev_date_zone)[1]:
                            date = self.get_attribute(date_zone, time_config)
                            last_date = date
                        difference_date.append(self.detect_change(date_zone, prev_date_zone)[0])

                        T_end_time = t.time()
                        T_time += T_end_time - T_start_time

                        T_start_km = t.time()
                        if prev_km_zone is None or self.detect_change(km_zone, prev_km_zone)[1]:
                            km = self.get_attribute(km_zone, km_config)
                            last_km = km
                        difference_km.append(self.detect_change(km_zone, prev_km_zone)[0])

                        T_end_km = t.time()
                        T_km += T_end_km - T_start_km

                        writer.writerow([self.frame_id, speed, time, km, date])
                        T_end_write = t.time()
                        T_write += T_end_write - T_end_km

                        prev_speed_zone = speed_zone
                        prev_time_zone = time_zone
                        prev_km_zone = km_zone
                        prev_date_zone = date_zone


                    self.frame_id += 1
                    progress_bar(T_start_process, self.frame_id, self.total_frames)
                else:
                    print(mess.P_getvid, end='')
                    break

            print("\rSpeed treatment took {0} to execute".format(convert_ms_to_time_format(T_speed * 1000)))
            print("\rTime treatment took {0} to execute".format(convert_ms_to_time_format(T_time * 1000)))
            print("\rKm treatment took {0} to execute".format(convert_ms_to_time_format(T_km * 1000)))
            print("\rWriting on the CSV took {0} to execute".format(convert_ms_to_time_format(T_write * 1000)))

            T_start_closing = t.time()
            self.capture.release()
            cv2.destroyAllWindows()
            self.file.close()
            T_end_all = t.time()
            T_closing = T_end_all - T_start_closing
            T_treatment = T_end_all - T_start_process
            T_others = T_treatment - (T_opening + T_info + T_speed + T_time + T_km + T_write + T_closing)

            # Ensure all values are non-negative
            T_treatment = max(T_treatment, 0)
            T_opening = max(T_opening, 0)
            T_info = max(T_info, 0)
            T_speed = max(T_speed, 0)
            T_time = max(T_time, 0)
            T_km = max(T_km, 0)
            T_write = max(T_write, 0)
            T_closing = max(T_closing, 0)
            T_others = max(T_others, 0)

            print("\rThis code took {0} to execute".format(convert_ms_to_time_format(T_treatment * 1000)))
            labels = ["Opening:", "Getting FPS:", "Speed Treatment:", "Time Treatment:", "Km Treatment:", "CSV Writing:", "Closing:", "Others"]
            values = [T_opening / T_treatment, T_info / T_treatment, T_speed / T_treatment, T_time / T_treatment, T_km / T_treatment, T_write / T_treatment, T_closing / T_treatment, T_others / T_treatment]
            print("Review:\n" + "\n".join(["{0} {1:%}".format(label, value) for label, value in zip(labels, values)]))
            fig, ax = plt.subplots()
            ax.pie(values, explode=explode, labels=None, startangle=90, labeldistance=1.2)
            plt.legend(labels, loc="best")
            plt.axis('equal')
            plt.show()
            
            plt.figure()
            plt.plot(difference_date, range(self.total_frames))
            plt.show()
            plt.figure()
            plt.plot(difference_speed, range(self.total_frames))
            plt.show()
            plt.figure()
            plt.plot(difference_time, range(self.total_frames))
            plt.show()
            plt.figure()
            plt.plot(difference_km, range(self.total_frames))
            plt.show()