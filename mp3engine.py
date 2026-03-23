"""" This module contains the Mp3Engine class, which is responsible for managing MP3 
metadata operations and caching. It provides methods to read and write MP3 tags, 
fetch album information from the MusicBrainz API, and cache metadata for efficient access.
 The Mp3Engine class is used by the Mp3Runner to organize MP3 files based on their metadata.
"""
import os
import requests
from tinytag import TinyTag
from mutagen.id3 import ID3, TPE1, ID3NoHeaderError
from mutagen.easyid3 import EasyID3
from musiccache import MusicCache  # pyright: ignore[reportMissingImports]


class Mp3Engine:
    """Class to manage MP3 metadata operations and caching"""

    def __init__(self):
        self.album_cache = MusicCache()

    def set_artist_tag(self, mp3_path, artist_name):
        """set artist tag on an mp3 file"""
        try:
            audiofile = EasyID3(mp3_path)
        except ID3NoHeaderError:
            # create basic ID3 with TPE1 then reopen as EasyID3
            id3 = ID3()
            id3.add(TPE1(encoding=3, text=artist_name))
            id3.save(mp3_path)
        audiofile = EasyID3(mp3_path)
        audiofile["artist"] = artist_name
        print(f"Setting artist tag to: {artist_name} for file: {mp3_path}")
        audiofile.save()

    def get_file_info(self, mp3_path):
        """Get metadata information from an MP3 file."""
        if not os.path.isfile(mp3_path):
            raise FileNotFoundError(f"File not found: {mp3_path}")

        try:
            tagg = TinyTag.get(mp3_path)
            if tagg is None:
                print(f"Unable to read tags for file: {mp3_path}")
                return None
            if tagg.album is None:
                print(f"No album tag found for file: {mp3_path}")
                return None
            if tagg.albumartist is None:
                print(f"No album artist tag found for file: {mp3_path}")
                return None
            if tagg.title is None:
                print(f"No title tag found for file: {mp3_path}")
                return None
            self.album_cache.album_cache_src_files.insert(
                mp3_path, os.path.basename(mp3_path)
            )
            self.album_cache.album_cache_files_song_names.insert(mp3_path, tagg.title)
            self.album_cache.album_cache_album_names.insert(mp3_path, tagg.album)
            self.album_cache.album_cache_album_artists.insert(
                mp3_path, tagg.albumartist
            )
            return os.path.basename(mp3_path)
        except (OSError, ValueError, TypeError) as e:
            print(f"Error reading MP3 file '{mp3_path}': {e}")
            return None

    def get_album_info(self, mp3_path, album_name, limit=1):
        """
        Fetch album information from MusicBrainz API.

        :param album_name: Name of the album to search for.
        :param limit: Number of results to return (default 1).
        :return: List of album details.
        """
        if not album_name or not isinstance(album_name, str):
            raise ValueError("Album name must be a non-empty string.")

        if self.album_cache.album_name_cache.search(album_name) is not None:
            self.album_cache.album_cache_album_names.insert(
                mp3_path, self.album_cache.album_name_cache.search(album_name)
            )
            self.album_cache.album_cache_album_artists.insert(
                mp3_path, self.album_cache.album_artist_cache.search(album_name)
            )
            return None

        url = "https://musicbrainz.org/ws/2/release/"
        params = {"query": f'release:"{album_name}"', "fmt": "json", "limit": limit}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "releases" not in data or not data["releases"]:
                return None

            for release in data["releases"]:
                self.album_cache.album_cache_album_names.insert(
                    mp3_path, release.get("title")
                )
                self.album_cache.album_name_cache.insert(
                    album_name, release.get("title")
                )
                if "artist-credit" in release and release["artist-credit"]:
                    self.album_cache.album_cache_album_artists.insert(
                        mp3_path, release["artist-credit"][0].get("name", "Unknown")
                    )
                    self.album_cache.album_artist_cache.insert(
                        album_name, release["artist-credit"][0].get("name", "Unknown")
                    )
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching album info: {e}")
            return None

    def get_contributing_artist(self, mp3_path):
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

        if aa is not None:
            self.album_cache.album_cache_album_artists.insert(mp3_path, aa)
        return None
