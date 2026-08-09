import http.server
import socketserver

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/datos':
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            # Aquí iría tu lógica para generar y devolver los datos en formato JSON
        else:
            super().do_GET()

if __name__ == '__main__':
    PORT = 8901
    Handler = Handler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    print("Serving at port", PORT)
    httpd.serve_forever()
