import socket
import sys
import os
from tkinter import *
import time
from tkinter import *
import tkinter as tk
from functools import partial
from tkinter import filedialog
import json
from tkinter import simpledialog


PORT = 1000
HOST = '127.0.0.1'  # switch to the IP of the server PC if not local
DICT = {'ERROR': "300".encode(), 'REGISTER': "70".encode(), 'LOGIN': "60".encode(),'DOWNLOAD_FILE': "50".encode(), 'SEND_FILE': "40".encode(), 'CHANGE_NAME':  "30".encode(), 'DELETE': "20".encode(), 'EXIT': "10".encode(), 'CONFIRMATION': "1".encode()}
LIST_OF_FILES_PLUS_SIZE = []
CLIENT_FILE_PATH = ""

class Table(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        #print(LIST_OF_FILES_PLUS_SIZE)
        t = SimpleTable(self, int(((LIST_OF_FILES_PLUS_SIZE.__len__())+1)/2), 1)
        t.pack(side="top", fill="both")


class SimpleTable(tk.Frame):
    def __init__(self, parent, rows, columns):
        print(rows)
        # use black background so it "peeks through" to
        # form grid lines
        tk.Frame.__init__(self, parent, background="black")
        self._widgets = []
        file_sizes = []
        file_names = []
        place = 0
        while place < LIST_OF_FILES_PLUS_SIZE.index(","):
            file_names.append(LIST_OF_FILES_PLUS_SIZE[place])
            print(file_names[place])
            print(LIST_OF_FILES_PLUS_SIZE[place])
            print(place)
            place += 1
            if LIST_OF_FILES_PLUS_SIZE[place] == ",":
                while place != LIST_OF_FILES_PLUS_SIZE.__len__():
                    place += 1
                    if place > LIST_OF_FILES_PLUS_SIZE.__len__()-1:
                        pass
                    else:
                        file_sizes.append(LIST_OF_FILES_PLUS_SIZE[place])
        place = 0
        for row in range(rows):
            current_row = []
            for column in range(columns):
                if row == 0 and column == 0 :
                    label = tk.Label(self, text="Storage:")
                    label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                else:
                    if place != file_names.__len__():
                        label = tk.Label(self, text="%s/%s" % (file_names[place], str(file_sizes[place]) +  " " + "MB"),borderwidth=0, width=10)
                        label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                        current_row.append(label)
                        place += 1
                self._widgets.append(current_row)


        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)


def login_page(s):
    tkWindow = Tk()
    tkWindow.geometry('300x100')
    tkWindow.title('Tkinter Login Form')
    tkWindow.resizable(False, False)

    # username label and text entry box
    usernameLabel = Label(tkWindow, text="User Name").grid(row=0, column=0)
    username = StringVar()
    usernameEntry = Entry(tkWindow, textvariable=username).grid(row=0, column=1)

    # password label and password entry box
    Label(tkWindow, text="Password").grid(row=1, column=0)
    password = StringVar()
    Entry(tkWindow, textvariable=password, show='*').grid(row=1, column=1)

    # register button
    validateR = partial(validateRegistration, s, username, password, tkWindow)
    registerButton = Button(tkWindow, text="Register", command=validateR).grid(row=4, column=1)

    # login button stuff
    validateL = partial(validateLogin, s, username, password, tkWindow)
    loginButton = Button(tkWindow, text="Login", command=validateL).grid(row=4, column=0)
    tkWindow.mainloop()


def validateRegistration(s, username, password, tkwindow):
    message = DICT['REGISTER'] + (str(username.get())).encode() + ','.encode() + (str(password.get())).encode()
    print(message)
    s.send(message)
    message = s.recv(1024)
    if message == DICT['ERROR']:
        print("username already taken")
        error_screen()
    elif message == DICT['CONFIRMATION']:
        active = False
        print("register")
        main_window(s, username,password, tkwindow)
    else:
        print("oh oh something went wrong")
        error_screen()
    return


def validateLogin(s, username, password, tkWindow):
    message = DICT['LOGIN'] + (str(username.get())).encode() + ','.encode() + (str(password.get())).encode()
    print(message)
    s.send(message)
    message = s.recv(1024)
    if message == DICT['ERROR']:
        print("Sorry your username or password is wrong")
        error_screen()
    elif message == DICT['CONFIRMATION']:
        active = False
        main_window(s, username,password, tkWindow)
    else:
        print("oh oh something went wrong")
        error_screen()


