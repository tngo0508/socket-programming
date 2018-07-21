import socket
import sys
import argparse

def create_connection(port):
    listenPort = port

    welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcomeSock.bind(('', port))
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
    print(type(port))
    welcomeSock = create_connection(port)
    while True:
        print('Waiting for connection...')

        clientSock, addr = welcomeSock.accept()
        print('Accepted connection from client: ', addr)
        print('\n')

        fileData = ''
        recvBuff = ''
        fileSize = 0
        fileSizeBuff = ''

        fileSizeBuff = recvAll(clientSock, 10)
        fileSize = int(fileSizeBuff)

        print('The file size is ', fileSize)

        fileData = recvAll(clientSock, fileSize)

        print('The file data is: ')
        print fileData

        clientsock.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP server side')
    parser.add_argument('port', type=int, help='server port number', metavar='<PORT NUMBER>')
    args = parser.parse_args()
    main(args.port)
