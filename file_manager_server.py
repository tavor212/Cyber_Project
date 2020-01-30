import socket
import threading
import os
import sys

PORT = 6543
HOST = '127.0.0.1'
ALL_IP = '0.0.0.0'
ERROR = 300
RESPONSE = 200
REQUEST = 100   # server asks the client for data
SEND_FILE = 40
CHANGE_NAME = 30
DELETE = 20
EXIT = 10
CONFIRMATION = 1


def send_file(client_socket, file_location):
    if os.path.exists(file_location):
        client_socket.send((str(CONFIRMATION)).encode() + (str(os.path.getsize(file_location))).encode())
        user_answer = client_socket.recv(1024)
        if user_answer[:1] == (str(CONFIRMATION)).encode():
            """reads the file 5120 bytes at a time."""
            with open(file_location, 'rb') as f:
                file_parts = f.read(5120)
                client_socket.send(file_parts)
                """if the file is bigger than 1024 bytes then the func reads another 1024 bytes and checks if the file is empty"""
                while os.path.getsize(file_location) != "":
                    file_parts = f.read(5120)
                    client_socket.send(file_parts)
        else:
            client_socket.send((str(ERROR)).encode())
    else:
        client_socket.send((str(ERROR)).encode())


def change_file_name(client_socket, file_location, new_file_name):
    if os.path.exists(file_location):
        """gets the dir of the file with dirname"""
        dir_path = os.path.dirname(file_location)
        """creates a new path with the directory, back slash and the new file name"""
        new_path = dir_path + "\\" + new_file_name
        """the func rename basiclly copies the original just with a diffrent name"""
        os.rename(file_location, new_path)
        client_socket.send((str(CONFIRMATION)).encode())
    else:
        client_socket.send((str(ERROR)).encode())


def delete_file(client_socket, file_location):
    if os.path.exists(file_location):
        os.remove(file_location)
        client_socket.send(str(CONFIRMATION).encode())
    else:
        client_socket.send(str(ERROR).encode())


def handel_thread(connection, ip, port, max_buffer_size=5120):
    active = True
    while active:
        client_input = receive_input(connection, max_buffer_size)
        print(client_input)
        print(type(client_input))
        print(connection)
        if client_input == str(EXIT):
            print("Client is requesting to quit")
            connection.send((str(EXIT)).encode())
            connection.close()
            message = "Connection " + ip + ": " + port + " closed"
            print(message)
            active = False
        elif client_input[:2] == str(SEND_FILE):
            file_location = client_input[2:]
            send_file(connection, file_location)
        elif client_input[:2] == str(DELETE):
            file_location = client_input[2:]
            print(file_location)
            delete_file(connection, file_location)
        elif client_input[:2] == str(CHANGE_NAME):
            """splits the client info using the ' ' in between the file path and the new name"""
            client_input = client_input[2:]
            client_input = client_input.split(" ")
            file_location = client_input[0]
            new_file_name = client_input[1]
            change_file_name(connection, file_location, new_file_name)
        else:
            connection.send("oh oh something went wrong".encode())
            print("there is a problem with the input")
            connection.close()
            active = False


def receive_input(connection, max_buffer_size):
    client_input = connection.recv(max_buffer_size)
    client_input_size = sys.getsizeof(client_input)

    if client_input_size == max_buffer_size:
        print("The input size is greater than expected, let me divide them")
        temp = "1"
        while temp != "":
            temp = connection.recv(max_buffer_size)
            client_input += temp
    decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line
    return decoded_input


def main():
    print("hello")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    """tells the operating system to reuse the port if something crashes or a user is disconnecting"""
    print("Socket created")

    try:
        s.bind((ALL_IP, PORT))

    except:
        print("ooh something went wrong")
        sys.exit()

    s.listen(5)
    print("server started")
    # infinite loop- do not reset for every requests
    while True:
        connection, address = s.accept()
        ip, port = str(address[0]), str(address[1])
        print("Connected with " + ip + " :" + port)

        try:
            """sends the threads to a func that checks their requests and redirects them"""
            threading.Thread(target=handel_thread, args=(connection, ip, port)).start()
        except:
            print("Thread did not start.")

    s.close()


if __name__ == '__main__':
    main()
        


