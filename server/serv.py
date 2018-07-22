import socket
import sys
import argparse
import commands

def create_connection(port):
    listenPort = port

    welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcomeSock.bind(('', port))
    welcomeSock.listen(1)
    return welcomeSock


def recvAll(sock, numBytes):
    recvBuff = ''
    tmpBuff = ''
    while len(recvBuff) < numBytes:
        tmpBuff = sock.recv(numBytes)
        if not tmpBuff:
            break
        recvBuff += tmpBuff
    return recvBuff


def main(port):
    welcomeSock = create_connection(port)
    while True:
        print('Waiting for connection...')

        clientSock, addr = welcomeSock.accept()
        print('Accepted connection from client: ', addr)
        print('\n')

        cmd_size_buff = ''
        cmd_size = 0
        client_cmd = ''

        cmd_size_buff = recvAll(clientSock, 10)
        print(cmd_size_buff)

        cmd_size = int(cmd_size_buff)
        print('The command size is ', cmd_size)
        client_cmd = recvAll(clientSock, cmd_size)
        print('command is ', client_cmd)
        for line in commands.getstatusoutput(client_cmd):
            print line
        print('break')

        if client_cmd == 'quit':
            break

    clientSock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP server side')
    parser.add_argument('port', type=int, help='server port number', metavar='<PORT NUMBER>')
    args = parser.parse_args()
    main(args.port)