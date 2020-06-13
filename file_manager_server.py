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
user_directory = ""


def register(s, conn, cursor, username, password, user_directory):
    global USERNAME
    if (username != "" and password != "") :
        cursor.execute("SELECT ID FROM users_info")
        all_ids = cursor.fetchall()
        # checks if the db is empty
        if not all_ids:
            load_db(conn, cursor, [1, username, password])
            s.send((str(CONFIRMATION)).encode())
            USERNAME = username
            user_directory = create_user_folder(user_directory)
            user_directory = check_files_and_send(s, user_directory)
        else:
            try:
                print(all_ids)
                print(len(all_ids))
                try:
                    last_ID = all_ids[len(all_ids) - 1]
                except:
                    last_ID = 0
                cursor.execute("SELECT user_name FROM users_info WHERE user_name == ?", (username,))
                existing_name = cursor.fetchone()
                print(existing_name)
                if existing_name is None:
                    # because last_ID is a tuple we need an extra [0] to get the correct value
                    load_db(conn, cursor, [last_ID[0] + 1, username, password])
                    s.send((str(CONFIRMATION)).encode())
                    USERNAME = username
                    user_directory = create_user_folder(user_directory)
                    user_directory = check_files_and_send(s, user_directory)
                    return user_directory
                else:
                    print("sorry the username is already used")
                    s.send((str(ERROR)).encode())
            except:
                print("something went wrong")
    else:
        s.send((str(ERROR)).encode())


def login(s, cursor, username, password, user_directory):
    global USERNAME
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
        user_directory = new_path
        print("aaaaaaaaaaaaaaaaaaaaa")
        print(user_directory)
        user_directory = check_files_and_send(s, user_directory)
        return user_directory


def load_db(conn, cursor, data_list):
    # Fills the table
    print("in load")
    hashed_password = hashlib.sha1(str(data_list[2]).encode())
    hashed_password = hashed_password.hexdigest()
    cursor.execute("INSERT INTO users_info VALUES (?,?,?)", (data_list[0], data_list[1], hashed_password))
    conn.commit()


def create_user_folder(user_directory):
    print(PROJECT_PATH)
    list = PROJECT_PATH.split('\\')
    print(list)
    list[-1] = USERNAME
    print(list)
    new_path = "\\".join(list)
    print(new_path)
    os.mkdir(os.path.abspath(new_path))
    user_directory = new_path
    return user_directory


def check_files_and_send(s, user_directory):
    print("in")
    print(user_directory)
    file_names = os.listdir(user_directory)
    print(file_names)
    file_size = [",", ]
    place = 0
    for x in range(file_names.__len__()):
        path = user_directory + "\\" + file_names[place]
        print(path)
        file_size.append(os.path.getsize(path))
        place += 1
    file_data = file_names + file_size
    file_data = json.dumps(file_data)
    print("lists")
    print(file_data)
    s.send(file_data.encode())
    return user_directory


def send_file(client_socket, file_name, user_directory):
    print(user_directory)
    if os.path.exists(user_directory + "\\" + file_name):
        file_location = user_directory + "\\" + file_name
        print("path exists")
        client_socket.send((str(CONFIRMATION)).encode())
        file_size = os.path.getsize(file_location)
        number_of_loops = file_size / 1024
        number_of_loops = int(number_of_loops)
        if number_of_loops < 1:
            number_of_loops = 1
        print(number_of_loops)
        """reads the file 1024 bytes at a time."""
        with open(file_location, 'rb') as f:
            for x in range(int(number_of_loops)):
                file_parts = f.read(1024)
                client_socket.send(file_parts)
            time.sleep(1)
            client_socket.send((str(CONFIRMATION)).encode())
            user_directory = check_files_and_send(client_socket, user_directory)
    else:
        client_socket.send((str(ERROR)).encode())


def store_file(client_socket, file_name, user_directory):
    print(file_name)
    file_format = file_name.split(".")[-1]
    """gets the number of times he needs to recv from the client"""
    number_of_loops = int((client_socket.recv(1024)).decode())
    print(number_of_loops)
    new_file_name = (client_socket.recv(1024)).decode()
    print(new_file_name)
    completeName = os.path.join(user_directory, new_file_name + "." + file_format)
    print(completeName)
    new_file = open(completeName, "wb")
    try:
        """recv the file parts x times"""
        for x in range(number_of_loops):
            new_file.write(client_socket.recv(1024))
        new_file.close()
        check_files_and_send(client_socket, user_directory)
    except Exception:
        print("something went wrong")
        client_socket.send((str(ERROR)).encode())


def change_file_name(client_socket, file_name, new_file_name, user_directory):
    print("in change file")
    print(file_name)
    print(user_directory + "\\" + file_name)
    old_path = user_directory + "\\" + file_name
    if os.path.exists(old_path):
        """gets the dir of the file with dirname"""
        """creates a new path with the directory, back slash and the new file name"""
        new_path = user_directory + "\\" + new_file_name
        print(new_path)
        """the func rename basiclly copies the original just with a diffrent name"""
        os.rename(old_path, new_path)
        client_socket.send((str(CONFIRMATION)).encode())
        check_files_and_send(client_socket, user_directory)
    else:
        client_socket.send((str(ERROR)).encode())


def delete_file(client_socket, file_name, user_directory):
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(user_directory + "\\" + file_name)
    if os.path.exists(user_directory + "\\" + file_name):
        print("in")
        os.remove(user_directory + "\\" + file_name)
        print("after remove")
        client_socket.send(str(CONFIRMATION).encode())
        check_files_and_send(client_socket, user_directory)
    else:
        client_socket.send(str(ERROR).encode())


def handel_thread(connection, ip, port, conn, cursor, user_directory, max_buffer_size=5120):
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

            if client_input[:2] == str(REGISTER):
                client_input = client_input[2:]
                data = client_input.split(',')
                print(data[0])
                print(data[1])
                user_directory = register(connection, conn, cursor, data[0], data[1], user_directory)

            if client_input[:2] == str(LOGIN):
                client_input = client_input[2:]
                data = client_input.split(',')
                user_directory = login(connection, cursor, data[0], data[1], user_directory)

            elif client_input[:2] == str(DOWNLOAD_FILE):
                file_location = client_input[2:]
                send_file(connection, file_location, user_directory)

            elif client_input[:2] == str(STORE_FILE):
                file_name = client_input[2:]
                store_file(connection, file_name, user_directory)

            elif client_input[:2] == str(DELETE):
                file_name = client_input[2:]
                delete_file(connection, file_name, user_directory)

            elif client_input[:2] == str(CHANGE_NAME):
                """splits the client info using the ' ' in between the file path and the new name"""
                client_input = client_input[2:]
                print(client_input.split("*"))
                client_input = client_input.split("*")
                file_name = client_input[0]
                new_file_name = client_input[1]
                print(file_name)
                print(new_file_name)
                change_file_name(connection, file_name, new_file_name, user_directory)

            else:
                print("there is a problem with the input")
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
    user_directory = ""
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

    # starting db
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
            threading.Thread(target=handel_thread, args=(connection, ip, port, conn, cursor, user_directory)).start()


        except:
            print("ooh something went wrong")
            s.close()
            sys.exit()


if __name__ == '__main__':
    main()

