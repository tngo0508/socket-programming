import socket
import sys
import argparse
import commands
import os

def create_connection(port):
    """create a TCP connection for control data_channel

    Args:
        port: Port number for FTP

    Returns:
        a welcome socket for control channel. Server will use this Socket
        to send status/error and receive commands from client
    """
    listenPort = port

    # Create a welcome socket.
    welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    welcomeSock.bind(('', port))

    # Start listening on the socket
    welcomeSock.listen(1)
    return welcomeSock


def recvAll(sock, numBytes):
    """Receives the specified number of bytes from the specified Socket

    Args:
        sock: the socket from which to receive
        numBytes: the number of bytes to receive

    Returns:
        The bytes recieved
    """
    recvBuff = '' # The buffer
    tmpBuff = '' # The temporary buffer

    # Keep receiving till all is received
    while len(recvBuff) < numBytes:
        tmpBuff = sock.recv(numBytes) # Attempt to receive bytes
        if not tmpBuff: # The other side has closed the socket
            break
        recvBuff += tmpBuff # Add the received bytes to the buffer
    return recvBuff


def send(data, sock):
    """Send data from server to client through a specified socket

    Args:
        data: the data from which client recieve
        sock: the socket from which to receive

    Returns:
        The number of bytes is sent if success. Otherwise, return 0
    """
    if data:

        # Get size of the data read and convert it to string
        data_size_string = str(len(data))

        # Prepend 0's to the size string until the size is 10 bytes
        # This is used for adding a header indicating the size of
        # file being sent
        while len(data_size_string) < 10:
            data_size_string = '0' + data_size_string

        # Prepend the size of data (header) to the file data
        fileData = data_size_string + data

        numSent = 0 # The number of bytes sent

        # Keep sending data until all bytes are sent
        while len(fileData) > numSent:
            numSent += sock.send(fileData[numSent:])
        return numSent
    return 0


def connect_to_data_channel(serverAddr, serverPort):
    """Connect to an open socket on data channel

    Args:
        serverAddr: Address of the host opened data channel
        serverPort: Port number of the host opened data channel

    Returns:
        Retrieve the connection socket for data transfering if success.
        Otherwise, return None if cannot connect to server
    """
    try:
        print 'open tcp connection for data transfering...'

        # Create a TCP socket
        connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        connSock.connect((serverAddr, serverPort))
        return connSock
    except socket.error as msg:
        print msg
        return connSock is None


def recv_from_client(sock):
    """Receive data from client on control channel

    Args:
        sock: the socket from which server uses for control channel

    Returns:
        The data which client sends to server on control channel.
        If there is a TCP buffer overflow, return None
    """
    data_size_buff = recvAll(sock, 10) # Get the header

    # Check for TCP buffer overflow
    if int(data_size_buff) > 65536:
        return None
    data_size = int(data_size_buff)
    data = recvAll(sock, data_size) # Receive data from client
    return data


def recv_ephemeral_port(sock, serverAddr):
    port_size = 0
    port_size_buff = ''
    ephemeral_port = ''
    ephemeral_port = recvAll(sock, 5)
    print 'emphemeral port: ', ephemeral_port
    return ephemeral_port


def main(port):
    # Create a welcome socket for control connection
    welcomeSock = create_connection(port)
    print'Waiting for connection...'
    clientSock, addr = welcomeSock.accept() # Accept connection

    # Get client's IP address
    client_addr = socket.gethostbyaddr(str(addr[0]))
    print 'Accepted connection from client: ', addr
    print '\n'

    # Accept connection forever
    while True:
        cmd_size_buff = '' # The temporary buffer for incoming command
        cmd_size = 0 # The size of incoming command
        client_cmd = '' # The buffer to commmand received from client

        # Receive the first 10 bytes indicating the size of the file
        cmd_size_buff = recvAll(clientSock, 10)
        print 'Size of incoming command: ', cmd_size_buff

        cmd_size = int(cmd_size_buff)
        print 'The command size is ', cmd_size, 'bytes'

        # Receive the commmand from client
        client_cmd = recvAll(clientSock, cmd_size).strip()
        print 'executing command: ', client_cmd

        if client_cmd == 'ls':
            ephemeral_port = recv_ephemeral_port(clientSock,client_addr[0])
            data_channel = connect_to_data_channel(client_addr[0], int(ephemeral_port))
            lines = ''
            for line in commands.getoutput('ls -l'):
                lines += str(line)
            print lines
            if send(lines, data_channel):
                send('server: executed successfully...', clientSock)
                print 'response success...\n'
            else:
                send('server: cannot execute command...', clientSock)
                print 'response fail...\n'
        elif client_cmd == 'quit':
            send('server: ack quit', clientSock)
            data = recv_from_client(clientSock)
            print data
            break
        elif len(client_cmd) > 2:
            file_name = client_cmd[4:]
            if 'get' in client_cmd[:4]:
                ephemeral_port = recv_ephemeral_port(clientSock, client_addr[0])
                data_channel = connect_to_data_channel(client_addr[0], int(ephemeral_port))
                print 'Sending ', file_name
                fileObj = None
                try:
                    fileObj = open(file_name, "rb")
                except IOError as msg:
                    send(str(msg), data_channel)
                    send(str(msg), clientSock)

                if fileObj:
                    curr_dir = os.getcwd() + '/' + file_name
                    req_file_size = os.path.getsize(curr_dir)
                    print 'file size: ', req_file_size, 'bytes'
                    if req_file_size > 65536:
                        msg = 'server: [Errno 27] File too large.'
                        if send(msg, data_channel):
                            print 'response success...\n'
                        else:
                            print 'response fail...\n'
                        send(msg, clientSock)
                    else:
                        fileData = fileObj.read()
                        if send(fileData, data_channel):
                            send('server: executed successfully...', clientSock)
                            print 'response success...\n'
                        else:
                            send('server: cannot execute commmand...', clientSock)
                            print 'response fail...\n'
            elif 'put' in client_cmd[:4]:
                print 'Downloading ', file_name, '...'
                send('server: ACK, prepare to receive', clientSock)
                ephemeral_port = recv_from_client(clientSock)
                data_channel = connect_to_data_channel(client_addr[0], int(ephemeral_port))
                data = recv_from_client(data_channel)
                if data:
                    with open(file_name, 'wb') as file_to_write:
                        file_to_write.write(data)
                        send('server: executed successfully...', data_channel)
                        print 'success'
                else:
                    print 'cannot execute command...'
                    send('server: cannot execute command...', data_channel)
                    print data
                data_channel.close()
            else:
                send('server: command not found...', clientSock)

    clientSock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP server side')
    parser.add_argument('port', type=int, help='server port number', metavar='<PORT NUMBER>')
    args = parser.parse_args()
    main(args.port)
