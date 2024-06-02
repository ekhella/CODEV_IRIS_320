from Modules import np, cv2, os, gp, sys
from VideoDataAnalyzer import VideoDataAnalyzer
from VideoDirectoryTool import PathManager

class VideoFrameDisplay:
    def __init__(self, video_path, data_path):
        self.video_path = video_path
        self.data_analyzer = VideoDataAnalyzer(data_path)
        self.video_cap = cv2.VideoCapture(video_path)
        self.path_manager = PathManager(user=gp.getuser())
        self.frame_dir = self.path_manager.get_or_create_dir('SavedFrames')
        if not self.video_cap.isOpened():
            raise ValueError("Error opening video file")

    def display_frame_for_time(self, time_input):
        frame_number = self.data_analyzer.get_frame_number(time_input)
        if frame_number is None:
            print("Could not calculate frame number from time input.")
            return None
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.video_cap.read()
        if ret:
            frame_path = os.path.join(self.frame_dir, f"frame_at_{time_input}s.png")
            cv2.imwrite(frame_path, frame)
            cv2.imshow(f'Frame for Time: {time_input}s', frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            print(f"Frame saved at {frame_path}")
        else:
            print("Failed to retrieve the frame.")

    def release_resources(self):
        self.video_cap.release()
        cv2.destroyAllWindows()

video_path = "Data_confidential/video_arriere.mp4"
data_path = "videotreatment.txt"

video_display = VideoFrameDisplay(video_path, data_path)
time_input = int(input("Time :"))
video_display.display_frame_for_time(time_input)
video_display.release_resources()
