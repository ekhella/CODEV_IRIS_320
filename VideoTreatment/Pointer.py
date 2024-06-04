import cv2

class VideoMouseHandler:
    def __init__(self, video_path):
        self.video_path = video_path
        self.capture = cv2.VideoCapture(video_path)
        self.window_name = 'First Frame'

    def mouse_callback(self, event, x, y, flags, param):
        """
        Handles mouse click events and prints the position of the click.
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Position: (x={x}, y={y})")

    def open_video(self):
        """
        Opens the video and sets up the mouse callback for the first frame.
        """
        if not self.capture.isOpened():
            print("Error: Could not open video.")
            return

        ret, frame = self.capture.read()
        if ret:
            cv2.namedWindow(self.window_name)
            cv2.setMouseCallback(self.window_name, self.mouse_callback)
            cv2.imshow(self.window_name, frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Error: Could not read the first frame.")

        self.capture.release()

# Example usage:
video_path = 'Data_confidential/video_arriere.mp4'
video_handler = VideoMouseHandler(video_path)
video_handler.open_video()