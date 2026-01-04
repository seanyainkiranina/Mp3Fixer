import os
import shutil
import re
import requests
from tinytag import TinyTag
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.easyid3 import EasyID3


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

        albums = []
        for release in data["releases"]:
            albums.append(
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
        return albums

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
    a = None
    if "TPE1" in tags:
        a = tags["TPE1"].text[0]
    elif "TPE2" in tags:
        a = tags["TPE2"].text[0]

    if a is None:
        try:
            audio = EasyID3(mp3_path)
            a = audio.get("artist", ["Unknown Artist"])
            if a is not None:
                a = a[0]
        except (ID3NoHeaderError, KeyError):
            return None

    return a


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
    PATH_DIR = "C:\\Users\\seany\\Music\\Tmp"
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
        if EXT == "mp3":
            targetFile = PATH_DIR + "\\" + file
            tagg: TinyTag = TinyTag.get(targetFile)
            if tagg.album is not None:
                albumNames[tagg.album] = file
    for f in albumNames:
        albums = get_album_info(f, limit=1)
        if albums:
            artistNames[albumNames[tagg.album]] = albums[0]["artist"]

    for file in files:
        ext = file[file.rfind(".") + 1 :]
        if ext == "mp3":
            targetFile = PATH_DIR + "\\" + file
            print(f"Processing file: {targetFile}")
            tag: TinyTag = TinyTag.get(targetFile)
            artist = get_contributing_artist(targetFile)
            if artist is None and file in artistNames:
                artist = artistNames[file]
            print(f"Artist: {artist}")
            if artist is not None:
                newdirArtist = NEW_DIR + "\\" + artist
                create_directory(newdirArtist)
                if tag.album is not None:
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
            else:
                print(f"No artist tag found for file: {file}")
