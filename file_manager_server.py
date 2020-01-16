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
CONFIRMATION = 10


def send_file(client_socket, file_location):
    if os.path.exists(file_location):
        client_socket.send(CONFIRMATION + os.path.getsize(file_location))
        user_answer = client_socket.recv(5120)
        if user_answer[:2] == CONFIRMATION:
            """reads the file 5120 bytes at a time."""
            with open(file_location, 'rb') as f:
                file_parts = f.read(5120)
                client_socket.send(file_parts)
                """if the file is bigger than 1024 bytes then the func reads another 1024 bytes and checks if the file is empty"""
                while os.path.getsize(file_location) != "":
                    file_parts = f.read(1024)
                    client_socket.send(file_parts)
        else:
            client_socket.send(ERROR)
            client_socket.close()
    else:
        client_socket.send(ERROR)
    client_socket.close()


def change_file_name(client_socket, file_location, new_file_name):
    if os.path.exists(file_location):
        client_socket.send(CONFIRMATION)
        """gets the dir of the file with dirname"""
        dir_path = os.path.dirname(file_location)
        """creates a new path with the directory, back slash and the new file name"""
        new_path = dir_path + "\\" + new_file_name
        """the func rename basiclly copies the original just with a difrent name"""
        os.rename(file_location, new_path)
    else:
        client_socket.send(ERROR)
    client_socket.close()


def delete_file(client_socket, file_location):
    if os.path.exists(file_location):
        client_socket.send(CONFIRMATION)
        os.remove(file_location)
    else:
        client_socket.send(ERROR)
    client_socket.close()


def handel_thread(connection, ip, port, max_buffer_size=5120):
    while True:
        client_input = receive_input(connection, max_buffer_size)


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
    result = process_input(decoded_input)

    return result


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
            Thread(target=handle_thread, args=(connection, ip, port)).start()
        except:
            print("Thread did not start.")

    soc.close()


if __name__ == '__main__':
    main()
        


