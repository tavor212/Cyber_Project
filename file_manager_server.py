import socket
import threading
import os
import sys
import sqlite3
import hashlib
import json
import time


PORT = 1000
HOST = '127.0.0.1'
ALL_IP = '0.0.0.0'
ERROR = 300
REGISTER = 70
LOGIN = 60
DOWNLOAD_FILE = 50
STORE_FILE = 40
CHANGE_NAME = 30
DELETE = 20
EXIT = 10
CONFIRMATION = 1
USERNAME = ""
PROJECT_PATH = os.path.abspath(__file__)
USER_DIRECTORY = ""


def register(s, conn, cursor, username, password):
    global USERNAME
    cursor.execute("SELECT ID FROM users_info")
    all_ids = cursor.fetchall()
    #checks if the db is empty
    if not all_ids:
        load_db(conn, cursor, [1,username,password])
        s.send((str(CONFIRMATION)).encode())
        USERNAME = username
        create_user_folder()
        check_files_and_send(s)
    else:
        try:
            print(all_ids)
            print(len(all_ids))
            try:
                last_ID = all_ids[len(all_ids)-1]
            except:
                last_ID = 0
            cursor.execute("SELECT user_name FROM users_info WHERE user_name == ?", (username,))
            existing_name = cursor.fetchone()
            print(existing_name)
            if existing_name is None:
                #because last_ID is a tuple we need an extra [0] to get the correct value
                load_db(conn, cursor, [last_ID[0] + 1, username, password])
                s.send((str(CONFIRMATION)).encode())
                USERNAME = username
                create_user_folder()
                check_files_and_send(s)
            else:
                print("sorry the username is already used")
                s.send((str(ERROR)).encode())
        except:
            print("something went wrong")


def login(s, cursor, username, password):
    global USERNAME, USER_DIRECTORY
    cursor.execute("SELECT user_name FROM users_info WHERE user_name == ?", (username,))
    existing_name = cursor.fetchone()
    print(password)
    password = hashlib.sha1(str(password).encode())
    password = password.hexdigest()
    print(password)
    cursor.execute("SELECT password FROM users_info WHERE user_name == ? AND password == ?", (username,) + (password,))
    existing_password = cursor.fetchone()
    print(existing_name)
    print(existing_password)
    if existing_name is None and existing_password is None:
        print("no user found")
        s.send((str(ERROR)).encode())
    elif existing_name is None or existing_password is None:
        print("Sorry your username or password is wrong")
        s.send((str(ERROR)).encode())
    else:
        s.send((str(CONFIRMATION)).encode())
        USERNAME = username
        list = PROJECT_PATH.split('\\')
        list[-1] = USERNAME
        new_path = "\\".join(list)
        USER_DIRECTORY = new_path
        check_files_and_send(s)

def load_db(conn, cursor, data_list):
    # Fills the table
    print("in load")
    hashed_password = hashlib.sha1(str(data_list[2]).encode())
    hashed_password = hashed_password.hexdigest()
    cursor.execute("INSERT INTO users_info VALUES (?,?,?)", (data_list[0], data_list[1], hashed_password))
    conn.commit()


def create_user_folder():
    print(PROJECT_PATH)
    list = PROJECT_PATH.split('\\')
    print(list)
    list[-1] = USERNAME
    print(list)
    new_path = "\\".join(list)
    print(new_path)
    os.mkdir(os.path.abspath(new_path))
    global USER_DIRECTORY
    USER_DIRECTORY = new_path


def check_files_and_send(s):
    print("in")
    file_names = os.listdir(USER_DIRECTORY)
    print(file_names)
    file_size = [",", ]
    place = 0
    for x in range (file_names.__len__()):
        path = USER_DIRECTORY + "\\" + file_names[place]
        file_size.append(os.path.getsize(path))
        place += 1
    file_data = file_names + file_size
    file_data = json.dumps(file_data)
    print("lists")
    print(file_data)
    s.send(file_data.encode())


def send_file(client_socket, file_location):
    check_files_and_send(client_socket)
    print(os.path.dirname(os.path.realpath(file_location)))
    print(USER_DIRECTORY)
    if os.path.dirname(os.path.realpath(file_location)) == USER_DIRECTORY:
        if os.path.exists(file_location):
            print("path exists")
            client_socket.send((str(CONFIRMATION)).encode() + (str(os.path.getsize(file_location))).encode())
            file_size = os.path.getsize(file_location)
            number_of_loops = file_size/1024
            number_of_loops = int(number_of_loops)
            if number_of_loops < 1:
                number_of_loops = 1
            print(number_of_loops)
            user_answer = client_socket.recv(1024)
            print("recived:" + str(user_answer))
            print(file_location)
            print(user_answer[:1].decode())
            if user_answer[:1].decode() == str(CONFIRMATION):
                """reads the file 1024 bytes at a time."""
                with open(file_location, 'rb') as f:
                    for x in range(int(number_of_loops)):
                        file_parts = f.read(1024)
                        client_socket.send(file_parts)
                    client_socket.send((str(CONFIRMATION)).encode())
            else:
                client_socket.send((str(ERROR)).encode())
        else:
            client_socket.send((str(ERROR)).encode())
    else:
        print("not in user directory")
        client_socket.send((str(ERROR)).encode())

