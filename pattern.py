import re
import warnings
from eyed3 import id3

PATTERNS = [r".* - \[.*\](.*)"]
ALBUM = u"Splatune"
GENRE = u""
ARTIST = u""


def set_meta_data(title, tag: id3.Tag):
    tag.album = ALBUM

    match = None
    for pattern in PATTERNS:
        pattern = pattern.replace(":", " -")
        match = re.match(pattern, title)
        if match is not None:
            break
    if match is None:
        warnings.warn(f"No match for {title}")
        tag.title = title.strip()
    else:
        tag.title = match.group(1).strip()
        # tag.disc_num = (int(match.group(1)), 2)
    tag.genre = GENRE
    # tag.album_artist = u""
    tag.artist = ARTIST

    return tag.title
