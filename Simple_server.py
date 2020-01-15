import socket
import sys
from threading import Thread


# Constants
PORT = 2000
ALL_IP = '0.0.0.0'
OPEN_METHOD = "a"
PRIO_EVENT = "Event"
PRIO_ERROR = "Error"
PRIO_INFO = "Info"


def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # SO_REUSEADDR flag tells the kernel to reuse a local
    # socket in TIME_WAIT state, without waiting for its natural timeout to expire
    message = "Socket created"
    print(message)

    try:
        soc.bind((ALL_IP, PORT))

    except:
        message = "Bind failed: " + str(sys.exc_info())
        print(message)
        sys.exit()

    soc.listen(5)  # queue up to 5 requests
    message = "Socket now listening"
    print(message)
    # infinite loop- do not reset for every requests
    while True:
        connection, address = soc.accept()
        ip, port = str(address[0]), str(address[1])
        message = "Connected with " + ip + " :" + port
        print(message)

        try:
            Thread(target=client_thread, args=(connection, ip, port)).start()
        except:
            message = "Thread did not start."
            print(message)
    soc.close()


def client_thread(connection, ip, port, max_buffer_size = 5120):
    is_active = True

    while is_active:
        client_input = receive_input(connection, max_buffer_size)

        if "--QUIT--" in client_input:
            message = "Client is requesting to quit"
            print(message)
            connection.close()
            message = "Connection " + ip + ": " + port + " closed"
            print(message)
            is_active = False
        else:
            message = "Instruction processed: IP {0} Drive: {1}".format(ip, client_input)
            print(message)

            connection.sendall("OK".encode("utf8"))


def receive_input(connection, max_buffer_size):
    client_input = connection.recv(max_buffer_size)
    client_input_size = sys.getsizeof(client_input)

    if client_input_size > max_buffer_size:
        message = "The input size is greater than expected {}".format(client_input_size)
        print(message)

    decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line
    result = process_input(decoded_input)

    return result


def process_input(input_str):
    message = "Processing the input received from client"
    print(message)

    return "PARAMS: " + str(input_str).upper()


if __name__ == "__main__":
    main()