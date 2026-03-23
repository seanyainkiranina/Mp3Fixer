"""  This module contains the Mp3Runner class, which is responsible for running 
the MP3 organization process. It provides a GUI for browsing folders and
 organizing MP3 files based on their metadata. The class uses the Mp3Engine to extract 
 metadata and organize files accordingly."""

import os
import tkinter as tk
from tkinter import filedialog
import shutil
from mp3engine import Mp3Engine


class Mp3Runner:
    """Class to run the MP3 organization process."""

    def __init__(self):
        """Initialize the Mp3Runner class."""
        self.mp3_engine = Mp3Engine()
        self.init_gui()

    def create_directory(self, path):
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

    def init_gui(self):
        """Initialize the GUI components."""
        root = tk.Tk()
        root.geometry("800x600")
        root.title("MP3 Browser")

        self.text_box = tk.Text(root, height=50, width=90)
        self.text_box.pack(padx=10, pady=10)

    def browse_folder(self):
        """Open a dialog to browse and select a folder."""
        folder_path = filedialog.askdirectory()
        print(f"Selected Folder: {folder_path}")
        return folder_path

    def read_directory(self, path_dir):
        """Read mp3 files from a directory and organize them by artist and album."""
        self.text_box.insert("end", f"start : {path_dir}\n")
        files = os.listdir(path_dir)
        for file in files:
            ext = file[file.rfind(".") + 1 :]
            if ext != "mp3":
                continue

            target_file = os.path.join(path_dir, file)
            album_artist = self.mp3_engine.get_file_info(target_file)
            if album_artist is None:
                self.text_box.insert(
                    "end", f"Skipping file (missing metadata): {target_file}\n"
                )
                continue
            self.mp3_engine.album_cache.cache.insert(target_file, file)
            album_name = self.mp3_engine.album_cache.album_cache_album_names_search(
                target_file
            )
            album_artist = self.mp3_engine.album_cache.album_cache_album_artists_search(
                target_file
            )
            title = self.mp3_engine.album_cache.album_cache_files_song_names_search(
                target_file
            )

            if album_name is None or album_artist is None or title is None:
                self.text_box.insert(
                    "end",
                    f"Skipping file (missing metadata): {target_file}\n",
                )
                continue

            self.mp3_engine.get_album_info(
                target_file,
                album_name,
            )
            self.text_box.insert("end", f"Processed file: {target_file}\n")
            self.text_box.insert("end", f"Artist: {album_artist}\n")
            self.text_box.insert(
                "end",
                f"Album: {album_name}\n",
            )
            self.text_box.insert(
                "end",
                f"Title: {title}\n",
            )
            self.text_box.insert(
                "end",
                f"Album Artist: {album_artist}\n",
            )
            self.create_directory(
                os.path.join(
                    path_dir,
                    album_artist,
                    album_name,
                )
            )
            shutil.copy(
                target_file,
                os.path.join(path_dir, album_artist, album_name, title, ".mp3"),
            )
