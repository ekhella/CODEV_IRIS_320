""" This code will be used to regroup Frames with their mesures and possibly applying image treatment"""

class Frame(object):
     def __init__(self, id, array):
        self.id = id
        self.array = array