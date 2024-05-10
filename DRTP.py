import random
import struct
from subprocess import call
import os
from os import system
import time
from time import sleep
import sys
import socket
import re
import subprocess
import platform
import argparse
from argparse import Namespace
from threading import Thread, Lock

#global variables
separator_line = "---------------------------------------------------------"
DRTP_struct = struct.Struct("!HHH")
Header_size = DRTP_struct.size
SEQ_START = 1
#flags
SYN_FLAG = 1 << 3
ACK_FLAG = 1 << 2
FIN_FLAG = 1 << 1
RST_FLAG = 1 << 0
PACKET_SIZE = 1024 
#set_flags function
def set_flags(SYN, ACK, FIN,RESET): 
    flags = 0 
    if SYN:
        flags |= 1 << 3
    if ACK:
        flags |= 1 << 2
    if FIN:
        flags |= 1 << 1
    if RESET:
        flags |= 1 << 0
    return flags

def parse_flags(flags):
    SYN = bool(flags & (1 << 3))  # True if the bit is set, otherwise False
    ACK = bool(flags & (1 << 2))
    FIN = bool(flags & (1 << 1))
    RESET = bool(flags & (1 << 0))
    return SYN, ACK, FIN, RESET

def display_active_flags(flags):
    SYN, ACK, FIN, RESET = parse_flags(flags)
    flag_names = ['syn', 'ack', 'fin', 'rst']
    flag_values = [SYN, ACK, FIN, RESET]
    active_flags = [name for name, value in zip(flag_names, flag_values) if value != 0]
    print("Flags: " + "".join(active_flags) if active_flags else "No flags")

def header(Seq_num, Ack_num, flags):
    return DRTP_struct.pack(Seq_num, Ack_num, flags)

def unpack_header(header):
    return DRTP_struct.unpack(header)


def strip_packet(data):
    header = data[:DRTP_struct.size]
    data = data[DRTP_struct.size:]
    return header, data

def create_packet(Seq_num, Ack_num, flags, data=b""):
    header = DRTP_struct.pack(Seq_num, Ack_num, flags)
    return header + data

separator_line = "---------------------------------------------------------"


def generate_random_isn():
    return random.randint(0, 2 ** 8 - 1)



def gbn_sender(server_ip, server_port,data,window_size=3):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.timeout(0.5) #timeout is set to 0.5 seconds

    try:
        data_segment = [data[i:i + 1024] for i in range(0, len(data), 1024)]
        base = 0
        next_send_seq_num = 0
        total_packets = len(data_segment)
      
        
        while base < len(data_segment):
            while next_seq_num < base + window_size and next_seq_num < total_packets:
                packet = header(next_seq_num, 0, set_flags(SYN=True)) + data_segment[next_seq_num]
                client_socket.sendto(packet, (server_ip, server_port))
                print(f"{time.time()} -- Packet {next_seq_num} is sent")
                next_seq_num += 1
            try:
                ack_packet, _ = client_socket.recvfrom(DRTP_struct.size)
                _, ack_num, flags = unpack_header(ack_packet)
                if flags & ACK_FLAG:
                    print(f"{time.time()} -- ACK {ack_num} is received")
                    base = ack_num + 1
                else:
                    print("ACK is not received")
            except socket.timeout:
                print(f"{time.time()} -- Timeout, resending from packet {base}")
                next_send_seq_num = base
    finally:
        client_socket.close()


def gbn_receiver(bind_ip, bind_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((bind_ip, bind_port))
    server_socket.timeout(0.5) #timeout is set to 0.5 seconds for the socket

    expected_seq_num = 0

    try:
        while True:
            try:
                packet, client_address = server_socket.recvfrom(DRTP_struct.size + PACKET_SIZE)
                seq_num, _, flags = unpack_header(packet[:DRTP_struct.size])
                print(f"{time.time()} -- Packet {seq_num} is received")

                if seq_num == expected_seq_num:
                    ack_packet = header(seq_num, 0, set_flags(ACK=True))
                    server_socket.sendto(ack_packet, client_address)
                    print(f"{time.time()} -- Sending ACK for {seq_num}")
                    expected_seq_num += 1
                else:
                    print("Packet is not received")
            except socket.timeout:
                print("Timeout")
    finally:
        server_socket.close()
        
def run_server(server_ip, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))

    print(separator_line)
    print()
    print(f"      Server is listening on {server_ip} on port {server_port}")
    print()
    print(separator_line)
    
    
    while True:
        packet, addr = server_socket.recvfrom(PACKET_SIZE)
        seq_num, ack_num, flags = unpack_header(packet)
        
        if flags & SYN_FLAG:
            print("SYN packet is received")
            syn_ack_header = create_packet(seq_num + 1, 0, SYN_FLAG | ACK_FLAG)
            server_socket.sendto(syn_ack_header, addr)
            print("SYN-ACK packet is sent")

        elif flags & ACK_FLAG:
            print("ACK packet is received")
            print("Connection established\n")
            break

    # Data reception and ACK sending
    expected_seq_num = seq_num + 2
    try:
        while True:
            packet, addr = server_socket.recvfrom(PACKET_SIZE)
            seq_num, ack_num, flags = unpack_header(packet[:Header_size])
            if flags & FIN_FLAG:
                print("FIN packet is received")
                fin_ack_header = create_packet(seq_num + 1, 0, FIN_FLAG)
                server_socket.sendto(fin_ack_header, addr)
                print("FIN ACK packet is sent")
                break
            if seq_num == expected_seq_num:
                print(f"{time.strftime('%H:%M:%S.%f')} -- packet {seq_num} is received")
                print(f"{time.strftime('%H:%M:%S.%f')} -- sending ack for the received {seq_num}")
                ack_header = create_packet(0, seq_num, ACK_FLAG)
                server_socket.sendto(ack_header, addr)
                expected_seq_num += 1

    finally:
        print("Connection closes")
        server_socket.close()
           

