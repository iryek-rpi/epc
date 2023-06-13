import customtkinter as ctk
 
ctk.set_appearance_mode("System")       
 
ctk.set_default_color_theme("green")   
 
class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("App")   
        self.geometry("200x200")   
 
 
if __name__ == "__main__":
    app = App()
    app.mainloop()   