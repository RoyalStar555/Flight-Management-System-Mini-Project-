"""
Hash Table Implementation with Separate Chaining for PNR / Ticket Lookup
Demonstrates:
  - Hash Function: Computes an integer index from a string key (PNR) using modulo arithmetic.
  - Bucket: A slot in the hash table that stores key-value pairs.
  - Collision: When two distinct keys compute to the exact same hash index.
  - Collision Resolution via Separate Chaining: Each bucket holds a chain (list) of pairs.
  - Time Complexity: O(1) average lookup, O(n) worst-case if all keys collide.
"""

class HashTable:
    def __init__(self, capacity=7):
        """
        Initializes the Hash Table with a prime number capacity (default: 7).
        Using a prime capacity minimizes collisions in modulo hashing.
        """
        self.capacity = capacity
        # Pre-allocate array of empty buckets (Separate Chaining)
        self.buckets = [[] for _ in range(capacity)]
        self.count = 0

    def _hash(self, key):
        """
        Custom hash function using ASCII summation and prime multiplier modulo table capacity.
        hash(key) = (sum(ord(char) * 31^pos)) % capacity
        """
        key_str = str(key).strip().upper()
        hash_val = 0
        for i, char in enumerate(key_str):
            hash_val = (hash_val * 31 + ord(char)) % self.capacity
        return hash_val

    def insert(self, key, value):
        """
        Inserts or updates a key-value pair.
        Returns a tuple: (bucket_index, collision_occurred_flag)
        """
        key_str = str(key).strip().upper()
        index = self._hash(key_str)
        bucket = self.buckets[index]

        # Check if key already exists in bucket -> Update in-place
        for i, (k, v) in enumerate(bucket):
            if k == key_str:
                bucket[i] = (key_str, value)
                return index, False

        # Collision occurs if bucket already contains other keys
        had_collision = len(bucket) > 0

        # Append new key-value pair to bucket chain
        bucket.append((key_str, value))
        self.count += 1
        return index, had_collision

    def search(self, key):
        """
        Looks up a value by its key.
        Average Time Complexity: O(1)
        """
        key_str = str(key).strip().upper()
        index = self._hash(key_str)
        bucket = self.buckets[index]

        for k, v in bucket:
            if k == key_str:
                return v, index
        return None, index

    def delete(self, key):
        """
        Removes a key-value pair by key.
        """
        key_str = str(key).strip().upper()
        index = self._hash(key_str)
        bucket = self.buckets[index]

        for i, (k, v) in enumerate(bucket):
            if k == key_str:
                del bucket[i]
                self.count -= 1
                return True
        return False

    def load_factor(self):
        """Returns the ratio of total elements to total bucket capacity."""
        return round(self.count / self.capacity, 2)

    def get_buckets_visualization(self):
        """
        Returns complete state of all buckets for UI visualization,
        highlighting collisions and bucket distributions.
        """
        result = []
        for i in range(self.capacity):
            items = []
            for k, v in self.buckets[i]:
                items.append({
                    "key": k,
                    "passenger_name": v.get("name", ""),
                    "flight_id": v.get("flight_id", ""),
                    "seat": v.get("seat", "")
                })
            result.append({
                "bucket_index": i,
                "chain_length": len(items),
                "has_collision": len(items) > 1,
                "items": items
            })
        return {
            "capacity": self.capacity,
            "total_keys": self.count,
            "load_factor": self.load_factor(),
            "buckets": result
        }
