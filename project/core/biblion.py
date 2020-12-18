from tkinter import *
from tkinter import ttk

import sqlite3

class Product:

    db_name = 'db.sqlite3'

    def __init__(self, window):
        self.wind = window
        self.wind.title('Biblion')
    
        # Creating a frame container
        frame = LabelFrame(self.wind, text='Register a new read book')
        frame.grid(row=0, column=0, columnspan=3, pady=20)

        # Name input
        Label(frame, text='Title: ').grid(row=1, column=0)
        self.name = Entry(frame)
        self.name.focus()
        self.name.grid(row=1, column=1)

        # Start date input
        Label(frame, text='Start date: ').grid(row=2, column=0)
        self.start_date = Entry(frame)
        self.start_date.grid(row=2, column=1)

        # End date input
        Label(frame, text='End date: ').grid(row=2, column=0)
        self.end_date = Entry(frame)
        self.end_date.grid(row=2, column=1)

        # Button add product
        ttk.Button(frame, text='Save book').grid(
            row=3, columnspan=2, sticky= W+E)

        # Table
        self.tree = ttk.Treeview(height=10, columns=2)
        self.tree.grid(row=4, column=0, columnspan=2)
        self.tree.heading('#0', text='Name', anchor=CENTER)
        self.tree.heading('#1', text='Price', anchor=CENTER)

        self.get_products()

    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    def get_products(self):
        # cleaning table
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)

        # quering data
        query = 'SELECT * FROM product ORDER BY name DESC'
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert('', 0, text=row[1], values=row[2])

if __name__ == '__main__':
    window = Tk()
    application = Product(window)
    window.mainloop()