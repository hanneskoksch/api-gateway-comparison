from http.server import BaseHTTPRequestHandler, HTTPServer
import time

class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 80), EchoHandler)
    print("Echo server running on port 80")
    server.serve_forever()