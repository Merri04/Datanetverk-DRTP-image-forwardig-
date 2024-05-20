# Datanetverk-DRTP-image-forwardig-

### Overview 

The Reliable Transport Protocol (DRTP) enhance UDP by ensuring reliable, in order data transmission without losses or duplications. This project is developed in Python and rigorously tested within a Mininet environment, highliting the protocol's effectiveness in controlled network scenarios. DRTP is optimized for image forwarding where maintaining the intergity and order of data packets is crucial. 

### Prerequisites

Python3 needs to be installed on your system before getting started: 
- verifly you have this by runing this in the terminal (python --version)


In order to use it in the mininet topology, you'll need to run the **simple_topo.py** code in Ubuntu.

Once you are in Ubuntu, make sure to open the terminal and install mininet:

Mininet provides a virtual test network that runs real kernel, switch, and application code. Install it using: 

```
$ sudo apt-get install mininet

$ sudo apt-get install openvswitch-switch

$ sudo service openvswitch-switch start

$ sudo apt-get install xterm
```
To run the program use this following commands: 
```
$ sudo mn -c
$ sudo fuser -k 6653/tcp
```
# How to run DRTP:
To run this project, you must run it either client or server mode. Server must be started first.

#### Server only arguments: 
Runing the application in server mode allows the server to accept files from a client via its DRTP/UDP. 

write this in the terminal to invoke the server mode:

```$ python3 application.py -s ```

`-s` indicates that the application is running in a server mode. 

Running this will print the following to the terminal: 
``` console

------------------------------------------------------------
Server started at 127.0.0.1:8080
------------------------------------------------------------

SYN packet is received
SYN-ACK packet is sent
ACK packet is received
Connection established

13:00:07.017935 -- packet 1 is received
13:00:07.017998 -- sending ack for the received 1
13:00:07.018466 -- packet 2 is received
13:00:07.018535 -- sending ack for the received 2
13:00:07.018601 -- packet 3 is received
13:00:07.018622 -- sending ack for the received 3
13:00:07.018661 -- packet 4 is received
13:00:07.018683 -- sending ack for the received 4
13:00:07.018733 -- packet 5 is received
13:00:07.018758 -- sending ack for the received 5
13:00:07.018823 -- packet 6 is received
13:00:07.018857 -- sending ack for the received 6
13:00:07.018915 -- packet 7 is received
13:00:07.018935 -- sending ack for the received 7
13:00:07.018970 -- packet 8 is received
13:00:07.018987 -- sending ack for the received 8
13:00:07.019019 -- packet 9 is received
13:00:07.019037 -- sending ack for the received 9
13:00:07.019079 -- packet 10 is received
13:00:07.019100 -- sending ack for the received 10
13:00:07.019137 -- packet 11 is received
13:00:07.019153 -- sending ack for the received 11
13:00:07.019187 -- packet 12 is received
13:00:07.019204 -- sending ack for the received 12
13:00:07.019245 -- packet 13 is received
13:00:07.019264 -- sending ack for the received 13
13:00:07.019304 -- packet 14 is received
13:00:07.019324 -- sending ack for the received 14
13:00:07.019361 -- packet 15 is received
13:00:07.019377 -- sending ack for the received 15
13:00:07.019433 -- packet 16 is received
13:00:07.019452 -- sending ack for the received 16
13:00:07.019488 -- packet 17 is received
13:00:07.019504 -- sending ack for the received 17
13:00:07.019549 -- packet 18 is received
13:00:07.019568 -- sending ack for the received 18
13:00:07.019604 -- packet 19 is received
13:00:07.019619 -- sending ack for the received 19
13:00:07.019654 -- packet 20 is received
13:00:07.019670 -- sending ack for the received 20
13:00:07.019705 -- packet 21 is received
13:00:07.019723 -- sending ack for the received 21

FIN packet is received
FIN-ACK packet is sent
Connection closed

Total data received: 19840 bytes
Total time taken: 0.001959 seconds
Throughput: 81.03 Mbps

Closing server socket
```


### common 

`-h` displace all the options you have as a user. Here you will see, some runs only in the client or the only the server. 

Usage: Python3 application.py -s -h 

it works in both client and server mode. 
it will display this in your terminal: 

