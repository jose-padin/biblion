import re
import sqlite3

from tkinter import *
from tkinter import ttk


class Book:

    db_name = 'db.sqlite3'

    def __init__(self, window):
        self.window = window
        self.window.title('Biblion')

        # To set the width and height of the window
        # self.window.geometry('1000x800')
    
        # Creating a frame container
        frame = LabelFrame(self.window, text='Register a new read book')
        frame.grid(row=0, column=0, columnspan=3, pady=20)

        # Title input
        Label(frame, text='Title: ').grid(row=1, column=0)
        self.title = Entry(frame)
        self.title.focus()
        self.title.grid(row=1, column=1)

        # Start date input
        Label(frame, text='Start date: ').grid(row=2, column=0)
        self.start_date = Entry(frame)
        self.start_date.grid(row=2, column=1)

        # End date input
        Label(frame, text='End date: ').grid(row=3, column=0)
        self.end_date = Entry(frame)
        self.end_date.grid(row=3, column=1)

        # Button add book
        ttk.Button(frame, text='Save book', command=self.add_book).grid(
            row=4, columnspan=2, sticky= W+E)

        # Button delete book
        ttk.Button(text='Delete', command=self.delete_book).grid(
            row=6,
            column=0,
            sticky=W+E
        )
        ttk.Button(text='Edit', command=self.edit_book).grid(
            row=6,
            column=1,
            sticky=W+E
        )

        # Filter by year
        Label("", text='Year to filter').grid(row=7, column=0)
        self.filter_entry = Entry(self.window)
        self.filter_entry.grid(row=7, column=1)

        ttk.Button(text='Filter', command=self.filter).grid(
            row=7,
            column=2,
            sticky=W+E
        )

        # Output messages
        self.message = Label(text='', fg='red')
        self.message.grid(row=3, column=0, columnspan=2, sticky=W+E)

        # Table
        self.tree = ttk.Treeview(height=10, columns=("title", "start_date", "end_date"))
        self.tree.grid(row=5, column=0, columnspan=2)
        self.tree.heading('title', text='Title', anchor=W)
        self.tree.heading('start_date', text='Start date', anchor=W)
        self.tree.heading('end_date', text='End date', anchor=W)

        self.get_books()

    def filter(self):
        year = self.filter_entry.get()
        if self.validate_year(year):
            window_filter = Toplevel(self.window)
            window_filter.title(f'Filter books. Year {year}')
            query = f'SELECT * FROM book WHERE end_date LIKE "%{year}" ORDER BY title DESC'
            parameters = (year,)
            result = self.run_query(query)

            tree = ttk.Treeview(window_filter, columns=('title', 'date_start', 'date_end'), show='headings')
            tree.grid(row=8, column=0, sticky=W+E)
            tree.heading('title', text='Title')
            tree.heading('date_start', text='Date start reading')
            tree.heading('date_end', text='Date end reading')

            total = 0
            for i, row in enumerate(result):
                tree.insert("", 0, values=(row[1], row[2], row[3]))
                total = i+1

            label_total = Label(window_filter, text=f'Total books read in the year {year}')
            label_total.grid(row=9, column=0)
            entry_total = Entry(
                window_filter,
                textvariable=StringVar("", total),
                state='readonly',
                justify='center')
            entry_total.grid(row=9, column=1)

    def validate_year(self, year):
        match = re.search('\d{4}', year)
        if match:
            return True
        return False

    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    def get_books(self):
        # cleaning table
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)

        # querying data
        query = 'SELECT * FROM book ORDER BY title DESC'
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert("", 0, text=row[0], values=(row[1], row[2], row[3]))

    def validations(self):
        if len(self.title.get()) != 0 and len(self.start_date.get()) != 0:
            return self.validate_start_date()

    def validate_start_date(self, date=None):
        if not date:
            start_date = self.start_date.get()
        else:
            start_date = date

        match = re.search('\d{1,2}/\d{1,2}/\d{4}', start_date)
        
        if match:
            return True
        return False

    def validate_end_date(self, date=None):
        if not date:
            end_date = self.end_date.get()
        else:
            end_date = date

        match = re.search('\d{1,2}/\d{1,2}/\d{4}', end_date)
        
        if match:
            return True
        return False


    def add_book(self):
        if self.validations():
            if len(self.end_date.get()) == 0:
                end_date = ''
            else:
                validated = self.validate_start_date()
                if validated:
                    end_date = self.end_date.get()
                else:
                    return False

            query = 'INSERT INTO book VALUES(NULL, ?, ?, ?)'
            parameters = (self.title.get(), self.start_date.get(), end_date)
            self.run_query(query, parameters)
            self.get_books()

            # print('Data saved!')
            self.message['text'] = f'Book {self.title.get()} added'
            self.title.delete(0, END)
            self.start_date.delete(0, END)
            self.end_date.delete(0, END)
        else:
            self.message['text'] = 'There was an error. \nHave you already inserted title and start date?'

    def delete_book(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'Please, select a record'
            return
        
        self.message['text'] = ''
        title = self.tree.item(self.tree.selection())['values'][0]
        query = 'DELETE FROM book WHERE title = ? LIMIT 1'
        self.run_query(query, (title,))
        self.message['text'] = f'Record {title} deleted'
        self.get_books()

    def edit_book(self):
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'Please, select a record'
            return
        
        old_title = self.tree.item(self.tree.selection())['values'][0]
        old_start_date = self.tree.item(self.tree.selection())['values'][1]
        old_end_date = self.tree.item(self.tree.selection())['values'][2]

        # Open a new window to edit a book
        self.edit_window = Toplevel()
        self.edit_window.title = 'Edit book'

        # Old title
        Label(self.edit_window, text='Old title').grid(row=0, column=1)
        Entry(
            self.edit_window,
            textvariable=StringVar(
                self.edit_window,
                value=old_title
            ),
            state='readonly').grid(row=0, column=2)

        # New title
        Label(self.edit_window, text='New title').grid(row=1, column=1)
        new_title = Entry(self.edit_window)
        new_title.grid(row=1, column=2)

        # Old start_date
        Label(self.edit_window, text='Old start date').grid(row=2, column=1)
        Entry(self.edit_window, textvariable=StringVar(
                self.edit_window,
                value=old_start_date),
            state='readonly').grid(row=2, column=2)

        # New start_date
        Label(self.edit_window, text='New start date').grid(row=3, column=1)
        new_start_date = Entry(self.edit_window)
        new_start_date.grid(row=3, column=2)

        # Old end_date
        Label(self.edit_window, text='Old end date').grid(row=4, column=1)
        Entry(self.edit_window, textvariable=StringVar(
                self.edit_window,
                value=old_end_date),
            state='readonly').grid(row=4, column=2)

        # New end_date
        Label(self.edit_window, text='New end date').grid(row=5, column=1)
        new_end_date = Entry(self.edit_window)
        new_end_date.grid(row=5, column=2)

        Button(self.edit_window, text='Update',
            command=lambda: self.edit_records(
                new_title.get(),
                old_title,
                new_start_date.get(),
                old_start_date,
                new_end_date.get(),
                old_end_date)).grid(row=6, column=2, sticky=W)

    def edit_records(self, new_title, old_title, new_start_date, old_start_date, new_end_date, old_end_date):
        if new_title == '':
            new_title = old_title
        if new_start_date == '':
            new_start_date = old_start_date
        if new_end_date == '':
            new_end_date = old_end_date

        if self.validate_start_date(new_start_date) and self.validate_end_date(new_end_date):
            query = 'UPDATE book SET title = ?, start_date = ?, end_date = ? WHERE title = ? AND start_date = ?'
            parameters = (new_title, new_start_date, new_end_date, old_title, old_start_date)
            self.run_query(query, parameters)
        else:
            return

        self.edit_window.destroy()
        self.message['text'] = 'Record updated succesfully!'
        self.get_books()


if __name__ == '__main__':
    window = Tk()
    application = Book(window)
    window.mainloop()