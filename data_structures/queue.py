"""
Fixed-Capacity Circular Queue Implementation (FIFO - First In First Out)
Demonstrates:
  - Enqueue: Adding an element at the rear of the queue.
  - Dequeue: Removing an element from the front of the queue.
  - Front & Rear Pointers: Tracking entry and exit points in memory.
  - Queue Overflow: Attempting to enqueue when queue is at max capacity.
  - Queue Underflow: Attempting to dequeue from an empty queue.
  - Circular Buffer: Reusing empty slots using modulo arithmetic to prevent false overflow.
"""

class QueueOverflowError(Exception):
    """Raised when an operation attempts to enqueue into a full queue."""
    pass

class QueueUnderflowError(Exception):
    """Raised when an operation attempts to dequeue from an empty queue."""
    pass

class CircularQueue:
    def __init__(self, capacity=5):
        """
        Initializes a fixed-capacity circular queue.
        :param capacity: Maximum number of elements allowed (default: 5)
        """
        self.capacity = capacity
        self.items = [None] * capacity  # Pre-allocated fixed memory slots
        self.front = 0                  # Points to the front item
        self.rear = -1                  # Points to the most recently added item
        self.count = 0                  # Tracks number of active elements

    def is_empty(self):
        """Returns True if the queue has no elements (Underflow condition)."""
        return self.count == 0

    def is_full(self):
        """Returns True if the queue is full (Overflow condition)."""
        return self.count == self.capacity

    def enqueue(self, item):
        """
        Adds a new element to the rear of the queue.
        Time Complexity: O(1)
        """
        if self.is_full():
            raise QueueOverflowError(
                f"Queue Overflow! Maximum capacity of {self.capacity} waitlist passengers reached."
            )
        # Advance rear circularly
        self.rear = (self.rear + 1) % self.capacity
        self.items[self.rear] = item
        self.count += 1
        return True

    def dequeue(self):
        """
        Removes and returns the element from the front of the queue.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise QueueUnderflowError(
                "Queue Underflow! Waitlist is completely empty, cannot dequeue."
            )
        item = self.items[self.front]
        self.items[self.front] = None  # Clear memory slot
        # Advance front circularly
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        # Reset pointers if empty for visual clarity
        if self.count == 0:
            self.front = 0
            self.rear = -1
        return item

    def peek(self):
        """
        Returns the front element without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise QueueUnderflowError("Queue is empty! Cannot peek.")
        return self.items[self.front]

    def size(self):
        """Returns current count of active elements."""
        return self.count

    def to_list(self):
        """
        Returns elements in logical FIFO order from front to rear.
        """
        if self.is_empty():
            return []
        result = []
        idx = self.front
        for _ in range(self.count):
            result.append(self.items[idx])
            idx = (idx + 1) % self.capacity
        return result

    def get_raw_slots(self):
        """
        Returns raw memory state showing all pre-allocated slots,
        front pointer, and rear pointer.
        """
        return {
            "capacity": self.capacity,
            "count": self.count,
            "front_index": self.front if not self.is_empty() else None,
            "rear_index": self.rear if not self.is_empty() else None,
            "slots": [
                {
                    "index": i,
                    "value": self.items[i],
                    "is_front": (i == self.front and not self.is_empty()),
                    "is_rear": (i == self.rear and not self.is_empty())
                }
                for i in range(self.capacity)
            ],
            "is_full": self.is_full(),
            "is_empty": self.is_empty()
        }
