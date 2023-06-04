import time
import threading
from threading import Thread
from threading import current_thread

import tkinter
import tkinter.filedialog as fdlg
import tkinter.messagebox
import customtkinter as ctk
import socket

PORT_ENC = 8501
PORT_DEC = 9501

ctk.set_appearance_mode(
    "Light")  #"System")  # Modes: "System" (standard), "Dark", "Light"
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

def init_enc_connection(_app):
    try:
        enc_ip = _app.entry_enc_ip.get()
        enc_port = _app.entry_enc_port.get()
        enc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        enc_socket.connect((enc_ip, int(enc_port)))  # connect to the server
    except socket.error:
        enc_socket.close()
        enc_socket = None
        tkinter.messagebox.showerror("오류", f"암호화단말({enc_ip}:{enc_port})에 연결할 수 없습니다.")
        return None
    else:
        _app.enc_socket = enc_socket
        _app.label_enc_status.configure(text="연결됨")
        _app.label_enc_status.configure(fg_color="green")
        return enc_socket

def init_dec_connection(_app):
    try:
        dec_ip = _app.entry_dec_ip.get()
        dec_port = _app.entry_dec_port.get()
        dec_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dec_socket.connect((dec_ip, int(dec_port)))  # connect to the server
    except socket.error:
        dec_socket.close()
        dec_socket = None
        tkinter.messagebox.showerror("오류", f"복호화단말({dec_ip}:{dec_port})에 연결할 수 없습니다.")
        return
    else:
        _app.dec_socket = dec_socket
        _app.label_dec_status.configure(text="연결됨")
        _app.label_dec_status.configure(fg_color="green")

def send_plaintext(_app):
    if not _app.enc_socket:
        if not init_enc_connection(_app):
            return
    else:
        plaintext = _app.send_textbox.get("1.0", "end-1c")
        if not plaintext:
            tkinter.messagebox.showerror("오류", "암호화할 평문을 입력하세요.")
            return

        else:
            _app.enc_socket.send(plaintext.encode())
            tnc = _app.enc_socket.recv(1024)
            _app.ciphertext = tnc
            _app.ciphertext_textbox.delete("1.0", "end-1c")
            _app.ciphertext_textbox.insert(tkinter.END, tnc)

def decrypt_ciphertext(_app):
    if not _app.dec_socket:
        if not init_dec_connection(_app):
            return
    else:
        ciphertext = _app.ciphertext_textbox.get("1.0", "end-1c")
        if not ciphertext:
            return
        else:
            _app.dec_socket.send(_app.ciphertext)
            tnc = _app.dec_socket.recv(1024)
            _app.decrypt_textbox.delete("1.0", "end-1c")
            _app.decrypt_textbox.insert(tkinter.END, tnc)

