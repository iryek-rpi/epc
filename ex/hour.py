# Import required libraries
from tkinter import *
from tkinter import ttk

pop=None

# Define a function to implement choice function
def choice(option):
   pop.destroy()
   if option == "yes":
      label.config(text="Hello, How are You?")
   else:
      label.config(text="You have selected No")

def click_fun():
   global pop
   pop = Toplevel(win)
   pop.title("Confirmation")
   pop.geometry("700x250")
   pop.config(bg="green3")
   # Create a Label Text
   label = Label(pop, text="Would You like to Proceed?", bg="green3", fg="white", font=('Aerial', 12))
   label.pack(pady=20)

   # Add a Frame
   frame = Frame(pop, bg="green3")
   frame.pack(pady=10)
   # Add Button for making selection
   button1 = Button(frame, text="Yes",
   command=lambda: choice("yes"), bg="green")
   button1.grid(row=0, column=1)
   button2 = Button(frame, text="No",
   command=lambda: choice("no"), bg="green")
   button2.grid(row=0, column=2)

win = Tk()
win.geometry("700x250")

label = Label(win, text="TEST", font=('Aerial', 14))
label.pack(pady=40)

ttk.Button(win, text="Click Here", command=click_fun).pack()

win.mainloop()
