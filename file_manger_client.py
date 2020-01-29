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
    print("'Send File' - a function that with a given path will send you a file from the server to your computer")
    print("'Change Name' - a function that with a given path the a file, will change its name with a name you will give")
    print("'Delete' - will delete the file in the path you will give")
    print("'EXIT' - will exit the program :(")
    print("What would you like me to do?\n")

    active = True
    while active:
        message = input()
        if message.upper() == "EXIT":
            active = False
            print("ok bye :(")
            s.send(DICT['EXIT'])
        elif message.upper() == "SEND FILE":
            pass
        elif message.upper() == "DELETE":
            print("What is the file path?")
            message = DICT['DELETE']+input().encode()
            s.send(message)
            message = s.recv(1024)
            print(message)
            if message == DICT['CONFIRMATION']:
                print("The file was deleted!!")
        elif message.upper() == "CHANGE NAME":
            pass
        else:
            print("there is a problem with your input, please try again")


if __name__ == "__main__":
    main()