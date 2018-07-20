import socket
import sys
import argparse
import re
import json
from threading import Lock
from thread import start_new_thread

HOST = '' # all availabe interfaces
PORT = 9999 # arbitrary non privileged port
LOCK = Lock()
formatter = None
REGEX = re.compile('/test-(\d+)')
PREV = 0
#test = open('test.txt', 'w')
DATA_Q  = ''

def find_json_array(data):
    stack = []
    for i in range(len(data)):
        c = data[i]
        if c == '{':
            stack.append(i)
        elif c == '}' and len(stack) > 1:
            stack.pop()
        elif c == '}' and len(stack) == 1:
            return stack.pop(), i+1
    return 0, 0

def get_json_array(data):
    global DATA_Q
    DATA_Q += data
    start, end = find_json_array(DATA_Q)
    json_array = DATA_Q[start:end]
    DATA_Q = DATA_Q[end:]
    return json_array

def json_data(data):
    try:
        data = get_json_array(data)
        json_object = json.loads(data)
        return '\n' + json.dumps(json_object, indent=2) + '\n'
    except ValueError, e:
        return data

def plain_data(data):
    return data

def testLogrotate(data):
    global PREV
    results = REGEX.findall(data)
    for number in results:
        number = int(number)
        if number-PREV != 1:
            test.write('number: %d, PREV: %d, diff: %d\n' % (
                number, PREV, number-PREV))
            test.flush()
        PREV = number


def printer(data, addr):
    #testLogrotate(data)
    with LOCK:            
        sys.stdout.write('[%(ip)s:%(port)s] %(data)s\n\n' % {
            'ip': addr[0],
            'port': str(addr[1]),
            'data': formatter(data.strip())
        })
        sys.stdout.flush()

def arg_parser():
    global PORT, formatter
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port",
                        type=int,
                        nargs=1,
                        help="specify port number on which server need to listen")
    parser.add_argument("-j", "--json",
                        action='store_true',
                        help="json pretty print")
    args = vars(parser.parse_args())
    if args['port'] is not None:
        PORT = args['port'][0]
    if args['json']:
        formatter = json_data
    else:
        formatter = plain_data


def client_thread(client, addr):
    client.send("Welcome to the Server. Type messages and press enter to send.\n")
    while True:
        try:
            data = client.recv(2048)
        except socket.error:
            break
        if not data:
            break
        printer(data, addr)
        reply = "OK . . " + data
        client.sendall(reply)
    print('[%(ip)s:%(port)s] %(data)s' % {
        'ip': addr[0],
        'port': str(addr[1]),
        'data': 'Connection closed.'
    })
    client.close()

def run_server(s):
    while True:
        # wait to accept a new connection (blocking call)
        conn, addr = s.accept()
        printer('Connection established', addr)
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
    #test.close()
