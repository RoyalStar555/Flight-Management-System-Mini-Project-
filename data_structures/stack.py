"""
Fixed-Capacity Stack Implementation (LIFO - Last In First Out)
Demonstrates:
  - Push: Adding an element to the top of the stack.
  - Pop: Removing an element from the top of the stack.
  - Peek: Inspecting the top element without removing it.
  - Stack Overflow: Condition when attempting to push onto a full stack.
  - Stack Underflow: Condition when attempting to pop from an empty stack.
"""

class StackOverflowError(Exception):
    """Raised when an operation attempts to push onto a full stack."""
    pass

class StackUnderflowError(Exception):
    """Raised when an operation attempts to pop from an empty stack."""
    pass

class Stack:
    def __init__(self, capacity=5):
        """
        Initializes a fixed-capacity stack using a static-sized array simulation.
        :param capacity: Maximum number of elements the stack can hold (default: 5)
        """
        self.capacity = capacity
        self.items = [None] * capacity  # Fixed size allocation in memory
        self.top = -1                   # Pointer pointing to the top element (-1 means empty)

    def is_empty(self):
        """Returns True if the stack has no elements (Underflow condition check)."""
        return self.top == -1

    def is_full(self):
        """Returns True if the stack has reached its maximum capacity (Overflow condition check)."""
        return self.top == self.capacity - 1

    def push(self, item):
        """
        Pushes a new item onto the top of the stack.
        Time Complexity: O(1)
        """
        if self.is_full():
            raise StackOverflowError(
                f"Stack Overflow! Maximum capacity of {self.capacity} items reached."
            )
        self.top += 1
        self.items[self.top] = item
        return True

    def pop(self):
        """
        Removes and returns the item from the top of the stack.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise StackUnderflowError(
                "Stack Underflow! Cannot pop from an empty stack."
            )
        item = self.items[self.top]
        self.items[self.top] = None  # Clear memory reference
        self.top -= 1
        return item

    def peek(self):
        """
        Returns the top item without removing it.
        Time Complexity: O(1)
        """
        if self.is_empty():
            raise StackUnderflowError(
                "Stack is empty! Cannot peek."
            )
        return self.items[self.top]

    def size(self):
        """Returns the current number of items in the stack."""
        return self.top + 1

    def to_list(self):
        """
        Returns the active elements as a list ordered from Top to Bottom.
        Useful for visualization and inspect UI.
        """
        if self.is_empty():
            return []
        # Return elements from index 'top' down to 0
        return [self.items[i] for i in range(self.top, -1, -1)]

    def get_raw_slots(self):
        """
        Returns the exact state of all memory slots including empty slots
        and where the 'top' pointer currently points.
        """
        return {
            "capacity": self.capacity,
            "top_index": self.top,
            "slots": [
                {
                    "index": i,
                    "value": self.items[i],
                    "is_top": (i == self.top)
                }
                for i in range(self.capacity)
            ],
            "is_full": self.is_full(),
            "is_empty": self.is_empty()
        }