```
usage: application.py [-h] [-c] [-s] [-i IP] [-p PORT] [-f FILE] [-w WINDOW] [-d DISCARD]

DRTP: Data Reliable Transfer Protocol based on UDP

options:
  -h, --help            show this help message and exit
  -c, --client          Run in client mode
  -s, --server          Run in server mode
  -i IP, --ip IP        IP address of the server
  -p PORT, --port PORT  Port number
  -f FILE, --file FILE  File to send (required in client mode)
  -w WINDOW, --window WINDOW
                        Sliding window size
  -d DISCARD, --discard DISCARD
                        Sequence number of the packet to discard (server mode) 

```
`-i` Is used to bind to an IP address.The default IP address is 127.0.0.1 
usage: ```python3 application.py -s -i 127.0.0.1```

`-p` Is used to bind to a port. It is by default 8088
usage: ```python3 application.py -s -p 8088```

# Client only arguments 

`-c` --client Run in client mode
Usage:```python3 application.py -c```

`-f` --file Name of the file to send
Usage:```python3 application.py -c -f filename.txt```
Running this will print the following to the terminal: 
``` console
------------------------------------------------------------
Server started at 127.0.0.1:8080
------------------------------------------------------------

SYN packet sent
SYN-ACK packet is received
ACK packet sent
Connection established

Data Transfer:

13:00:07.017861 -- Packet with seq = 1 is sent, sliding window = [1]
13:00:07.018128 -- Packet with seq = 2 is sent, sliding window = [1, 2]
13:00:07.018157 -- Packet with seq = 3 is sent, sliding window = [1, 2, 3]
13:00:07.018180 -- ACK for packet = 1 received
13:00:07.018202 -- Packet with seq = 4 is sent, sliding window = [2, 3, 4]
13:00:07.018566 -- ACK for packet = 2 received
13:00:07.018606 -- Packet with seq = 5 is sent, sliding window = [3, 4, 5]
13:00:07.018661 -- ACK for packet = 3 received
13:00:07.018688 -- Packet with seq = 6 is sent, sliding window = [4, 5, 6]
13:00:07.018714 -- ACK for packet = 4 received
13:00:07.018735 -- Packet with seq = 7 is sent, sliding window = [5, 6, 7]
13:00:07.018775 -- ACK for packet = 5 received
13:00:07.018800 -- Packet with seq = 8 is sent, sliding window = [6, 7, 8]
13:00:07.018887 -- ACK for packet = 6 received
13:00:07.018928 -- Packet with seq = 9 is sent, sliding window = [7, 8, 9]
13:00:07.018956 -- ACK for packet = 7 received
13:00:07.018981 -- Packet with seq = 10 is sent, sliding window = [8, 9, 10]
13:00:07.019004 -- ACK for packet = 8 received
13:00:07.019025 -- Packet with seq = 11 is sent, sliding window = [9, 10, 11]
13:00:07.019046 -- ACK for packet = 9 received
13:00:07.019067 -- Packet with seq = 12 is sent, sliding window = [10, 11, 12]
13:00:07.019130 -- ACK for packet = 10 received
13:00:07.019165 -- Packet with seq = 13 is sent, sliding window = [11, 12, 13]
13:00:07.019196 -- ACK for packet = 11 received
13:00:07.019218 -- Packet with seq = 14 is sent, sliding window = [12, 13, 14]
13:00:07.019236 -- ACK for packet = 12 received
13:00:07.019256 -- Packet with seq = 15 is sent, sliding window = [13, 14, 15]
13:00:07.019274 -- ACK for packet = 13 received
13:00:07.019294 -- Packet with seq = 16 is sent, sliding window = [14, 15, 16]
13:00:07.019355 -- ACK for packet = 14 received
13:00:07.019391 -- Packet with seq = 17 is sent, sliding window = [15, 16, 17]
13:00:07.019430 -- ACK for packet = 15 received
13:00:07.019454 -- Packet with seq = 18 is sent, sliding window = [16, 17, 18]
13:00:07.019476 -- ACK for packet = 16 received
13:00:07.019495 -- Packet with seq = 19 is sent, sliding window = [17, 18, 19]
13:00:07.019515 -- ACK for packet = 17 received
13:00:07.019535 -- Packet with seq = 20 is sent, sliding window = [18, 19, 20]
13:00:07.019581 -- ACK for packet = 18 received
13:00:07.019609 -- Packet with seq = 21 is sent, sliding window = [19, 20, 21]
13:00:07.019629 -- ACK for packet = 19 received
13:00:07.019682 -- ACK for packet = 20 received
13:00:07.019733 -- ACK for packet = 21 received

Sending FIN packet
Connection closed
```



