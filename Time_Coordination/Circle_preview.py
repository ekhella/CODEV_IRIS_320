import cv2
import numpy as np
from segmentation_settings import radius, center

def circular_subimage(video_path, radius, center, frame_num):
    # Load the video
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video is loaded correctly
    if not cap.isOpened():
        print("Error loading the video.")
        return None
    
    # Go to the specified frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    
    # Read the frame
    ret, frame = cap.read()
    
    # Check if reading the frame was successful
    if not ret:
        print("Error reading the frame.")
        cap.release()
        return None
    
    # Create a circular mask
    h, w = frame.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, center, radius, (255, 255, 255), -1)
    
    # Apply the mask to the frame
    sub_image = cv2.bitwise_and(frame, frame, mask=mask)
    
    # Release the video
    cap.release()
    
    return sub_image, frame

video_path = 'Data_confidential/video_vision_perif.mp4'
frame_num = 10  # Frame number
sub_img = circular_subimage(video_path, radius, center, frame_num)[0]
frame = circular_subimage(video_path, radius, center, frame_num)[1]

# Display the sub-image
if sub_img is not None:
    cv2.imshow("Circular Sub-image", sub_img)
    cv2.imshow("Original Image", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Failed to generate the sub-image.")