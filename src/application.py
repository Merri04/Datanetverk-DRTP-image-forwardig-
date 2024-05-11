import argparse
import os
import sys
import ipaddress
from DRTP import DRTPClient, DRTPServer

def check_port(value):
    """ Validates the port number. """
    ivalue = int(value)
    if ivalue < 1024 or ivalue > 65535:
        raise argparse.ArgumentTypeError(f"Port number must be between 1024 and 65535, got {ivalue}")
    return ivalue

def check_ip(value):
    """ Validates the IP address. """
    try:
        ipaddress.ip_address(value)
    except ValueError as ve:
        raise argparse.ArgumentTypeError(f"Invalid IP address: {value}. Error: {ve}")
    return value

def check_window_size(value):
    """ Validates the window size for the sliding window protocol. """
    ivalue = int(value)
    if ivalue < 1 or ivalue > 10:
        raise argparse.ArgumentTypeError("Window size must be between 1 and 10.")
    return ivalue

def check_discard(value):
    """ Validates the discard parameter for simulating packet loss. """
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("Discard value must be a non-negative integer.")
    return ivalue

def check_file_exists(value):
    """ Checks if the file exists. """
    if not os.path.isfile(value):
        raise argparse.ArgumentTypeError(f"The file {value} does not exist.")
    return value

def main():
    parser = argparse.ArgumentParser(description="DRTP: Data Reliable Transfer Protocol based on UDP")
    parser.add_argument("-c", "--client", action="store_true", help="Run in client mode")
    parser.add_argument("-s", "--server", action="store_true", help="Run in server mode")
    parser.add_argument("-i", "--ip", type=check_ip, help="IP address of the server", default="127.0.0.1")
    parser.add_argument("-p", "--port", type=check_port, help="Port number", default=8080)
    parser.add_argument("-f", "--file", type=check_file_exists, help="File to send (required in client mode)")
    parser.add_argument("-w", "--window", type=check_window_size, help="Sliding window size", default=3)
    parser.add_argument("-d", "--discard", type=check_discard, help="Sequence number of the packet to discard (server mode)", default=None)

    args = parser.parse_args()

    if args.client and args.server:
        parser.error("Specify either --client or --server, not both.")

    if args.client:
        if not args.file:
            parser.error("The --file option is required in client mode.")
        client = DRTPClient(args.ip, args.port, args.file, args.window)
        client.run()

    elif args.server:
        server = DRTPServer(args.ip, args.port, args.window, args.discard)
        server.run()

if __name__ == "__main__":
    main()
