import os
import re
import ffmpeg
from eyed3 import mp3

def get_segment(l, index, default=0):
    if index >= len(l):
        return default
    else:
        return int(l[index])

def parse_table(path):
    table = []
    with open(path) as file:
        for line in file.readlines():
            time_str, name = line.split(" - ")
            match = re.search(r"(\d*)\.\ (.*)", name)
            if not match:
                raise ValueError(f"Line didn't parse! {line}")
            name = match.group(2)
            time_split = time_str.split(":")
            hour = get_segment(time_split, 0)
            minute = get_segment(time_split, 1)
            second = get_segment(time_split, 2)
            millisecond = get_segment(time_split, 3)

            timestamp = int(hour * 3600 * 1000 + minute * 60 * 1000 + second * 1000 + millisecond)

            table.append((timestamp, name))
    return table

def get_table_segment(table):
    start_timestamp = 0
    stop_timestamp = 0
    for index in range(len(table) - 1):
        start_timestamp, name = table[index]
        stop_timestamp, _ = table[index + 1]
        yield index, start_timestamp, stop_timestamp, name
    start_timestamp, name = table[-1]
    stop_timestamp = None
    yield len(table) - 1, start_timestamp, stop_timestamp, name


def main():
    path = "/home/ben/Downloads/Splatoon 3 – Complete Original Soundtrack OST W_ Timestamps [2022] [k630b0Cc-JI].mp3"
    out_dir = "playlist"
    table = parse_table("table.txt")

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    
    in_file = mp3.Mp3AudioFile(path)
    duration = in_file.info.time_secs
    for track_num, start_timestamp, stop_timestamp, name in get_table_segment(table):
        if stop_timestamp is None:
            stop_timestamp = duration
        duration_s = (stop_timestamp - start_timestamp) / 1000.0
        out_path = os.path.join(out_dir, name + ".mp3")
        with open(out_path, "w+b") as file:
            ffmpeg_cmd = (
                ffmpeg
                .input(path, ss=start_timestamp / 1000, t=duration_s)
                .output(file.name, acodec='copy')
                .overwrite_output()
                .global_args('-loglevel', 'error')
            )
            ffmpeg_cmd.run()
        
        mp3_file = mp3.Mp3AudioFile(out_path)
        mp3_file.initTag()

        mp3_file.tag.album = "Splatune 3"
        mp3_file.tag.title = name

        mp3_file.tag.track_num = (track_num, len(table))
        mp3_file.tag.save()

        print(out_path)

main()
