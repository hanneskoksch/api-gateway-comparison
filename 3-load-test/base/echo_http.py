from http.server import BaseHTTPRequestHandler, HTTPServer
import os

SERVICE_NAME = os.getenv("SERVICE_NAME", "echo-unknown")


class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        msg = f"response from {SERVICE_NAME}".encode()
        self.wfile.write(msg)


if __name__ == "__main__":
    server_port = 5001
    server_address = ('', server_port)
    server = HTTPServer(server_address, EchoHandler)
    print(f"Echo server {SERVICE_NAME} running on port {server_port}")
    server.serve_forever()
