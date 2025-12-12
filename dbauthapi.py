#C:/Users/robiu/AppData/Local/Programs/Python/Python313/python.exe -m pip install --user mysql-connector-python
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import mysql.connector
from mysql.connector import Error

def is_valid_api_key(key):
    sql = "SELECT id FROM api_keys WHERE api_key = %s"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (key,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Error:
        return False
    finally:
        if conn:
            conn.close()

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



def update_teacher_in_db(teacher_id, name, role): # 2, tamim, teacher
    sql = "UPDATE teachers SET name = %s, role = %s WHERE id = %s"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (name, role, teacher_id))
        conn.commit()
        updated_rows = cursor.rowcount
        cursor.close()
        return updated_rows
    except Error:
        return None
    finally:
        if conn:
            conn.close()


def delete_teacher_from_db(teacher_id):
    sql = "DELETE FROM teachers WHERE id = %s"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (teacher_id,))
        conn.commit()
        deleted_rows = cursor.rowcount
        cursor.close()
        return deleted_rows
    except Error:
        return None
    finally:
        if conn:
            conn.close()


class SimpleAPI(BaseHTTPRequestHandler):
    # AUTH CHECK
    def authenticate(self):
       key = self.headers.get("X-API-KEY")

       if not key:
         self.send_response(401)
         self.send_header("Content-type", "application/json")
         self.end_headers()
         self.wfile.write(b'{"error": "Missing API Key"}')
         return False

       if not is_valid_api_key(key):
         self.send_response(403)
         self.send_header("Content-type", "application/json")
         self.end_headers()
         self.wfile.write(b'{"error": "Invalid API Key"}')
         return False

       return True

    def do_GET(self):
        # AUTH REQUIRED
        if not self.authenticate():
            return


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



    def do_POST(self):
        # AUTH REQUIRED
        if not self.authenticate():
            return


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

    def do_PUT(self):
        if not self.authenticate():
            return
        parsed = urlparse(self.path)
        teacher_id = parsed.query.split('=')[1]
        if parsed.path == "/teacher":
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data)
            name = data.get("name")
            role = data.get("role")
            updated_rows = update_teacher_in_db(int(teacher_id), name, role) # 2 , tamim,teacher
            result = {
                    "message": "Teacher updated successfully",
                    "updated_rows": updated_rows
                }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
    def do_DELETE(self):
        if not self.authenticate():
            return

        parsed = urlparse(self.path)
        teacher_id = parsed.query.split('=')[1]
        if parsed.path == "/teacher":
            
            deleted_rows = delete_teacher_from_db(int(teacher_id))
                    
            result = {
                    "message": "Teacher deleted successfully",
                    "deleted_rows": deleted_rows
                }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()  
            self.wfile.write(json.dumps(result).encode())



server_address = ('', 5000)
httpd = HTTPServer(server_address, SimpleAPI)
print("Server running on port 5000...")
httpd.serve_forever()
