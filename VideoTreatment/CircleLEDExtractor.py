import cv2
import numpy as np
from VideoTreatment.Settings import Settings

class CircleLEDExtractor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.settings = Settings()
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            raise ValueError("Error loading the video.")

    def get_circular_subimage(self, frame_num):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        
        ret, frame = self.cap.read()
        if not ret:
            print("Error reading the frame.")
            return None, None
        
        h, w = frame.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, self.settings.segmentation.center, self.settings.segmentation.radius, (255, 255, 255), -1)
        
        sub_image = cv2.bitwise_and(frame, frame, mask=mask)
        
        return sub_image, frame

    def display_images(self, sub_image, frame):
        if sub_image is not None:
            cv2.imshow("Circular Sub-image", sub_image)
            cv2.imshow("Original Image", frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Failed to generate the sub-image.")

    def release_resources(self):
        self.cap.release()

video_path = 'Data_confidential/video_vision_perif.mp4'
frame_num = 60 

extractor = CircleLEDExtractor(video_path)
sub_img, frame = extractor.get_circular_subimage(frame_num)
extractor.display_images(sub_img, frame)
extractor.release_resources()
