import time
import threading
from threading import Thread
from threading import current_thread

import tkinter
import tkinter.filedialog as fdlg
import tkinter.messagebox
import customtkinter as ctk
import serial

ctk.set_appearance_mode(
    "light")  #"System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme(
    "blue")  # Themes: "blue" (standard), "green", "dark-blue"

APP = None

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def receive_serial(app):
    device = serial.Serial(app.comm['port'], 9600, timeout=1)
    while not current_thread().stopped():
        data = device.read()
        if data:
            app.receive_textbox.insert("0.0", data.decode())
            print(data)

    device.close()
    device = None

class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.comm = {
            "device": None,
            "port": "COM2",
            "baudrate": 9600,
            "parity": "N",
            "bytesize": 8,
            "stopbits": 1
        }

        self.serial_port = "COM2"
        self.serial_speed = 9600
        self.serial_parity = "N"
        self.serial_databits = 8
        self.serial_stopbits = 1
        self.cipher = "XOR"

        self.receive_thread = None

        # configure window
        self.title("(주)위너스시스템 데이터암호화 모듈 클라이언트")
        self.geometry(f"{1100}x{580}")

        self.grid_columnconfigure((2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=160, corner_radius=0)  #,
        #fg_color='green')
        self.sidebar_frame.grid(row=0, column=0, rowspan=8, sticky="nsew")
        #self.sidebar_frame.grid_rowconfigure((5), weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame,
                                       text="암호화 단말 정보",
                                       font=ctk.CTkFont(size=14,
                                                        weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(10, 10))

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
        self.baud_optionmenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["9600", "19200", "38400", "57600", "115200"],
            #values=[9600, 19200, 38400, 57600, 115200],
            command=self.change_speed_event)
        self.baud_optionmenu.grid(row=12,
                                  column=0,
                                  padx=10,
                                  pady=1,
                                  sticky="nw")  #,
        #        self.entry_baud = ctk.CTkEntry(self.sidebar_frame,
        #                                       placeholder_text="9600")
        #        self.entry_baud.grid(row=12, column=0, padx=10, pady=1, sticky="nw")
        self.label_parity = ctk.CTkLabel(self.sidebar_frame, text="패리티")
        self.label_parity.grid(row=13, column=0, padx=10, pady=1, sticky="nw")
        self.parity_optionmenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["N", "1", "2"],
            command=self.change_parity_event)
        self.parity_optionmenu.grid(row=14,
                                    column=0,
                                    padx=10,
                                    pady=1,
                                    sticky="nw")  #,

        self.label_databits = ctk.CTkLabel(self.sidebar_frame, text="데이타 비트")
        self.label_databits.grid(row=15,
                                 column=0,
                                 padx=10,
                                 pady=1,
                                 sticky="nw")
        self.databits_optionmenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["8", "9"],
            command=self.change_databits_event)
        self.databits_optionmenu.grid(row=16,
                                      column=0,
                                      padx=10,
                                      pady=1,
                                      sticky="nw")  #,

        self.label_stopbits = ctk.CTkLabel(self.sidebar_frame, text="스톱 비트")
        self.label_stopbits.grid(row=17,
                                 column=0,
                                 padx=10,
                                 pady=1,
                                 sticky="nw")
        self.stopbits_optionmenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["1", "2"],
            command=self.change_stopbits_event)
        self.stopbits_optionmenu.grid(row=18,
                                      column=0,
                                      padx=10,
                                      pady=1,
                                      sticky="nw")  #,

        self.label_cipher = ctk.CTkLabel(self.sidebar_frame,
                                         text="암호화 방식:")  #,
        #anchor="w")
        self.label_cipher.grid(
            row=20,
            column=0,
            padx=10,
            #pady=(2, 0),
            pady=(30, 1),
            #pady=(20, 0),
            sticky="nw")

        self.cipher_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["XOR", "AES"],
            command=self.change_cipher_event)
        self.cipher_optionemenu.grid(row=21,
                                     column=0,
                                     padx=10,
                                     pady=(0, 10),
                                     sticky="nw")

        #=================================================================================
        #
        self.send_frame = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,  #)#,
            fg_color='transparent')
        self.send_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.send_frame.grid_rowconfigure(2, weight=1)

        # create textbox
        #self.file_button = ctk.CTkButton(master=self.inputfile_frame,
        #                                 command=self.load_file_event)
        self.send_button = ctk.CTkButton(self.send_frame,
                                         command=self.send_button_event)

        self.send_button.configure(text="데이터 전송")
        self.send_button.grid(row=0,
                              column=0,
                              padx=30,
                              pady=(15, 5),
                              sticky="nswe")

        self.clear_button = ctk.CTkButton(self.send_frame,
                                          command=self.clear_button_event)

        self.clear_button.configure(text="전송 내용 지우기")
        self.clear_button.grid(row=0,
                               column=1,
                               padx=30,
                               pady=(15, 5),
                               sticky="nswe")
        self.label_data2send = ctk.CTkLabel(self.send_frame, text="")  #,
        #fg_color='blue')
        self.label_data2send.grid(row=1,
                                  column=0,
                                  padx=20,
                                  pady=(1, 5),
                                  sticky="nw")

        self.textbox = ctk.CTkTextbox(self.send_frame, width=450)
        self.textbox.grid(row=2,
                          column=0,
                          columnspan=2,
                          padx=(20, 20),
                          pady=(1, 55),
                          sticky="nsew")

        #=================================================================================
        #
        self.receive_frame = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,  #)#,
            fg_color='transparent')
        self.receive_frame.grid(row=0, column=2, rowspan=3, sticky="nsew")
        self.receive_frame.grid_rowconfigure(2, weight=1)

        # create textbox
        self.receive_button = ctk.CTkButton(self.receive_frame,
                                            command=self.receive_button_event)
        #self.receive_button = ctk.CTkLabel(self.receive_frame, text="수신 데이터")

        self.receive_button.configure(text="데이터 수신",
                                      bg_color='#889933',
                                      fg_color='#889933')
        self.receive_button.grid(row=0,
                                 column=0,
                                 padx=30,
                                 pady=(15, 5),
                                 sticky="nswe")

        self.label_filename = ctk.CTkLabel(self.receive_frame, text="")  #,
        #fg_color='blue')
        self.label_filename.grid(row=1,
                                 column=0,
                                 padx=10,
                                 pady=(1, 5),
                                 sticky="nw")

        self.receive_textbox = ctk.CTkTextbox(self.receive_frame, width=420)
        self.receive_textbox.grid(row=2,
                          column=0,
                          padx=(20, 20),
                          pady=(1, 55),
                          sticky="nsew")

    def load_file_event(self):
        self.filename = fdlg.askopenfilename()
        file_contents = None
        with open(self.filename, 'r') as f:
            file_contents = f.read()
        file_info = f'{self.filename} : {len(file_contents)} bytes'
        self.label_filename.configure(text=file_info)
        self.textbox.insert("0.0", file_contents)

    def send_button_event(self):
        if self.comm['device']:
            self.comm['device'].close()

        self.comm['device'] = serial.Serial(self.entry_serial_port.get(), 9600)
        device = self.comm['device']
        data = self.textbox.get("1.0", "end-1c")
        
        start = 0
        step = 16
        while(start < len(data)):
            if len(data)<step:
                device.write(data.encode())
                #device.write(data)
                break
            else:
                device.write(data[start:start+step].encode())
                start += step
            time.sleep(0.2)
    
        msg = f"{len(data)}바이트 전송 완료"
        #self.pop_up_msg(msg)
        self.label_data2send.configure(text=msg)



    def pop_up_msg(self, msg:str):
        win = ctk.CTkToplevel()
        win.wm_title("전송 결과")
        win.maxsize(300,180)
        win.minsize(300,180)
        frame = ctk.CTkFrame(master=win)
        frame.pack(pady=20, padx=20,fill="both", expand=True)

        label = ctk.CTkLabel(master=frame, text=msg)
        label.pack(pady=10, padx=10)

        btn = ctk.CTkButton(master=frame, text="OK", command=win.destroy)
        btn.pack(ipady=5,ipadx=5,pady=10,padx=10)

    def receive_button_event(self):
        if self.receive_thread:
            self.receive_thread.stop()
            self.receive_thread.join()
            self.receive_thread = None

        self.receive_thread = StoppableThread(target=receive_serial,args=(self,))
        self.receive_thread.start()

    def clear_button_event(self):
        self.textbox.delete("1.0", "end-1c")
        self.label_data2send.configure(text="")

    def change_speed_event(self, new_speed: str):
        pass

    def change_parity_event(self, new_parity: str):
        pass

    def change_databits_event(self, new_databits: str):
        pass

    def change_stopbits_event(self, new_stopbits: str):
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
    APP = app


    app.mainloop()
'''
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
'''