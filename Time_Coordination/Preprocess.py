from Modules import cv2

gaussian_kernel_size = (5, 5)
adaptive_threshold_block_size = 11
adaptive_threshold_constant = 4
max_intensity = 255

class Preprocess(object):
    def __init__(self):
        self.id = None
        self.preprocessed = preproccess()

def preproccess(self):

    gray = cv2.cvtColor(self, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, gaussian_kernel_size, 0) # Apply Gaussian blur to reduce noise
    thresh = cv2.adaptiveThreshold(blurred, 
                                   max_intensity, 
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 
                                   adaptive_threshold_block_size, 
                                   adaptive_threshold_constant)     # Apply adaptive thresholding to binarize the image

    return thresh
