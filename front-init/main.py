from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from pathlib import Path
import mimetypes
from datetime import datetime
import json
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path()  # "C:/Users/user/Desktop/front-init/front-init"
jinja = Environment(loader=FileSystemLoader("storage"))

class VladisLoveFramework(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case "/":
                self.send_html("index.html")
            case "/message":
                self.send_html("message.html")
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html("error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        data_dict = {current_time: {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}}
        try:
            with open("storage/data.json", "a") as file:
                file.write(json.dumps(data_dict, indent=4) + ',\n')
        except Exception as e:
            print(f"Error writing to file: {e}")
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header("Content-Type", mime_type)
        else:
            self.send_header("Content-Type", "text/plain")
        self.end_headers()
        with open(filename, "rb", ) as file:
            self.wfile.write(file.read())


def run_server():
    address = ("localhost", 3000)
    http_server = HTTPServer(address, VladisLoveFramework)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


if __name__ == "__main__":
    run_server()
