import argparse
import os
from config import *
import argparse
import socket
import ipaddress
import DRTP

import argparse

formatting_line = "-" * 45  # Formatting line = -----------------------------
max_filename_length = 32  # Maximum length of the file
default_server_save_path = "received_files"  # Path to the folder where received files are stored
default_ip = "127.0.0.1"
default_port = 8080
default_discard = 9999999999999999999999


def main():
    def check_file(value):
    # gives default error message if the file does not exist  
        error_message = None
        try:
            if max_filename_length < len(value):
                error_message = f"Filename too long. Max length is {max_filename_length} words"
            if not os.path.exists(value):
                error_message = f'File "{value}", does not exist'
        except:
            error_message = "An error occurred while checking the file"
        if error_message:
            raise argparse.ArgumentTypeError(error_message)
        return value

    def check_saved_file(path):
        """Checks if the given path is valid and writable."""
        error_message = None
        try:
            if not os.path.isdir(path):
                os.makedirs(path, mode=0o777)  # Create the directory if it does not exist
                print(f"Directory '{path}' created")
            if not os.access(path, os.W_OK):
                error_message = f"Path '{path}' is not writable"
        except OSError as e:
            error_message = f"'{path}' is not a valid path: {e}" 
        if error_message:
            raise argparse.ArgumentTypeError(error_message)
        return path
    


    def check_port(port):
        """Checks if the given port is in the valid range (0-65535)."""
        error_message = None
        try:
            port = int(port)
            if not 1014 <= port <= 65535:
                error_message = "Port number must be in the range [1024, 65535]"
        except:
            error_message = "Invalid port number"
        if error_message:
            raise argparse.ArgumentTypeError(error_message)
        return port


    def check_ip(ip):
        """Checks if the given IP address is in the correct format and within the valid range (0-255)."""
        error_message = None
        try:
            ip = ipaddress.ip_address(ip)
            if not all(0 <= int(x) <= 255 for x in ip.exploded.split('.')):
                error_message = "Invalid IP range. Each block should be in the range of [0,255]"
        except:
            error_message = f"{ip} is invalid IP. It must be in the dotted decimal notation format, e.g. 10.0.0.2"
        if error_message:
            raise argparse.ArgumentTypeError(error_message)
        return str(ip)

        
        
    def check_window(window):
        """Checks if the given window size is in the valid range (1, 10)."""
        error_message = None
        try:
            window = int(window)
            if not 1 <= window <= 10:
                error_message = "Window size must be in the range [1, 10]"
        except:
            error_message = "Invalid window size"
        if error_message:
            raise argparse.ArgumentTypeError(error_message)
        return window


    def check_discard(discard):
        """Checks if the given discard value is in the valid range (0, 9999999999999999999999)."""
        error_message = None
        try:
            discard = int(discard)
            if not 0 <= discard <= 9999999999999999999999:
                error_message = "Discard value must be in the range [0, 9999999999999999999999]"
        except:
            error_message = "Invalid discard value"
        if error_message:
            raise argparse.ArgumentTypeError(error_message)
        return discard

    parser = argparse.ArgumentParser(description="Simple Reliable Data Transfer Protocol")

    #client only arguments
    client_group = parser.add_argument_group("Client")  #this creates a group for the client arguments.
    client_group.add_argument("-c", "--client", action="store_true", help="runns in client mode") #this adds the file argument to the client group.
    client_group.add_argument("-f", "--file", type=check_file, help="What is the file you want to sent") #this adds the file argument to the client group.


    #server only arguments
    server_group = parser.add_argument_group("Server")  #this creates a group for the server arguments.
    server_group.add_argument("-s", "--server", action="store_true", help="runns in server mode") #this adds the file argument to the server group.
    server_group.add_argument("-o", "--output", type=check_saved_file, default=default_server_save_path, help="Where to save the file, default %(default)s") #this adds the output argument to the server group.


    #common arguments
    parser.add_argument("-p", "--port", type=check_port, default=default_port, help="Port number, default %(default)s") #this adds the port argument to the parser.
    parser.add_argument("-i", "--ip", type=check_ip, default=default_ip,help="IP address of the server's interface %(default)s") #this adds the IP argument to the parser.
    parser.add_argument("-w", "--window", type=check_window, default=3, help="Sliding window size %(default)s") #this adds the window argument to the parser.
    parser.add_argument("-d", "--discard", type=check_discard, default=default_discard, help="Discard a packet with blbalabala") #this adds the discard argument to the parser.
#choices[3,5,10] instead of 3 
    args = parser.parse_args() #this parses the arguments and stores them in the args variable.rin

    if args.server:
        DRTP.run_server(args.ip, args.port)
    elif args.client:
        DRTP.run_client(args.ip, args.port)


if __name__ == "__main__":
    main() #this starts the main function when you run the program.
    