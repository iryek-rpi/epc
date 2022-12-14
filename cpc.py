import tkinter
import tkinter.filedialog as fdlg
import tkinter.messagebox
import customtkinter as ctk

ctk.set_appearance_mode(
    "light")  #"System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme(
    "blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("(주)위너스시스템 데이터암호화 모듈 클라이언트")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        #self.grid_columnconfigure((2,3), weight=1)
        self.grid_columnconfigure((2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        #===========================================================================
        # create sidebar frame with widgets
        self.sidebar_frame = ctk.CTkFrame(self, width=160, corner_radius=0)  #,
        #fg_color='green')
        self.sidebar_frame.grid(row=0, column=0, rowspan=8, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure((13, 14), weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame,
                                       text="암호화 단말 정보",
                                       font=ctk.CTkFont(size=14,
                                                        weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(10, 10))

        self.label_ip = ctk.CTkLabel(self.sidebar_frame, text="단말 IP:")
        self.label_ip.grid(row=1, column=0, padx=10, pady=(5, 1), sticky="nw")

        self.entry_ip = ctk.CTkEntry(self.sidebar_frame,
                                     placeholder_text="IP Address")
        self.entry_ip.grid(row=2, column=0, padx=10, pady=(1, 10), sticky="nw")

        self.label_wifi = ctk.CTkLabel(self.sidebar_frame, text="WIFI")
        self.label_wifi.grid(row=3,
                             column=0,
                             padx=10,
                             pady=(1, 1),
                             sticky="nw")

        self.label_ssid = ctk.CTkLabel(self.sidebar_frame, text="SSID")
        self.label_ssid.grid(row=4,
                             column=0,
                             padx=10,
                             pady=(1, 1),
                             sticky="nw")

        self.entry_ssid = ctk.CTkEntry(self.sidebar_frame,
                                       placeholder_text="SSID")
        self.entry_ssid.grid(row=5,
                             column=0,
                             padx=10,
                             pady=(1, 1),
                             sticky="nw")
        self.label_pass = ctk.CTkLabel(self.sidebar_frame, text="비밀번호")
        self.label_pass.grid(row=6,
                             column=0,
                             padx=10,
                             pady=(1, 1),
                             sticky="nw")
        self.entry_pass = ctk.CTkEntry(self.sidebar_frame,
                                       placeholder_text="Password")
        self.entry_pass.grid(row=7,
                             column=0,
                             padx=10,
                             pady=(2, 10),
                             sticky="nw")

        self.label_serial = ctk.CTkLabel(self.sidebar_frame, text="시리얼 통신")
        self.label_serial.grid(row=8,
                               column=0,
                               padx=10,
                               pady=(10, 1),
                               sticky="nw")

        self.label_com = ctk.CTkLabel(self.sidebar_frame, text="포트")
        self.label_com.grid(row=9, column=0, padx=10, pady=1, sticky="nw")

        self.entry_serial_port = ctk.CTkEntry(self.sidebar_frame,
                                              placeholder_text="COM2")
        self.entry_serial_port.grid(row=10,
                                    column=0,
                                    padx=10,
                                    pady=1,
                                    sticky="nw")

        self.label_baud = ctk.CTkLabel(self.sidebar_frame, text="속도")
        self.label_baud.grid(row=11, column=0, padx=10, pady=1, sticky="nw")

        self.entry_baud = ctk.CTkEntry(self.sidebar_frame,
                                       placeholder_text="115200")
        self.entry_baud.grid(row=12, column=0, padx=10, pady=1, sticky="nw")

        self.label_cipher = ctk.CTkLabel(self.sidebar_frame,
                                         text="암호화 방식:",
                                         anchor="w")
        self.label_cipher.grid(row=13, column=0, padx=20, pady=(20, 0))

        self.cipher_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["XOR", "AES"],
            command=self.change_cipher_event)
        self.cipher_optionemenu.grid(row=14, column=0, padx=20, pady=(0, 10))

        #=================================================================================
        #
        self.inputfile_frame = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,  #)#,
            fg_color='transparent')
        self.inputfile_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.inputfile_frame.grid_rowconfigure(2, weight=1)

        # create textbox
        self.file_button = ctk.CTkButton(master=self.inputfile_frame,
                                         command=self.load_file_event)
        self.file_button.configure(text="입력 파일 선택")
        self.file_button.grid(row=0,
                              column=0,
                              padx=10,
                              pady=(40, 5),
                              sticky="nswe")

        self.label_filename = ctk.CTkLabel(self.inputfile_frame, text="")  #,
        #fg_color='blue')
        self.label_filename.grid(row=1,
                                 column=0,
                                 padx=10,
                                 pady=(10, 5),
                                 sticky="nw")

        self.textbox = ctk.CTkTextbox(self.inputfile_frame, width=450)
        self.textbox.grid(row=2,
                          column=0,
                          padx=(20, 20),
                          pady=(20, 10),
                          sticky="nsew")

        #=================================================================================
        # create slider and progressbar frame
        self.slider_progressbar_frame = ctk.CTkFrame(self)  #,
        #fg_color='transparent')  #, fg_color='yellow')  #"transparent")
        self.slider_progressbar_frame.grid(
            row=0,
            column=2,
            #columnspan=2,
            rowspan=3,
            padx=(5, 0),
            pady=(20, 10),
            sticky="nsew")
        #self.slider_progressbar_frame.grid_rowconfigure(2, weight=1)
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(4, weight=1)

        self.send_button = ctk.CTkButton(master=self.slider_progressbar_frame,
                                         command=self.send_file_event)
        self.send_button.configure(text="파일 송신")
        self.send_button.grid(row=0,
                              column=0,
                              padx=10,
                              pady=(20, 5),
                              sticky="nswe")

        self.progressbar_1 = ctk.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.grid(row=1,
                                column=0,
                                padx=(20, 10),
                                pady=(10, 10),
                                sticky="ew")
        self.progressbar_2 = ctk.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_2.grid(row=2,
                                column=0,
                                padx=(20, 10),
                                pady=(10, 10),
                                sticky="ew")
        self.slider_1 = ctk.CTkSlider(self.slider_progressbar_frame,
                                      from_=0,
                                      to=1,
                                      number_of_steps=4)

        # set default values
        #self.sidebar_button_3.configure(state="disabled",
        #                                text="Disabled CTkButton")

        self.cipher_optionemenu.set("XOR")
        self.slider_1.configure(command=self.progressbar_2.set)
        self.progressbar_1.configure(mode="indeterminnate")
        self.progressbar_1.start()
        #self.textbox.insert(
        #    "0.0", "CTkTextbox\n\n" +
        #    "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n"
        #    * 20)

    def load_file_event(self):
        self.filename = fdlg.askopenfilename()
        file_contents = None
        with open(self.filename, 'r') as f:
            file_contents = f.read()
        file_info = f'{self.filename} : {len(file_contents)} bytes'
        self.label_filename.configure(text=file_info)
        self.textbox.insert("0.0", file_contents)

    def send_file_event(self):
        pass

    def change_cipher_event(self, new_cipher: str):
        pass

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")


if __name__ == "__main__":
    app = App()
    app.mainloop()
