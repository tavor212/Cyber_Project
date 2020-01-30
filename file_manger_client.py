import socket
import sys

PORT = 6543
HOST = '127.0.0.1'  # switch to the IP of the server PC if not local
DICT = {'ERROR': "300".encode(), 'RESPONSE': "200".encode(), 'REQUEST': "100".encode(), 'SEND_FILE': "40".encode(), 'CHANGE_NAME':  "30".encode(), 'DELETE': "20".encode(), 'EXIT': "10".encode(), 'CONFIRMATION': "1".encode()}


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
        print("'Send File' - a function that with a given path will send you a file from the server to your computer")
        print("'Change Name' - a function that with a given path the a file, will change its name with a name you give")
        print("'Delete' - will delete the file in the path you will give")
        print("'EXIT' - will exit the program :(")
        message = input()
        if message.upper() == "EXIT":
            active = False
            s.send(DICT['EXIT'])
            message = s.recv(1024)
            if message == DICT['EXIT']:
                print("Ok bye :(")
                sys.exit()
        elif message.upper() == "SEND FILE":
            print("What is the file path")
            path = input()
            message = DICT['SEND_FILE'] + path.encode()
            s.send(message)
            message = s.recv(1024)
            if message[:1] == DICT['CONFIRMATION']:
                message = message[1:].decode()
                print(message + '\n' + "This is the file size. Do you still want to download?")
                answer = input()
                if answer.upper() == "YES":
                    s.send(DICT['CONFIRMATION'])
                elif answer.upper() == "NO":
                    print("Ok. Cancelling...")
                else:
                    print("Sorry, this is not a valid request")
            else:
                print("Oh oh something went wrong.\n")
        elif message.upper() == "DELETE":
            print("What is the file path?")
            message = DICT['DELETE']+input().encode()
            s.send(message)
            message = s.recv(1024)
            if message == DICT['CONFIRMATION']:
                print("The file was deleted!!\n")
            if message == DICT['ERROR']:
                print("Oh oh. Something went wrong. The file was not deleted")
        elif message.upper() == "CHANGE NAME":
            print("What is the path of the file you want to change the name of")
            path = input()
            for char in path[::-1]:
                if char != '.':
                    file_format += char
                else:
                    break
            file_format = file_format[::-1]
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
        else:
            print("there is a problem with your input, please try again\n")


if __name__ == "__main__":
    main()
