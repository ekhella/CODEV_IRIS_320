from Modules import sys, cv2, np, csv, pytesseract, t, plt
from Base import mess
from segmentation_settings import w_speed, h_speed
from segmentation_settings import h_time
from segmentation_settings import w_hour_s, w_hour_e
from segmentation_settings import w_minute_s, w_minute_e
from segmentation_settings import w_second_s, w_second_e
from segmentation_settings import w_km_e, w_km_s, h_km
from segmentation_settings import w_m_e, w_m_s, h_m
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
        zone_text = pytesseract.image_to_string(zone_bw, config=spec_config)
        return str(zone_text.strip())

    def detect_change(self, zone_current, zone_previous, threshold=0):
        zone_current_gray = cv2.cvtColor(zone_current, cv2.COLOR_BGR2GRAY)
        zone_previous_gray = cv2.cvtColor(zone_previous, cv2.COLOR_BGR2GRAY)
        _, zone_current_bw = cv2.threshold(zone_current_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) 
        _, zone_previous_bw = cv2.threshold(zone_previous_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        difference = np.sum(np.abs(zone_current_bw.astype(int) - zone_previous_bw.astype(int)))
        return difference > threshold

    def process_video(self):
        """
        Returns frames, frame_number, fps, frame_size
        """
        T_start_process = t.time()

        capture = cv2.VideoCapture(self.video_path)
        file = open('videotreatment.csv', 'w', newline='')
        T_end_opening = t.time()
        T_opening = T_end_opening - T_start_process
        print("\rOpening the video took {0} to execute".format(convert_ms_to_time_format(T_opening * 1000)))
        writer = csv.writer(file)
        writer.writerow(['Frame', 'Speed', 'Time', 'Km marker'])
        self.total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

        if not capture.isOpened():
            print(mess.P_open, end='')
            return None
        else:
            T1 = t.time()
            self.fps = capture.get(cv2.CAP_PROP_FPS)
            self.frame_dimensions = [int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))]  # [WIDTH, HEIGHT]
            Tf = t.time()
            T_fps = Tf - T1
            print("\rGetting the FPS/dimensions took {0} to execute".format(convert_ms_to_time_format(T_fps * 1000)))
            T_speed, T_time, T_km, T_write = 0, 0, 0, 0
            prev_speed_zone, prev_km_zone, prev_m_zone = None, None, None
            prev_hour_zone, prev_minute_zone, prev_second_zone = None, None, None
            last_speed, last_km, last_m = "", "", ""
            last_hour, last_minute, last_second = "", "", ""

            while True:
                success, frame = capture.read()
                if success:
                    speed_zone = frame[-h_speed:, :w_speed]
                    km_zone = frame[:h_km, w_km_s:w_km_e]
                    m_zone = frame[:h_m, w_m_s:w_m_e]
                    hour_zone = frame[:h_time, w_hour_s:w_hour_e]
                    minute_zone = frame[:h_time, w_minute_s:w_minute_e]
                    second_zone = frame[:h_time, w_second_s:w_second_e]

                    self.frames.append(Frame(self.frame_id, np.array(frame)))  # For now, the Frame Class is Useless but let's keep it

                    if self.frame_id % frame_decimation == 0:
                        speed, km = last_speed, last_km
                        hour, minute, second = last_hour, last_minute, last_second

                        T_start_speed = t.time()
                        if prev_speed_zone is None or self.detect_change(speed_zone, prev_speed_zone):
                            speed = self.get_attribute(speed_zone, speed_config)
                            last_speed = speed
                        T_end_speed = t.time()
                        T_speed += T_end_speed - T_start_speed

                        T_start_time = t.time()
                        if prev_hour_zone is None or self.detect_change(hour_zone, prev_hour_zone):
                            hour = self.get_attribute(hour_zone, time_config)
                            last_hour = hour
                        if prev_minute_zone is None or self.detect_change(minute_zone, prev_minute_zone):
                            minute = self.get_attribute(minute_zone, time_config)
                            last_minute = minute
                        if prev_second_zone is None or self.detect_change(second_zone, prev_second_zone):
                            second = self.get_attribute(second_zone, time_config)
                            last_second = second
                        time = "{}:{}:{}".format(hour, minute, second)
                        T_end_time = t.time()
                        T_time += T_end_time - T_start_time

                        T_start_km = t.time()
                        if prev_km_zone is None or self.detect_change(km_zone, prev_km_zone):
                            km = self.get_attribute(km_zone, km_config)
                            last_km = km
                        if prev_m_zone is None or self.detect_change(m_zone, prev_m_zone):
                            m = self.get_attribute(m_zone, km_config)
                            last_m = m
                        distance = "{}+{}".format(km, m)
                        T_end_km = t.time()
                        T_km += T_end_km - T_start_km

                        writer.writerow([self.frame_id, speed, time, distance])
                        T_end_write = t.time()
                        T_write += T_end_write - T_end_km

                        prev_speed_zone = speed_zone
                        prev_hour_zone = hour_zone
                        prev_minute_zone = minute_zone
                        prev_second_zone = second_zone
                        prev_km_zone = km_zone
                        prev_m_zone = m_zone

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
            capture.release()
            cv2.destroyAllWindows()
            file.close()
            T_end_all = t.time()
            T_closing = T_end_all - T_start_closing
            T_treatment = T_end_all - T_start_process
            T_others = T_treatment - (T_opening + T_fps + T_speed + T_time + T_km + T_write + T_closing)

            # Ensure all values are non-negative
            T_treatment = max(T_treatment, 0)
            T_opening = max(T_opening, 0)
            T_fps = max(T_fps, 0)
            T_speed = max(T_speed, 0)
            T_time = max(T_time, 0)
            T_km = max(T_km, 0)
            T_write = max(T_write, 0)
            T_closing = max(T_closing, 0)
            T_others = max(T_others, 0)

            print("\rThis code took {0} to execute".format(convert_ms_to_time_format(T_treatment * 1000)))
            labels = ["Opening:", "Getting FPS:", "Speed Treatment:", "Time Treatment:", "Km Treatment:", "CSV Writing:", "Closing:", "Others"]
            values = [T_opening / T_treatment, T_fps / T_treatment, T_speed / T_treatment, T_time / T_treatment, T_km / T_treatment, T_write / T_treatment, T_closing / T_treatment, T_others / T_treatment]
            print("Review:\n" + "\n".join(["{0} {1:%}".format(label, value) for label, value in zip(labels, values)]))
            fig, ax = plt.subplots()
            ax.pie(values, explode=explode, labels=None, startangle=90, labeldistance=1.2)
            plt.legend(labels, loc="best")
            plt.axis('equal')
            plt.show()