# Imports
from Modules import sys, cv2, np, csv, pytesseract, t, plt
from Base import mess
from segmentation_settings import bar_length, frame_decimation, w_speed, h_speed, w_time, w_km_e, w_km_s, h_km, h_time, explode
from pytesseract_configs import speed_config, km_config, time_config
from FrameConstructor import Frame

Video_Path = 'Data_confidential/video_arriere.mp4'

def convert_ms_to_time_format(ms):
    """
    Convert milliseconds to a time format (hours:minutes:seconds:milliseconds).
    """
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}:{int(ms):03}"


def get_frame_time(frame_index, fps): #UNUSED YET
    """
    Returns time in ms
    """
    initial_time = 0 # TBD
    time_in_ms = (frame_index / fps) * 1000
    return initial_time+time_in_ms

def progress_bar(frame_id, total_frames):
    """
    Prints the progress bar of the video treatment
    """
    progress = frame_id/total_frames
    block= int(round(bar_length*progress))
    progress_text= "\rProgress: [{0}] {1:.2f}% ({2}/{3} frames)".format(
        "#" * block + "-" * (bar_length - block), progress * 100, frame_id, total_frames)
    sys.stdout.write(progress_text)
    sys.stdout.flush()

class Video(object):
    def __init__(self):
        self.id = None
        self.Frames, self.Frame_number, self.fps, self.frame_dimensions = self.video_treatment() #NOT CLEAN
    
    def get_attribute(self, zone, spec_config):
        zone_gray= cv2.cvtColor(zone, cv2.COLOR_BGR2GRAY)
        zone_text= pytesseract.image_to_string(zone_gray, config=spec_config)
        return ''.join(filter(str.isdigit,zone_text))


    def video_treatment(self) -> list:
        """
        Returns frames, frame_number, fps, frame_size
        """
        Ti = t.time()

        capture = cv2.VideoCapture(Video_Path)
        file = open('videotreatment.csv', 'w', newline='')
        Tf = t.time()
        T_opening= Tf-Ti
        print("\rOpening the video took {0} to excecute ".format(convert_ms_to_time_format((T_opening)*1000)))
        writer= csv.writer(file)
        writer.writerow(['Frame', 'Speed', 'Time', 'Km marker'])
        frames = []
        frame_id = 0
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) 

        if not capture.isOpened():
                print(mess.P_open, end='')
                return None
        else:
            T1=t.time()
            fps = capture.get(cv2.CAP_PROP_FPS)
            frame_dimensions=[int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))] # [WIDTH, HEIGH]
            Tf = t.time()
            T_fps=Tf-T1
            print("\rGetting the FPS/dimensions took {0} to excecute ".format(convert_ms_to_time_format((T_fps)*1000)))
            T_speed, T_time, T_km, T_write = 0,0,0,0
            while True:
                success, frame = capture.read()
                if success:
                    speed_zone = frame[-h_speed:, :w_speed]
                    time_zone = frame[:h_time, w_time:]
                    km_zone = frame[:h_km, w_km_s:w_km_e]  

                    frames.append(Frame(id, np.array(frame)))

                    if frame_id%frame_decimation==0:
                        T1=t.time()
                        speed = self.get_attribute(speed_zone, speed_config)
                        T2=t.time()
                        T_speed+=T2-T1

                        time = self.get_attribute(time_zone, time_config)
                        T3=t.time()
                        T_time+= T3-T2

                        km = self.get_attribute(km_zone, km_config)
                        T4=t.time()
                        T_km+= T4-T3

                        writer.writerow([frame_id, speed, time, km])
                        T5=t.time()
                        T_write+= T5-T4

                    frame_id += 1
                    progress_bar(frame_id, total_frames)
                else:
                    print(mess.P_getvid, end='')
                    break
            print("\rSpeed treatment took {0} to excecute ".format(convert_ms_to_time_format((T_speed)*1000))) 
            print("\rTime treatment took {0} to excecute ".format(convert_ms_to_time_format((T_time)*1000))) 
            print("\rKm treatment took {0} to excecute ".format(convert_ms_to_time_format((T_km)*1000))) 
            print("\rWriting on the CSV took {0} to excecute ".format(convert_ms_to_time_format((T_write)*1000))) 

            T6 = t.time()
            capture.release()
            cv2.destroyAllWindows()
            file.close()
            Tf =t.time()
            T_closing =Tf- T6
            T_treatment= Tf-Ti
            T_others = T_treatment - (T_opening + T_fps + T_speed + T_time + T_km + T_write + T_closing)
            print("\rThis code took {0} to excecute ".format(convert_ms_to_time_format((T_treatment)*1000)))
            labels = ["Opening :","Getting FPS :","Speed Treatment :","Time Treatment :", "Km Treatment :","CSV Writing : ", "Closing :", "Others"]
            values =[T_opening/T_treatment, T_fps/T_treatment, T_speed/T_treatment, T_time/T_treatment, T_km/T_treatment, T_write/T_treatment, T_closing, T_others/T_treatment]
            print("Review :\n" +"\n".join(["{0} {1:%}".format(label, value) for label, value in zip(labels, values)]))
            fig, ax = plt.subplots()
            ax.pie(values, explode= explode, labels=None, startangle=90, labeldistance= 1.2)
            plt.legend(labels,loc= "best")
            plt.axis('equal')
            plt.show()
            return frames, frame_id, fps, frame_dimensions
    

