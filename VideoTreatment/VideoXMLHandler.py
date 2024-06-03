import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

class VideoXMLHandler:
    def __init__(self, xml_file):
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()

    @staticmethod
    def check_date_format(date_str):
        pattern = r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}:\d{3}$"
        return bool(re.match(pattern, date_str))

    @staticmethod
    def parse_datetime_with_milliseconds(date_str):
        """ Parse datetime string with milliseconds 'DD/MM/YY HH:MM:SS:XXX' """
        main_part, ms_part = date_str.rsplit(':', 1)
        dt = datetime.strptime(main_part, "%d/%m/%y %H:%M:%S")
        ms_delta = timedelta(milliseconds=int(ms_part))
        return dt + ms_delta

    def time_to_video(self, date_str):
        if not self.check_date_format(date_str):
            raise ValueError("Date format is incorrect. Use 'DD/MM/YY HH:MM:SS:XXX'.")

        given_date = self.parse_datetime_with_milliseconds(date_str)
        videos = []
        closest_date = None

        for section in self.root.findall(".//Section"):
            date_section_str = section.get('Date')
            if date_section_str:
                # XML dates are written without seconds and milliseconds
                date_section = datetime.strptime(date_section_str, "%d/%m/%y %H:%M")
                if date_section <= given_date:
                    if closest_date is None or date_section > closest_date:
                        closest_date = date_section
                        videos = [section.get('Video')]
                    elif date_section == closest_date:
                        videos.append(section.get('Video'))

        return videos

    def get_all_video_files(self):
        video_files = []
        for video in self.root.findall(".//Section"):
            video_file = video.get('Video')
            if video_file:
                video_files.append(video_file)
        return video_files

    def videos_in_time_interval(self, start_date_str, end_date_str):
        if not self.check_date_format(start_date_str) or not self.check_date_format(end_date_str):
            raise ValueError("Date formats are incorrect. Use 'DD/MM/YY HH:MM:SS:XXX'.")

        start_date = self.parse_datetime_with_milliseconds(start_date_str)
        end_date = self.parse_datetime_with_milliseconds(end_date_str)
        
        if start_date > end_date:
            raise ValueError("Start date must be earlier than the end date.")
        
        videos = []
        for section in self.root.findall(".//Section"):
            date_section_str = section.get('Date')
            if date_section_str:
                date_section = datetime.strptime(date_section_str, "%d/%m/%y %H:%M")
                
                if start_date <= date_section <= end_date:
                    video_file = section.get('Video')
                    if video_file:
                        videos.append(video_file)

        return videos
