import socket
import os
import sys
import argparse
import commands

def create_data_connection():
    welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcomeSock.bind(('', 0))
    print('ephmeral port: ', welcomeSock.getsockname()[1])
    return welcomeSock


def create_control_connection(serverAddr, serverPort):
    try:
        connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connSock.connect((serverAddr, serverPort))
        return True
    except socket.error as msg:
        connSock = None
        print(msg)
        return False


def main(host, port):
    if (create_control_connection(host, port)):
        while True:
            user_input = raw_input('ftp>')

            if (user_input == 'ls'):
                data_


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP client side')
    parser.add_argument('host', type=str, help='domain name of server', metavar='<server machine>')
    parser.add_argument('port', type=int, help='server port number', metavar='<server port>')
    args = parser.parse_args()
    main(args.host, args.port)
