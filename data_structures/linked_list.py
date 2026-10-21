"""
Singly Linked List Implementation for Confirmed Passenger Manifest
Demonstrates:
  - Node: An individual element containing 'data' and a 'next' reference/pointer.
  - Head: The reference to the first node in the linked list.
  - Dynamic Memory Chaining: Unlike fixed arrays, nodes are dynamically linked at runtime.
  - Insertion (At End): Appending a confirmed passenger to the manifest.
  - Deletion (By PNR): Unlinking a node by updating the predecessor's next pointer.
  - Traversal: Walking through the nodes sequentially from head to NULL.
"""

class Node:
    def __init__(self, data):
        """
        Initializes an individual node.
        :param data: The payload dictionary containing passenger details.
        """
        self.data = data
        self.next = None  # Pointer to the next node in sequence


class SinglyLinkedList:
    def __init__(self):
        """Initializes an empty Singly Linked List with head pointing to None."""
        self.head = None
        self._size = 0

    def is_empty(self):
        """Returns True if the linked list has no nodes."""
        return self.head is None

    def size(self):
        """Returns the number of nodes currently linked."""
        return self._size

    def insert_at_end(self, data):
        """
        Appends a new node with 'data' at the end of the list.
        Time Complexity: O(n) traversal to the tail node.
        """
        new_node = Node(data)
        if self.is_empty():
            self.head = new_node
        else:
            curr = self.head
            while curr.next is not None:
                curr = curr.next
            curr.next = new_node
        self._size += 1
        return True

    def insert_at_beginning(self, data):
        """
        Inserts a new node directly at the head of the list.
        Time Complexity: O(1)
        """
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1
        return True

    def delete_by_pnr(self, pnr):
        """
        Deletes the first node matching the specified PNR.
        Time Complexity: O(n) search and pointer unlinking.
        Returns: The deleted passenger data, or None if not found.
        """
        if self.is_empty():
            return None

        # Case 1: The head node itself holds the target PNR
        if str(self.head.data.get("pnr", "")).upper() == str(pnr).upper():
            deleted_data = self.head.data
            self.head = self.head.next
            self._size -= 1
            return deleted_data

        # Case 2: Traverse to find node to delete while tracking 'prev'
        prev = self.head
        curr = self.head.next
        while curr is not None:
            if str(curr.data.get("pnr", "")).upper() == str(pnr).upper():
                deleted_data = curr.data
                prev.next = curr.next  # Bypass/unlink current node
                self._size -= 1
                return deleted_data
            prev = curr
            curr = curr.next

        return None  # Not found

    def search_by_pnr(self, pnr):
        """
        Sequentially traverses the linked list to find a passenger by PNR.
        Time Complexity: O(n)
        """
        curr = self.head
        while curr is not None:
            if str(curr.data.get("pnr", "")).upper() == str(pnr).upper():
                return curr.data
            curr = curr.next
        return None

    def to_list(self):
        """Traverses the linked list and returns passenger dictionaries in sequence."""
        result = []
        curr = self.head
        while curr is not None:
            result.append(curr.data)
            curr = curr.next
        return result

    def get_chain_visualization(self):
        """
        Returns structured data representing the linked list chain
        with explicit node pointers for UI visual rendering.
        """
        nodes = []
        curr = self.head
        index = 0
        while curr is not None:
            nodes.append({
                "index": index,
                "data": curr.data,
                "has_next": (curr.next is not None)
            })
            curr = curr.next
            index += 1
        return {
            "head_exists": (self.head is not None),
            "total_nodes": self._size,
            "nodes": nodes
        }
