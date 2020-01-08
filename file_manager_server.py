import socket
import threading
import os

ERROR = 300
RESPONSE = 200
REQUEST = 100   # server asks the client for data
CONFIRMATION = 10

HOST = '127.0.0.1'
PORT = 158

# client sends request for a file(will look something like this):
# 101test.txt
# first part is the code part of the request: 101, second part is the data: test.txt


def send_file(client_socket, file_location):
    if os.path.exists(file_location):
        client_socket.send(CONFIRMATION + os.path.getsize(file_location))
        user_answer = client_socket.recv(1024)
        if user_answer[:2] == CONFIRMATION:
            """reads the file 1024 bytes at a time."""
            with open(file_location, 'rb') as f:
                file_parts = f.read(1024)
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



def main():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(5)
    print("server started")


if __name__ == "main":
    main()
        


