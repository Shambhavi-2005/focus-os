from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
from urllib.parse import urlparse, parse_qs


# Stores the latest browser information
browser_state = {
    "browser": "Unknown",
    "domain": "Unknown"
}


class BrowserRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        parsed_url = urlparse(self.path)

        # -----------------------------------------------------
        # Browser extension sends:
        #
        # /update?browser=chrome&domain=youtube.com
        # -----------------------------------------------------

        if parsed_url.path == "/update":

            query = parse_qs(parsed_url.query)

            browser = query.get(
                "browser",
                ["Unknown"]
            )[0]

            domain = query.get(
                "domain",
                ["Unknown"]
            )[0]

            browser_state["browser"] = browser
            browser_state["domain"] = domain

            # Send response
            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.end_headers()

            response = {
                "status": "ok"
            }

            self.wfile.write(
                json.dumps(response).encode()
            )

            return

        # -----------------------------------------------------
        # Get current browser state
        # -----------------------------------------------------

        if parsed_url.path == "/browser":

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.end_headers()

            self.wfile.write(
                json.dumps(browser_state).encode()
            )

            return

        # -----------------------------------------------------
        # Unknown endpoint
        # -----------------------------------------------------

        self.send_response(404)
        self.end_headers()

    # Prevent terminal spam
    def log_message(self, format, *args):
        return


def start_browser_server():

    server = HTTPServer(
        ("127.0.0.1", 8765),
        BrowserRequestHandler
    )

    print(
        "Browser monitor running on "
        "http://127.0.0.1:8765"
    )

    server.serve_forever()


def start_browser_monitor():

    server_thread = threading.Thread(
        target=start_browser_server,
        daemon=True
    )

    server_thread.start()