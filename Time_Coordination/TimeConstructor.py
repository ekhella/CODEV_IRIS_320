""" This code will be a class where the input is a time and the output a Directory with frames corresponding to the input"""
class Time:
    def __init__(self, time):
        self.id = None
        self.time= time

    def get_frame_time(frame_index, fps): #UNUSED YET
        """
        Returns time in ms
        """
        initial_time = 0 # TBD
        time_in_ms = (frame_index / fps) * 1000
        return initial_time+time_in_ms
