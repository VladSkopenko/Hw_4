import socket


def main(host=socket.gethostname(), port=5000):
    with socket.socket() as s:
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        while True:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            print(f"Received {msg}")
            message = input(">>>")
            conn.send(message.encode())
        conn.close()


if __name__ == "__main__":
    main()
