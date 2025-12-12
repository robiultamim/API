import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

data = [
    {"id": 1, "name": "Saif", "role": "Teacher"},
    {"id": 2, "name": "Mahbub", "role": "Teacher"},
    {"id": 3, "name": "Arnab", "role": "Teacher"}
]


class SimpleAPI(BaseHTTPRequestHandler):

    @staticmethod
    def get_info(target_id):
        for item in data:
            if item.get('id') == target_id:
                return item
        return None

    def do_GET(self):
        parsed = urlparse(self.path)
        # print(parsed.query)
        # print(parsed.query.split('='))
        # print(parsed.query.split('=')[1])
        teacher_id = parsed.query.split('=')[1]
        if parsed.path == "/teacher":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            result = self.get_info(int(teacher_id))
            self.wfile.write(json.dumps(result).encode())


server_address = ('', 5000)
httpd = HTTPServer(server_address, SimpleAPI)
print("Server running on port 5000...")
httpd.serve_forever()
