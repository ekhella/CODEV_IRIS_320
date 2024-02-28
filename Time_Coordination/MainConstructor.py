from Modules import sys, cv2, np, csv, pytesseract
from Base import mess

Video_Path = 'Data_confidential/video_arriere.mp4'

class Video(object):
    def __init__(self):
        self.id = None
        self.Frames, self.Frame_number, self.fps, self.frame_dimensions = self.video_treatment()


    def video_treatment(self) -> list:
        """
        Returns frames, frame_number, fps, frame_size
        """
        frames = []
        frame_id = 0
        total_frames = 2548 # NOT CLEAN

        x_speed, y_speed, w_speed, h_speed = 0,0, 90, 50
        capture = cv2.VideoCapture(Video_Path)
        file = open('speed.csv', 'w', newline='')
        writer= csv.writer(file)
        writer.writerow(['Frame', 'Speed'])

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

                    interest_zone = frame[-h_speed:, :w_speed]
                    gray= cv2.cvtColor(interest_zone, cv2.COLOR_BGR2GRAY)
                    text= pytesseract.image_to_string(gray, config='--psm 6 digits')
                    speed = ''.join(filter(str.isdigit,text))
                    writer.writerow([frame_id, speed])

                    frame_id += 1

                    progress = frame_id/total_frames
                    bar_length = 50
                    block= int(round(bar_length*progress))
                    progress_text= "\rProgress: [{0}] {1:.2f}% ({2}/{3} frames)".format("#" * block + "-" * (bar_length - block), progress * 100, frame_id, total_frames)
                    sys.stdout.write(progress_text)
                    sys.stdout.flush()
                    
                else:
                    print(mess.P_getvid, end='')
                    break
            capture.release()
            cv2.destroyAllWindows()
            file.close()
            return frames, frame_id, fps, frame_dimensions
    
    def get_frame_time(frame_index, fps):
        """
        Returns time in ms"""
        initial_time = 0 # TBD
        time_in_ms = (frame_index / fps) * 1000
        return time_in_ms
    
    def convert_ms_to_time_format(ms):
        """
        Convert milliseconds to a time format (hours:minutes:seconds:milliseconds).
        """
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        seconds, ms = divmod(ms, 1000)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}:{int(ms):03}"

class Frame(object):
     def __init__(self, id, array):
        self.id = id
        self.array = array