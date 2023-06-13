from customtkinter import *
 
app = CTk()
app.geometry("400x300")
 
password = CTkEntry(app, placeholder_text="password please...")
password.pack()
 
def clicked():
    cp = "I don't know"
    p = password.get()
    if p == cp:
        label = CTkLabel(app, text="Correct password")
        label.pack()
    else:
        label = CTkLabel(app, text="Incorrect password")
        label.pack()
 
btn = CTkButton(master=app, text="Click Me!", command=clicked)
btn.pack()
 
app.mainloop()