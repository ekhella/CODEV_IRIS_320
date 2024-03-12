from Modules import sys, cv2, np, csv, pytesseract, t
from Base import mess
from segmentation_settings import *
from pytesseract_configs import *

Video_Path = 'Data_confidential/video_arriere.mp4'

class Video(object):
    def __init__(self):
        self.id = None
        self.Frames, self.Frame_number, self.fps, self.frame_dimensions = self.video_treatment() #NOT CLEAN


    def video_treatment(self) -> list:
        """
        Returns frames, frame_number, fps, frame_size
        """
        global frame_id
        global total_frames
        global frame

        Ti = t.time()

        capture = cv2.VideoCapture(Video_Path)
        file = open('videotreatment.csv', 'w', newline='')
        writer= csv.writer(file)
        writer.writerow(['Frame', 'Speed', 'Time', 'Km marker'])


        frames = []
        frame_id = 0
        frame_decimation = 100 # Analyse every 100 frame of this video
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

        if not capture.isOpened():
                print(mess.P_open, end='')
                return None
        else:
            fps = capture.get(cv2.CAP_PROP_FPS)
            frame_dimensions=[int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))] # [WIDTH, HEIGH]

            while True:
                success, frame = capture.read()
                if success:
                    frames.append(Frame(id, np.array(frame)))

                    if frame_id%frame_decimation==0:
                        speed_treatment()
                        time_treatment()
                        km_treatment()

                        writer.writerow([frame_id, speed, time, km])

                    frame_id += 1
                    progress_bar()

                else:
                    print(mess.P_getvid, end='')
                    break

            capture.release()
            cv2.destroyAllWindows()
            file.close()
            Tf =t.time()
            print("\rThis code took {0} to excecute ".format(convert_ms_to_time_format((Tf-Ti)*1000)))
            
            return frames, frame_id, fps, frame_dimensions
    
    

class Frame(object):
     def __init__(self, id, array):
        self.id = id
        self.array = array

def convert_ms_to_time_format(ms):
    """
    Convert milliseconds to a time format (hours:minutes:seconds:milliseconds).
    """
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}:{int(ms):03}"

def get_frame_time(frame_index, fps):
        """
        Returns time in ms
        """
        initial_time = 0 # TBD
        time_in_ms = (frame_index / fps) * 1000
        return time_in_ms

def progress_bar():
    """
    Prints the progress bar of the video treatment
    """
    progress = frame_id/total_frames
    bar_length = 50
    block= int(round(bar_length*progress))
    progress_text= "\rProgress: [{0}] {1:.2f}% ({2}/{3} frames)".format("#" * block + "-" * (bar_length - block), progress * 100, frame_id, total_frames)
    sys.stdout.write(progress_text)
    sys.stdout.flush()

def speed_treatment():
    global speed

    speed_zone = frame[-h_speed:, :w_speed]
    speed_gray= cv2.cvtColor(speed_zone, cv2.COLOR_BGR2GRAY)
    speed_text= pytesseract.image_to_string(speed_gray, config=speed_config)
    speed = ''.join(filter(str.isdigit,speed_text))

def time_treatment():
    global time

    time_zone = frame[:h_time, w_time:]
    time_gray = cv2.cvtColor(time_zone, cv2.COLOR_BGR2GRAY)
    time_text = pytesseract.image_to_string(time_gray, config=time_config)
    time = ''.join(str(time_text)).strip()

def km_treatment():
    global km

    km_zone = frame[:h_km, w_km_s:w_km_e]
    km_gray = cv2.cvtColor(km_zone, cv2.COLOR_BGR2GRAY)
    km_text = pytesseract.image_to_string(km_gray, config=km_config)
    km = ''.join(str(km_text)).strip()