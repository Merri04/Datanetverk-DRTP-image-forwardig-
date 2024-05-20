import datetime
import socket
import struct
import os
import time
from config import *

class DRTPBase:
    def __init__(self, ip, port, window_size=3):
        """THis class initializes the DRTPBase class.
        Args:
            ip (str): The IP address of the server.
            port (int): The port number to bind the socket.
            window_size (int): The size of the sliding window.

        use: Sets up the socket, configurations and prototocol.
        variables:
            TIMEOUT_INTERVAL (int): The timeout interval for the socket.
            HEADER_FORMAT (str): The format of the packet header.
            HEADER_SIZE (int): The size of the packet header.
            DATA_SIZE (int): The size of the data in the packet.
            PACKET_SIZE (int): The size of the packet. (header + data)
            SYN (int): The SYN flag for the packet.
            ACK (int): The ACK flag for the packet.
            FIN (int): The FIN flag for the packet.
            socket (socket): UDP socket for communication.
            ip (str): The IP address of the server.
            port (int): The port number.
            window_size (int): The size of the sliding window.
            expected_seq (int): The next expected sequence number (server-side)
            next_seq_num (int): The next sequence number to be sent. (client-side)
            window (list): The sliding window. (client-side) 3,5 or 10
            send_buffer (dict): The dictionary to store the packets to be sent. 
        """
        self.TIMEOUT_INTERVAL = TIMEOUT_INTERVAL
        self.HEADER_FORMAT = HEADER_FORMAT
        self.HEADER_SIZE = HEADER_SIZE
        self.DATA_SIZE = DATA_SIZE
        self.PACKET_SIZE = PACKET_SIZE
        self.SYN = SYN
        self.ACK = ACK
        self.FIN = FIN
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.window_size = window_size
        self.expected_seq = 1
        self.next_seq_num = 1
        self.window = []
        self.send_buffer = {} 

    def encode_header(self, seq_num, ack_num, flags):
        """
        Encodes the header of the packet.
        Args:
            seq_num (int): The sequence number of the packet.
            ack_num (int): The acknowledgment number of the packet.
            flags (int): The flags for the packet (SYN, ACK, FIN).
        Returns:
        encoded header as bytes
        """
        return struct.pack(self.HEADER_FORMAT, seq_num, ack_num, flags)

    def decode_header(self, packet):
        """
        Decodes the header of the packet.
        Args:
            packet (bytes): The packet received.
        Returns:
        tuple of (seq_num, ack_num, flags)
        """
        return struct.unpack(self.HEADER_FORMAT, packet[:self.HEADER_SIZE])

    def send_packet(self, seq_num, ack_num, flags, data=b'', addr=None):
        """
        send_packet sends a packet to the specified address.
        Args:
            seq_num (int): The sequence number of the packet.
            ack_num (int): The acknowledgment number of the packet.
            flags (int): The flags for the packet (SYN, ACK, FIN).
            data (bytes): The data to be sent in the packet.
            addr (tuple): The address to send the packet to.
        return: None

        """
        packet = self.encode_header(seq_num, ack_num, flags) + data
        if addr is None:
            addr = (self.ip, self.port)
        self.socket.sendto(packet, addr)
        #print(f"Packet sent: Seq={seq_num}, Ack={ack_num}, Flags={flags}, Data={data[:20]}... to {addr}")

    def receive_packet(self):
        """
        receive_packet receives a packet.
        args: None
        return: tuple of (header, data, address)
        header: tuple of (seq_num, ack_num, flags)
        data: Data received in the packet
        address: The address from which the packet is received.
        """
        packet, addr = self.socket.recvfrom(self.PACKET_SIZE)
        seq_num, ack_num, flags = self.decode_header(packet)
        data = packet[self.HEADER_SIZE:]
        #print(f"Packet received: Seq={seq_num}, Ack={ack_num}, Flags={flags}, Data={data[:20]}... from {addr}")
        return (seq_num, ack_num, flags), data, addr
      

