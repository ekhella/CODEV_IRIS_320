from Modules import os
from VideoConstructor import VideoProcessor
from VideoXMLHandler import VideoXMLHandler
from VideoFrameDisplay import VideoFrameDisplay
import traceback

Video_Directory = 'Data_confidential/'

def get_user_date():
    return input("Input your date at this format: DD/MM/YY HH:MM:SS OR DD/MM/YY HH:MM:SS.XXX \nEx: 23/10/18 16:01:32.234\n")

def process_videos(videos, user_date):
    analyzed_videos = set()
    
    try:
        with open('analyzed_videos.txt', 'r') as file:
            analyzed_videos = set(file.read().splitlines())
    except FileNotFoundError:
        print("No previously analyzed videos file found. Creating new file.")

    if not videos:
        print("No video files found for the given date. Insert videos in your directory, or check the date format.")
        return
    
    print("Video files containing the desired frame for the user are:")
    with open('analyzed_videos.txt', 'a') as file: 
        print(videos)
        for video in videos:
            video_path = os.path.join(Video_Directory, video)
            user_time = user_date.split(' ')[1]
            video_processor = VideoProcessor(video_path)
            video_name = video_processor.video_name
            data_path= get_data_path(video_name)
            if video not in analyzed_videos:
                process_video(video_path)
                file.write(video + '\n')  # Log the newly analyzed video
                print(f"{video} has been analyzed and logged.")
            else:
                print(f"{video} has already been analyzed. Do you want to analyze it again ? [Y/N]")
                response = input().lower()
                if response == 'y':
                    process_video(video_path)
            display_video(video_path, data_path , video_name, user_time)
            print(f"{video} frame displayed.")

def get_data_path(video_name):
    try:
        with open(f'{video_name}.csv', 'r') as file:
            return f'{video_name}.csv'
    except FileNotFoundError:
        try:
            with open(f'{video_name}.txt', 'r') as file:
                return f'{video_name}.txt'
        except FileNotFoundError:
            print(f"No data file found for {video_name}.")
            raise FileNotFoundError(f"No data file available for {video_name} in .txt or .csv format.")


def process_video(video_path):
    try:
        video_processor = VideoProcessor(video_path)
        video_name = video_processor.video_name
        print(f"Processing Video: {video_name}")
        print(f"Total Frames: {video_processor.total_frames}")
        print(f"FPS: {video_processor.fps}")
        print(f"Frame Size: {video_processor.frame_dimensions}")
        video_processor.process_video()
    except Exception as e:
        print(f"Error processing video {video_path}: {e}")
        traceback.print_exc()

def display_video(video_path, data_path, video_name, user_time):
    try:
        video_display = VideoFrameDisplay(video_path, data_path, video_name)
        video_display.display_frame_for_time(user_time)
        video_display.release_resources()
        print(f"Displayed and saved frame for {user_time} successfully.")
    except Exception as e:
        print(f"Error displaying video {video_path}: {e}")
        traceback.print_exc()

def main():
    xml_handler = VideoXMLHandler('Data_confidential/videoxml.xml')
    user_date = get_user_date()
    try:
        videos = xml_handler.time_to_video(user_date)
        process_videos(videos, user_date)
    except Exception as e:
        print(f"Error finding videos for the date {user_date}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
