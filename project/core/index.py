from tkinter import *
from tkinter import ttk

import sqlite3

class Product:

    db_name = 'db.sqlite3'

    def __init__(self, window):
        self.wind = window
        self.wind.title('Products Application')
    
        # Creating a frame container
        frame = LabelFrame(self.wind, text='Register a new product')
        frame.grid(row=0, column=0, columnspan=3, pady=20)

        # Name input
        Label(frame, text='Name: ').grid(row=1, column=0)
        self.name = Entry(frame)
        self.name.focus()
        self.name.grid(row=1, column=1)

        # Price input
        Label(frame, text='Price: ').grid(row=2, column=0)
        self.price = Entry(frame)
        self.price.grid(row=2, column=1)

        # Button add product
        ttk.Button(frame, text='Save product').grid(
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
        query = 'SELECT * FROM product ORDER BY name DESC'
        db_rows = self.run_query(query)


if __name__ == '__main__':
    window = Tk()
    application = Product(window)
    window.mainloop()