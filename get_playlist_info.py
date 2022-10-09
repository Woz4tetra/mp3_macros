import os
import argparse
import youtube_dl


def download_playlist_names(url, output_dir):
    download = False
    ydl_opts = {
        # 'dump_single_json': True,
        'extract_flat': True,
        # 'outtmpl'         : "playlist-info.json"
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ie_result = ydl.extract_info(url, download)

    out_file = output_dir + "/urls.txt"
    with open(out_file, 'w') as file:
        for entry in ie_result["entries"]:
            entry_url = entry["url"]
            entry_title = entry["title"]
            file.write(f"{entry_url}\t{entry_title}\n")

    print(f"URLs and titles written to {out_file}. Delete entries that you want EXCLUDED in your download. "
          f"Then run download.py <path to urls.txt>")


def main():
    parser = argparse.ArgumentParser(description="youtube_downloader")
    parser.add_argument("url",
                        help="URL to download from")
    parser.add_argument("--output", default="playlist", help="Output directory")

    args = parser.parse_args()

    url = args.url
    playlist_dir = args.output

    if not os.path.isdir(playlist_dir):
        os.makedirs(playlist_dir)

    download_playlist_names(url, playlist_dir)


if __name__ == '__main__':
    main()
