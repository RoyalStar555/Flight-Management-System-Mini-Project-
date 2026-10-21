"""
Upgraded Airport Route Network Graph Implementation
Demonstrates:
  - Graph Representation: Weighted Adjacency List (each airport node maps to connected destinations
    with flight distance in km, average fare in INR, and duration in minutes).
  - Breadth-First Search (BFS): Guarantees minimum flight stops/legs (Unweighted optimal).
  - Depth-First Search (DFS): Deep recursive exploration demonstrating LIFO stack traversal.
  - Dijkstra's Algorithm: Optimal path finding for weighted metrics:
      * Minimum total physical flight distance (km)
      * Lowest cumulative ticket fare (INR)
  - All Alternative Paths (Backtracking DFS): Discovers multiple connecting routing options.
  - Time Complexities:
      * BFS: O(V + E)
      * DFS: O(V + E)
      * Dijkstra: O(V^2) (using pure standard list search, zero external dependencies)
"""

class AirportGraph:
    def __init__(self):
        """Initializes an empty graph with a weighted adjacency list representation."""
        # adj_list maps: airport_code -> { "name": ..., "city": ..., "x": ..., "y": ..., "connections": [ {...} ] }
        self.adj_list = {}

    def add_airport(self, code, name, city="", x=50, y=50):
        """
        Adds an airport vertex to the graph with geographical coordinates
        (normalized percentages for 2D visual route radar rendering).
        """
        code = code.upper().strip()
        if code not in self.adj_list:
            self.adj_list[code] = {
                "name": name,
                "city": city if city else name,
                "x": x,
                "y": y,
                "connections": []
            }

    def add_route(self, from_code, to_code, distance_km=1000, fare=4000, duration_mins=120, bidirectional=True):
        """
        Adds a weighted flight edge between two airports.
        Stores distance, ticket fare, and duration.
        """
        from_c = from_code.upper().strip()
        to_c = to_code.upper().strip()

        if from_c in self.adj_list and to_c in self.adj_list:
            # Check if edge already exists from -> to
            existing_forward = next((c for c in self.adj_list[from_c]["connections"] if c["to"] == to_c), None)
            if not existing_forward:
                self.adj_list[from_c]["connections"].append({
                    "to": to_c,
                    "distance_km": distance_km,
                    "fare": fare,
                    "duration_mins": duration_mins
                })

            if bidirectional:
                existing_backward = next((c for c in self.adj_list[to_c]["connections"] if c["to"] == from_c), None)
                if not existing_backward:
                    self.adj_list[to_c]["connections"].append({
                        "to": from_c,
                        "distance_km": distance_km,
                        "fare": fare,
                        "duration_mins": duration_mins
                    })

    def get_airports(self):
        """Returns list of all airport vertices with metadata."""
        return [
            {
                "code": code,
                "name": data["name"],
                "city": data["city"],
                "x": data["x"],
                "y": data["y"]
            }
            for code, data in self.adj_list.items()
        ]

    def _calculate_path_metrics(self, path):
        """Helper to calculate cumulative distance, fare, and flight legs for a path."""
        total_dist = 0
        total_fare = 0
        total_mins = 0
        legs = []

        for i in range(len(path) - 1):
            src = path[i]
            dst = path[i + 1]
            conn = next((c for c in self.adj_list[src]["connections"] if c["to"] == dst), None)
            if conn:
                dist = conn.get("distance_km", 0)
                fare = conn.get("fare", 0)
                mins = conn.get("duration_mins", 0)
                total_dist += dist
                total_fare += fare
                total_mins += mins
                legs.append({
                    "from": src,
                    "to": dst,
                    "distance_km": dist,
                    "fare": fare,
                    "duration_mins": mins
                })

        hrs = total_mins // 60
        rem_mins = total_mins % 60
        duration_str = f"{hrs}h {rem_mins}m" if hrs > 0 else f"{rem_mins}m"

        return {
            "total_distance_km": total_dist,
            "total_fare": total_fare,
            "total_duration_mins": total_mins,
            "formatted_duration": duration_str,
            "legs": legs
        }

    # =========================================================================
    # 1. BREADTH-FIRST SEARCH (BFS) - UNWEIGHTED SHORTEST PATH (FEWEST HOPS)
    # =========================================================================
    def bfs_shortest_route(self, start_code, dest_code):
        """
        Finds the shortest route with the minimum number of flight connections
        using Breadth-First Search (Queue - FIFO).
        Time Complexity: O(V + E)
        """
        start = start_code.upper().strip()
        dest = dest_code.upper().strip()

        if start not in self.adj_list or dest not in self.adj_list:
            return {"found": False, "message": "One or both airports do not exist in the route network."}

        if start == dest:
            return {
                "found": True,
                "path": [start],
                "path_names": [self.adj_list[start]["name"]],
                "stops": 0,
                "total_distance_km": 0,
                "total_fare": 0,
                "formatted_duration": "0m",
                "visited_order": [start],
                "algorithm": "Breadth-First Search (BFS - Minimum Stops)"
            }

        # Queue storing tuple of (current_airport, path_taken)
        queue = [(start, [start])]
        visited = set([start])
        visited_order = [start]

        while len(queue) > 0:
            current, path = queue.pop(0)  # FIFO Dequeue

            for edge in self.adj_list[current]["connections"]:
                neighbor = edge["to"]
                if neighbor == dest:
                    full_path = path + [neighbor]
                    visited_order.append(neighbor)
                    metrics = self._calculate_path_metrics(full_path)
                    return {
                        "found": True,
                        "path": full_path,
                        "path_names": [self.adj_list[code]["name"] for code in full_path],
                        "stops": len(full_path) - 1,
                        "total_distance_km": metrics["total_distance_km"],
                        "total_fare": metrics["total_fare"],
                        "formatted_duration": metrics["formatted_duration"],
                        "legs": metrics["legs"],
                        "visited_order": visited_order,
                        "algorithm": "Breadth-First Search (BFS - Minimum Stops)"
                    }

                if neighbor not in visited:
                    visited.add(neighbor)
                    visited_order.append(neighbor)
                    queue.append((neighbor, path + [neighbor]))  # FIFO Enqueue

        return {
            "found": False,
            "message": f"No connecting flight path exists between {start} and {dest}.",
            "visited_order": visited_order,
            "algorithm": "Breadth-First Search (BFS)"
        }

    # =========================================================================
    # 2. DEPTH-FIRST SEARCH (DFS) - EXPLORATORY LIFO ROUTE TRAVERSAL
    # =========================================================================
    def dfs_route(self, start_code, dest_code):
        """
        Explores a flight itinerary using Depth-First Search (Stack - LIFO).
        Demonstrates deep recursive path exploration.
        Time Complexity: O(V + E)
        """
        start = start_code.upper().strip()
        dest = dest_code.upper().strip()

        if start not in self.adj_list or dest not in self.adj_list:
            return {"found": False, "message": "One or both airports do not exist."}

        visited = set()
        visited_order = []
        found_path = []

        def dfs_recursive(current, target, current_path):
            visited.add(current)
            visited_order.append(current)

            if current == target:
                found_path.extend(current_path)
                return True

            for edge in self.adj_list[current]["connections"]:
                neighbor = edge["to"]
                if neighbor not in visited:
                    if dfs_recursive(neighbor, target, current_path + [neighbor]):
                        return True
            return False

        has_path = dfs_recursive(start, dest, [start])

        if has_path and found_path:
            metrics = self._calculate_path_metrics(found_path)
            return {
                "found": True,
                "path": found_path,
                "path_names": [self.adj_list[c]["name"] for c in found_path],
                "stops": len(found_path) - 1,
                "total_distance_km": metrics["total_distance_km"],
                "total_fare": metrics["total_fare"],
                "formatted_duration": metrics["formatted_duration"],
                "legs": metrics["legs"],
                "visited_order": visited_order,
                "algorithm": "Depth-First Search (DFS - Exploratory Path)"
            }

        return {
            "found": False,
            "message": f"DFS could not discover a valid path between {start} and {dest}.",
            "visited_order": visited_order,
            "algorithm": "Depth-First Search (DFS)"
        }

    # =========================================================================
    # 3. DIJKSTRA'S ALGORITHM - OPTIMAL WEIGHTED ROUTE (DISTANCE OR FARE)
    # =========================================================================
    def dijkstra_shortest_route(self, start_code, dest_code, weight_metric="distance_km"):
        """
        Finds the globally optimal route using Dijkstra's Algorithm based on:
          - 'distance_km': Shortest physical flight kilometers
          - 'fare': Lowest total ticket price in INR
        Implemented using pure Python list scanning (O(V^2) textbook algorithm, no external libs).
        """
        start = start_code.upper().strip()
        dest = dest_code.upper().strip()

        if start not in self.adj_list or dest not in self.adj_list:
            return {"found": False, "message": "One or both airports do not exist."}

        # Initialize distances, predecessors, and unvisited set
        distances = {node: float("inf") for node in self.adj_list}
        distances[start] = 0
        predecessors = {node: None for node in self.adj_list}
        unvisited = set(self.adj_list.keys())
        visited_order = []

        while len(unvisited) > 0:
            # Find unvisited vertex with the minimum tentative distance
            current = None
            min_dist = float("inf")
            for node in unvisited:
                if distances[node] < min_dist:
                    min_dist = distances[node]
                    current = node

            if current is None or distances[current] == float("inf"):
                # All remaining nodes are unreachable
                break

            unvisited.remove(current)
            visited_order.append(current)

            if current == dest:
                break

            # Relax edges
            for edge in self.adj_list[current]["connections"]:
                neighbor = edge["to"]
                if neighbor in unvisited:
                    weight = edge.get(weight_metric, 1)
                    new_dist = distances[current] + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        predecessors[neighbor] = current

        # Reconstruct path from dest to start
        if distances[dest] == float("inf"):
            return {
                "found": False,
                "message": f"No weighted flight path exists between {start} and {dest}.",
                "visited_order": visited_order,
                "algorithm": f"Dijkstra's Algorithm (By {weight_metric.replace('_', ' ').title()})"
            }

        path = []
        curr = dest
        while curr is not None:
            path.insert(0, curr)
            curr = predecessors[curr]

        metrics = self._calculate_path_metrics(path)
        metric_label = "Distance (km)" if weight_metric == "distance_km" else "Ticket Fare (₹)"

        return {
            "found": True,
            "path": path,
            "path_names": [self.adj_list[c]["name"] for c in path],
            "stops": len(path) - 1,
            "optimal_metric": metric_label,
            "optimal_value": distances[dest],
            "total_distance_km": metrics["total_distance_km"],
            "total_fare": metrics["total_fare"],
            "formatted_duration": metrics["formatted_duration"],
            "legs": metrics["legs"],
            "visited_order": visited_order,
            "algorithm": f"Dijkstra's Shortest Path ({metric_label})"
        }

    # =========================================================================
    # 4. ALL ALTERNATIVE ROUTES (BACKTRACKING DFS)
    # =========================================================================
    def find_all_routes(self, start_code, dest_code, max_stops=3):
        """
        Discovers all alternative flight itineraries (up to max_stops)
        between two airports using Backtracking DFS.
        """
        start = start_code.upper().strip()
        dest = dest_code.upper().strip()

        if start not in self.adj_list or dest not in self.adj_list:
            return {"found": False, "routes": []}

        all_paths = []

        def backtrack(current, target, path, visited):
            if len(path) - 1 > max_stops:
                return

            if current == target:
                all_paths.append(list(path))
                return

            for edge in self.adj_list[current]["connections"]:
                neighbor = edge["to"]
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    backtrack(neighbor, target, path, visited)
                    path.pop()
                    visited.remove(neighbor)

        visited_set = set([start])
        backtrack(start, dest, [start], visited_set)

        # Sort paths by stops, then fare
        formatted_routes = []
        for p in all_paths:
            metrics = self._calculate_path_metrics(p)
            formatted_routes.append({
                "path": p,
                "stops": len(p) - 1,
                "total_distance_km": metrics["total_distance_km"],
                "total_fare": metrics["total_fare"],
                "formatted_duration": metrics["formatted_duration"],
                "legs": metrics["legs"]
            })

        formatted_routes.sort(key=lambda r: (r["stops"], r["total_fare"]))

        return {
            "found": len(formatted_routes) > 0,
            "origin": start,
            "destination": dest,
            "total_routes_found": len(formatted_routes),
            "routes": formatted_routes,
            "algorithm": "Backtracking DFS (All Connecting Itineraries)"
        }

    # =========================================================================
    # 5. VISUALIZATION & NETWORK SERIALIZATION
    # =========================================================================
    def get_network_visualization(self):
        """
        Returns serialized nodes with 2D radar layout coordinates
        and unique weighted edges for SVG/Canvas rendering.
        """
        nodes = []
        edges = []
        seen_edges = set()

        for code, info in self.adj_list.items():
            nodes.append({
                "code": code,
                "name": info["name"],
                "city": info["city"],
                "x": info["x"],
                "y": info["y"]
            })
            for conn in info["connections"]:
                target = conn["to"]
                edge_id = tuple(sorted([code, target]))
                if edge_id not in seen_edges:
                    seen_edges.add(edge_id)
                    edges.append({
                        "from": code,
                        "to": target,
                        "distance_km": conn.get("distance_km", 1000),
                        "fare": conn.get("fare", 4000),
                        "duration_mins": conn.get("duration_mins", 120)
                    })

        return {
            "nodes": nodes,
            "edges": edges,
            "total_airports": len(nodes),
            "total_routes": len(edges)
        }
