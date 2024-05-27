#The goal of this page is to get to the right video according to a certain time given by the user,
#in order to analyse it after, to access to the exact wanted frame
#We are using the XML file to search for the right video

#Pour préciser le fichier xml : le fichier contient plusieurs LIGNES, qui contiennent plusieurs VOIES,
#qui contiennent plusieurs SECTIONS, qui contiennent chacunes au minimum 2 vidéos (M1 et M2)

import re
import xml.etree.ElementTree as ET
from datetime import datetime

# Fonction pour vérifier le format de la date
def check_date_format(date_str):
    pattern = r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}$"
    return bool(re.match(pattern, date_str))

# Charger et analyser le fichier XML
tree = ET.parse('Data_confidential/videoxml.xml')
root = tree.getroot()

# Fonction pour parcourir et trouver les fichiers vidéo correspondant à une date ou la date la plus proche (inférieure ou égale)
def time_to_video(root, date_str):
    if not check_date_format(date_str):
        raise ValueError("La date n'est pas au bon format. Utilisez 'JJ/MM/AA HH:MM'.")

    # Convertir la date donnée en objet datetime pour comparaison
    date_donnee = datetime.strptime(date_str, "%d/%m/%y %H:%M")
    videos = []
    closest_date = None

    for section in root.findall(".//Section"):
        date_section_str = section.get('Date')
        if date_section_str is not None:  # Vérifier si l'attribut 'Date' existe
            date_section = datetime.strptime(date_section_str, "%d/%m/%y %H:%M")

            if date_section <= date_donnee:
                # Si nous trouvons une date plus proche de la date donnée, nous mettons à jour
                if closest_date is None or date_section > closest_date:
                    closest_date = date_section
                    videos = [section.get('Video')]
                elif date_section == closest_date:
                    videos.append(section.get('Video'))

    return videos

# Exemple d'utilisation
date_utilisateur = "23/10/18 15:34"
videos = time_to_video(root, date_utilisateur)

if videos:
    print(f"Les fichiers vidéo contenant la frame souhaitée par l'utilisateur sont :")
    for video in videos:
        print(video)
else:
    print(f"Aucun fichier vidéo trouvé pour la date {date_utilisateur}.")



#Now, if we want to access all the videos, to analyze them all

def get_all_video_files(root):
    video_files = []
    for video in root.findall(".//Section"):
        video_file = video.get('Video')
        if video_file:
            video_files.append(video_file)
    return video_files

#Vérification du bon fonctionnement de get_all_video_files
all_videos = get_all_video_files(root)
#print(f"Tous les fichiers vidéo contenus dans le fichier XML sont :")
#for video in all_videos:
#    print(video)

#Now, if we want to access some videos between an interval of time

def videos_in_time_interval(root, start_date_str, end_date_str):
    if not check_date_format(start_date_str) or not check_date_format(end_date_str):
        raise ValueError("Les dates ne sont pas au bon format. Utilisez 'JJ/MM/AA HH:MM'.")

    # Convertir les dates données en objets datetime pour comparaison
    start_date = datetime.strptime(start_date_str, "%d/%m/%y %H:%M")
    end_date = datetime.strptime(end_date_str, "%d/%m/%y %H:%M")
    
    if start_date > end_date:
        raise ValueError("La date de début doit être antérieure à la date de fin.")
    
    videos = []

    for section in root.findall(".//Section"):
        date_section_str = section.get('Date')
        if date_section_str is not None:
            date_section = datetime.strptime(date_section_str, "%d/%m/%y %H:%M")
            
            if start_date <= date_section <= end_date:
                video_file = section.get('Video')
                if video_file:
                    videos.append(video_file)

    return videos

#Vérification du bon fonctionnement de videos_in_time_interval

start_date = "23/10/18 08:10"
end_date = "23/10/18 08:40"
videos_interval = videos_in_time_interval(root, start_date, end_date)

print(f"Les fichiers vidéo compris entre {start_date} et {end_date} sont :")
for video in videos_interval:
    print(video)