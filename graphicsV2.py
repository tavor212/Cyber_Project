from tkinter import *
import tkinter as tk
from functools import partial
from tkinter import filedialog

CLIENT_FILE_PATH = ""


class Table(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        t = SimpleTable(self, 10, 1)
        t.pack(side="top", fill="both")
        t.set(0, 0, "Storage")



class SimpleTable(tk.Frame):
    def __init__(self, parent, rows=10, columns=1):
        # use black background so it "peeks through" to
        # form grid lines
        tk.Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = tk.Label(self, text="%s/%s" % ("martingay.png", "150MB"),
                                 borderwidth=0, width=10)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)


def login_page():
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
    validateR = partial(validateRegistration, username, password)
    """TODO - when register is pressed, check correct terms and then wait for login"""
    registerButton = Button(tkWindow, text="Register", command=validateR).grid(row=4, column=1)

    # login button stuff
    validateL = partial(main_window, username, password, tkWindow)
    """TODO - when login is pressed, check user existes and then go to main window"""
    loginButton = Button(tkWindow, text="Login", command=validateL).grid(row=4, column=0)
    tkWindow.mainloop()


def browseFiles(label_file_explorer):
    global CLIENT_FILE_PATH
    filename = filedialog.askopenfilename(initialdir="/",title="Select a File",filetypes=(("Text files","*.txt*"),("all files","*.*")))
    # Change label contents
    label_file_explorer.configure(text="File Opened: " + filename)
    print(filename)
    CLIENT_FILE_PATH = filename
    print(CLIENT_FILE_PATH)



def file_explorer():
    # Create the root window
    window = Tk()

    # Set window title
    window.title('File Explorer')

    # Set window size
    window.geometry("500x500")

    # Set window background color
    window.config(background="white")

    # Create a File Explorer label
    label_file_explorer = Label(window,text="File Explorer using Tkinter",width=100, height=4,fg="blue")

    change_later = partial(browseFiles, label_file_explorer)
    button_explore = Button(window,text="Browse Files",command=change_later)

    button_exit = Button(window,text="Exit",command=exit)

    # Grid method is chosen for placing
    # the widgets at respective positions
    # in a table like structure by
    # specifying rows and columns
    label_file_explorer.grid(column=0, row=0)

    button_explore.grid(column=0, row=1)

    button_exit.grid(column=1, row=3)

    # Let the window wait for any events
    window.mainloop()


def main_window(username, password, tkwindow):
    print("username entered :", username.get())
    print("password entered :", password.get())
    tkwindow.destroy()
    data_table = Table()
    data_table.title("Cloud service")
    data_table.resizable(True,False)
    """TODO match every button to a server function"""
    Sendfile_Button = Button(data_table, text="Send file", command = file_explorer)
    Downloadfile_Button = Button(data_table, text="Download file")
    Changename_Button = Button(data_table, text="Change name")
    Delete_Button = Button(data_table, text="Delete")
    Sendfile_Button.pack(side=LEFT, fill="x")
    Downloadfile_Button.pack(side=LEFT, fill="x")
    Changename_Button.pack(side=LEFT, fill="x")
    Delete_Button.pack(side=LEFT, fill="x")
    return


def validateRegistration(username, password):
    print("username entered :", username.get())
    print("password entered :", password.get())
    return






login_page()