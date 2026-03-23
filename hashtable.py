from typing import Optional
from node import Node
from mp3cache import Mp3Cache


class HashTable:
    """Simple hash table implementation using chaining for collision resolution"""

    def __init__(self, capacity=10):
        self.capacity = capacity
        self.size = 0
        self.buckets: list[Optional[Node]] = [None] * capacity
        self.keys = []  # To keep track of existing keys for quick lookup

    def _hash(self, key):
        return hash(key) % self.capacity

    def list_keys(self):
        """Return a list of all keys in the hash table"""
        return self.keys

    def get_cache(self, key, attribute_name):
        """Retrieve the Mp3Cache object for a given key and attribute name"""
        node = self.search(key)
        if node is not None:
            cache = node.value
            if isinstance(cache, Mp3Cache):
                if attribute_name == "artist":
                    return cache.artist
                elif attribute_name == "album":
                    return cache.album
                elif attribute_name == "title":
                    return cache.title
                elif attribute_name == "file_with_full_path":
                    return cache.file_with_full_path
                elif attribute_name == "file_name":
                    return cache.file_name
        return None


    def update(self, key, value, attribute_name):
        """Insert or update a key-value pair in the hash table"""
        stored_value = self.search(key)  # Ensure the key exists before updating
        if stored_value is None:
            stored_value = Mp3Cache()  # Create a new Mp3Cache if key doesn't exist
            if attribute_name == "artist":
                stored_value.set_artist(value)
            elif attribute_name == "album":
                stored_value.set_album(value)
            elif attribute_name == "title":
                stored_value.set_title(value)
            elif attribute_name == "file_with_full_path":
                stored_value.set_file_with_full_path(value)
            elif attribute_name == "file_name":
                stored_value.set_file_name(value)
            self.insert(key, stored_value)
        else:
            if attribute_name == "artist":
                stored_value.set_artist(value)
            elif attribute_name == "album":
                stored_value.set_album(value)
            elif attribute_name == "title":
                stored_value.set_title(value)
            elif attribute_name == "file_with_full_path":
                stored_value.set_file_with_full_path(value)
            elif attribute_name == "file_name":
                stored_value.set_file_name(value)
            self.insert(key, stored_value)  # Update the existing key with new value
    def insert(self, key, value):
        """Insert or update a key-value pair in the hash table"""
        index = self._hash(key)
        node = self.buckets[index]
        while node:
            if node.key == key:
                node.value = value  # Update value if key exists
                return
            node = node.next
        new_node = Node(key, value)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.size += 1
        if key not in self.keys:
            self.keys.append(key)

    def search(self, key):
        """Search for a value by key in the hash table"""
        index = self._hash(key)
        node = self.buckets[index]
        while node:
            if node.key == key:
                return node.value
            node = node.next
        return None

    def delete(self, key):
        """Delete a key-value pair from the hash table"""
        index = self._hash(key)
        node = self.buckets[index]
        prev = None
        while node:
            if node.key == key:
                if prev:
                    prev.next = node.next
                else:
                    self.buckets[index] = node.next
                self.size -= 1
                self.keys.remove(key)
                return
            prev, node = node, node.next
        return None
