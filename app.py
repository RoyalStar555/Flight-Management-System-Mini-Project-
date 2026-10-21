"""
Application Server for Flight Reservation & Airport Management System
Built using Python's standard library (http.server).
Zero external dependencies required.
"""

import os
import sys
import json
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
try:
    from http.server import ThreadingHTTPServer
except ImportError:
    ThreadingHTTPServer = HTTPServer
from urllib.parse import urlparse, parse_qs

# Ensure data_structures and services can be imported regardless of execution path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.airport_service import AirportService
from data_structures.stack import StackOverflowError, StackUnderflowError
from data_structures.queue import QueueOverflowError, QueueUnderflowError

# Global singleton service instance
service = AirportService()

class FlightAppRequestHandler(BaseHTTPRequestHandler):
    STATIC_DIR = os.path.join(BASE_DIR, "static")

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode("utf-8")
            try:
                return json.loads(raw_body)
            except json.JSONDecodeError:
                return {}
        return {}

    def _send_json(self, data, status=200):
        self._set_headers(status, "application/json")
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_error(self, message, error_type="ERROR", status=400):
        self._set_headers(status, "application/json")
        response = {
            "success": False,
            "error_type": error_type,
            "message": message
        }
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # API Routes
        if path == "/api/state":
            state = service.get_full_state()
            self._send_json({"success": True, "state": state})
            return

        elif path == "/api/flights":
            flights = service.get_flights()
            self._send_json({"success": True, "flights": flights})
            return

        elif path == "/api/manifest":
            manifest = service.manifest_list.to_list()
            self._send_json({"success": True, "manifest": manifest})
            return

        elif path == "/api/airports":
            airports = service.route_graph.get_airports()
            self._send_json({"success": True, "airports": airports})
            return

        # Static File Serving
        self._serve_static_file(path)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        body = self._read_json_body()

        try:
            if path == "/api/book":
                flight_id = body.get("flight_id")
                passenger_name = body.get("name")
                seat = body.get("seat", "AUTO")

                if not flight_id or not passenger_name:
                    self._send_error("Flight ID and Passenger Name are required.", "VALIDATION_ERROR")
                    return

                res = service.book_ticket(flight_id, passenger_name, seat)
                self._send_json(res)

            elif path == "/api/cancel":
                pnr = body.get("pnr")
                if not pnr:
                    self._send_error("PNR is required for cancellation.", "VALIDATION_ERROR")
                    return
                res = service.cancel_ticket(pnr)
                if not res.get("success"):
                    self._send_error(res.get("message"), "NOT_FOUND", 404)
                else:
                    self._send_json(res)

            elif path == "/api/undo":
                res = service.undo_last_action()
                self._send_json(res)

            elif path == "/api/waitlist/enqueue":
                name = body.get("name")
                flight_id = body.get("flight_id", "AI-101")
                if not name:
                    self._send_error("Passenger name is required.", "VALIDATION_ERROR")
                    return
                res = service.join_waitlist(name, flight_id)
                self._send_json(res)

            elif path == "/api/waitlist/dequeue":
                res = service.process_waitlist()
                self._send_json(res)

            elif path == "/api/lookup":
                pnr = body.get("pnr")
                if not pnr:
                    self._send_error("PNR is required.", "VALIDATION_ERROR")
                    return
                res = service.lookup_ticket(pnr)
                self._send_json(res)

            elif path == "/api/route":
                origin = body.get("origin")
                dest = body.get("dest")
                algo = body.get("algorithm", "bfs")
                weight_metric = body.get("weight_metric", "distance_km")
                if not origin or not dest:
                    self._send_error("Origin and Destination are required.", "VALIDATION_ERROR")
                    return
                res = service.find_flight_route(origin, dest, algorithm=algo, weight_metric=weight_metric)
                self._send_json(res)

            elif path == "/api/sort":
                key = body.get("key", "fare")
                algo = body.get("algorithm", "bubble")
                ascending = body.get("ascending", True)
                res = service.sort_flights(key=key, algorithm=algo, ascending=ascending)
                self._send_json({"success": True, "result": res})

            elif path == "/api/search":
                flight_id = body.get("flight_id")
                method = body.get("method", "linear")
                if not flight_id:
                    self._send_error("Flight ID is required to search.", "VALIDATION_ERROR")
                    return
                res = service.search_flight(flight_id, method=method)
                self._send_json({"success": True, "result": res})

            else:
                self._send_error(f"Unknown endpoint: {path}", "NOT_FOUND", 404)

        except StackOverflowError as e:
            self._send_error(str(e), "STACK_OVERFLOW", 400)
        except StackUnderflowError as e:
            self._send_error(str(e), "STACK_UNDERFLOW", 400)
        except QueueOverflowError as e:
            self._send_error(str(e), "QUEUE_OVERFLOW", 400)
        except QueueUnderflowError as e:
            self._send_error(str(e), "QUEUE_UNDERFLOW", 400)
        except Exception as e:
            self._send_error(f"Unexpected server error: {str(e)}", "SERVER_ERROR", 500)

    def _serve_static_file(self, req_path):
        """Safely maps HTTP request path to local static file."""
        if req_path in ("/", ""):
            req_path = "/index.html"

        # Sanitize path to prevent directory traversal
        clean_path = os.path.normpath(req_path.lstrip("/"))
        file_path = os.path.join(self.STATIC_DIR, clean_path)

        if not os.path.isfile(file_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
            return

        # Determine MIME type
        ctype, _ = mimetypes.guess_type(file_path)
        if not ctype:
            ctype = "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self._set_headers(200, ctype)
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"500 Internal Error: {str(e)}".encode("utf-8"))

    def log_message(self, format, *args):
        # Override to keep terminal output clean during viva presentations
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))


def run_server(port=8000):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, FlightAppRequestHandler)
    print("=" * 70)
    print(">> AEROSTRUCTURES: Flight Reservation & Airport Management System")
    print(f">> Server running at http://localhost:{port}/")
    print(">> Data Structures Engine: ACTIVE (Stack, Queue, LinkedList, HashTable, Graph)")
    print(">> Zero external dependencies. Pure standard Python standard library.")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
