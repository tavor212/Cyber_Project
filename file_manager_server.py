import socket
import threading
import os

ERROR = 300
RESPONSE = 200
REQUEST = 100   # server asks the client for data
FILE = 1   #
FILE_NAME = 2
CONFIRMATION = 10

HOST = '127.0.0.1'
PORT = 158

# client sends request for a file(will look something like this):
# 101test.txt
# first part is the code part of the request: 101, second part is the data: test.txt

"""
the function "send_file" gets a connection to the user and a file path from the mother PC that he wants to download.
the function checks if the path given by the user exists and sends a CONFIRMATION if exists and sends the size of the file to let the user know if he wants to download it.
the function checks if the user choose to download it and if yes, opens the file, reads 1024 bytes from it and sends it
if the file is bigger than 1024 bytes then the func enters a loop which reads and takes 1024 additional bytes and sends them
"""
def send_file(client_socket, file_location):
    if os.path.exists(file_location):
        client_socket.send(CONFIRMATION + os.path.getsize(File_Location))
        user_answer = client_sock.recv(1024)
        if user_answer[:2] == CONFIRMATION:
            with open(file_location, 'rb') as f:
                file_parts = f.read(1024)
                client_socket.send(file_parts)
                while os.path.getsize(file_location) != "":
                    file_parts = f.read(1024)
                    client_socket.send(file_parts)
        else:
            client_socket.send(ERROR)
            client_socket.close()
    else:
        client_socket.send(ERROR)
    client_socket.close()

"""
the function "change_file_name" gets a connection to the user, a path of an existing file, and a name of the clients choosing that he wants to rename the file to that string.
the function checks if the path given by the user exists and sends a CONFIRMATION if exists.
the function gets the file directory using the func "os.path.dirname".
the function joins the directory plus the new file name and then uses the func "os.rename" with the new_file_location".
"new_file_location" includes the new file name that the user wants to change
"""
def change_file_name(client_socket, file_location, new_file_name):
    if os.path.exists(file_location):
        client_socket.send(CONFIRMATION)
        file_path = os.path.dirname(file_location)
        new_file_location = file_path.join(file_path, new_file_name)
        os.rename(file_location,new_file_location)
    else:
        client_socket.send(ERROR)
    client_socket.close()

def main():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(5)

    print "server started"
    while True:
        


