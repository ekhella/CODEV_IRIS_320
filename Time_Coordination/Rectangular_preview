#This part of the code is used to see what part of the "video_arriere" we are looking at when we get the information (marker, speed, date, hour...)
#This allowed us to define more precisely the zones we are analyzing

import cv2
import numpy as np

def rectangular_subimage(video_path, rectangle, frame_num):
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
    
    # Define rectangle coordinates and size
    x, y, width, height = rectangle
    
    # Create a rectangular mask
    h, w = frame.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(mask, (x, y), (x + width, y + height), (255, 255, 255), -1)
    
    # Apply the mask to the frame
    sub_image = cv2.bitwise_and(frame, frame, mask=mask)
    
    # Release the video
    cap.release()
    
    return sub_image, frame

# Example usage
video_path = 'Data_confidential/video_arriere.mp4'
frame_num = 10  # Frame number
rectangle_marker = (95, 0, 65, 16)  # Rectangle coordinates (x, y, width, height)
rectangle_speed = (0, 500, 30, 16)
rectangle_date = (456, 0, 93, 16)
rectangle_time = (557, 0, 83, 16)
sub_img = rectangular_subimage(video_path, rectangle_time, frame_num)[0]
frame = rectangular_subimage(video_path, rectangle_time, frame_num)[1]

# Display the sub-image
if sub_img is not None:
    cv2.imshow("Rectangular Sub-image", sub_img)
    cv2.imshow("Original Image", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Failed to generate the sub-image.")
