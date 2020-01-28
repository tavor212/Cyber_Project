import socket
import threading
import os
import sys

DICT = {'ERROR': "300".encode(), 'RESPONSE': "200".encode(), 'REQUEST': "100".encode(), 'SEND_FILE': "40".encode(), 'CHANGE_NAME':  "30".encode(), 'DELETE': "20".encode(), 'EXIT': "10", 'CONFIRMATION': "1".encode()}

PORT = 6543
HOST = '127.0.0.1'
ALL_IP = '0.0.0.0'
ERROR = "300".encode()
RESPONSE = "200".encode()
REQUEST = "100".encode()
SEND_FILE = "40".encode()
CHANGE_NAME = "30".encode()
DELETE = "20".encode()
EXIT = "10".encode()
CONFIRMATION = "1".encode()


def send_file(client_socket, file_location):
    if os.path.exists(file_location):
        client_socket.send(CONFIRMATION, str(os.path.getsize(file_location)).encode())
        user_answer = client_socket.recv(5120)
        if user_answer[:2] == CONFIRMATION:
            """reads the file 5120 bytes at a time."""
            with open(file_location, 'rb') as f:
                file_parts = f.read(5120)
                client_socket.send(file_parts)
                """if the file is bigger than 5120 bytes then the func reads another 1024 bytes and checks if the file is empty"""
                while os.path.getsize(file_location) != "":
                    file_parts = f.read(5120)
                    client_socket.send(file_parts)
        else:
            client_socket.send(ERROR)
            client_socket.close()
    else:
        client_socket.send(ERROR)
    client_socket.close()


def change_file_name(client_socket, file_location, new_file_name):
    if os.path.exists(file_location):
        """gets the dir of the file with dirname"""
        dir_path = os.path.dirname(file_location)
        """creates a new path with the directory, back slash and the new file name"""
        new_path = dir_path + "\\" + new_file_name
        """the func rename basiclly copies the original just with a diffrent name"""
        os.rename(file_location, new_path)
        client_socket.send(CONFIRMATION)
    else:
        client_socket.send(ERROR)
    client_socket.close()


def delete_file(client_socket, file_location):
    if os.path.exists(file_location):
        os.remove(file_location)
        client_socket.send(CONFIRMATION)
    else:
        client_socket.send(ERROR)
    client_socket.close()


def handel_thread(connection, ip, port, max_buffer_size=5120):
    active = True
    client_input = receive_input(connection, max_buffer_size)
    while active:
        if client_input == DICT['EXIT']:
            print("Client is requesting to quit")
            connection.close()
            print("Connection " + ip + ": " + port + " closed")
            active = False
        elif client_input[3:] == DICT['SEND_FILE']:
            file_location = client_input[3:]
            send_file(connection, file_location)
        elif client_input[3:] == DICT['DELETE']:
            file_location = client_input[3:]
            delete_file(connection, file_location)
        elif client_input[3:] == DICT['CHANGE_NAME']:
            """splits the client info using the '@' in between the file path and the new name"""
            client_input = client_input[3:]
            client_input.split('@')
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
    decoded_input = client_input.decode().rstrip()  # decode and strip end of line
    result = str(decoded_input)

    return result


def main():
    print("hello")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    """tells the operating system to reuse the port if something crashes or a user is disconnecting"""
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Socket created")

    try:
        s.bind((ALL_IP, PORT))

    except:
        print("oh oh something went wrong")
        sys.exit()

    s.listen(7)
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
            connection.send(ERROR)
            connection.close()
    s.close()


if __name__ == '__main__':
    main()
        


