from Modules import t, os
from MainConstructor import Video

# Assuming the Video class is already defined as per your earlier message

def main():
    # Initialize the Video object
    video = Video()

    # Since video_treatment is called inside __init__, your frames, frame number, fps, and frame size are already set
    # You can access these attributes directly now
    print(f"Total Frames: {video.Frame_number}")
    print(f"FPS: {video.fps}")
    print(f"Frame Size: {video.frame_size}")

    # If you have additional methods in your Video class to process or display video frames, call them here
    # For example, video.display_frames() or any other method you've defined for processing

if __name__ == "__main__":
    main()
