import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def limit(text):
    """ Determine if inp string is a valid integer (or empty) and is no more
        than MAX_DIGITS long.
    """
    MAX_DIGITS = 11

    print(text)

    try:
        int(text)  # Valid integer?
    except ValueError:
        valid = (text == '')  # Invalid unless it's just empty.
    else:
        valid = (len(text) <= MAX_DIGITS)   # OK unless it's too long.

    if not valid:
        messagebox.showinfo('Entry error',
                            'Invalid input (should be {} digits)'.format(MAX_DIGITS),
                            icon=messagebox.WARNING)
    return valid


root = tk.Tk()
root.geometry('200x100')  # Initial size of root window.

label = tk.Label(root, text="Phone Number:", font=20, bg="#33BEFF")
label.pack()

reg = root.register(limit)  # Register Entry validation function.
string = tk.StringVar()
phno = ttk.Entry(root, textvariable=string, text="",
                 validate='key', validatecommand=(reg, '%P'))
phno.pack()
phno.focus_set()  # Set initial input focus to this widget.

root.mainloop()