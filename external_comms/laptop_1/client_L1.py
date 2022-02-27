import paramiko
from paramiko import SSHClient, AutoAddPolicy

def sshCommand(hostname, port, username, password, command):
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.load_system_host_keys()
    sshClient.connect(hostname, port, username, password)
    stdin, stdout, stderr = sshClient.exec_command(command)
    print(stdout.read())

# if __name__ == '__main__':
#     sshCommand('sunfire.comp.nus.edu.sg', 22, 'shawntan', 'stzc@S9817869D', 'ls')

# import socket
#
# clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# clientsocket.connect(('localhost', 15432))
# clientsocket.send('hello')

# import paramiko
# import sshtunnel
#
# from sshtunnel import SSHTunnelForwarder
#
# server = SSHTunnelForwarder(
#     'sunfire.comp.nus.edu.sg',
#     ssh_username="shawntan",
#     ssh_password="stzc@S9817869D",
#     remote_bind_address=('127.0.0.1', 8080)
# )
#
# server.start()
#
# print(server.local_bind_port)  # show assigned local port
# # work with `SECRET SERVICE` through `server.local_bind_port`.

# server.stop()
import paramiko
import sshtunnel
from sshtunnel import open_tunnel
from time import sleep
import socket


def open_ssh_tunneling_to_ultra96():
    ssh_tunnel =  open_tunnel(
        ('sunfire.comp.nus.edu.sg', 22),
        ssh_username="shawntan",
        ssh_password="stzc@S9817869D",
        remote_bind_address=('137.132.86.238', 22),
        block_on_close=False)
    ssh_tunnel.start()
    # print(ssh_tunnel.local_bind_port)
    print("Connection to ssh tunnel: OK...")
    ultra96_tunnel = open_tunnel(
        #('127.0.0.1',ssh_tunnel.local_bind_port),
        ssh_address_or_host=('localhost', ssh_tunnel.local_bind_port),
        remote_bind_address=('127.0.0.1', 15435),
        ssh_username='xilinx',
        ssh_password='apricot816',
        local_bind_address=('127.0.0.1', 15435),
        block_on_close=False
    )
    ultra96_tunnel.start()
    print(ultra96_tunnel.local_bind_port)
    print("Connection to ultra 96: OK...")
    # sshCommand('localhost', ultra96_tunnel.local_bind_port, 'xilinx', 'apricot816', 'ls')
    connect_socket()


def connect_socket():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientsocket:
            clientsocket.connect(('localhost', 15435))
            print('Connection to server: OK...')
            clientsocket.send(b'Hello Nice to Meet you')
            data = clientsocket.recv(1024)
            print(f'Received {data}')
    except ConnectionRefusedError:
        print("Unable to connect")


if __name__ == '__main__':
    open_ssh_tunneling_to_ultra96()
    # connect_socket()