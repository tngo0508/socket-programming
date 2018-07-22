import socket
import os
import sys
import argparse
import commands

def create_tcp_connection(serverAddr, serverPort):
    connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(serverAddr, serverPort)
    connSock.connect((serverAddr, serverPort))


def main(host, port):
    if len(sys.argv) < 2:
        print('USAGE python' + sys.argv[0] + "<FILE NAME>")

    create_tcp_connection(host, port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP client side')
    parser.add_argument('host', type=str, help='domain name of server', metavar='<server machine>')
    parser.add_argument('port', type=int, help='server port number', metavar='<server port>')
    args = parser.parse_args()
    main(args.host, args.port)
