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

def receive_serial(_app):
    try:
        _app.comm['port'] = _app.entry_serial_port.get()
        device = serial.Serial(port=_app.comm['port'], 
                               baudrate=_app.comm['baudrate'], 
                               bytesize=_app.comm['bytesize'],
                               parity=_app.comm['parity'],
                               stopbits=_app.comm['stopbits'],
                               timeout=0.005) #5ms
    except serial.serialutil.SerialException as e:
        print('시리얼 예외 발생: ', e)
    else:
        while not current_thread().stopped():
            data = device.read()
            if data:
                _app.receive_textbox.insert("0.0", data.decode())
                print(data)
            elif _app.data_to_send:
                _written = device.write(_app.data_to_send.encode())
                _app.data_to_send = None
                print(f"written: {_written}")
                msg = f"{_written}바이트 전송 완료"
                _app.label_data2send.configure(text=msg)

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

        self.cipher = "XOR"

        self.receive_thread = None
        self.data_to_send = None

        # configure window
        self.title("데이터암호화 모듈 클라이언트")
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
            row=19,
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
        self.cipher_optionemenu.grid(row=20,
                                     column=0,
                                     padx=10,
                                     pady=(0, 10),
                                     sticky="nw")

        self.apply_options_button = ctk.CTkButton(self.sidebar_frame,
                                        fg_color='#CC6600', hover_color='#AA4400',
                                         command=self.apply_options_event)
        self.apply_options_button.configure(text="옵션 적용")
        self.apply_options_button.grid(row=22,
                              column=0,
                              padx=10,
                              pady=(30, 1),
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
                                            command=self.receive_button_dummy_event)
        #self.receive_button = ctk.CTkLabel(self.receive_frame, text="수신 데이터")

        self.receive_button.configure(text="수신 데이터",
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

        self.receive_textbox = ctk.CTkTextbox(self.receive_frame, width=420)#, border_color='blue', bg_color='blue')
        self.receive_textbox.grid(row=2,
                          column=0,
                          padx=(20, 20),
                          pady=(1, 55),
                          sticky="nsew")
        #self.receive_textbox.configure(bg_color='blue', fg_color='blue', border_color='blue')

    def load_file_event(self):
        self.filename = fdlg.askopenfilename()
        file_contents = None
        with open(self.filename, 'r') as f:
            file_contents = f.read()
        file_info = f'{self.filename} : {len(file_contents)} bytes'
        self.label_filename.configure(text=file_info)
        self.textbox.insert("0.0", file_contents)

    def send_button_event(self):
        if not self.receive_thread:
            self.init_comm_thread()

        self.data_to_send = self.textbox.get("1.0", "end-1c")

    def apply_options_event(self):
        self.init_comm_thread()

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

    def init_comm_thread(self):
        if self.receive_thread:
            self.receive_thread.stop()
            self.receive_thread.join()
            self.receive_thread = None

        self.receive_thread = StoppableThread(target=receive_serial,args=(self,))
        self.receive_thread.start()

    def receive_button_dummy_event(self):
        pass

    def clear_button_event(self):
        self.textbox.delete("1.0", "end-1c")
        self.label_data2send.configure(text="")

    def change_speed_event(self, new_speed: str):
        self.comm['baudrate'] = new_speed

    def change_parity_event(self, new_parity: str):
        self.comm['parity'] = new_parity

    def change_databits_event(self, new_databits: str):
        self.comm['bytesize'] = new_databits

    def change_stopbits_event(self, new_stopbits: str):
        self.comm['stopbits'] = new_stopbits

    def change_cipher_event(self, new_cipher: str):
        self.cipher = new_cipher

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

if __name__ == "__main__":

    app = App()
    app.entry_serial_port.insert(0, "COM3")
    app.init_comm_thread()

    app.mainloop()
