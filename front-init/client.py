import socket


def main(host=socket.gethostname(), port=5000):
    with socket.socket() as client:
        client.connect((host, port))
        message = input(">>> ")
        while message.lower().strip() != "exit":
            client.send(message.encode())
            msg = client.recv(1024).decode()
            print(f"Received message {msg}")
            message = input(">>> ")


if __name__ == "__main__":
    main()
