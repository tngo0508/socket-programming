import socket
import os
import sys
import argparse
import commands

def create_data_connection():
    try:
        welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        welcomeSock.bind(('', 0))
        print('ephemeral port: ', welcomeSock.getsockname()[1])
        welcomeSock.listen(1)
        return welcomeSock
    except socket.error as msg:
        print(msg)
        return welcomeSock is None


def create_control_connection(serverAddr, serverPort):
    try:
        connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connSock.connect((serverAddr, serverPort))
        return connSock
    except socket.error as msg:
        print(msg)
        return connSock is None


def send_command(cmd, control_sock, data_sock=None):
    if cmd:
        cmd_size_string = str(len(cmd))
        while len(cmd_size_string) < 10:
            cmd_size_string = '0' + cmd_size_string
        cmd_data = cmd_size_string + cmd
        if cmd == 'ls':
            cmd_data += str(data_sock.getsockname()[1])
        print(cmd_data)
        numSent = 0
        while len(cmd_data) > numSent:
            numSent += control_sock.send(cmd_data[numSent:])
        return numSent
    return 0


def recvAll(sock, numBytes):
    recvBuff = ''
    tmpBuff = ''
    while len(recvBuff) < numBytes:
        tmpBuff = sock.recv(numBytes)
        if not tmpBuff:
            break
        recvBuff += tmpBuff
    return recvBuff


def main(host, port):
    control_channel = create_control_connection(host, port)
    if (control_channel):
        while True:
            user_input = raw_input('ftp> ')

            if user_input == 'ls':
                data_channel = create_data_connection()
                numSent = send_command(user_input, control_channel, data_channel)
                data_sock, addr = data_channel.accept()
                data_size_buff = recvAll(data_sock, 10)
                data_size = int(data_size_buff)
                data = recvAll(data_sock, data_size)
                print(data)
                data_channel.close()
            elif user_input == 'quit':
                numSent = send_command(user_input, control_channel)
                # control_channel.close()
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP client side')
    parser.add_argument('host', type=str, help='domain name of server', metavar='<server machine>')
    parser.add_argument('port', type=int, help='server port number', metavar='<server port>')
    args = parser.parse_args()
    main(args.host, args.port)
