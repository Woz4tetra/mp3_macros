import os
import csv
from eyed3 import mp3

base_dir = "splatune/converted_files"
path = os.path.join(base_dir, "album.csv")

artwork = {
    "Turquoise October": "S_Band_Turquoise_October.jpg",
    "Chirpy Chips": "S_Band_Chirpy_Chips.jpg",
    "DJ Lee Fish": "S_Band_DJ_Lee_Fish.jpg",
    "Hightide Era": "S_Band_Hightide_Era.png",
    "Squid Sisters": "S_Band_Squid_Sisters.jpg",
    "DJ Octavio": "S_Band_DJ_Octavio.jpg",
    "Bob Dub": "S_Band_Bob_Dub.jpg",
    
}

with open(path) as file:
    reader = csv.reader(file)
    header = next(reader)
    for row in reader:
        filename = row[0]
        track_name = row[1].strip()
        artist = row[2]

        if len(track_name) == 0:
            track_name = filename.strip()
        if artist in artwork:
            album_art = os.path.join(base_dir, "artwork", artwork[artist])
        else:
            album_art = ""
        
        file_path = os.path.join(base_dir, filename + ".mp3")
        mp3_file = mp3.Mp3AudioFile(file_path)
        mp3_file.initTag()

        mp3_file.tag.artist = artist
        mp3_file.tag.album = artist + " Anthology"
        mp3_file.tag.title = track_name

        if len(album_art) > 0:
            with open(album_art, "rb") as cover_art:
                _, art_ext = os.path.splitext(album_art)
                art_ext = art_ext[1:]
                if art_ext == "jpg":
                    art_ext = "jpeg"
                mp3_file.tag.images.set(3, cover_art.read(), f"image/{art_ext}")

        mp3_file.tag.save()


