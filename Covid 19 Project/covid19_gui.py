from tkinter import *
from tkinter import messagebox as ms
from tkinter import ttk
import sqlite3
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


with sqlite3.connect('Users.db') as db:
    cursor = db.cursor()

cursor.execute(
    "CREATE TABLE IF NOT EXISTS Users(First TEXT, Last TEXT, Email TEXT, username TEXT, password TEXT)")
db.commit()
db.close()


class main:

    def __init__(self, tk):

        self.tk = tk

        self.First_Name = StringVar()
        self.Last_Name = StringVar()
        self.Email = StringVar()
        # Login
        self.username = StringVar()
        self.password = StringVar()
        # Register
        self.Username = StringVar()
        self.Password = StringVar()

        self.state = StringVar()

        self.id = StringVar()
        self.clicked = StringVar()
        self.widgets()

    def login(self):
        with sqlite3.connect('Users.db') as db:
            cursor = db.cursor()

            # Check if username and password is in the database
            check_user = (
                'SELECT * FROM Users WHERE username = ? and password = ?')
            cursor.execute(
                check_user, [(self.username.get()), (self.password.get())])
            result = cursor.fetchall()
            if self.username.get() == 'admin' and self.password.get() == 'pass':
                self.login_frame.pack_forget()
                self.head['text'] = 'Admin Page'
                self.head['pady'] = 150
                self.admin_page.pack()

            elif result:
                self.login_frame.pack_forget()
                self.head['text'] = self.username.get() + ' Logged in'
                self.head['pady'] = 50
                self.user_page.pack()
            else:
                ms.showerror('Username or Password is incorrect')

    # Add User to database

    def register(self):
        with sqlite3.connect('Users.db') as db:
            cursor = db.cursor()

        # Check if username already exists
        check_user = ('SELECT username FROM Users WHERE username = ?')
        cursor.execute(check_user, [(self.Username.get())])
        if cursor.fetchall():
            ms.showerror('Username Already Taken')
        else:
            insert = 'INSERT INTO Users(First, Last, Email, username, password) VALUES(?,?,?,?,?)'
            cursor.execute(insert, [(self.First_Name.get()), (self.Last_Name.get(
            )), (self.Email.get()), (self.Username.get()), (self.Password.get())])
            ms.showinfo('Registration Complete')
            self.log()

        db.commit()

    # Bring user back to login page

    def log(self):
        self.First_Name.set('')
        self.Last_Name.set('')
        self.Email.set('')
        self.username.set('')
        self.password.set('')
        self.register_frame.pack_forget()
        self.admin_page.pack_forget()
        self.head['text'] = 'COVID 19 LOGIN'
        self.login_frame.pack()

    # Bring user to registration page

    def create(self):
        self.Username.set('')
        self.Password.set('')
        self.login_frame.pack_forget()
        self.head['text'] = 'Create Account'
        self.register_frame.pack()

    # List all the users

    def listUsers(self):
        with sqlite3.connect('Users.db') as db:
            cursor = db.cursor()

        cursor.execute("SELECT *, oid FROM Users")
        records = cursor.fetchall()
        print_records = ''
        for record in records:
            print_records += str(record[0]) + " " + \
                str(record[1]) + " " + "\t" + str(record[5]) + "\n"
        list_label = Label(self.admin_page, text=print_records)
        list_label.grid(row=8, column=1)

        db.commit()

    # Remove users from database
    def removeUsers(self):
        with sqlite3.connect('Users.db') as db:
            cursor = db.cursor()

        cursor.execute('DELETE from Users WHERE oid = ?', (self.id.get(),))

        # delete_box.delete(0, END)

      # Commit Changes
        db.commit()

    def goToUS(self):
        self.user_page.pack_forget()
        self.us_page.pack()

    def goToUser(self):
        self.us_page.pack_forget()
        self.user_page.pack()

    # Plot data onto GUI

    def plot(self):
        choice = self.clicked.get()
        if choice == 'Confirmed':
            df = pd.read_csv('time_series_covid_19_confirmed.csv')
        elif choice == 'Deaths':
            df = pd.read_csv('time_series_covid_19_deaths.csv')
        else:
            df = pd.read_csv('time_series_covid_19_recovered.csv')

        df = df.drop(columns=["Province/State", "Lat", "Long"])
        df = df.groupby("Country/Region").aggregate(np.sum).T
        df.index.name = "Date"
        df = df.reset_index()
        melt_c_df = df.melt(
            id_vars=["Date"], var_name="Country", value_name=self.clicked.get())
        melt_c_df["Date"] = pd.to_datetime(melt_c_df["Date"])
        max_date = melt_c_df["Date"].max()
        total_c_df = melt_c_df[melt_c_df["Date"] == max_date]
        total_c_df = total_c_df.loc[total_c_df[self.clicked.get()] >= 100000]
        country = total_c_df['Country']
        cases = total_c_df[self.clicked.get()]

        fig = Figure(figsize=(15, 8), dpi=80)
        plot1 = fig.add_subplot(111)
        plot1.bar(country, cases, width=0.2)
        plot1.set_title(self.clicked.get()+' Cases by Country')
        plot1.set_ylabel('Cases')
        plot1.set_xticklabels(country, rotation=90)

        canvas = FigureCanvasTkAgg(fig, self.user_page)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=1)

    def plot_states(self):
        choice = self.clicked.get()
        if choice == 'Confirmed':
            df = pd.read_csv('time_series_covid_19_confirmed_US.csv')
        else:
            df = pd.read_csv('time_series_covid_19_deaths_US.csv')
            df = df.drop(columns=["Population"])

        df = df.drop(columns=["UID", "iso2", "iso3", "code3", "FIPS",
                     "Admin2", "Country_Region", "Lat", "Long_", "Combined_Key"])
        df = df.groupby("Province_State").aggregate(np.sum).T
        df.index.name = "Date"
        df = df.reset_index()
        melt_s_df = df.melt(
            id_vars=["Date"], var_name="Province_State", value_name=self.clicked.get())
        melt_s_df["Date"] = pd.to_datetime(melt_s_df["Date"])
        max_date = melt_s_df["Date"].max()
        total_s_df = melt_s_df[melt_s_df["Date"] == max_date]
        states = total_s_df['Province_State']
        cases = total_s_df[self.clicked.get()]

        fig = Figure(figsize=(15, 8), dpi=80)
        plot1 = fig.add_subplot(111)
        plot1.bar(states, cases, width=0.2)
        plot1.set_title(self.clicked.get()+' Cases by States')
        plot1.set_ylabel('Cases')
        plot1.set_xticklabels(states, rotation=90)

        canvas = FigureCanvasTkAgg(fig, self.us_page)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=1)

    def widgets(self):
        self.head = Label(self.tk, text='COVID 19 LOGIN',
                          font=('', 35), pady=10)
        self.head.pack()

        # Login Page
        self.login_frame = Frame(self.tk, padx=10, pady=10)
        Label(self.login_frame, text='Username: ', font=(
            '', 20), padx=5, pady=5).grid(sticky=W)
        Entry(self.login_frame, textvariable=self.username,
              bd=5, font=('', 15)).grid(row=0, column=1)
        Label(self.login_frame, text='Password: ', font=(
            '', 20), pady=5, padx=5).grid(sticky=W)
        Entry(self.login_frame, textvariable=self.password, bd=5,
              font=('', 15), show='*').grid(row=1, column=1)
        Button(self.login_frame, text=' Login ', bd=3, font=(
            '', 15), padx=5, pady=5, command=self.login).grid()
        Button(self.login_frame, text=' Create Account ', bd=3, font=(
            '', 15), padx=5, pady=5, command=self.create).grid(row=2, column=1)
        self.login_frame.pack()

        # Registration Page
        self.register_frame = Frame(self.tk, padx=10, pady=10)
        Label(self.register_frame, text='First Name: ',
              font=('', 20), padx=5, pady=5).grid(sticky=W)
        Entry(self.register_frame, textvariable=self.First_Name,
              bd=5, font=('', 15)).grid(row=0, column=1)
        Label(self.register_frame, text='Last Name: ',
              font=('', 20), padx=5, pady=5).grid(sticky=W)
        Entry(self.register_frame, textvariable=self.Last_Name,
              bd=5, font=('', 15)).grid(row=1, column=1)
        Label(self.register_frame, text='Email: ', font=(
            '', 20), padx=5, pady=5).grid(sticky=W)
        Entry(self.register_frame, textvariable=self.Email,
              bd=5, font=('', 15)).grid(row=2, column=1)
        Label(self.register_frame, text='Username: ',
              font=('', 20), pady=5, padx=5).grid(sticky=W)
        Entry(self.register_frame, textvariable=self.Username,
              bd=5, font=('', 15)).grid(row=3, column=1)
        Label(self.register_frame, text='Password: ',
              font=('', 20), pady=5, padx=5).grid(sticky=W)
        Entry(self.register_frame, textvariable=self.Password,
              bd=5, font=('', 15), show='*').grid(row=4, column=1)
        Button(self.register_frame, text='Create Account', bd=3, font=(
            '', 15), padx=5, pady=5, command=self.register).grid()
        Button(self.register_frame, text='Go to Login', bd=3, font=(
            '', 15), padx=5, pady=5, command=self.log).grid(row=5, column=1)

        # Admin Page
        self.admin_page = Frame(self.tk, padx=10, pady=10)
        Label(self.admin_page, text='First Name: ', font=(
            '', 20), padx=5, pady=5).grid(sticky=W)
        Entry(self.admin_page, textvariable=self.First_Name,
              bd=5, font=('', 15)).grid(row=0, column=1)
        Label(self.admin_page, text='Last Name: ', font=(
            '', 20), padx=5, pady=5).grid(sticky=W)
        Entry(self.admin_page, textvariable=self.Last_Name,
              bd=5, font=('', 15)).grid(row=1, column=1)
        Label(self.admin_page, text='Email: ', font=(
            '', 20), padx=5, pady=5).grid(sticky=W)
        Entry(self.admin_page, textvariable=self.Email,
              bd=5, font=('', 15)).grid(row=2, column=1)
        Label(self.admin_page, text='Username: ', font=(
            '', 20), pady=5, padx=5).grid(sticky=W)
        Entry(self.admin_page, textvariable=self.Username,
              bd=5, font=('', 15)).grid(row=3, column=1)
        Label(self.admin_page, text='Password: ', font=(
            '', 20), pady=5, padx=5).grid(sticky=W)
        Entry(self.admin_page, textvariable=self.Password, bd=5,
              font=('', 15), show='*').grid(row=4, column=1)
        Button(self.admin_page, text='Add User', bd=3, font=(
            '', 15), padx=5, pady=5, command=self.register).grid()
        Label(self.admin_page, text="Enter ID", bd=3,
              font=('', 15)).grid(row=6, column=0)
        Entry(self.admin_page, textvariable=self.id,
              bd=5, font=('', 15)).grid(sticky=W)
        Button(self.admin_page, text='Remove User', bd=3, font=('', 15),
               padx=5, pady=5, command=self.removeUsers).grid(row=5, column=1)
        Button(self.admin_page, text='Go to Login', bd=3, font=('', 15),
               padx=5, pady=5, command=self.log).grid(row=5, column=2)
        Button(self.admin_page, text="List Users", bd=3, font=('', 15),
               padx=5, pady=5, command=self.listUsers).grid(row=7, column=1)

        # Drop Down Menu
        options = [
            "Confirmed",
            "Deaths",
            "Recovered"
        ]

        # Initial Option
        self.clicked.set(options[0])

        # US Page
        self.us_page = Frame(self.tk, padx=10, pady=10)
        Button(self.us_page, text='View World',
               command=self.goToUser).grid(row=1, column=2)

        OptionMenu(self.us_page, self.clicked, *["Confirmed", "Deaths"]).grid(row=0, column=1)
        Button(self.us_page, text='Plot',
               command=self.plot_states).grid(row=1, column=1)
        # User page

        self.user_page = Frame(self.tk, padx=10, pady=10)

        OptionMenu(self.user_page, self.clicked,
                   *options).grid(row=0, column=1)
        Button(self.user_page, text='Plot',
               command=self.plot).grid(row=1, column=1)
        Button(self.user_page, text='View US',
               command=self.goToUS).grid(row=1, column=2)


if __name__ == '__main__':
    root = Tk()
    root.title('Covid 19')
    root.geometry('500x500')
    main(root)
    root.mainloop()
