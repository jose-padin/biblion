import re
import sqlite3

from tkinter import *
from tkinter import ttk


class Book:

    db_name = 'db.sqlite3'

    def __init__(self, window):
        self.window = window
        self.window.title('Biblion')
    
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

        # quering data
        query = 'SELECT * FROM book ORDER BY title DESC'
        db_rows = self.run_query(query)
        for row in db_rows:
            self.tree.insert("", 0, text=row[0], values=(row[1], row[2], row[3]))

    def validations(self):
        if len(self.title.get()) != 0 and len(self.start_date.get()) != 0:
            # return self.validate_title() and self.validate_start_date()
            return self.validate_start_date()

    # def validate_title(self):
    #     return len(self.title.get()) != 0

    def validate_start_date(self):
        start_date = self.start_date.get()
        match = re.search('\d{1,2}/\d{1,2}/\d{4}', self.start_date.get())
        
        if match:
            return True
        
        return False

    def validate_end_date(self):
        start_date = self.end_date.get()
        match = re.search('\d{1,2}/\d{1,2}/\d{4}', self.end_date.get())
        
        if match:
            return True
        
        return False

    def add_book(self):
        if self.validations():
            if len(self.end_date.get()) == 0:
                end_date = ''
            else:
                validated = self.validate_end_date()
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
            self.message['text'] = 'There was an error'
            print('Error')

    def delete_book(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = 'Please, select a record'
            return
        
        self.message['text'] = ''
        title = self.tree.item(self.tree.selection())['text']
        query = 'DELETE FROM book WHERE title = ? LIMIT 1'
        self.run_query(query, (title,))
        self.message['text'] = f'Record {title} deleted'
        self.get_books()

    def edit_book(self):
        try:
            self.tree.item(self.tree.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = 'Please, select a record'
            return
        
        # Old title
        old_title = self.tree.item(self.tree.selection())['text']
        old_start_date = self.tree.item(self.tree.selection())['values'][0]
        # old_end_date = self.tree.item(self.tree.selection())['values'][]

        self.edit_window = Toplevel()
        self.edit_window.title = 'Edit book'

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
        Entry(self.edit_window).grid(row=3, column=2)

        # ToDo
        # Old end_date
        # Label(self.edit_window, text='Old end date').grid(row=4, column=1)
        # Entry(self.edit_window, textvariable=StringVar(
        #         self.edit_window,
        #         value=old_end_date),
        #     state='readonly').grid(row=2, column=2)

        # ToDo
        # New end_date

        Button(self.edit_window, text='Update',
            command=lambda: self.edit_records(
                new_title.get(),
                old_title,
                new_start_date.get(),
                old_start_date,
                new_end_date.get(),
                old_end_date)).grid(row=4, column=2, sticky=W)

    def edit_records(self, new_title, old_title, new_start_date, old_start_date, new_end_date, old_end_date):
        query = 'UPDATE book SET title = ?, start_date = ?, end_date = ? WHERE title = ? AND start_date = ?'
        parameters = (new_title, new_start_date, new_end_date, old_title, old_start_date)
        self.run_query(query, parameters)
        self.edit_window.destroy()
        self.messages['text'] = 'Record updated succesfully!'
        self.get_books()


if __name__ == '__main__':
    window = Tk()
    application = Book(window)
    window.mainloop()