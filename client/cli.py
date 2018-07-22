import socket
import os
import sys
import argparse
import commands

def create_data_connection():
    welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcomeSock.bind(('', 0))
    print('ephemeral port: ', welcomeSock.getsockname()[1])
    welcomeSock.listen(1)
    return welcomeSock


def create_control_connection(serverAddr, serverPort):
    try:
        connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connSock.connect((serverAddr, serverPort))
        return connSock
    except socket.error as msg:
        print(msg)
        return connSock is None


def add_header(cmd):
    if cmd:
        cmd_size_string = str(len(cmd))
        while len(cmd_size_string) < 10:
            cmd_size_string = '0' + cmd_size_string
        return cmd_size_string
    return None


def list_file_command(cmd, data_socket):
    cmd_data = add_header(cmd) + cmd
    print(cmd_data)
    numSent = 0
    while len(cmd_data) > numSent:
        numSent += data_socket.send(cmd_data[numSent:])
    return numSent


def main(host, port):
    control_channel = create_control_connection(host, port)
    if (control_channel):
        while True:
            user_input = raw_input('ftp> ')

            if user_input == 'ls':
                data_channel = create_data_connection()
                numSent = list_file_command(user_input, control_channel)
                data_channel.close()
            if user_input == 'quit':
                # control_channel.close()
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP client side')
    parser.add_argument('host', type=str, help='domain name of server', metavar='<server machine>')
    parser.add_argument('port', type=int, help='server port number', metavar='<server port>')
    args = parser.parse_args()
    main(args.host, args.port)
