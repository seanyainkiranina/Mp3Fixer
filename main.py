import os
import shutil
import re
import requests
from tinytag import TinyTag
from mutagen.id3 import ID3, TPE1, ID3NoHeaderError
from mutagen.easyid3 import EasyID3


def set_artist_tag(path, artist_name):
    """set artist tag on an mp3 file"""
    try:
        audiofile = EasyID3(path)
    except ID3NoHeaderError:
        # create basic ID3 with TPE1 then reopen as EasyID3
        id3 = ID3()
        id3.add(TPE1(encoding=3, text=artist_name))
        id3.save(path)
    audiofile = EasyID3(path)
    audiofile["artist"] = artist_name
    print(f"Setting artist tag to: {artist_name} for file: {path}")
    audiofile.save()


def get_album_info(album_name, limit=1):
    """
    Fetch album information from MusicBrainz API.

    :param album_name: Name of the album to search for.
    :param limit: Number of results to return (default 1).
    :return: List of album details.
    """
    if not album_name or not isinstance(album_name, str):
        raise ValueError("Album name must be a non-empty string.")

    url = "https://musicbrainz.org/ws/2/release/"
    params = {"query": f'release:"{album_name}"', "fmt": "json", "limit": limit}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "releases" not in data or not data["releases"]:
            return []

        albums_return = []
        for release in data["releases"]:
            albums_return.append(
                {
                    "title": release.get("title"),
                    "artist": (
                        release["artist-credit"][0]["name"]
                        if "artist-credit" in release
                        else "Unknown"
                    ),
                    "date": release.get("date", "Unknown"),
                    "country": release.get("country", "Unknown"),
                    "id": release.get("id"),
                }
            )
        return albums_return

    except requests.exceptions.RequestException as e:
        print(f"Error fetching album info: {e}")
        return []


def remove_non_ascii(text: str | None) -> str:
    """
    Remove all non-ASCII characters from the given string.
    ASCII range: 0 to 127.
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    # Using regex to keep only ASCII characters
    text = text.replace("'", "")  # Remove apostrophes
    return re.sub(r"[^\x00-\x7F]+", "", text.replace("?", ""))


def get_contributing_artist(mp3_path):
    """
    Reads the 'Contributing Artist' (TPE1 or TPE2) from an MP3 file.
    Returns None if not found.
    """
    if not os.path.isfile(mp3_path):
        raise FileNotFoundError(f"File not found: {mp3_path}")

    try:
        tags = ID3(mp3_path)
    except ID3NoHeaderError:
        return None  # No ID3 tags present

    # TPE1 = Lead performer / Soloist
    # TPE2 = Band / Orchestra / Accompaniment
    aa = None
    if "TPE1" in tags:
        aa = tags["TPE1"].text[0]
    elif "TPE2" in tags:
        aa = tags["TPE2"].text[0]

    if aa is None:
        try:
            audio_file = EasyID3(mp3_path)
            aa = audio_file.get("albumartist", None)
            if aa is not None:
                aa = aa[0]
        except (ID3NoHeaderError, KeyError):
            return None

    return aa


def create_directory(path):
    """
    Creates a directory if it does not exist.

    Args:
        path (str): The directory path to create.
    """
    try:
        # os.makedirs with exist_ok=True will not raise an error if the folder exists
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory '{path}': {e}")


# Example usage
if __name__ == "__main__":
    PATH_DIR = "C:\\Users\\seany\\Music"
    # create_directory(folder_path)
    files = os.listdir(PATH_DIR)
    madeDirs = {}
    NEW_DIR = PATH_DIR
    EXT = ""
    # Get album names from files
    albumNames = {}
    artistNames = {}
    for file in files:
        EXT = file[file.rfind(".") + 1 :]
        if EXT != "mp3":
            continue
        targetFile = PATH_DIR + "\\" + file
        tagg: TinyTag = TinyTag.get(targetFile)
        if tagg.album is not None and tagg.album not in albumNames:
            albumNames[tagg.album] = file
        if tagg.album is None:
            print(f"No album tag found for file: {file}")
            continue
        if tagg.albumartist is not None and file not in artistNames:
            artistNames[file] = tagg.albumartist
            artistNames[tagg.album] = tagg.albumartist
            print(f"Found artist tag: {tagg.albumartist} for file: {file}")
        for f in albumNames:
            if f not in artistNames:
                albums = get_album_info(f, limit=1)
                if albums:
                    print(
                        f"Setting artist tag to: {albums[0]['artist']} for file: {file}"
                    )
                    artistNames[file] = albums[0]["artist"]
                    artistNames[f] = albums[0]["artist"]
            else:
                artistNames[file] = artistNames[f]

    for file in files:
        ext = file[file.rfind(".") + 1 :]
        if ext != "mp3":
            continue
        targetFile = PATH_DIR + "\\" + file
        print(f"Processing file: {targetFile}")
        tag: TinyTag = TinyTag.get(targetFile)
        if tag.album is None:
            print(f"No album tag found for file: {file}")
            continue
        artist = tag.albumartist
        if artist is None:
            artist = get_contributing_artist(targetFile)
        if artist is not None and file not in artistNames:
            artistNames[file] = artist

        if artist is None and file in artistNames:
            artist = artistNames[file]
            set_artist_tag(targetFile, artist)

        if artist is None:
            print(f"No artist found for file: {file}")
            continue

        print(f"Artist: {artist}")
        newdirArtist = NEW_DIR + "\\" + artist
        create_directory(newdirArtist)
        if tag.album is None:
            print(f"No album tag found for file: {file}")
            continue
        newdirArtistAlbum = newdirArtist + "\\" + tag.album + "\\"
        newdirArtistFile = (
            newdirArtist
            + "\\"
            + tag.album
            + "\\"
            + remove_non_ascii(tag.title)
            + "."
            + ext
        )
        create_directory(newdirArtistAlbum)
        shutil.copy(targetFile, newdirArtistFile)
        madeDirs[tag.album] = newdirArtistAlbum
        print(f"Copied file to: {newdirArtistFile}")
