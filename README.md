# socket-programming

Author: Thomas Ngo <br />
Instructor: Dr. Yun Tian <br />
California University State, Fullerton

## Project Description

In this assignment, I will implement (simplified) FTP server and FTP client. The client shall connect to the server and support uploading and downloading of files to/from server.

## How to execute

Make sure you change user permission to execute the program
```
$ chmod u+x project.py
```
### server
- Copy and paste _serv.py_ into your server's machine
- Type the following command to get help instruction
```
$ python serv.py -h
```
**USAGE**
```
usage: serv.py [-h] <PORT NUMBER>

Socket Programming for FTP server side

positional arguments:
  <PORT NUMBER>  server port number

optional arguments:
  -h, --help     show this help message and exit
```
**Example**
```
$ python serv.py 1234
```
Or if you are using _ecs.fullerton.edu_. Type the following in your terminal
```
$ ssh <your_username>@ecs.fullerton.edu
Last login: Tue Jul 24 01:22:30 2018 from 76.89.212.85
[<your_username>@jupiter ~]$ python serv.py <PORT NUMBER>
```
### client
- Make sure to run _serv.py_ before _cli.py_
- Copy and paste _cli.py_ into your server's machine. _cli.py_ and _serv.py_ need to be placed on different directories.
- Type the following command to get help instruction
```
$ python cli.py -h
```
**USAGE**
```
usage: cli.py [-h] <server machine> <server port>

Socket Programming for FTP client side

positional arguments:
  <server machine>  domain name of server
  <server port>     server port number

optional arguments:
  -h, --help        show this help message and exit
```
**Example**
```
$ python cli.py localhost 1234
```
Or if you are using _ecs.fullerton.edu_. Type the following in your terminal
```
$ python cli.py ecs.fullerton.edu <PORT NUMBER>
```
Type one of the following commands to use FTP socket:
```
ftp> get <file name> (downloads file <file name> from the server)
ftp> put <filename> (uploads file <file name> to the server)
ftp> ls (lists files on the server)
ftp> quit (disconnects from the server and exits)
```
