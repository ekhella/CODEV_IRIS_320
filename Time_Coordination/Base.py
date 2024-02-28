from Modules import os

class Break(Exception):
    pass

class Mess:
    def __init__(self):
        # B:begining, E:End, P:problem, I:input, S:info

        self.B_proc = "\rInitialization of the procedure\n\n"
        self.E_proc = "\n\nProcedure finished"
        self.P_open = "\rError: Could not open video.\n\n"
        self.P_getvid= "Reached the end of the video. \n\n"
        
mess = Mess()