def store_file(client_socket, file_location):
    check_files_and_send(client_socket)
    print(file_location)
    file_format = file_location.split(".")[-1]
    """gets the number of times he needs to recv from the client"""
    number_of_loops = int((client_socket.recv(1024)).decode())
    print(number_of_loops)
    new_file_name = (client_socket.recv(1024)).decode()
    print(new_file_name)
    completeName = os.path.join(USER_DIRECTORY, new_file_name + "." + file_format)
    print(completeName)
    new_file = open(completeName, "wb")
    try:
        """recv the file parts x times"""
        for x in range(number_of_loops):
            new_file.write(client_socket.recv(1024))
        new_file.close()
        print("why")
    except Exception:
        print("something went wrong")
        client_socket.send((str(ERROR)).encode())


def change_file_name(client_socket, file_name, new_file_name):
    print("in change file")
    print(file_name)
    print (USER_DIRECTORY + "\\" + file_name)
    old_path = USER_DIRECTORY + "\\" + file_name
    if os.path.exists(old_path):
        """gets the dir of the file with dirname"""
        """creates a new path with the directory, back slash and the new file name"""
        new_path = USER_DIRECTORY + "\\" + new_file_name
        print(new_path)
        """the func rename basiclly copies the original just with a diffrent name"""
        os.rename(old_path, new_path)
        client_socket.send((str(CONFIRMATION)).encode())
        check_files_and_send(client_socket)
    else:
        client_socket.send((str(ERROR)).encode())


def delete_file(client_socket, file_name):
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(USER_DIRECTORY + "\\" + file_name)
    if os.path.exists(USER_DIRECTORY + "\\" + file_name):
        print("in")
        os.remove(USER_DIRECTORY + "\\" + file_name)
        print("after remove")
        client_socket.send(str(CONFIRMATION).encode())
        check_files_and_send(client_socket)
    else:
        client_socket.send(str(ERROR).encode())


def handel_thread(connection, ip, port, conn, cursor, max_buffer_size=5120):
    active = True
    while active:
        print("waiting for request")
        client_input = receive_input(connection, max_buffer_size)
        print(client_input)
        print(type(client_input))
        print(connection)
        try:
            if client_input == str(EXIT):
                print("Client is requesting to quit")
                connection.send((str(EXIT)).encode())
                connection.close()
                message = "Connection " + ip + ": " + port + " closed"
                print(message)
                active = False

            elif client_input[:2] == str(REGISTER):
                client_input = client_input[2:]
                data = client_input.split(',')
                print(data[0])
                print(data[1])
                register(connection, conn, cursor, data[0], data[1])

            elif client_input[:2] == str(LOGIN):
                client_input = client_input[2:]
                data = client_input.split(',')
                login(connection, cursor, data[0], data[1])

            elif client_input[:2] == str(DOWNLOAD_FILE):

                file_location = client_input[2:]
                send_file(connection, file_location)

            elif client_input[:2] == str(STORE_FILE):
                file_location = client_input[2:]
                store_file(connection, file_location)

            elif client_input[:2] == str(DELETE):
                file_name = client_input[2:]
                delete_file(connection, file_name)

            elif client_input[:2] == str(CHANGE_NAME):
                """splits the client info using the ' ' in between the file path and the new name"""
                client_input = client_input[2:]
                print(client_input.split("*"))
                client_input = client_input.split("*")
                file_name = client_input[0]
                new_file_name = client_input[1]
                print(file_name)
                print(new_file_name)
                change_file_name(connection, file_name, new_file_name)

            else:
                connection.send("oh oh something went wrong".encode())
                print("there is a problem with the input")
                connection.close()
                active = False

        except:
            print("client ended the connection unexpectedly")
            connection.close()
            active = False


def receive_input(connection, max_buffer_size):
    try:
        client_input = connection.recv(max_buffer_size)
        client_input_size = sys.getsizeof(client_input)
        if client_input_size > max_buffer_size:
            print("The input size is greater than expected, let me divide them")
            temp = "1"
            while temp != "":
                temp = connection.recv(max_buffer_size)
                client_input += temp
        decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line
        return decoded_input
    except Exception:
        print("ERROR")


def main():
    print("hello")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    """tells the operating system to reuse the port if something crashes or a user is disconnecting"""
    print("Socket created")

    try:
        s.bind((ALL_IP, PORT))

    except:
        print("couldent bind")

    s.listen(5)
    print("server started")

    #starting db
    conn = sqlite3.connect("users_info.db", check_same_thread=False)

    cursor = conn.cursor()
    # creates a table
    tb_create = """CREATE TABLE users_info(ID INT, user_name TEXT, password TEXT)"""

    tb_exists = "SELECT name FROM sqlite_master WHERE type='table' AND name='users_info'"
    if not conn.execute(tb_exists).fetchone():
        conn.execute(tb_create)
    conn.commit()

    # infinite loop- do not reset for every requests
    while True:
        try:
            connection, address = s.accept()
            ip, port = str(address[0]), str(address[1])
            print("Connected with " + ip + " :" + port)
            """sends the threads to a func that checks their requests and redirects them"""
            threading.Thread(target=handel_thread, args=(connection, ip, port, conn, cursor)).start()


        except:
            print("ooh something went wrong")
            s.close()
            sys.exit()


if __name__ == '__main__':
    main()
        