`-w` Is to decide how many packets per window 
Set the window size, default 3 packets per window this needs to be the same as the
client
Usage:```python3 application.py -s -w 10```
Running this will print the following to the terminal: 

``` console
------------------------------------------------------------
Server started at 127.0.0.1:8080
------------------------------------------------------------

SYN packet sent
SYN-ACK packet is received
ACK packet sent
Connection established

Data Transfer:

13:06:38.245943 -- Packet with seq = 1 is sent, sliding window = [1]
13:06:38.245992 -- Packet with seq = 2 is sent, sliding window = [1, 2]
13:06:38.246015 -- Packet with seq = 3 is sent, sliding window = [1, 2, 3]
13:06:38.246037 -- Packet with seq = 4 is sent, sliding window = [1, 2, 3, 4]
13:06:38.246058 -- Packet with seq = 5 is sent, sliding window = [1, 2, 3, 4, 5]
13:06:38.246081 -- Packet with seq = 6 is sent, sliding window = [1, 2, 3, 4, 5, 6]
13:06:38.246107 -- Packet with seq = 7 is sent, sliding window = [1, 2, 3, 4, 5, 6, 7]
13:06:38.246137 -- Packet with seq = 8 is sent, sliding window = [1, 2, 3, 4, 5, 6, 7, 8]
13:06:38.246176 -- Packet with seq = 9 is sent, sliding window = [1, 2, 3, 4, 5, 6, 7, 8, 9]
13:06:38.246217 -- Packet with seq = 10 is sent, sliding window = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
13:06:38.246258 -- ACK for packet = 1 received
13:06:38.246296 -- Packet with seq = 11 is sent, sliding window = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
13:06:38.246332 -- ACK for packet = 2 received
13:06:38.246373 -- Packet with seq = 12 is sent, sliding window = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
13:06:38.246446 -- ACK for packet = 3 received
13:06:38.246498 -- Packet with seq = 13 is sent, sliding window = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
13:06:38.246551 -- ACK for packet = 4 received
13:06:38.246602 -- Packet with seq = 14 is sent, sliding window = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
13:06:38.246651 -- ACK for packet = 5 received
13:06:38.246699 -- Packet with seq = 15 is sent, sliding window = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
13:06:38.246739 -- ACK for packet = 6 received
13:06:38.246775 -- Packet with seq = 16 is sent, sliding window = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
13:06:38.246808 -- ACK for packet = 7 received
13:06:38.246841 -- Packet with seq = 17 is sent, sliding window = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
13:06:38.246879 -- ACK for packet = 8 received
13:06:38.246914 -- Packet with seq = 18 is sent, sliding window = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
13:06:38.246945 -- ACK for packet = 9 received
13:06:38.246977 -- Packet with seq = 19 is sent, sliding window = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
13:06:38.247009 -- ACK for packet = 10 received
13:06:38.247043 -- Packet with seq = 20 is sent, sliding window = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
13:06:38.247080 -- ACK for packet = 11 received
13:06:38.247112 -- Packet with seq = 21 is sent, sliding window = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
13:06:38.247134 -- ACK for packet = 12 received
13:06:38.247150 -- ACK for packet = 13 received
13:06:38.247167 -- ACK for packet = 14 received
13:06:38.247183 -- ACK for packet = 15 received
13:06:38.247199 -- ACK for packet = 16 received
13:06:38.247221 -- ACK for packet = 17 received
13:06:38.247238 -- ACK for packet = 18 received
13:06:38.247254 -- ACK for packet = 19 received
13:06:38.247269 -- ACK for packet = 20 received
13:06:38.247349 -- ACK for packet = 21 received

Sending FIN packet
Connection closed
```

#### Common options:
```
-h, --help show this help message and exit
Usage:```python3 application.py -h```

-i, --ip IP address to connect/bind to, in dotted decimal notation. Default 127.0.0.1

* Usage:```python3 application.py -i 127.0.0.1```

-p, --port Port to use, default 8088

Usage: ```python3 application.py -p 8080```
```


### Troubleshooting

If the save folder does not exist, it will automaticly be created. If the file already exists and you send it again, it will be overwritten.





