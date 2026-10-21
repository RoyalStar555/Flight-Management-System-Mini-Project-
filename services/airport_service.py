"""
Airport Service Layer
Integrates the domain logic (flights, bookings, routes, waitlist)
with the custom Data Structures:
  - Stack (Undo history)
  - Circular Queue (Waitlist management)
  - Singly Linked List (Confirmed passenger manifest)
  - Hash Table (Instant PNR lookup)
  - Graph (Airport route map & BFS navigation)
  - Algorithms (Linear & Binary search, Bubble & Selection sort)
"""

from data_structures.stack import Stack, StackOverflowError, StackUnderflowError
from data_structures.queue import CircularQueue, QueueOverflowError, QueueUnderflowError
from data_structures.linked_list import SinglyLinkedList
from data_structures.hash_table import HashTable
from data_structures.graph import AirportGraph
from data_structures.algorithms import (
    linear_search_flight,
    binary_search_flight,
    bubble_sort_flights,
    selection_sort_flights
)

class AirportService:
    def __init__(self):
        # 1. Flight Directory (Array of flight dictionaries)
        self.flights = [
            {
                "flight_id": "AI-101",
                "airline": "Air India",
                "origin": "BOM",
                "origin_city": "Mumbai",
                "dest": "DEL",
                "dest_city": "Delhi",
                "departure": "06:30",
                "fare": 4500,
                "available_seats": 24
            },
            {
                "flight_id": "6E-204",
                "airline": "IndiGo",
                "origin": "DEL",
                "origin_city": "Delhi",
                "dest": "BLR",
                "dest_city": "Bengaluru",
                "departure": "09:15",
                "fare": 5200,
                "available_seats": 12
            },
            {
                "flight_id": "UK-305",
                "airline": "Vistara",
                "origin": "BOM",
                "origin_city": "Mumbai",
                "dest": "GOI",
                "dest_city": "Goa",
                "departure": "11:45",
                "fare": 3800,
                "available_seats": 8
            },
            {
                "flight_id": "SG-402",
                "airline": "SpiceJet",
                "origin": "BLR",
                "origin_city": "Bengaluru",
                "dest": "CCU",
                "dest_city": "Kolkata",
                "departure": "14:10",
                "fare": 6100,
                "available_seats": 15
            },
            {
                "flight_id": "QP-507",
                "airline": "Akasa Air",
                "origin": "DEL",
                "origin_city": "Delhi",
                "dest": "HYD",
                "dest_city": "Hyderabad",
                "departure": "16:40",
                "fare": 4100,
                "available_seats": 19
            },
            {
                "flight_id": "AI-610",
                "airline": "Air India",
                "origin": "HYD",
                "origin_city": "Hyderabad",
                "dest": "MAA",
                "dest_city": "Chennai",
                "departure": "19:20",
                "fare": 3200,
                "available_seats": 30
            },
            {
                "flight_id": "EK-702",
                "airline": "Emirates",
                "origin": "BOM",
                "origin_city": "Mumbai",
                "dest": "DXB",
                "dest_city": "Dubai",
                "departure": "22:00",
                "fare": 14500,
                "available_seats": 5
            }
        ]

        # 2. Stack for Action History / Undo (Max size 5)
        self.action_stack = Stack(capacity=5)

        # 3. Circular Queue for Waitlist (Max size 5)
        self.waitlist_queue = CircularQueue(capacity=5)

        # 4. Singly Linked List for Confirmed Passenger Manifest
        self.manifest_list = SinglyLinkedList()

        # 5. Hash Table for PNR ticket lookups (Capacity 7 prime)
        self.pnr_table = HashTable(capacity=7)

        # 6. Route Network Graph + BFS
        self.route_graph = AirportGraph()
        self._init_network()

        # Counter for generating sequential ticket PNRs
        self._pnr_seq = 100

        # Seed initial sample confirmed passengers
        self._seed_initial_data()

    def _init_network(self):
        """Initializes airport vertices with radar coordinates and weighted domestic/international flight routes."""
        airports = [
            ("DXB", "Dubai Intl", "Dubai", 10, 35),
            ("DEL", "Indira Gandhi Intl", "Delhi", 42, 18),
            ("BOM", "Chhatrapati Shivaji Maharaj Intl", "Mumbai", 28, 56),
            ("GOI", "Dabolim Intl", "Goa", 30, 80),
            ("HYD", "Rajiv Gandhi Intl", "Hyderabad", 50, 60),
            ("BLR", "Kempegowda Intl", "Bengaluru", 44, 82),
            ("MAA", "Chennai Intl", "Chennai", 64, 84),
            ("CCU", "Netaji Subhash Chandra Bose Intl", "Kolkata", 84, 40)
        ]
        for code, name, city, x, y in airports:
            self.route_graph.add_airport(code, name, city=city, x=x, y=y)

        # Weighted flight routes: (from, to, distance_km, fare_inr, duration_mins)
        routes = [
            ("BOM", "DEL", 1150, 4500, 130),
            ("BOM", "GOI", 440, 3800, 75),
            ("BOM", "BLR", 840, 4200, 105),
            ("BOM", "HYD", 620, 3600, 90),
            ("BOM", "DXB", 1930, 14500, 210),
            ("DEL", "BLR", 1740, 5200, 165),
            ("DEL", "CCU", 1310, 4900, 135),
            ("DEL", "HYD", 1260, 4100, 130),
            ("DEL", "DXB", 2180, 16000, 240),
            ("BLR", "CCU", 1560, 6100, 155),
            ("BLR", "MAA", 290, 2600, 55),
            ("HYD", "MAA", 510, 3200, 75),
            ("MAA", "CCU", 1370, 5500, 140),
            ("GOI", "BLR", 480, 3400, 70)
        ]
        for origin, dest, dist, fare, dur in routes:
            self.route_graph.add_route(origin, dest, distance_km=dist, fare=fare, duration_mins=dur)

    def _seed_initial_data(self):
        """Pre-seeds 3 initial confirmed passengers to make the visualizer interactive right away."""
        initial_passengers = [
            {"name": "Aarav Sharma", "flight_id": "AI-101", "seat": "1A"},
            {"name": "Priya Patil", "flight_id": "6E-204", "seat": "3A"},
            {"name": "Rohan Deshmukh", "flight_id": "UK-305", "seat": "5B"}
        ]
        for p in initial_passengers:
            self._pnr_seq += 1
            pnr = f"PNR-{self._pnr_seq}"
            ticket = {
                "pnr": pnr,
                "name": p["name"],
                "flight_id": p["flight_id"],
                "seat": p["seat"],
                "status": "CONFIRMED"
            }
            self.manifest_list.insert_at_end(ticket)
            self.pnr_table.insert(pnr, ticket)

    def get_flights(self):
        """Returns all flights in current directory."""
        return self.flights

    def sort_flights(self, key="fare", algorithm="bubble", ascending=True):
        """Sorts the flight directory by price or departure time."""
        if algorithm == "selection":
            return selection_sort_flights(self.flights, key=key, ascending=ascending)
        else:
            return bubble_sort_flights(self.flights, key=key, ascending=ascending)

    def search_flight(self, flight_id, method="linear"):
        """Searches for a flight by Flight ID using Linear or Binary Search."""
        if method == "binary":
            # For Binary Search, the array must be sorted by flight_id
            sorted_by_id = sorted(self.flights, key=lambda f: f["flight_id"])
            return binary_search_flight(sorted_by_id, flight_id)
        else:
            return linear_search_flight(self.flights, flight_id)

    def book_ticket(self, flight_id, passenger_name, seat="AUTO"):
        """
        Books a confirmed flight ticket:
          1. Inserts into Singly Linked List (manifest)
          2. Inserts into Hash Table (PNR index)
          3. Pushes action onto Stack (for undo)
        """
        self._pnr_seq += 1
        pnr = f"PNR-{self._pnr_seq}"

        # Resolve seat: if AUTO or empty, pick the next available cabin chair
        assigned_seats = {str(p.get("seat", "")).upper() for p in self.manifest_list.to_list()}
        chosen_seat = seat.strip().upper() if seat and seat.strip().upper() != "AUTO" else None
        if not chosen_seat:
            cabin_seats = [
                "1A", "1F", "2A", "2F",
                "3A", "3C", "3D", "3F", "4A", "4C", "4D", "4F",
                "5A", "5B", "5C", "5D", "5E", "5F", "6A", "6B", "6C", "6D", "6E", "6F"
            ]
            for cs in cabin_seats:
                if cs not in assigned_seats:
                    chosen_seat = cs
                    break
            if not chosen_seat:
                chosen_seat = f"{self._pnr_seq % 30 + 1}{chr(65 + self._pnr_seq % 6)}"

        ticket = {
            "pnr": pnr,
            "name": passenger_name.strip(),
            "flight_id": flight_id.upper().strip(),
            "seat": chosen_seat,
            "status": "CONFIRMED"
        }

        # 1. Linked List insertion
        self.manifest_list.insert_at_end(ticket)

        # 2. Hash Table insertion with collision tracking
        bucket_idx, had_collision = self.pnr_table.insert(pnr, ticket)

        # 3. Stack push (Record for Undo)
        # Note: If stack is full, we allow it to push or raise depending on user demo
        stack_event = "Action pushed to Undo Stack."
        try:
            self.action_stack.push({
                "action": "BOOK",
                "pnr": pnr,
                "ticket_data": ticket
            })
        except StackOverflowError as e:
            stack_event = f"⚠️ Undo Stack is Full! {str(e)}"

        return {
            "success": True,
            "ticket": ticket,
            "pnr": pnr,
            "hash_bucket": bucket_idx,
            "hash_collision": had_collision,
            "stack_status": stack_event,
            "message": f"Ticket {pnr} confirmed for {passenger_name} on {flight_id}."
        }

    def cancel_ticket(self, pnr):
        """
        Cancels a confirmed ticket:
          1. Removes from Linked List
          2. Removes from Hash Table
          3. Pushes CANCEL action onto Stack
        """
        pnr_clean = pnr.upper().strip()
        deleted = self.manifest_list.delete_by_pnr(pnr_clean)

        if not deleted:
            return {"success": False, "message": f"PNR {pnr_clean} not found in passenger manifest."}

        self.pnr_table.delete(pnr_clean)

        stack_event = "Action pushed to Undo Stack."
        try:
            self.action_stack.push({
                "action": "CANCEL",
                "pnr": pnr_clean,
                "ticket_data": deleted
            })
        except StackOverflowError as e:
            stack_event = f"⚠️ Undo Stack is Full! {str(e)}"

        return {
            "success": True,
            "cancelled_ticket": deleted,
            "stack_status": stack_event,
            "message": f"Ticket {pnr_clean} successfully cancelled."
        }

    def undo_last_action(self):
        """
        Pops the most recent action from the Stack and reverses it (LIFO).
        """
        # May raise StackUnderflowError if stack is empty
        action_item = self.action_stack.pop()
        action_type = action_item.get("action")
        pnr = action_item.get("pnr")
        ticket = action_item.get("ticket_data")

        if action_type == "BOOK":
            # Reverse BOOK -> Delete from manifest & hash table
            self.manifest_list.delete_by_pnr(pnr)
            self.pnr_table.delete(pnr)
            revert_msg = f"Undid booking for {pnr} ({ticket.get('name')}). Ticket removed."
        elif action_type == "CANCEL":
            # Reverse CANCEL -> Re-insert back into manifest & hash table
            self.manifest_list.insert_at_end(ticket)
            self.pnr_table.insert(pnr, ticket)
            revert_msg = f"Undid cancellation for {pnr}. Ticket restored."
        else:
            revert_msg = f"Reversed action: {action_type}"

        return {
            "success": True,
            "reverted_action": action_type,
            "pnr": pnr,
            "message": revert_msg
        }

    def join_waitlist(self, passenger_name, flight_id):
        """
        Enqueues a passenger into the Circular Waitlist Queue.
        May raise QueueOverflowError if the waitlist has reached 5 passengers.
        """
        passenger = {
            "name": passenger_name.strip(),
            "flight_id": flight_id.upper().strip(),
            "type": "WAITLIST"
        }
        self.waitlist_queue.enqueue(passenger)
        return {
            "success": True,
            "passenger": passenger,
            "current_waitlist_size": self.waitlist_queue.size(),
            "message": f"{passenger_name} added to waitlist for {flight_id}."
        }

    def process_waitlist(self):
        """
        Dequeues the first passenger from the waitlist (FIFO) and confirms their ticket.
        May raise QueueUnderflowError if the queue is empty.
        """
        passenger = self.waitlist_queue.dequeue()
        # Automatically book this passenger now that a seat opened
        book_res = self.book_ticket(passenger["flight_id"], passenger["name"])
        return {
            "success": True,
            "dequeued_passenger": passenger,
            "ticket": book_res["ticket"],
            "message": f"Processed {passenger['name']} from waitlist -> Confirmed with {book_res['pnr']}."
        }

    def lookup_ticket(self, pnr):
        """Looks up a ticket instantly via the custom Hash Table."""
        val, bucket_idx = self.pnr_table.search(pnr)
        if val is None:
            return {
                "found": False,
                "pnr": pnr,
                "bucket_index": bucket_idx,
                "message": f"PNR '{pnr}' not found in Hash Table (checked Bucket #{bucket_idx})."
            }
        return {
            "found": True,
            "ticket": val,
            "pnr": pnr,
            "bucket_index": bucket_idx,
            "message": f"Found PNR '{pnr}' in Bucket #{bucket_idx}."
        }

    def find_flight_route(self, origin, destination, algorithm="bfs", weight_metric="distance_km"):
        """
        Computes route using upgraded Graph algorithms:
          - 'bfs': Minimum flight connections/hops
          - 'dfs': Deep exploratory path
          - 'dijkstra': Shortest physical distance (km) or lowest fare (INR)
          - 'all_routes': Discovers all alternative connecting routes
        """
        if algorithm == "dfs":
            return self.route_graph.dfs_route(origin, destination)
        elif algorithm == "dijkstra":
            return self.route_graph.dijkstra_shortest_route(origin, destination, weight_metric=weight_metric)
        elif algorithm == "all_routes":
            return self.route_graph.find_all_routes(origin, destination)
        else:
            return self.route_graph.bfs_shortest_route(origin, destination)

    def find_shortest_flight_route(self, origin, destination):
        """Backward-compatible alias for BFS shortest route."""
        return self.find_flight_route(origin, destination, algorithm="bfs")

    def get_full_state(self):
        """
        Returns the complete internal state across all 6 data structures
        for real-time live synchronization with the frontend inspector.
        """
        return {
            "stack": self.action_stack.get_raw_slots(),
            "queue": self.waitlist_queue.get_raw_slots(),
            "linked_list": self.manifest_list.get_chain_visualization(),
            "hash_table": self.pnr_table.get_buckets_visualization(),
            "graph": self.route_graph.get_network_visualization(),
            "flights_count": len(self.flights),
            "manifest_count": self.manifest_list.size(),
            "waitlist_count": self.waitlist_queue.size()
        }
