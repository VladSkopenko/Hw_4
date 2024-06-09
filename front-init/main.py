from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from pathlib import Path
import mimetypes
import logging
from datetime import datetime
import json
from threading import Thread
import socket


BASE_DIR = Path()   # Шлях цього файлу
PORT_HTTP = 3000    # Це порт на якому буде працювати наш сервер http
HOST_HTTP = "0.0.0.0" #
SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 5000  # теж саме для сокету
BUFFER_SIZE = 1024  #розір  максимальний повідомлень



class VladisLoveFramework(BaseHTTPRequestHandler):

    def do_GET(self):  # метод який обробляє статичні ресурси
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

    def do_POST(self): # В цьому методі ми реалізувати сокет-клієнта а також повідомлення
        size = self.headers.get("Content-Length")
        data = self.rfile.read(int(size))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


    def send_html(self, filename, status_code=200): # це допоміжна функція для читабельності кода
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        with open(filename, "rb") as file:
            self.wfile.write(file.read())

    def send_static(self, filename, status_code=200): # Теж саме але для логотипа
        self.send_response(status_code)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header("Content-Type", mime_type)
        else:
            self.send_header("Content-Type", "text/plain")
        self.end_headers()
        with open(filename, "rb", ) as file:
            self.wfile.write(file.read())


def run_socket_server(host, port): # запуск сервера який буде працювати з повідомленнями
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    logging.info("Starting socket")
    try:
        while True:
            msg, address = server_socket.recvfrom(BUFFER_SIZE)
            logging.info("++")
            save_data(msg)
    except KeyboardInterrupt:
        server_socket.close()



def run_http_server(host, port): # запуск основного сервера
    address = (host, port)
    http_server = HTTPServer(address, VladisLoveFramework)
    logging.info("Starting http")
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()

def save_data(data): # збереження повідомлень
    data_parse = urllib.parse.unquote_plus(data.decode())
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        new_data = {current_time: {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}}

        file_path = "storage/data.json"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = {}
        except ValueError:
            existing_data = {}

        existing_data.update(new_data)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=2)

    except ValueError as error:
        logging.error(f"ValueError: {error}")
    except OSError as oser:
        logging.error(f"OSError: {oser}")


if __name__ == "__main__": # і нарешні запуск нашого скрипту в різних потоках
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s%(message)s")

    ser_http = Thread(target=run_http_server, args=(HOST_HTTP, PORT_HTTP))
    ser_http.start()

    ser_socker = Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    ser_socker.start()

