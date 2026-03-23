from typing import Optional


class Node:
    """Node class for linked list in hash table"""

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next: Optional["Node"] = None
