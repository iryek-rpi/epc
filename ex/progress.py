import customtkinter as CTK
import tkinter


class App(CTK.CTk):
    def __init__(self):
        super().__init__()

        self.check_var = CTK.StringVar(value="on-DHCP")

        self.checkbox = CTK.CTkCheckBox(master=self, text="CTkCheckBox", command=self.checkbox_event,
                                     variable=self.check_var, onvalue="on", offvalue="off")
        #self.checkbox.pack(padx=20, pady=10)
        self.checkbox.grid(row=0, column=0, pady=10, padx=20, sticky="n")
        self.bar = CTK.CTkProgressBar(master=self,#self.checkbox,
                                  orientation='horizontal',
                                  mode='determinate')
    
        self.bar.grid(row=10, column=0, pady=10, padx=20, sticky="n")
    
        # Set default starting point to 0
        self.bar.set(0)
    
    def checkbox_event(self):
        print("checkbox toggled, current value:", self.check_var.get())
        self.test()

    def test(self):
        n = 500
        iter_step = 1/n
        progress_step = iter_step
        self.bar.start()
        
        for x in range(500):
            self.bar.set(progress_step)
            progress_step += iter_step
            self.update_idletasks()
        self.bar.stop()

app = App()
app.test()
app.mainloop()