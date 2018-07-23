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


def send(data, sock):
    if data:
        data_size_string = str(len(data))
        while len(data_size_string) < 10:
            data_size_string = '0' + data_size_string
        fileData = data_size_string + data
        numSent = 0
        while len(fileData) > numSent:
            numSent += sock.send(fileData[numSent:])
        return numSent
    return 0


def create_data_connection(serverAddr, serverPort):
    try:
        connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connSock.connect((serverAddr, serverPort))
        return connSock
    except socket.error as msg:
        print msg
        return connSock is None

def tranfer(data, client_addr, client_sock):
    port_size = 0
    port_size_buff = ''
    ephemeral_port = ''
    ephemeral_port = recvAll(client_sock, 5)
    print 'emphemeral port ', ephemeral_port
    data_channel = create_data_connection(client_addr[0], int(ephemeral_port))
    if send(data, data_channel):
        return True
    return False


def main(port):
    welcomeSock = create_connection(port)
    print'Waiting for connection...'
    clientSock, addr = welcomeSock.accept()
    client_addr = socket.gethostbyaddr(str(addr[0]))
    print 'Accepted connection from client: ', addr
    print '\n'
    while True:
        cmd_size_buff = ''
        cmd_size = 0
        client_cmd = ''

        cmd_size_buff = recvAll(clientSock, 10)
        print cmd_size_buff

        cmd_size = int(cmd_size_buff)
        print 'The command size is ', cmd_size, 'bytes'
        client_cmd = recvAll(clientSock, cmd_size)
        print 'command is ', client_cmd

        if client_cmd == 'ls':
            lines = ''
            for line in commands.getoutput(client_cmd):
                lines += str(line)
            print lines
            if (tranfer(lines, client_addr, clientSock)):
                print 'success'
            else:
                print 'fail'
            # port_size = 0
            # port_size_buff = ''
            # ephemeral_port = ''
            # ephemeral_port = recvAll(clientSock, 5)
            # print('emphemeral port', ephemeral_port)
            # data_channel = create_data_connection(client_addr[0], int(ephemeral_port))
            # send(lines, data_channel)
        elif client_cmd == 'quit':
            break
        elif len(client_cmd) > 2:
            file_name = client_cmd[4:]
            if 'get' in client_cmd[:4]:
                print 'Sending ', file_name, '...'
                fileObj = None
                try:
                    fileObj = open(file_name, "r")
                except IOError as msg:
                    tranfer(str(msg), client_addr, clientSock)

                if fileObj:
                    while True:
                        fileData = fileObj.read(65536)
                        if fileData:
                            tranfer(fileData, client_addr, clientSock)
                        else:
                            break

    clientSock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP server side')
    parser.add_argument('port', type=int, help='server port number', metavar='<PORT NUMBER>')
    args = parser.parse_args()
    main(args.port)
