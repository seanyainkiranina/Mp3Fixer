"""This module contains the MusicCache class,
which is responsible for managing music metadata caching using hash tables.
It provides methods to search for album artists, album names, song names, 
full paths, and file names in the cache. The MusicCache class is used by 
the Mp3Engine to efficiently access
cached metadata when organizing MP3 files."""

from hashtable import HashTable


class MusicCache:
    """Class to manage music metadata caching using hash tables"""

    def __init__(self):
        self.cache = HashTable()

    def album_cache_album_artists_search(self, key):
        """Search for album artist in the cache"""
        return self.cache.get_cache(key, "artist")

    def album_cache_album_names_search(self, key):
        """Search for album name in the cache"""
        return self.cache.get_cache(key, "album")

    def album_cache_files_song_names_search(self, key):
        """Search for song name in the cache"""
        return self.cache.get_cache(key, "title")

    def file_to_full_path_cache_search(self, key):
        """Search for full path in the cache"""
        return self.cache.get_cache(key, "file_with_full_path")

    def file_name_cache_search(self, key):
        """Search for file name in the cache"""
        return self.cache.get_cache(key, "file_name")
