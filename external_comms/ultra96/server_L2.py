import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Waiting for connection....")
s.bind(('localhost', 15430))
s.listen()
connection, address = s.accept()
print("Connected to client")
with connection:
    print(f"Connected by {address}")
    while True:
        buf = connection.recv(1024)
        if not buf:
            break
        connection.sendall(buf)
        print(buf)


