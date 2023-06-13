from tkinter import *

def callback(name, index, mode, sv):
    print(name, index, mode)
    print(sv.get())

root = Tk()
sv = StringVar()
sv.trace("w", lambda name, index, mode, sv=sv: callback(name, index, mode, sv))
e = Entry(root, textvariable=sv)
e.pack()
root.mainloop()  