def main_window(s, username, password, window):
    global LIST_OF_FILES_PLUS_SIZE
    print("here")
    window.destroy()
    print("username entered :", username.get())
    print("password entered :", password.get())
    LIST_OF_FILES_PLUS_SIZE = s.recv(1024)
    print("help")
    print(LIST_OF_FILES_PLUS_SIZE)
    LIST_OF_FILES_PLUS_SIZE = LIST_OF_FILES_PLUS_SIZE.decode()
    print(LIST_OF_FILES_PLUS_SIZE)
    LIST_OF_FILES_PLUS_SIZE = json.loads(LIST_OF_FILES_PLUS_SIZE)
    print(LIST_OF_FILES_PLUS_SIZE)
    data_table = Table()
    data_table.title("Cloud service")
    data_table.resizable(True,False)

    sendfile = partial(file_explorer, s, username, password, data_table)
    Sendfile_Button = Button(data_table, text="Send file", command = sendfile)


    Downloadfile_Button = Button(data_table, text="Download file")


    Changename_Button = Button(data_table, text="Change name")

    deletefile = partial(delete, s, username, password, data_table)
    Delete_Button = Button(data_table, text="Delete", command = deletefile)

    Sendfile_Button.pack(side=LEFT, fill="x")
    Downloadfile_Button.pack(side=LEFT, fill="x")
    Changename_Button.pack(side=LEFT, fill="x")
    Delete_Button.pack(side=LEFT, fill="x")
    return


def error_screen():
    window = Tk()
    window.title('ERROR')
    window.geometry("600x200")
    window.config(background="white")
    label_file_explorer = Label(window, text="oh oh something went wrong.", width=100, height=4, fg="blue")
    label_file_explorer.grid(column=0, row=0)


def browse_and_sendFiles(s, username, password, label_file_explorer, window):
    global CLIENT_FILE_PATH
    filepath = filedialog.askopenfilename(initialdir="/",title="Select a File",filetypes=(("Text files","*.txt*"),("all files","*.*")))
    # Change label contents
    label_file_explorer.configure(text="File Opened: " + filepath)
    CLIENT_FILE_PATH = filepath
    print(CLIENT_FILE_PATH)
    send_file(s)
    main_window(s, username, password, window)


def file_explorer(s, username, password, window):
    # Create the root window
    window.destroy()
    explorer_window = Tk()

    # Set window title
    explorer_window.title('File Explorer')

    # Set window size
    explorer_window.geometry("600x250")

    # Set window background color
    explorer_window.config(background="white")

    # Create a File Explorer label
    label_file_explorer = Label(explorer_window,text="File Explorer using Tkinter",width=100, height=4,fg="blue")

    browse = partial(browse_and_sendFiles, s, username, password, label_file_explorer, explorer_window)
    button_explore = Button(explorer_window,text="Browse Files",command=browse)

    # Grid method is chosen for placing
    # the widgets at respective positions
    # in a table like structure by
    # specifying rows and columns
    label_file_explorer.grid(column=0, row=0)

    button_explore.grid(column=0, row=1)

    # Let the window wait for any events

    explorer_window.mainloop()

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
    path = CLIENT_FILE_PATH
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
    new_file_name = simpledialog.askstring(title = "name gathering", prompt ="what would you like to name your file?")
    s.send((str(new_file_name)).encode())
    print("sent")
    """reads the file 1024 bytes at a time and sends to the server"""
    with open(path, 'rb') as f:
        for x in range(number_of_loops):
            file_parts = f.read(1024)
            s.send(file_parts)
            print("parts")
        time.sleep(2)




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


def delete(s, username, password, window):
    print("What is the file path?")
    file_name = simpledialog.askstring(title = "name gathering", prompt ="what file would you like to delete (include the format)?")
    message = DICT['DELETE'] + file_name.encode()
    print("before sent")
    s.send(message)
    print("after send")
    message = s.recv(1024)
    print("here?")
    if message == DICT['CONFIRMATION']:
        print("The file was deleted!!\n")
        main_window(s,username, password, window)
    if message == DICT['ERROR']:
        error_screen()
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
    login_page(s)
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
