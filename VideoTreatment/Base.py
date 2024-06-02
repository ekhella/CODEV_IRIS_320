from Modules import os

class Break(Exception):
    pass

class Mess:
    def __init__(self):
        # B:begining, E:End, P:problem, I:input, S:info

        self.B_proc = "\rInitialization of the procedure\n\n"
        self.E_proc = "\n\nProcedure finished"
        self.P_open = "\rError: Could not open video.\n\n"
        self.P_getvid= "\n\nReached the end of the video. \n\n"
        self.P_gettype = "\rPlease, save data in the accepted format (csv, dict/list(.txt))"
        self.P_vi1 = "\rPlease, paste a video in the accepted format (mp4, mov, avi)"
        self.P_vi2 = "\rPlease, only paste one video"
        self.B_gfs = "\rGetting the video ..."
        self.E_gfs = "\rGot it ! ------------------------------------------ OK\n\n"
        
mess = Mess()