def run_client(server_ip, server_port, file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.connect((server_ip, server_port))
    client_socket.settimeout(0.5)

    print(separator_line)
    print()
    print(f"     Client is connected to server {server_ip} on port {server_port}")
    print()
    print(separator_line)

    try:
        # Connection Establishment
        print("Connection Establishment Phase:")
        syn_header = create_packet(SEQ_START, 0, SYN_FLAG)
        client_socket.sendto(syn_header, (server_ip, server_port))
        print("SYN packet is sent")

        response, _ = client_socket.recvfrom(PACKET_SIZE)
        _, _, flags = unpack_header(response)
        if flags & (SYN_FLAG | ACK_FLAG):
            print("SYN-ACK packet is received")
            ack_header = create_packet(SEQ_START + 1, 0, ACK_FLAG)
            client_socket.sendto(ack_header, (server_ip, server_port))
            print("ACK packet is sent")
            print("Connection established\n")

        # Data Transfer
        print("Data Transfer:")
        with open(file_path, "rb") as file:
            sequence_num = SEQ_START + 1  # Start after connection sequence
            window_size = 5
            base_seq_num = sequence_num
            packets = {}
            acks_received = Thread(target=receive_acks, args=(client_socket, base_seq_num, packets, window_size))
            acks_received.start()

            while True:
                data = file.read(994)  # Read data in chunks
                if not data:
                    break
                while sequence_num >= base_seq_num + window_size:
                    time.sleep(0.05)  # Wait for window to slide

                packet = create_packet(sequence_num, 0, 0) + data
                packets[sequence_num] = packet
                client_socket.sendto(packet, (server_ip, server_port))
                print(f"{time.strftime('%H:%M:%S.%f')} -- packet with seq = {sequence_num} is sent, sliding window = {{{base_seq_num} to {base_seq_num + window_size - 1}}}")
                sequence_num += 1

            acks_received.join()

        # Connection Teardown
        print("\nConnection Teardown:")
        fin_header = create_packet(sequence_num, 0, FIN_FLAG)
        client_socket.sendto(fin_header, (server_ip, server_port))
        print("FIN packet is sent")

        response, _ = client_socket.recvfrom(PACKET_SIZE)
        _, _, flags = unpack_header(response)
        if flags & FIN_FLAG:
            print("FIN ACK packet is received")

    finally:
        print("Connection closes")
        client_socket.close()

    def receive_acks(sock, base_seq, packets, window_size):
        while True:
            try:
                response, _ = sock.recvfrom(PACKET_SIZE)
                _, ack_num, flags = unpack_header(response)
                if flags & ACK_FLAG:
                    print(f"{time.strftime('%H:%M:%S.%f')} -- ACK for packet = {ack_num} is received")
                    with Lock():
                        if ack_num >= base_seq:
                            base_seq = ack_num + 1
            except socket.timeout:
                with Lock():
                    for seq in range(base_seq, base_seq + window_size):
                        if seq in packets:
                            sock.sendto(packets[seq], (server_ip, server_port))
                            print(f"{time.strftime('%H:%M:%S.%f')} -- Retransmitting packet with seq = {seq}")
            except:
                break  # Exit when file transfer is complete
#make a function that tels the port is listening
def server_listening_on_port(listening_port):
    print(separator_line)
    print(f"Server is listening on port {listening_port}")
    print(separator_line)   
    

default_ip = "127.0.0.1"
default_time = 25
default_port = 8080
default_print_format = "KB"


parser = argparse.ArgumentParser(description="DRTP - Data Transfer Protocol") #this creates a parser object with a description of the program.
def check_serverip(ip):
    error_message = None
    #split the ip into a list of octets
    ip_octets = ip.split(".")
    ip = "" 
    try:
        #check if ip has 4 elements in it
        if len(ip_octets) != 4:
            error_message = f"{ip} is invalid IP address, it must have 4 elements eks; x.x.x.x"
        else:
            #check if numbers are between 0 and 255 and has 4 elements in it
            for octet in ip_octets:

                if int(octet) < 0 or int(octet) > 255:
                    error_message = f"{octet} is invalid IP address, it must be between 0 and 255"
                    break 
                ip += f"{int(octet)}."  

    except ValueError:
        error_message = f"{ip} is invalid IP address, it must be a number"
        parser.print_help()
        exit(1)
    #remove the last dot
    ip = ip[:-1]
    return ip


def check_throughput(throughput):
    error_message = None
    try: 
        throughput = int(throughput)
        if throughput < 0:
            error_message = f"{throughput} is invalid throughput, it must be a positive number"
        #check if string starts with number and ends with B, KB or MB
        if not re.match(r"^\d+[B|KB|MB]$", str(throughput)):
            error_message = f"{throughput} is invalid throughput, it must be a number followed by B, KB or MB"
    except ValueError:
        error_message = f"{throughput} is invalid throughput, it must be a number"
    return throughput


def check_time(time):
    error_message = None
    try: 
        time = int(time)
        if time < 0: #check if time is a positive number
            error_message = f"{time} is invalid number, it must be a positive number"
    except ValueError:
        error_message = f"{time} is invalid, it must be a number"
        parser.print_help()
        exit(1)
    return time


def check_port(port):
    error_message = None
    try: 
        port = int(port)
        if port < 1024 or port > 65535: #check if port is between 0 and 65535
            error_message = f"{port} is invalid port number, it must be between 1024 and 65535"
    except ValueError:
        error_message = f"{port} is invalid port number, it must be a number"
        parser.print_help()
        exit(1) 

    return port 