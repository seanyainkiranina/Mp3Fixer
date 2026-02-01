import os
import tkinter as tk
from tkinter import filedialog
import shutil
import re
import requests
from tinytag import TinyTag
from mutagen.id3 import ID3, TPE1, ID3NoHeaderError
from mutagen.easyid3 import EasyID3

taxt_box = None  # Global text box for logging

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


def read_directory(path_dir):
    """Read mp3 files from a directory and organize them by artist and album."""
    #    PATH_DIR = "C:\\Users\\seany\\Music"
    # create_directory(folder_path)
    text_box.insert("end",f"start : {path_dir}\n")
    files = os.listdir(path_dir)
    made_dirs = {}
    new_dir = path_dir
    ext = ""
    # Get album names from files
    album_names = {}
    artist_names = {}
    for file in files:
        ext = file[file.rfind(".") + 1 :]
        if ext != "mp3":
            continue
        target_file = path_dir + "\\" + file
        tagg: TinyTag = TinyTag.get(target_file)
        if tagg.album is not None and tagg.album not in album_names:
            album_names[tagg.album] = file
        if tagg.album is None:
            text_box.insert("end",f"No album tag found for file: {file}")
            continue
        if tagg.albumartist is not None and file not in artist_names:
            artist_names[file] = tagg.albumartist
            artist_names[tagg.album] = tagg.albumartist
            text_box.insert("end",f"Found artist tag: {tagg.albumartist} for file: {file}")
        for f in album_names:
            if f not in artist_names:
                albums = get_album_info(f, limit=1)
                if albums:
                    text_box.insert("end",f"Setting artist tag to: {albums[0]['artist']} for file: {file}")
                    artist_names[file] = albums[0]["artist"]
                    artist_names[f] = albums[0]["artist"]
            else:
                artist_names[file] = artist_names[f]
                artist_names[file] = artist_names[f]

    for file in files:
        ext = file[file.rfind(".") + 1 :]
        if ext != "mp3":
            continue
        target_file = path_dir + "\\" + file
        text_box.insert("end",f"Processing file: {target_file}")
        tag: TinyTag = TinyTag.get(target_file)
        if tag.album is None:
            text_box.insert("end",f"No album tag found for file: {file}")
            text_box.insert("end",f"Processing file: {target_file}")
            continue
        artist = tag.albumartist
        if artist is None:
            artist = get_contributing_artist(target_file)
        if artist is not None and file not in artist_names:
            artist_names[file] = artist
            text_box.insert("end",f"Artist set to : {artist}")

        if artist is None and file in artist_names:
            artist = artist_names[file]
            set_artist_tag(target_file, artist)
            text_box.insert("end",f"setting {target_file} set to : {artist}")

        if artist is None:
            print(f"No artist found for file: {file}")
            text_box.insert("end",f"No artist found for file: {file}")
            continue

        text_box.insert("end",f"Artist: {artist}")
        newdir_artist = new_dir + "\\" + artist
        create_directory(newdir_artist)
        if tag.album is None:
            text_box.insert("end",f"No album tag found for file: {file}")
            continue
        newdir_artist_album = newdir_artist + "\\" + tag.album + "\\"
        newdir_artist_file = (
            newdir_artist
            + "\\"
            + tag.album
            + "\\"
            + remove_non_ascii(tag.title)
            + "."
            + ext
        )
        create_directory(newdir_artist_album)
        shutil.copy(target_file, newdir_artist_file)
        made_dirs[tag.album] = newdir_artist_album
        text_box.insert("end",f"Copied file to: {newdir_artist_file}")


def browse_folder():
    """Open a dialog to browse and select a folder."""
    folder_path = filedialog.askdirectory()
    print(f"Selected Folder: {folder_path}")
    return folder_path


# Example usage
if __name__ == "__main__":
   # root.withdraw()  # Hide the root window
    root = tk.Tk()
    root.geometry("800x600")  
    root.title("MP3 Browser")

    text_box = tk.Text(root, height=50, width=50)
    text_box.pack(padx=10, pady=10)

    directory = filedialog.askdirectory()
    if os.path.isdir(directory):
        text_box.insert("end",f"Running on: {directory}\n")
        read_directory(directory)
    print(directory)
    root.mainloop()