class DRTPServer(DRTPBase):
    def __init__(self, ip, port, window_size=3, discard=None):
        """
        this class initializes the DRTPServer class.
        Args:
            ip (str): The IP address of the server.
            port (int): The port number to bind the socket.
            window_size (int): The size of the sliding window default 3.
            discard (int): The sequence number of the packet to discard default None.
        use: Sets up the socket, configurations, socket binding and initial state.
        variables:
            discard_seq (int): The sequence number of the packet to discard.
            connection_state (str): The state of the connection (LISTEN, SYN_RCVD, ESTABLISHED, CLOSED).
            socket (socket): UDP socket for communication.
            ip (str): The IP address of the server.
            port (int): The port number.
            window_size (int): The size of the sliding window.
            last_acked_seq (int): The last acknowledged sequence number.
            buffered_packets (dict): The dictionary to store out-of-order packets.
            total_data_received (int): The total data received by the server.
            start_time (float): The start time of the connection when the data transfer started.
            end_time (float): The end time of the connection when the data transfer ended.
        """
        super().__init__(ip, port, window_size)
        self.discard_seq = discard
        self.connection_state = "LISTEN"
        self.socket.bind((self.ip, self.port))
        self.last_acked_seq = 0
        self.buffered_packets = {}
        self.total_data_received = 0  
        self.start_time = None
        self.end_time = None


    def run(self):
        """
        run starts the server and listens for incoming packets.
        args: None
        return: None
        use:continuously listens for incoming packets and processes them based on the connection state.
        """
        #print("discard_seq", self.discard_seq)
        print(split_line)
        print(f"Server started at {self.ip}:{self.port}")
        print(split_line)
        print() # just to have some space
        packet_discarded = False
        try:
            while self.connection_state != "CLOSED":
                header, data, addr = self.receive_packet()
                #print("printing data received  ", len(data))
                if header:
                    seq_num, ack_num, flags = header
                    if self.discard_seq and int(self.discard_seq) == seq_num and not packet_discarded:
                        print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- packet {seq_num} is intentionally discarded")
                        packet_discarded = True
                        continue
                    if flags & self.SYN and self.connection_state == "LISTEN":
                        self.handle_syn(seq_num, addr)
                    elif flags & self.ACK and self.connection_state == "SYN_RCVD":
                        self.start_time = time.perf_counter() 
                        self.handle_established()
                    elif flags & self.FIN and self.connection_state == "ESTABLISHED":
                        self.end_time = time.perf_counter()  # End time of the connection
                        print() # just to have some space
                        self.handle_fin(seq_num, addr)
                        print() # just to have some space
                    elif self.connection_state == "ESTABLISHED":
                        self.handle_data_packet(seq_num, data, addr)

        except KeyboardInterrupt:
            print("Keyboard interrupt detected")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.calculate_throughput()

            print() # just to have some space
            self.close()

    def handle_syn(self, seq_num, addr):
        """
        Handles the SYN packet to establish a connection.
        Args:
            seq_num (int): The sequence number of the SYN packet.
            addr (tuple): The address from which the SYN packet is received.
        use: Sends a SYN-ACK packet and update the connection state to SYN_RCVD.    
        """
        print("SYN packet is received")
        self.send_packet(0, seq_num + 1, self.SYN | self.ACK, addr=addr)
        print("SYN-ACK packet is sent")
        self.connection_state = "SYN_RCVD"

    def handle_established(self):
        """
        Handles the ACK packet to establish a connection.
        Args: None
        use: Updates the connection state to ESTABLISHED.
        """
        print("ACK packet is received")
        print("Connection established")
        print() # just to have some space
        self.connection_state = "ESTABLISHED"
        

    def handle_fin(self, seq_num, addr):
        """
        Handles the FIN packet to close the connection.
        Args:
            seq_num (int): The sequence number of the FIN packet.
            addr (tuple): The address from which the FIN packet is received.
        use: Sends a FIN-ACK packet and update the connection state to CLOSED.
        """
        print("FIN packet is received")
        self.send_packet(seq_num + 1, 0, self.ACK, addr=addr)
        print("FIN-ACK packet is sent")
        self.connection_state = "CLOSED"
        print("Connection closed")

    #def close(self):
     #   self.socket.close()

            

    def handle_data_packet(self, seq_num, data, addr):
        """
        Handles the data packet received.
        Args:
            seq_num (int): The sequence number of the packet.
            data (bytes): The data received in the packet.
            addr (tuple): The address from which the packet is received.
        use: Writes the data to the file and sends an ACK packet and buffering for out-of-order packets.
        """
        if not hasattr(self, 'filepath'): 
        # Assume the first packet contains the filename
            if data.startswith(b'FILENAME:'):
                filename = data.decode().split(':')[1]  # Extract filename from packet
                directory = "received_files"
                if not os.path.exists(directory):
                    os.makedirs(directory)
                self.filepath = os.path.join(directory, filename)
                print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- packet {seq_num} is received") #new
                self.send_packet(0, seq_num, self.ACK, addr=addr) #new
                self.last_acked_seq += 1 #new
                print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- sending ack for the received {seq_num}") #new
                #print(f"Filename set to {self.filepath}")
                return  # Do not write this packet's data to file

        # Write data to the file specified by the first packet
        with open(self.filepath, "ab") as file:
            file.write(data)
        #print(f"Data written to {self.filepath}")

        if seq_num == self.last_acked_seq + 1:
            # Track total packet received not data as it is not the whole package
            self.total_data_received += len(data) # Track total packet received
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- packet {seq_num} is received")
            self.send_packet(0, seq_num, self.ACK, addr=addr)
            self.last_acked_seq += 1
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- sending ack for the received {seq_num}")
            self.process_buffered_packets(addr)
        elif seq_num > self.last_acked_seq + 1:
            self.buffered_packets[seq_num] = data
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- out-of-order packet {seq_num} is received")
            #make a logic that handles discarding of packets
            if seq_num == self.discard_seq:
                print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- packet {seq_num} is discarded")
        else:
            print(f"{time.strftime('%H:%M:%S.%f')[:-3]} -- duplicate packet {seq_num} is received")
            self.send_packet(0, seq_num, self.ACK, addr=addr)
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- sending ack for the duplicate received {seq_num}")

    def process_buffered_packets(self, addr):
        """
        process_buffered_packets processes the buffered packets that are received out-of-order.
        Args:
            addr (tuple): The address to send the ACK packet.
        use: Sends an ACK packet for the buffered packets and updates the last acknowledged sequence number. 
        """
        # Attempt to process any buffered packets that can now be accepted
        while self.last_acked_seq + 1 in self.buffered_packets:
            seq_num = self.last_acked_seq + 1
            data = self.buffered_packets.pop(seq_num)
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- packet {seq_num} from buffer is now received")
            self.send_packet(0, seq_num, self.ACK, addr=addr)
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- sending ack for the buffered received {seq_num}")
            self.last_acked_seq = seq_num

    def calculate_throughput(self):
        """
        Calculates the throughput of the connection.
        Args: None
        use: Calculates the throughput based on the total data received and the time taken for the transfer.
        """
        if self.start_time and self.end_time and self.total_data_received > 0:
            duration = self.end_time - self.start_time
            throughput = (self.total_data_received * 8) / (duration * 1000000)  # Mbps calculation
            print(f"Total data received: {self.total_data_received} bytes")
            print(f"Total time taken: {duration:.6f} seconds")
            print(f"Throughput: {throughput:.2f} Mbps")
        else:
            print("Insufficient data to calculate throughput.")

    def close(self): #this clothes the connection and the UDP socket used by the server
        print("Closing server socket")
        self.socket.close()

