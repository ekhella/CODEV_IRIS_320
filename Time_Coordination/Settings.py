class PyTesseractConfig:
    def __init__(self):
        self.speed = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        self.time = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789:'
        self.km = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789+'
        self.date = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789/'

class SegmentationSettings:
    def __init__(self):
        self.bar_length = 50
        self.height_speed = self.height_marker = self.height_time = self.height_date = 16
        self.width_speed = 30
        self.width_time = (557, 640)
        self.width_marker = (95, 161)
        self.width_date = (456, 553)
        self.explode = (.1,) * 8
        self.led_bounds = (200, 225, 567, 578)
        self.thresholds = {'speed': 0.1, 'time': 0.05, 'marker': 0.1, 'date': 0.1}
        self.frame_decimation = 1
        self.center = (218, 575)
        self.radius = 6

class Settings:
    def __init__(self):
        self.pytesseract = PyTesseractConfig()
        self.segmentation = SegmentationSettings()
