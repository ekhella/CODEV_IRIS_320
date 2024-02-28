from Modules import os,t, cv2, np
from Base import mess

Video_Path = 'Data_confidential/video_arriere.mp4'

class Video(object):
    def __init__(self):
        self.id = None
        self.Frames, self.Frame_number, self.fps, self.frame_size = self.video_treatment()


    def video_treatment(self) -> list:
        """
        Returns frames, frame_number, fps, frame_size
        """
        frames = []
        frame_number = 0
        capture = cv2.VideoCapture(Video_Path)
        if not capture.isOpened():
                print(mess.P_open, end='')
        else:
            fps = capture.get(cv2.CAP_PROP_FPS)
            frame_size=[int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))] # [WIDTH, HEIGH]
            while True:
                success, frame = capture.read()
                if success:
                    frames.append(Frame(frame_number, np.array(frame)))
                    frame_number += 1
                else:
                    print(mess.P_getvid, end='')
                    break
            capture.release()
            cv2.destroyAllWindows()
            return frames, frame_number, fps, frame_size
    
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
     def __init__(self, array, id):
        self.id = id
        self.array = array
        self.BWarray = None