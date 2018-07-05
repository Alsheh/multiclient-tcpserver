import socket
import sys
import argparse
from thread import start_new_thread

HOST = '' # all availabe interfaces
PORT = 9999 # arbitrary non privileged port 

def arg_parser():
    global PORT
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port",
                        type=int,
                        nargs=1,
                        help="specify port number on which server need to listen")
    args = vars(parser.parse_args())
    if args['port'] is not None:
        PORT = args['port'][0]

def client_thread(client, addr):
    client.send("Welcome to the Server. Type messages and press enter to send.\n")
    while True:
        data = client.recv(1024)
        if not data:
            break
        print('[%(ip)s:%(port)s] %(data)s' % {
            'ip': addr[0],
            'port': str(addr[1]),
            'data': str(data.strip())
        })
        reply = "OK . . " + data
        client.sendall(reply)
    client.close()

def run_server(s):
    while True:
        # blocking call, waits to accept a connection
        conn, addr = s.accept()
        print("[-] Connected to " + addr[0] + ":" + str(addr[1]))
        start_new_thread(client_thread, (conn, addr))

    
if __name__ == '__main__':
    arg_parser()
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print("Could not create socket. Error Code: ", str(msg[0]), "Error: ", msg[1])
        sys.exit(0)

    print("[-] Socket Created")

    # bind socket
    try:
        s.bind((HOST, PORT))
        print("[-] Socket Bound to port " + str(PORT))
    except socket.error, msg:
        print("Bind Failed. Error Code: {} Error: {}".format(str(msg[0]), msg[1]))
        sys.exit()

    s.listen(10)
    print("Listening...")
    run_server(s)
    s.close()
