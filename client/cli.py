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


def send_command(cmd, control_sock, data_sock=None):
    if cmd:
        cmd_size_string = str(len(cmd))
        while len(cmd_size_string) < 10:
            cmd_size_string = '0' + cmd_size_string
        cmd_data = cmd_size_string + cmd
        if not 'quit' in cmd:
            cmd_data += str(data_sock.getsockname()[1])
        print 'Packet being sent: ', cmd_data
        numSent = 0
        while len(cmd_data) > numSent:
            numSent += control_sock.send(cmd_data[numSent:])
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


def transfer(user_input, control_sock):
    print 'open tcp connection for data tranfering...'
    data_channel = create_data_connection()
    numSent = send_command(user_input, control_sock, data_channel)
    data_sock, addr = data_channel.accept()
    data_size_buff = recvAll(data_sock, 10)
    # print str(data_size_buff), 'data size buff'
    data_size = int(data_size_buff)
    data = recvAll(data_sock, data_size)
    data_channel.close()
    print 'close tcp connection for data tranfering...'
    return data


def main(host, port):
    control_channel = create_control_connection(host, port)
    if (control_channel):
        while True:
            user_input = raw_input('ftp> ')

            if user_input == 'ls':
                # data_channel = create_data_connection()
                # numSent = send_command(user_input, control_channel, data_channel)
                # data_sock, addr = data_channel.accept()
                # data_size_buff = recvAll(data_sock, 10)
                # data_size = int(data_size_buff)
                # data = recvAll(data_sock, data_size)
                # print(data)
                data = transfer(user_input, control_channel)
                print data
                # data_channel.close()
            elif user_input == 'quit':
                numSent = send_command(user_input, control_channel)
                break
            elif len(user_input) > 2:
                # curr_dir = os.getcwd()
                file_name = user_input[4:].strip()
                if 'get' in user_input[:4]:
                    data = transfer(user_input, control_channel)
                    if not 'Errno' in data:
                        # with open(os.path.join(curr_dir, file_name), 'wb') as file_to_write:
                        with open(file_name, 'wb') as file_to_write:
                            file_to_write.write(data)
                        print 'success'
                    else:
                        print 'fail'
                        print data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP client side')
    parser.add_argument('host', type=str, help='domain name of server', metavar='<server machine>')
    parser.add_argument('port', type=int, help='server port number', metavar='<server port>')
    args = parser.parse_args()
    main(args.host, args.port)