class DRTPClient(DRTPBase):
    def __init__(self, ip, port, filename, window_size=3):
        """
        This class initializes the DRTPClient class.
        Args:
            ip (str): The IP address of the server.
            port (int): The port number to bind the socket.
            filename (str): The name of the file to be send.
            window_size (int): The size of the sliding window default 3.
        use: Sets up the socket, configurations and initial state.
        variables:
            filename (str): The name of the file to be sent.
            ack_received (int): Last acknowledged sequence number.
        """
        super().__init__(ip, port, window_size)
        self.socket.settimeout(self.TIMEOUT_INTERVAL)
        self.filename = filename
        self.ack_received = 1  # Initial expected ACK
    
    def run(self):
        """
        Runs the client and sends the data.
        Args: None
        return: None
        use: Initiates the connection and sends the data using a sliding window protocol.
        """
        print(split_line)
        print(f"Server started at {self.ip}:{self.port}")
        print(split_line)
        print() # just to have some space
        self.initiate_connection()
        print() # just to have some space
        print("Data Transfer:")
        print() # just to have some space
        self.send_data()

    
    def initiate_connection(self):
        """ Initiates a connection to the server using a three-way handshake.
        use: Sends a SYN packet and waits for a SYN-ACK packet to complete the handshake then sends an ACK packet to establish the connection with the server.
        """
        self.send_packet(0, 0, self.SYN)
        print("SYN packet sent")
        while True:
            header, _, addr = self.receive_packet()
            if header:
                seq_num, ack_num, flags = header
                if flags == (self.SYN | self.ACK):
                    print("SYN-ACK packet is received")
                    self.send_packet(0, ack_num, self.ACK, addr=addr)
                    print("ACK packet sent")
                    print("Connection established")
                    break  # Exit loop once handshake is complete

    def send_data(self):
        """ Sends data using a sliding window protocol. 
        use: Reads data from the file and sends it in packets. Manages the sliding window and retransmissions. 
        """
        with open(self.filename, 'rb') as file:
        # First send the filename
            filename_packet = f"FILENAME:{os.path.basename(self.filename)}".encode('utf-8')
            self.send_packet(self.next_seq_num, 0, 0, filename_packet)
            self.window.append(self.next_seq_num)
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- Packet with seq = {self.next_seq_num} is sent, sliding window = {self.window}")

            self.send_buffer[self.next_seq_num] = filename_packet
            self.next_seq_num += 1

            # Then send the file data
            data = file.read(self.PACKET_SIZE)
            while data or self.window:
                # Send new packets if the window is not full, 
                while len(self.window) < self.window_size and data:
                    self.send_packet(self.next_seq_num, 0, 0, data)
                    self.window.append(self.next_seq_num)
                    print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- Packet with seq = {self.next_seq_num} is sent, sliding window = {self.window}")
                    self.send_buffer[self.next_seq_num] = data
                    self.next_seq_num += 1
                    data = file.read(self.DATA_SIZE)

                self.handle_acknowledgments()

    def handle_acknowledgments(self):
        """ Handles the acknowledgments received from the server.
        use: waits forACK packets and updates the window and send buffer accordingly. Retransmits unacknowledged packets if a timeout occurs.
        """
        try:
            header, _, addr = self.receive_packet()
            if header:
                _, ack_num, flags = header
                if flags & self.ACK:
                    # Update window on receiving ACK
                    while self.window and self.window[0] <= ack_num:
                        acknowledged_seq = self.window.pop(0)
                        del self.send_buffer[acknowledged_seq]
                        print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- ACK for packet = {ack_num} received")
        except socket.timeout:
            print(f"{time.strftime('%H:%M:%S.%f')[:-3]} -- RTO occurred")
            self.retransmit_unacknowledged_packets()
        finally:
            if not self.window and not self.send_buffer:
                print() # just to have some space
                self.teardown_connection()


    def retransmit_unacknowledged_packets(self):
        """ Retransmits the unacknowledged packets in the window.
        use: Retransmits the packets in the window that have not been acknowledged by the server.
        """
        for seq in self.window:
            data = self.send_buffer[seq]
            self.send_packet(seq, 0, 0, data)
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')} -- Retransmitting packet with seq = {seq}")
            continue


    def teardown_connection(self):
        """
        Tears down the connection by sending a FIN packet and handling the final ACK.
        use: Sends a FIN packet to close the connection and waits for the final ACK packet to close the connection.
        """
        print("Sending FIN packet")
        #send fin packet
        self.send_packet(self.next_seq_num, 0, self.FIN)
        self.next_seq_num += 1
        #receive ack packet
        header, _, addr = self.receive_packet()
        if header:
            seq_num, ack_num, flags = header
            if flags & self.ACK:
                print("Connection closed")
                self.socket.close()


