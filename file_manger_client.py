import socket
import sys

PORT = 6543
HOST = '127.0.0.1'  # switch to the IP of the server PC if not local
DICT = {'ERROR': "300".encode(), 'RESPONSE': "200".encode(), 'REQUEST': "100".encode(), 'DOWNLOAD_FILE': "50".encode(), 'SEND_FILE': "40".encode(), 'CHANGE_NAME':  "30".encode(), 'DELETE': "20".encode(), 'EXIT': "10".encode(), 'CONFIRMATION': "1".encode()}


def download_file(s):
    print("What is the file path")
    path = input()
    file_format = path.split(".")[-1]
    print(file_format)
    message = DICT['DOWNLOAD_FILE'] + path.encode()
    s.send(message)
    message = s.recv(1024)
    print(message[:1])
    if message[:1] == DICT['CONFIRMATION']:
        size = message[1:].decode()
        size = int(size)
        size = size / 1000
        size = str(size)
        print(size + "M" + '\n' + "This is the file size. Do you still want to download?")
        answer = input()
        if answer.upper() == "YES":
            print("Ok lets start")
            s.send(DICT['CONFIRMATION'])
            file_parts = s.recv(1024)
            new_file = open("Server_file" + "." + file_format, "wb")
            if file_parts == DICT['CONFIRMATION']:
                print("The file was succsfuly transfered")
                file_parts = ""
                new_file.close()
            try:
                new_file.write(file_parts)
            except:
                file_parts = ""
            while file_parts != "":
                file_parts = s.recv(1024)
                if file_parts == DICT['CONFIRMATION']:
                    print("The file was succsfuly transfered")
                    file_parts = ""
                    new_file.close()
                else:
                    new_file = open("Server_file" + "." + file_format, "ab")
                    new_file.write(file_parts)
        elif answer.upper() == "NO":
            print("Ok. Cancelling...")
        else:
            print("Sorry, this is not a valid request")
    else:
        print("Oh oh something went wrong.\n")


def send_file(s):
    print("What is the path of the file you want to send?")
    path = input()
    if os.path.exists(path):
        file_format = path.split(".")[-1]
        s.send(file_format)
        print(file_format)
        message = DICT['SEND_FILE'] + path.encode()
        s.send(message)
        message = s.recv(1024)
        if message == DICT['CONFIRMATION']:
            print("ok lets start")
            file_size = os.path.getsize(path)
            number_of_loops = file_size / 1024
            number_of_loops = int(number_of_loops)
            if number_of_loops < 1:
                number_of_loops += 1
            print(number_of_loops)
            s.send(number_of_loops)
            with open(file_location, 'rb') as f:
                for x in range(int(number_of_loops)):
                    file_parts = f.read(1024)
                    client_socket.send(file_parts)
                client_socket.send((str(CONFIRMATION)).encode())
    else:
        print("Im sorry there is a problem with your path")


def change_name(s):
    print("What is the path of the file you want to change the name of")
    path = input()
    file_format = path.split(".")[-1]
    print("What is the new file name?")
    new_name = input()
    new_name = new_name + "." + file_format
    message = DICT['CHANGE_NAME'] + path.encode() + ' '.encode() + new_name.encode()
    s.send(message)
    message = s.recv(1024)
    if message == DICT['CONFIRMATION']:
        print("The name was succsfuly changed\n")
    if message == DICT['ERROR']:
        print("Oh oh something went wrong. The file was not changed\n")


def delete(s):
    print("What is the file path?")
    message = DICT['DELETE'] + input().encode()
    s.send(message)
    message = s.recv(1024)
    if message == DICT['CONFIRMATION']:
        print("The file was deleted!!\n")
    if message == DICT['ERROR']:
        print("Oh oh. Something went wrong. The file was not deleted")


def exit(s):
    active = False
    s.send(DICT['EXIT'])
    message = s.recv(1024)
    if message == DICT['EXIT']:
        print("Ok bye :(")
        sys.exit()


def print_menu():
    print("'Download File' - a function that with a given path will download a file from the server to your computer")
    print("'Send File' - a function that with a given path will send a file from your computer to the server")
    print("'Change Name' - a function that with a given path the a file, will change its name with a name you give")
    print("'Delete' - will delete the file in the path you will give")
    print("'EXIT' - will exit the program :(")


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except:
        print("oh oh something went wrong")
        sys.exit()

    print("Hello \nWelcome to my amazing file management program. you wont find any other in the market :)")
    print("At your disposal are 3 main tools.")
    print("What would you like me to do?\n")

    active = True
    file_format = ""
    while active:
        print_menu()
        message = input()

        if message.upper() == "EXIT":
            exit(s)
        elif message.upper() == "DOWNLOAD FILE":
            download_file(s)
        elif message.upper() == "SENT FILE":
            send_file(s)
        elif message.upper() == "DELETE":
            delete(s)
        elif message.upper() == "CHANGE NAME":
            change_name(s)
        else:
            print("there is a problem with your input, please try again\n")


if __name__ == "__main__":
    main()
