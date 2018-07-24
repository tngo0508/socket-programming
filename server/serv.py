import socket
import sys
import argparse
import commands
import os

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
        print 'open tcp connection for data tranfering...'
        connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connSock.connect((serverAddr, serverPort))
        return connSock
    except socket.error as msg:
        print msg
        return connSock is None


def transfer(data_sock):
    data_size_buff = recvAll(data_sock, 10)
    print 'data size buff: ', str(data_size_buff)
    data_size = int(data_size_buff)
    data = recvAll(data_sock, data_size)
    return data


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
        print 'cmd_size_buff: ', cmd_size_buff

        cmd_size = int(cmd_size_buff)
        print 'The command size is ', cmd_size, 'bytes'
        client_cmd = recvAll(clientSock, cmd_size).strip()
        print 'executing command: ', client_cmd

        # if 'quit' not in client_cmd:
        if any(cmd in client_cmd for cmd in ['ls', 'get', 'put']):
            port_size = 0
            port_size_buff = ''
            ephemeral_port = ''
            ephemeral_port = recvAll(clientSock, 5)
            print 'emphemeral port: ', ephemeral_port
            data_channel = create_data_connection(client_addr[0], int(ephemeral_port))

        if client_cmd == 'ls':
            lines = ''
            for line in commands.getoutput('ls'):
                lines += str(line)
            print lines
            if send(lines, data_channel):
                send('server: executed successfully', clientSock)
                print 'response success...\n'
            else:
                send('server: cannot execute command', clientSock)
                print 'response fail...\n'
        elif client_cmd == 'quit':
            send('server: ack quit', clientSock)
            data = transfer(clientSock)
            print data
            break
        elif len(client_cmd) > 2:
            file_name = client_cmd[4:]
            if 'get' in client_cmd[:4]:
                print 'Sending ', file_name, '...'
                fileObj = None
                try:
                    fileObj = open(file_name, "rb")
                except IOError as msg:
                    send(str(msg), data_channel)

                if fileObj:
                    curr_dir = os.getcwd() + '/' + file_name
                    req_file_size = os.path.getsize(curr_dir)
                    print 'file size: ', req_file_size, 'bytes'
                    if req_file_size > 65536:
                        msg = 'server: [Errno 27] File too large.'
                        if send(msg, data_channel):
                            send('server: The allowed FTP receive window size is 65536 bytes', clientSock)
                            print 'response success...\n'
                        else:
                            print 'response fail...\n'
                    else:
                        fileData = fileObj.read()
                        if send(fileData, data_channel):
                            send('server: executed successfully', clientSock)
                            print 'response success...\n'
                        else:
                            print 'response fail...\n'
            elif 'put' in client_cmd[:4]:
                print 'Downloading ', file_name, '...'
                send('ack', data_channel)
                # data = transfer(data_channel)
                if not 'Errno' in data:
                    print 'break'
                    with open(file_name, 'wb') as file_to_write:
                        file_to_write.write(data)
                        send('success!', data_channel)
                        print 'success'
                else:
                    print 'fail'
                    send('fail', data_channel)
                    print data
            else:
                send('server: command not found', clientSock)

    clientSock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP server side')
    parser.add_argument('port', type=int, help='server port number', metavar='<PORT NUMBER>')
    args = parser.parse_args()
    main(args.port)
