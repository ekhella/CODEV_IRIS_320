from Modules import os
from VideoConstructor import VideoProcessor
from VideoXMLHandler import VideoXMLHandler
from VideoFrameDisplay import VideoFrameDisplay

Video_Directory = 'Data_confidential/'

def get_user_date():
    return input("Input your date at this format: DD/MM/YY HH:MM:SS OR DD/MM/YY HH:MM:SS.XXX \nEx: 23/10/18 16:01:32.234\n")

def process_videos(videos, user_date):
    if not videos:
        print("No video files found for the given date. Insert videos in your directory, or check the date format.")
        return
    
    print("Video files containing the desired frame for the user are:")
    for video in videos:
        print(video)
        video_path = os.path.join(Video_Directory, video)
        process_video(video_path, user_date)

def process_video(video_path, user_time):
    try:
        video_processor = VideoProcessor(video_path)
        video_name = video_processor.video_name
        print(f"Processing Video: {video_name}")
        print(f"Total Frames: {video_processor.total_frames}")
        print(f"FPS: {video_processor.fps}")
        print(f"Frame Size: {video_processor.frame_dimensions}")
        video_processor.process_video()
        display_video(video_path, video_processor.data_path, video_name, user_time)
    except Exception as e:
        print(f"Error processing video {video_path}: {e}")

def display_video(video_path, data_path, video_name, user_time):
    try:
        video_display = VideoFrameDisplay(video_path, data_path, video_name)
        video_display.display_frame_for_time(user_time)
        video_display.release_resources()
    except Exception as e:
        print(f"Error displaying video {video_path}: {e}")

def main():
    xml_handler = VideoXMLHandler('Data_confidential/videoxml.xml')
    user_date = get_user_date()
    try:
        videos = xml_handler.time_to_video(user_date)
        process_videos(videos, user_date)
    except Exception as e:
        print(f"Error finding videos for the date {user_date}: {e}")

if __name__ == "__main__":
    main()
