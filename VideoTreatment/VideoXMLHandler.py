import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

class VideoXMLHandler:
    def __init__(self, xml_file):
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()

    @staticmethod
    def check_date_format(date_str):
        # Pattern to check input format with optional fractional seconds
        pattern = r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?$"
        return bool(re.match(pattern, date_str))

    @staticmethod
    def parse_datetime(date_str):
        """ Parse datetime string potentially with fractional seconds 'DD/MM/YY HH:MM:SS.XXX' """
        # Detect if the datetime string includes fractional seconds
        if '.' in date_str:
            dt = datetime.strptime(date_str, "%d/%m/%y %H:%M:%S.%f")
        else:
            dt = datetime.strptime(date_str, "%d/%m/%y %H:%M:%S")
        return dt
    
    def get_seconds_from_time(time_str):
        """ Parse time string and return total seconds, handling optional milliseconds. """
        try:
            # Attempt to parse time with milliseconds
            dt = datetime.strptime(time_str, "%d/%m/%y %H:%M:%S.%f")
        except ValueError:
            # Fallback for time without milliseconds
            dt = datetime.strptime(time_str, "%d/%m/%y %H:%M:%S")
        
        # Convert time part to seconds
        total_seconds = dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1e6
        return total_seconds

    def time_to_video(self, date_str):
        if not self.check_date_format(date_str):
            raise ValueError("Date format is incorrect. Use 'DD/MM/YY HH:MM:SS' or 'DD/MM/YY HH:MM:SS.XXX'.")

        given_date = self.parse_datetime(date_str)
        videos = []
        closest_date = None

        for section in self.root.findall(".//Section"):
            date_section_str = section.get('Date')
            if date_section_str:
                # XML dates are stored without seconds and milliseconds
                date_section = datetime.strptime(date_section_str, "%d/%m/%y %H:%M")
                # Round down to the nearest minute to compare with user input
                date_section_full = datetime(date_section.year, date_section.month, date_section.day, date_section.hour, date_section.minute, 0)

                if date_section_full <= given_date:
                    if closest_date is None or date_section_full > closest_date:
                        closest_date = date_section_full
                        videos = [section.get('Video')]
                    elif date_section_full == closest_date:
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
            raise ValueError("Date formats are incorrect. Use 'DD/MM/YY HH:MM:SS' or 'DD/MM/YY HH:MM:SS.XXX'.")

        start_date = self.parse_datetime(start_date_str)
        end_date = self.parse_datetime(end_date_str)
        
        if start_date > end_date:
            raise ValueError("Start date must be earlier than the end date.")
        
        videos = []
        for section in self.root.findall(".//Section"):
            date_section_str = section.get('Date')
            if date_section_str:
                date_section = datetime.strptime(date_section_str, "%d/%m/%y %H:%M:%S")
                
                if start_date <= date_section <= end_date:
                    video_file = section.get('Video')
                    if video_file:
                        videos.append(video_file)

        return videos
