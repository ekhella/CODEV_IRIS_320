import traceback
from Modules import os, traceback
from VideoProcessor import VideoProcessor
from VideoFrameDisplay import VideoFrameDisplay
from VideoXMLHandler import VideoXMLHandler

VIDEO_DIRECTORY = 'Data_confidential/'

def get_user_date():
    return input("Input your date at this format: DD/MM/YY HH:MM:SS OR DD/MM/YY HH:MM:SS.XXX \nEx: 23/10/18 16:01:32.234\n")

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

def list_videos(directory):
    """List all video files in the given directory."""
    return [file for file in os.listdir(directory) if file.endswith('.avi')]  # assuming the videos are .avi files

def process_video(video_path):
    """Process a single video."""
    try:
        video_processor = VideoProcessor(video_path)
        print(f"Processing Video: {os.path.basename(video_path)}")
        video_processor.process_video()
    except Exception as e:
        print(f"Error processing video {video_path}: {e}")
        traceback.print_exc()

def check_analyzed_videos():
    """Check and read the list of already analyzed videos."""
    try:
        with open('analyzed_videos.txt', 'r') as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        print("No previously analyzed videos file found. Creating new file.")
        return set()

def update_analyzed_videos(video_name):
    """Update the list of analyzed videos."""
    with open('analyzed_videos.txt', 'a') as file:
        file.write(video_name + '\n')

def process_videos(directory):
    """Process all videos in the specified directory."""
    videos = list_videos(directory)
    analyzed_videos = check_analyzed_videos()

    for video in videos:
        video_path = os.path.join(directory, video)
        if video not in analyzed_videos:
            process_video(video_path)
            update_analyzed_videos(video)
        else:
            response = input(f"{video} has already been analyzed. Do you want to analyze it again? [Y/N] ").strip().lower()
            if response == 'y':
                process_video(video_path)
            else:
                print(f"Skipping analysis of {video}.")
                continue  # Skip to the next video

def display_video():
    """Display a specific frame from the video."""
    xml_handler = VideoXMLHandler('Data_confidential/videoxml.xml')
    user_date = get_user_date()
    videos = xml_handler.time_to_video(user_date)
    for video in videos:
        video_path = os.path.join(VIDEO_DIRECTORY, video)
        user_time = user_date.split(' ')[1]
        base_name = os.path.basename(video_path)
        file_name_without_extension, _ = os.path.splitext(base_name)
        video_name = file_name_without_extension
        data_path= get_data_path(video_name)
        try:
            video_display = VideoFrameDisplay(video_path, data_path, video_name)
            video_display.display_frame_for_time(user_time)
            video_display.release_resources()
            print(f"Displayed and saved frame for {user_time} successfully.")
        except Exception as e:
            print(f"Error displaying video {video_path}: {e}")
            traceback.print_exc()


def main():
    P= input(" Do you want to process all videos ? [Y/N]")
    if P.lower() == 'y':
        process_videos(VIDEO_DIRECTORY)
    D= input(" Do you want to display a frame ? [Y/N]")
    if D.lower() == 'y':
        display_video()

if __name__ == "__main__":
    main()
