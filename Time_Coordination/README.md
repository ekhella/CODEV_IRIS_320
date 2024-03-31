# Projet-CODEV
Cet algorithme a été développé dans le cadre du projet CODEV de l'IMT Atlantique.

## Auteurs
Les auteurs de ce projet sont les suivants :
- KHELLA Eric
- HUBERT Baptiste
- GATARD Antoine

## Objectif
L'objectif est de ce projet est de pouvoir effectuer des mesures par analyse vidéo.  
Les mesures en question sont les suivantes : 

## Comment l'utiliser  
Il faut avoir intégrer à l'environnement les modules numpy, Opencv, pymediainfo et csv.  
Lorsque on exécute le programme dans la console de l'IDE un dosssier est créé sur le bureau de l'ordinateur dans lequel il faut glisser la vidéo à étudier (le programme accepte les vidéos au format mp4 ou mov les fichiers qui ne sont pas sous ses formats seront déplacés vers le bureau).
Pendant le traitement des informations sont transmises à l'utilisateur par le biais de la console.
À l'issue du traitement de la vidéo les résultats sont stockés dans un dossier sur le bureau. Il est possible de changer l'emplacement des dossiers utilisés dans le dossier Base.py.


## Principe de fonctionnement 

La video est dans un premier temps décomposée en un ensemble de frames, puis on traite chacune de ces frames les unes après les autres.
