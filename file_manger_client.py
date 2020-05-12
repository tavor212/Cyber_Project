import socket
import sys
import os
from tkinter import *
import time
from tkinter import *
import tkinter as tk
from functools import partial

PORT = 1000
HOST = '127.0.0.1'  # switch to the IP of the server PC if not local
DICT = {'ERROR': "300".encode(), 'REGISTER': "70".encode(), 'LOGIN': "60".encode(),'DOWNLOAD_FILE': "50".encode(), 'SEND_FILE': "40".encode(), 'CHANGE_NAME':  "30".encode(), 'DELETE': "20".encode(), 'EXIT': "10".encode(), 'CONFIRMATION': "1".encode()}



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
        """calculates the file size in megabytes"""
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
                    new_file.write(file_parts)
        elif answer.upper() == "NO":
            print("Ok. Cancelling...")
        else:
            print("Sorry, this is not a valid request")
    else:
        print("not in user directory.\n")


def send_file(s):
    print("What is the path of the file you want to send?")
    path = input()
    message = DICT['SEND_FILE'] + path.encode()
    s.send(message)
    file_size = os.path.getsize(path)

    """calculates the number of times the server will need to recv 1024 bytes"""
    number_of_loops = file_size / 1024
    number_of_loops = int(number_of_loops)
    if number_of_loops < 1:
        number_of_loops += 1
    print(number_of_loops)
    s.send((str(number_of_loops)).encode())
    print("What is the name of your created file?")
    new_file_name = input()
    s.send((str(new_file_name)).encode())

    """reads the file 1024 bytes at a time and sends to the server"""
    with open(path, 'rb') as f:
        for x in range(number_of_loops):
            file_parts = f.read(1024)
            s.send(file_parts)
            time.sleep(1)
        s.send(DICT['CONFIRMATION'])
        if s.recv(1024) == DICT['CONFIRMATION']:
            print("the file is stored in the server")



def change_name(s):
    print("What is the path of the file you want to change the name of")
    path = input()
    file_format = path.split(".")[-1]
    print("What is the new file name?")
    new_name = input()
    new_name = new_name + "." + file_format
    """adds a * in between the variables so i can seperate them later in the server"""
    message = DICT['CHANGE_NAME'] + path.encode() + '*'.encode() + new_name.encode()
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
    print("Yo you need to login in order to have or use a cloud service")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except:
        print("oh oh something went wrong")
        sys.exit()
    active = True
    while active:
        print("would you like to register, login or exit?")
        answer = input()
        if answer.upper() == "REGISTER":
            print("great, lets begin")
            print("please enter your username")
            username = input()
            print("please enter your password")
            password = input()
            message = DICT['REGISTER'] + (str(username)).encode() + ','.encode() + (str(password)).encode()
            print(message)
            s.send(message)
            message = s.recv(1024)
            if message == DICT['ERROR']:
                print("username already taken")
            elif message == DICT['CONFIRMATION']:
                active = False
            else:
                print("oh oh something went wrong")
        elif answer.upper() == "LOGIN":
            print("great, lets begin")
            print("please enter your username")
            username = input()
            print("please enter your password")
            password = input()
            message = DICT['LOGIN'] + (str(username)).encode() + ','.encode() + (str(password)).encode()
            print(message)
            s.send(message)
            message = s.recv(1024)
            if message == DICT['ERROR']:
                print("Sorry your username or password is wrong")
            elif message == DICT['CONFIRMATION']:
                active = False
            else:
                print("oh oh something went wrong")

        elif answer.upper() == "EXIT":
            print("ok bye")
            active = False
        else:
            print("sorry this isnt an option")
            active = True

    print("Hello \nWelcome to my amazing file management program. you wont find any other in the market :)")
    print("At your disposal are 4 main tools.")
    print("What would you like me to do?\n")

    active = True
    while active:
        print_menu()
        message = input()
        if message.upper() == "EXIT":
            exit(s)
        elif message.upper() == "DOWNLOAD FILE":
            download_file(s)
        elif message.upper() == "SEND FILE":
            send_file(s)
        elif message.upper() == "DELETE":
            delete(s)
        elif message.upper() == "CHANGE NAME":
            change_name(s)
        else:
            print("there is a problem with your input, please try again\n")


if __name__ == "__main__":
    main()
