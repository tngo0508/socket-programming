import socket
import sys
import argparse

def create_connection():
    listenPort = 1234

    welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcomeSock.bind(('', 0))
    print('Ephemeral Port: ', welcomeSock.getsockname())[1]
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
    welcomeSock = create_connection()
    while True:
        print('Waiting for connection...')

        clientSock, addr = welcomeSock.accept()
        print('Accepted connection from client: ', addr)
        print('\n')

        fileData = ''
        recvBuff = ''
        fileSize = 0
        fileSizeBuff = ''
        fileSize = int(fileSizeBuff)

        print('The file size is ', fileSize)

        fileData = recvAll(clientSock, fileSize)

        print('The file data is: ')
        print fileData

        clientsock.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP server side')
    parser.add_argument('<PORT NUMBER>', type=int, help='server port number')
    port = parser.parse_args()
    main(port)
