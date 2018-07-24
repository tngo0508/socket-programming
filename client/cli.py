import socket
import os
import sys
import argparse
import commands

def create_data_connection():
    try:
        welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        welcomeSock.bind(('', 0))
        print 'ephemeral port: ', welcomeSock.getsockname()[1]
        welcomeSock.listen(1)
        return welcomeSock
    except socket.error as msg:
        print 'Socket error: ', msg
        return welcomeSock is None


def create_control_connection(serverAddr, serverPort):
    try:
        connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connSock.connect((serverAddr, serverPort))
        return connSock
    except socket.error as msg:
        print 'Socket error: ', msg
        return connSock is None


def send(data, sock, data_sock=None):
    if data:
        data_size_string = str(len(data))
        while len(data_size_string) < 10:
            data_size_string = '0' + data_size_string
        new_data = data_size_string + data
        #append the ephemeral_port at the end of the packet
        if any(cmd in data for cmd in ['ls', 'get', 'put']) and data_sock:
            new_data += str(data_sock.getsockname()[1])
        print 'Packet being sent: ', new_data
        numSent = 0
        while len(new_data) > numSent:
            numSent += sock.send(new_data[numSent:])
        print 'Sent', numSent, 'bytes'
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


def data_transfer(user_input, control_sock):
    print 'open tcp connection for data tranfering...'
    data_channel = create_data_connection()
    numSent = send(user_input, control_sock, data_channel)
    data_sock, addr = data_channel.accept()
    data_size_buff = recvAll(data_sock, 10)
    data_size = int(data_size_buff)
    data = recvAll(data_sock, data_size)
    data_channel.close()
    print 'close tcp connection for data tranfering...'
    return data


def recv_from_control(control_sock):
    data_size_buff = recvAll(control_sock, 10)
    data_size = int(data_size_buff)
    data = recvAll(control_sock, data_size)
    return data


def main(host, port):
    control_channel = create_control_connection(host, port)
    if control_channel:
        while True:
            print '\n'
            user_input = raw_input('ftp> ').strip()

            if user_input == 'ls':
                data = data_transfer(user_input, control_channel)
                sv_data = recv_from_control(control_channel)
                print sv_data
                print '\nlist files on server: \n'
                print data
            elif user_input == 'quit':
                numSent = send(user_input, control_channel)
                data = recv_from_control(control_channel)
                print data
                numSent = send('quit successfully', control_channel)
                break
            elif len(user_input) > 2:
                file_name = user_input[4:].strip()
                if 'get' in user_input[:4]:
                    data = data_transfer(user_input, control_channel)
                    if not 'Errno' in data:
                        with open(file_name, 'wb') as file_to_write:
                            file_to_write.write(data)
                    sv_data = recv_from_control(control_channel)
                    print sv_data
                elif 'put' in user_input[:4]:
                    try:
                        fileObj = open(file_name, "rb")
                    except IOError as msg:
                        print msg
                        continue
                    curr_dir = os.getcwd() + '/' + file_name
                    sending_file_size = os.path.getsize(curr_dir)
                    print 'size of sending file: ', sending_file_size, ' bytes'
                    if sending_file_size > 65536:
                        print '[Errno 27] File too large.'
                        print 'Maximum size allowed to send is 65536 bytes'
                    else:
                        send(user_input, control_channel)
                        sv_data = recv_from_control(control_channel)
                        print sv_data
                        print 'open tcp connection for data tranfering...'
                        data_channel = create_data_connection()
                        ephemeral_port = data_channel.getsockname()[1]
                        send(str(ephemeral_port), control_channel)
                        data_sock, addr = data_channel.accept()
                        if data_sock:
                            fileData = fileObj.read()
                            send(fileData, data_sock)
                        data_channel.close()


                else:
                    send(user_input, control_channel)
                    sv_data = recv_from_control(control_channel)
                    print sv_data

    control_channel.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP client side')
    parser.add_argument('host', type=str, help='domain name of server', metavar='<server machine>')
    parser.add_argument('port', type=int, help='server port number', metavar='<server port>')
    args = parser.parse_args()
    main(args.host, args.port)
