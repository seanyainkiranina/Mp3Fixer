"""This module contains the Mp3Cache class, which is responsible for 
storing MP3 file information in memory.
It provides methods to set and retrieve metadata such as file name, full path,
artist, album, and title. The Mp3Cache class also includes a method to
remove non-ASCII characters from strings 
to ensure that file names and metadata are safe for use in file paths."""
import re


class Mp3Cache:
    """A simple in-memory cache for storing MP3 file information."""

    def __init__(self):
        """ "Initialize the MP3 cache."""
        self.file_name = None
        self.file_with_full_path = None
        self.artist = None
        self.album = None
        self.title = None

    def remove_non_ascii(self, text: str | None) -> str:
        """
        Remove all non-ASCII characters from the given string.
        ASCII range: 0 to 127.
        """
        if not isinstance(text, str):
            raise TypeError("Input must be a string.")

        # Using regex to keep only ASCII characters
        text = text.replace("'", "")  # Remove apostrophes
        return self.safe_path(re.sub(r"[^\x00-\x7F]+", "", text.replace("?", "")))

    def safe_path(self, path):
        """Replace characters that are not allowed in file paths with underscores."""
        return re.sub(r'[<>:"/\\|?*]', "_", path)

    def set_file_name(self, file_name):
        """ "Set the file name in the cache."""
        self.file_name = self.remove_non_ascii(file_name)

    def set_file_with_full_path(self, file_with_full_path):
        """ "Set the file with full path in the cache."""
        self.file_with_full_path = file_with_full_path

    def set_artist(self, artist):
        """ "Set the artist in the cache."""
        self.artist = self.remove_non_ascii(artist)

    def set_album(self, album):
        """ "Set the album in the cache."""
        self.album = self.remove_non_ascii(album)

    def set_title(self, title):
        """ "Set the title in the cache."""
        self.title = self.remove_non_ascii(title)
