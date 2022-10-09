import os
import argparse


def prep_downloaded(output_dir, clear_file):
    url_file = output_dir + "/urls.txt"
    with open(url_file) as file:
        contents = file.read()
    skip_list = ""
    for line in contents.splitlines():
        line_index = line.index("\t")
        url = line[:line_index]
        # title = line[line_index:]

        skip_list += f"youtube {url}\n"

    with open("./downloaded.txt", 'w' if clear_file else 'a') as file:
        file.write(skip_list)


def main():
    """
    Take contents of urls.txt, format it to youtube-dl's liking and append it
    to downloaded.txt
    """
    parser = argparse.ArgumentParser(description="youtube_downloader")
    parser.add_argument("--output", default="playlist", help="Output directory")
    parser.add_argument("--clear", action="store_true", help="Clear downloaded.txt before writing to it")

    args = parser.parse_args()

    playlist_dir = args.output

    if not os.path.isdir(playlist_dir):
        os.makedirs(playlist_dir)

    prep_downloaded(playlist_dir, args.clear)


if __name__ == '__main__':
    main()
