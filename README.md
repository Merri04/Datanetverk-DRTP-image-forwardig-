# Datanetverk-DRTP-image-forwardig-

### Overview 

The Reliable Transport Protocol (DRTP) enhance UDP by ensuring reliable, in order data transmission without losses or duplications. This project is developed in Python and rigorously tested within a Mininet environment, highliting the protocol's effectiveness in controlled network scenarios. DRTP is optimized for image forwarding where maintaining the intergity and order of data packets is crucial. 

### Prerequisites

Python3 needs to be installed on your system before getting started: 
- verifly you have this by runing this in the terminal (python --version)


In order to use it in the mininet topology, you'll need to run the **simple_topo.py** code in Ubuntu.

Once you are in Ubuntu, make sure to open the terminal and install mininet:

Mininet provides a virtual test network that runs real kernel, switch, and application code. Install it using: 

$ sudo apt-get install mininet

If necessary, install also: 

$ sudo apt-get install openvswitch-switch

$ sudo service openvswitch-switch start

Xterm is used to open multiple terminal windows from within Mininet. Install it using: 

$ sudo apt-get install xterm


# How to run DRTP:
To run this project, you must run it either client or server mode. Server must be started first.

#### Server only arguments: 
Runing the application in server mode allows the server to accept files from a client via its DRTP/UDP. 

write this in the terminal to invoke the server mode:

```$ python3 application.py -s ```

`-s` indicates that the application is running in a server mode. 

Running this will print the following to the terminal: 
```Server started at <IP> : <PORT>```


### common 

`-h` displace all the options you have as a user. Here you will see, some runs only in the client or the only the server. 

Usage: Python3 application.py -s -h 

it works in both client and server mode. 
it will display this in your terminal: 


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


`-i` Is used to bind to an IP address.The default IP address is 127.0.0.1 
usage: `python3 application.py -s -i 127.0.0.1`

`-p` Is used to bind to a port. It is by default 8088
usage: `python3 application.py -s -p 8088`

# Client only arguments 

-c, --client Run in client mode
Usage `python3 application.py -c`

-f, --file Name of the file to send
Usage `python3 application.py -c -f filename.txt`


`-w` Is to decide how many packets per window 
Set the window size, default 3 packets per window this needs to be the same as the
client
Usage `python3 application.py -s -w 10`

19:37:15 -- Packet with seq = 10 is sent, sliding window = [8, 9, 10]
19:37:15 -- ACK for packet = 8 received
19:37:15 -- Packet with seq = 11 is sent, sliding window = [9, 10, 11]
19:37:15 -- ACK for packet = 9 received
19:37:15 -- Packet with seq = 12 is sent, sliding window = [10, 11, 12]
19:37:15 -- ACK for packet = 10 received
19:37:15 -- Packet with seq = 13 is sent, sliding window = [11, 12, 13]
19:37:15 -- ACK for packet = 11 received

#### Common options:

-h, --help show this help message and exit
Usage `python3 application.py -h`

-i, --ip IP address to connect/bind to, in dotted decimal notation. Default 127.0.0.1

* Usage `python3 application.py -i 127.0.0.1`

-p, --port Port to use, default 8088

Usage `python3 application.py -p 8080`



### Troubleshooting

If the save folder does not exist, it will automaticly be created. If the file already exists and you send it again, it will be overwritten.





