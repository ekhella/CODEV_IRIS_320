from Modules import os
from VideoConstructor import VideoProcessor
from VideoXMLHandler import VideoXMLHandler
from VideoFrameDisplay import VideoFrameDisplay

Video_Directory = 'Data_confidential/'

def main():
    xml_handler = VideoXMLHandler('Data_confidential/videoxml.xml')
    user_date = input("Input your date at this format : DD/MM/YY HH:MM:SS:XXX \n Ex :23/10/18 15:34") ##CHECK
    videos = xml_handler.time_to_video(user_date)
    if videos:
        print("Video files containing the desired frame for the user are:")
        for video in videos:
            print(video)
    else:
        print("No video files found for the given date. Insert videos in your directory, or check the date format.")
    for video in videos : 
        video_path = os.path.join(Video_Directory, video)
        video_processor = VideoProcessor(video_path)
        print(f"Total Frames: {video_processor.total_frames}")
        print(f"FPS: {video_processor.fps}")
        print(f"Frame Size: {video_processor.frame_dimensions}")
        video_processor.process_video()
        data_path=video_processor.video_name()
        video_display = VideoFrameDisplay(video_path, data_path)

        time_input = int(input("Time in seconds :"))
        video_display.display_frame_for_time(time_input)
        video_display.release_resources()

if __name__ == "__main__":
    main()
