from Modules import t, os
from VideoConstructor import VideoProcessor

Video_Path = 'Data_confidential/video_arriere.mp4'

def main():
    # Initialize the Video object
    video_processor = VideoProcessor(Video_Path)
    video_processor.process_video()
    print(f"Total Frames: {video_processor.total_frames}")
    print(f"FPS: {video_processor.fps}")
    print(f"Frame Size: {video_processor.frame_dimensions}")

if __name__ == "__main__":
    main()
