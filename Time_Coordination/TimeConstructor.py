""" This code will be a class where the input is a time and the output a Directory with frames corresponding to the input"""
def get_frame_time(frame_index, fps): #UNUSED YET
    """
    Returns time in ms
    """
    initial_time = 0 # TBD
    time_in_ms = (frame_index / fps) * 1000
    return initial_time+time_in_ms
