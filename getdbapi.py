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

def get_teacher_from_db(teacher_id):
    sql = "SELECT id, name, role FROM teachers WHERE id = %s"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (teacher_id,))
        row = cursor.fetchone()
        cursor.close()
        return row
    except Error as e:
        # In production you might log this
        return None
    finally:
        if conn:
            conn.close()


class SimpleAPI(BaseHTTPRequestHandler):
    


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
            result = get_teacher_from_db(int(teacher_id))
            self.wfile.write(json.dumps(result).encode())



server_address = ('', 5000)
httpd = HTTPServer(server_address, SimpleAPI)
print("Server running on port 5000...")
httpd.serve_forever()