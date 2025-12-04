from http.server import BaseHTTPRequestHandler, HTTPServer


class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


if __name__ == "__main__":
    server_port = 80
    server_address = ('', server_port)
    server = HTTPServer(server_address, EchoHandler)
    print(f"Echo server running on port {server_port}")
    server.serve_forever()
