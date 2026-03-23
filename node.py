""""This module contains the Node class, which is used as a building block 
for the linked list implementation in the hash table. Each Node instance stores a 
key-value pair and a reference to the next node in the list. 
The Node class is used by the HashTable class to handle collisions when multiple keys
 hash to the same index.
"""
from typing import Optional


class Node:
    """Node class for linked list in hash table"""

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next: Optional["Node"] = None
