# make sure title regex matches in pattern.py before running this script
import os
import re
import argparse
import warnings
import traceback

from eyed3 import mp3
from shutil import copyfile
import youtube_dl

import multiprocessing
from multiprocessing import Pool

from pattern import set_meta_data


def convert(path):
    global num_tracks

    print(f"Starting conversion for {path}")
    try:
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)

        pattern = r"(\d*) (.*)\.mp3"
        match = re.search(pattern, filename)
        if match is None:
            warnings.warn(f"{filename} does not match supplied regex: {pattern}")
            return

        track_num = int(match.group(1))
        title = match.group(2)

        mp3_file = mp3.Mp3AudioFile(path)
        mp3_file.initTag()

        new_name = set_meta_data(title, mp3_file.tag)

        mp3_file.tag.track_num = (track_num, num_tracks)
        mp3_file.tag.save()

        new_path = os.path.join(dirname, new_name)
        if os.path.isfile(new_path):
            print("Removing", new_path)
            os.remove(new_path)

        mp3_file.rename(new_name)
        print(f"{path} -> {new_name} done")
    except BaseException as e:
        traceback.print_tb(e.__traceback__)
        print(e)
        print(f"{path} failed!")


num_tracks = 0


def get_options(output_dir):
    autonumber_start = 0
    for name in os.listdir(output_dir):
        if not name.endswith(".mp3"):
            continue
        match = re.search(r"(\d{5})", name)
        if match:
            autonumber = int(match.group(1))
            if autonumber > autonumber_start:
                autonumber_start = autonumber

    autonumber_start += 1
    ydl_opts = {
        "download_archive": "downloaded.txt",
        # "nooverwrites": True,
        # "audioformat": "mp3",
        # "extractaudio": True,
        'format'          : 'bestaudio/best',
        'postprocessors'  : [{
            'key'             : 'FFmpegExtractAudio',
            'preferredcodec'  : 'mp3',
            'preferredquality': '192',
        }],
        "autonumber_start": autonumber_start,
        "outtmpl"         : f"{output_dir}/%(autonumber)s %(title)s.%(ext)s",

    }
    return ydl_opts


def download(url, output_dir):
    # ydl_opts = get_options(output_dir)
    # ydl = youtube_dl.YoutubeDL(ydl_opts)
    # ydl.download([url])
    command = "cd {} && yt-dlp " \
              "--download-archive downloaded.txt " \
              "--no-post-overwrites -ciwx " \
              "--extract-audio " \
              "--audio-format mp3 " \
              "-o \"%(autonumber)s %(title)s.%(ext)s\" {}".format(output_dir, url)
    os.system(command)


def download_from_file(input_file, output_dir):
    ydl_opts = get_options(output_dir)

    with open(input_file) as file:
        contents = file.read()
    urls = []
    for line in contents.splitlines():
        video_id = line.split("\t")[0]

        url = f"https://www.youtube.com/watch?v={video_id}"
        urls.append(url)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)


def download_with_retries(url, output_dir):
    success = False
    attempts = 0
    while not success:
        try:
            if os.path.isfile(url):
                download_from_file(url, output_dir)
            else:
                download(url, output_dir)
            success = True
        except youtube_dl.utils.DownloadError as e:
            warnings.warn(str(e))
        attempts += 1
        if attempts > 25:
            print("Reached 25 attempts, exiting.")
            return


def main():
    global num_tracks

    num_cpus = multiprocessing.cpu_count()

    parser = argparse.ArgumentParser(description="youtube_downloader")
    parser.add_argument("url",
                        help="URL to download from or local list of files")
    parser.add_argument("--output", default="playlist", help="Output directory")
    parser.add_argument("--download-only", action="store_true", help="Download files and do nothing")
    parser.add_argument("--convert-only", action="store_true",
                        help="Take already downloaded files and convert them again")
    parser.add_argument("--processes", default=num_cpus,
                        help="Specify number of simulatenous processes to run while converting mp3's")

    args = parser.parse_args()

    url = args.url
    playlist_dir = args.output
    converted_dir = os.path.join(playlist_dir, "converted_files")

    if not os.path.isdir(playlist_dir):
        os.makedirs(playlist_dir)

    if not os.path.isdir(converted_dir):
        os.makedirs(converted_dir)

    should_download = True
    should_convert = True
    if args.download_only:
        should_convert = False
    if args.convert_only:
        should_download = False

    if should_download:
        download_with_retries(url, playlist_dir)

    if should_convert:
        playlist = os.listdir(playlist_dir)
        song_list = []
        for filename in playlist:
            if filename.endswith(".mp3"):
                original_path = os.path.join(playlist_dir, filename)
                converted_path = os.path.join(converted_dir, filename)
                copyfile(original_path, converted_path)

                song_list.append(converted_path)

        num_tracks = len(song_list)
        print(num_tracks)

        if args.processes == 1:
            for song_path in song_list:
                convert(song_path)
        elif args.processes > 1:
            pool = Pool(processes=args.processes)
            result = pool.map_async(convert, iter(song_list))
            try:
                result.get()
            except KeyboardInterrupt:
                print()
        else:
            raise ValueError("Can't have less than 1 process!")


if __name__ == '__main__':
    main()