class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.enc_socket = None
        self.dec_socket = None

        self.send_thread = None
        self.data_to_send = None

        self.ciphertext = None

        # configure window
        self.title("(주)위너스시스템 데이터암호화 모듈 테스트 클라이언트")
        self.geometry(f"{1100}x{580}")

        self.grid_columnconfigure((2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=160, corner_radius=0)  #,
        #fg_color='green')
        self.sidebar_frame.grid(row=0, column=0, rowspan=8, sticky="nsew")
        #self.sidebar_frame.grid_rowconfigure((5), weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="암호화 단말 정보",
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(10, 10))

        self.label_enc = ctk.CTkLabel(self.sidebar_frame, text="암호화단말 주소")
        self.label_enc.grid(row=9, column=0, padx=10, pady=1, sticky="nw")
        self.entry_enc_ip = ctk.CTkEntry(self.sidebar_frame, placeholder_text="127.0.0.1")
        self.entry_enc_ip.grid(row=10, column=0, padx=10, pady=1, sticky="nw")

        self.label_enc = ctk.CTkLabel(self.sidebar_frame, text="암호화단말 포트")
        self.label_enc.grid(row=11, column=0, padx=10, pady=(10,1), sticky="nw")
        self.entry_enc_port = ctk.CTkEntry(self.sidebar_frame, placeholder_text=f"{PORT_ENC}")
        self.entry_enc_port.grid(row=12, column=0, padx=10, pady=1, sticky="nw")

        self.label_enc_status = ctk.CTkLabel(self.sidebar_frame, fg_color='grey', text="암호화단말 미연결")
        self.label_enc_status.grid(row=13, column=0, padx=10, pady=(10,1), sticky="nw")

        self.label_dec_ip = ctk.CTkLabel(self.sidebar_frame, text="복호화단말 주소")
        self.label_dec_ip.grid(row=14, column=0, padx=10, pady=(30,1), sticky="nw")
        self.entry_dec_ip = ctk.CTkEntry(self.sidebar_frame, placeholder_text="127.0.0.1")
        self.entry_dec_ip.grid(row=15, column=0, padx=10, pady=1, sticky="nw")

        self.label_dec_port = ctk.CTkLabel(self.sidebar_frame, text="복호화단말 포트")
        self.label_dec_port.grid(row=16, column=0, padx=10, pady=(10,1), sticky="nw")
        self.entry_dec_port = ctk.CTkEntry(self.sidebar_frame, placeholder_text=f"{PORT_DEC}")
        self.entry_dec_port.grid(row=17, column=0, padx=10, pady=1, sticky="nw")

        self.label_dec_status = ctk.CTkLabel(self.sidebar_frame, fg_color='grey', text="복호화단말 미연결")
        self.label_dec_status.grid(row=18, column=0, padx=10, pady=(10,1), sticky="nw")

        #=================================================================================
        #
        self.send_frame = ctk.CTkFrame( self, width=220, corner_radius=0, fg_color='transparent')
        self.send_frame.grid(row=0, column=1, rowspan=1, sticky="nsew")
        self.send_frame.grid_rowconfigure(2, weight=1)

        #self.file_button = ctk.CTkButton(master=self.inputfile_frame,
        #                                 command=self.load_file_event)
        self.send_button = ctk.CTkButton(self.send_frame, command=self.send_button_event)
        self.send_button.configure(text="암호화 요청")
        self.send_button.grid(row=1, column=0, padx=30, pady=(15, 5), sticky="nswe")

        self.clear_button = ctk.CTkButton(self.send_frame, command=self.clear_button_event)
        self.clear_button.configure(text="전송 내용 지우기")
        self.clear_button.grid(row=1, column=1, padx=30, pady=(15, 5), sticky="nswe")

        #self.label_data2send = ctk.CTkLabel(self.send_frame, text="")  #,
        #fg_color='blue')
        #self.label_data2send.grid(row=1, column=0, padx=20, pady=(1, 5), sticky="nw")

        self.send_textbox = ctk.CTkTextbox(self.send_frame, width=450)
        self.send_textbox.grid(row=2, column=0, columnspan=2, padx=(20, 20), pady=(30, 0), sticky="nsew")

        self.label_ciphertext = ctk.CTkLabel(self.send_frame, text="수신 암호문")
        self.label_ciphertext.grid(row=3, column=0, padx=20, pady=(20, 10), sticky="nswe")

        self.ciphertext_textbox = ctk.CTkTextbox(self.send_frame, width=450)
        self.ciphertext_textbox.grid(row=4, column=0, columnspan=2, padx=30, pady=(0, 5), sticky="nsew")

        #=================================================================================
        self.receive_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color='transparent')
        self.receive_frame.grid(row=0, column=2, rowspan=3, sticky="nsew")
        self.receive_frame.grid_rowconfigure(2, weight=1)

        # create textbox
        self.decrypt_button = ctk.CTkButton(self.receive_frame,
                                            command=self.decrypt_event)
        self.decrypt_button.configure(text="복호화 요청", bg_color='#889933', fg_color='green')
        self.decrypt_button.grid(row=0, column=0, padx=30, pady=(15, 5), sticky="nswe")

        self.label_filename = ctk.CTkLabel(self.receive_frame, text="")  #,
        #fg_color='blue')
        self.label_filename.grid(row=1, column=0, padx=10, pady=(1, 5), sticky="nw")

        self.decrypt_textbox = ctk.CTkTextbox(self.receive_frame, width=420)#, border_color='blue', bg_color='blue')
        self.decrypt_textbox.grid(row=2, column=0, padx=(20, 20), pady=(1, 55), sticky="nsew")
        #self.receive_textbox.configure(bg_color='blue', fg_color='blue', border_color='blue')

    def load_file_event(self):
        self.filename = fdlg.askopenfilename()
        file_contents = None
        with open(self.filename, 'r') as f:
            file_contents = f.read()
        file_info = f'{self.filename} : {len(file_contents)} bytes'
        self.label_filename.configure(text=file_info)
        self.send_textbox.insert("0.0", file_contents)

    def send_button_event(self):
        send_plaintext(self)
        #if not self.send_thread:
        #    self.init_client_thread()

        #self.data_to_send = self.send_textbox.get("1.0", "end-1c")

    def decrypt_event(self):
        decrypt_ciphertext(self)

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

    def init_client_thread(self):
        if self.send_thread:
            self.send_thread.stop()
            self.send_thread.join()
            self.send_thread = None

        self.send_thread = StoppableThread(target=send_data,args=(self,))
        self.send_thread.start()

    def clear_button_event(self):
        self.send_textbox.delete("1.0", "end-1c")
        #self.label_data2send.configure(text="")

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

if __name__ == "__main__":

    app = App()
    app.entry_enc_ip.insert(0, "127.0.0.1")
    app.entry_enc_port.insert(0, PORT_ENC)
    app.entry_dec_ip.insert(0, "127.0.0.1")
    app.entry_dec_port.insert(0, PORT_DEC)
    #app.entry_key.insert(0, "12345678")
    #app.entry_serial_port.insert(0, "COM3")
    #app.init_comm_thread()

    app.mainloop()
