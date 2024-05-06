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


#global variables
separator_line = "---------------------------------------------------------"
DRTP_struct = struct.Struct("!HHH")
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

def create_packet(Seq_num, Ack_num, flags, data):
    header = header(Seq_num, Ack_num, flags)
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
    timeout = 5
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.settimeout(timeout)
    server_socket.bind((server_ip, server_port))

    print(separator_line)
    print()
    print(f"      Server is listening on {server_ip} on port {server_port}")
    print()
    print(separator_line)
    
    
    while True:
        try:
            syn_packet, client_address = server_socket.recvfrom(DRTP_struct.size)
            _, _, flags = unpack_header(syn_packet)
            print("SYN packet is received")
            if flags & SYN_FLAG:
                # Generate a random initial sequence number for SYN-ACK
                server_isn = generate_random_isn()
                syn_ack_packet = header(server_isn, 0, set_flags(1, 1, 0, 0))
                server_socket.sendto(syn_ack_packet, client_address)
                print("SYN-ACK packet is sent") 
                
                ack_packet, _ = server_socket.recvfrom(DRTP_struct.size)
                _, _, flags = unpack_header(ack_packet)
            if flags & ACK_FLAG:
                    print("ACK packet is received")
        
            
        except:
            print("Connection established")
            print()
            print()
        
            print(f"An unexpected error occurred: {e}")

def run_client(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.connect((server_ip, server_port))

    print(separator_line)
    print()
    print(f"     Client is connected to server {server_ip} on port {server_port}")
    print()
    print(separator_line)

    client_isn = generate_random_isn()
    syn_packet = header(client_isn, 0, set_flags(1, 0, 0, 0))
    client_socket.send(syn_packet)
    print(f"SYN packet is sent {client_isn}")
    
    #receive syn-ack and validate
    SYN_FLAG = 1 << 3
    ACK_FLAG = 1 << 2
    syn_packet = header(0, 0, set_flags(1, 0, 0, 0))
    client_socket.send(syn_packet)
    print("SYN packet is sent")

    # Receive SYN-ACK packet
    syn_ack_packet = client_socket.recv(DRTP_struct.size)
    _, _, flags = unpack_header(syn_ack_packet)
    if flags & (SYN_FLAG | ACK_FLAG):
        print("SYN-ACK packet is received")
        # Send ACK packet
        ack_packet = header(0, 1, set_flags(0, 1, 0, 0))
        client_socket.send(ack_packet)
        print("ACK packet is sent")
        print("Connection established")
    else:
        print("SYN-ACK packet not correctly received")
    print()
    print("Data transfer: ")
    print()

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



