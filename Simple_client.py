import socket
import sys

# Constants

ADDRESS = '127.0.0.1' # server IP address
PORT = 2000  # server port number
EVENT = 1
OPEN_METHOD = "a"
PRIO_EVENT = "Event"
PRIO_ERROR = "Error"
PRIO_INFO = "Info"

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        soc.connect((ADDRESS, PORT))

    except:
        log_message = "Connection error"
        print(log_message)
        sys.exit()

    # this client is launched by another program that passes parameters
    message = " " + " ".join(sys.argv[EVENT:])  # event parameters received as arguments
    while message != 'QUIT':
        soc.sendall(message.encode("utf8"))
        if soc.recv(5120).decode("utf8") == "OK": # server received the message
            pass        # null operation

        message = 'QUIT'

    soc.send(b'--QUIT--')


if __name__ == "__main__":
    main()