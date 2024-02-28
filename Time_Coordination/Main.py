from Modules import t, os
from MainConstructor import Video


def main():
    # Initialize the Video object
    video = Video()
    print(f"Total Frames: {video.Frame_number}")
    print(f"FPS: {video.fps}")
    print(f"Frame Size: {video.frame_dimensions}")

if __name__ == "__main__":
    main()
