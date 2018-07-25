import socket
import os
import sys
import argparse
import commands

def create_data_connection():
    """Establish data channel for transfering data

    Returns:
        The socket from which ephemeral port is created for
        data tranfering between client and server
        Otherwise, return None if socket is not created
    """
    try:
        # Create a socket
        welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Binding the socket to port 0
        welcomeSock.bind(('', 0))

        # Check for the ephemeral port number
        print 'ephemeral port: ', welcomeSock.getsockname()[1]

        # Start listening on the socket
        welcomeSock.listen(1)
        return welcomeSock
    except socket.error as msg:
        print 'Socket error: ', msg
        return welcomeSock is None


def create_control_connection(serverAddr, serverPort):
    """Connect to control channel to send commands to server

    Args:
        serverAddr: the server's IP address
        serverPort: the server's Port number

    Returns:
        The connectioned socket for control channel
    """
    try:
        # Create a TCP socket
        connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        connSock.connect((serverAddr, serverPort))
        return connSock
    except socket.error as msg:
        print 'Socket error: ', msg
        return connSock is None


def send(data, sock, data_sock=None):
    """Send data from client to server using a specified socket

    Args:
        data: the data that client wants to send to server
        sock: the specified socket for transferring data
        data_sock: the socket from which data connection uses

    Returns:
        The number of bytes is sent if success.
        Otherwise, return 0 if fail sending data
    """
    if data:
        # Get the size of the sending data and convert to string
        data_size_string = str(len(data))

        # Prepend 0's to the size string until the size is 10 bytes
        # The first 10 bytes created is for header which indicating
        # the size of data being sent
        while len(data_size_string) < 10:
            data_size_string = '0' + data_size_string

        # Prepend the size of the data to the file data
        new_data = data_size_string + data

        # Append the ephemeral_port at the end of the packet
        # if the command contains one of three keywords
        if any(cmd in data for cmd in ['ls', 'get', 'put']) and data_sock:
            new_data += str(data_sock.getsockname()[1])
        print 'Packet being sent: ', new_data

        # The number of bytes sent
        numSent = 0

        # Keep sending the data until all bytes sent
        while len(new_data) > numSent:
            numSent += sock.send(new_data[numSent:])
        print 'Sent', numSent, 'bytes'
        return numSent
    return 0


def recvAll(sock, numBytes):
    """Receives the specified number of bytes from the specified socket

    Args:
        sock: the socket from which to receive
        numBytes: the number of bytes to receive

    Returns:
        The bytes received
    """
    recvBuff = '' # The buffer
    tmpBuff = '' # The temporary buffer

    # Keep receiving till all is received
    while len(recvBuff) < numBytes:

        # Attempt to receive bytes
        tmpBuff = sock.recv(numBytes)

        # The other side has closed the socket
        if not tmpBuff:
            break

        # Add the received bytes to the buffer
        recvBuff += tmpBuff
    return recvBuff


def data_transfer(user_input, control_sock):
    """Establish data channel for sending and receiving data.
    Firstly, it creates data connection for tranferring between
    client and server. Secondly, it sends the command line to server.
    Thirdly, it waits until server sends a response on data channel.
    Finally, it gets the data from server.

    Args:
        user_input: the command line that user enter on console
        control_sock: the socket from which uses for control channel

    Returns:
        The data that received from other side
    """
    print 'open tcp connection for data tranfering...'

    # Open data connection
    data_channel = create_data_connection()

    # Send command line to server
    numSent = send(user_input, control_sock, data_channel)

    # Accept connection from server
    data_sock, addr = data_channel.accept()

    # Get the size of received packet
    data_size_buff = recvAll(data_sock, 10)
    data_size = int(data_size_buff)

    # Get the data from server
    data = recvAll(data_sock, data_size)
    data_channel.close()
    print 'close tcp connection for data tranfering...'
    return data


def recv_from_control(control_sock):
    """Received data (status/error) from server using control channel

    Args:
        control_sock: the socket that control channel uses

    Returns:
        The status or error data from server
    """
    data_size_buff = recvAll(control_sock, 10) # Get the header
    data_size = int(data_size_buff)
    data = recvAll(control_sock, data_size) # Get the actual data
    return data


def main(host, port):
    # Create control connection
    control_channel = create_control_connection(host, port)
    if control_channel:
        # Accept connection forever
        while True:
            print '\n'
            user_input = raw_input('ftp> ').strip() # Get user's input

            if user_input == 'ls':
                # Send the command to server and receive data
                # from server
                data = data_transfer(user_input, control_channel)

                # Receive that status/error from server
                sv_data = recv_from_control(control_channel)
                print sv_data
                print '\nlist files on server: \n'
                print data
            elif user_input == 'quit':
                # Closing the control connection using 3-way handshake
                # Send FIN packet
                numSent = send(user_input, control_channel)

                # Receive ACK AND FIN packet from server
                data = recv_from_control(control_channel)
                print data

                # Send ACK packet
                numSent = send('quit successfully', control_channel)
                break
            elif len(user_input) > 2:
                file_name = user_input[4:].strip() # Get the file's name

                # Downloading file from server
                if 'get' in user_input[:4]:

                    # Send the command to server and receive data
                    # from server
                    data = data_transfer(user_input, control_channel)

                    if not 'Errno' in data:

                        # Create file with the received data
                        with open(file_name, 'wb') as file_to_write:
                            file_to_write.write(data)

                    # Receive the status/error from server
                    sv_data = recv_from_control(control_channel)
                    print sv_data

                # Uploading file to server
                elif 'put' in user_input[:4]:

                    # Check if file is opened or not
                    try:
                        fileObj = open(file_name, "rb")
                    except IOError as msg:
                        print msg
                        continue

                    # Get the size of sending file
                    curr_dir = os.getcwd() + '/' + file_name
                    sending_file_size = os.path.getsize(curr_dir)
                    print 'size of sending file: ', sending_file_size, ' bytes'

                    # Check for TCP buffer overflow
                    if sending_file_size > 65536:
                        print '[Errno 27] File too large.'
                        print 'Maximum size allowed to send is 65536 bytes'
                    else:

                        # Send command to server
                        send(user_input, control_channel)

                        # Receive ACK from server
                        sv_data = recv_from_control(control_channel)
                        print sv_data
                        print 'open tcp connection for data tranfering...'

                        # Open data connection for transerring data
                        data_channel = create_data_connection()

                        # Get ephemeral port for data connection
                        ephemeral_port = data_channel.getsockname()[1]

                        # Send ephemeral port to server for data
                        # connection through control channel
                        send(str(ephemeral_port), control_channel)

                        # Accept connection from server in
                        # data connecction
                        data_sock, addr = data_channel.accept()

                        # Uploading file
                        if data_sock:
                            fileData = fileObj.read()
                            send(fileData, data_sock)
                        data_channel.close()

                # Send the unknown commands to server
                else:

                    # Send the unknown commands to server
                    send(user_input, control_channel)

                    # Get status/error data from server
                    sv_data = recv_from_control(control_channel)
                    print sv_data

    control_channel.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Socket Programming for FTP client side')
    parser.add_argument('host', type=str, help='domain name of server', metavar='<server machine>')
    parser.add_argument('port', type=int, help='server port number', metavar='<server port>')
    args = parser.parse_args()
    main(args.host, args.port)
