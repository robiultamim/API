import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import mysql.connector
from mysql.connector import Error


# DB config - update if your XAMPP uses different credentials
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",   # change if root has a password
    "database": "school"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def add_teacher_to_db(name, role):
    sql = "INSERT INTO teachers (name, role) VALUES (%s, %s)"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (name, role))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        return new_id
    except Error as e:
        # In production you might log this
        return None
    finally:
        if conn:
            conn.close()


class SimpleAPI(BaseHTTPRequestHandler):
    


     def do_POST(self):


        parsed = urlparse(self.path)
        if parsed.path == "/teacher":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            name = data.get("name")
            role = data.get("role")
            new_id = add_teacher_to_db(name, role)

            result = {
                "message": "Teacher added successfully",
                "id": new_id
            }
            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(result).encode())


server_address = ('', 5000)
httpd = HTTPServer(server_address, SimpleAPI)
print("Server running on port 5000...")
httpd.serve_forever()