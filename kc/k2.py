import time
import threading
from threading import Thread
from threading import current_thread

import serial
import tkinter
import tkinter.filedialog as fdlg
import tkinter.messagebox
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import socket

from crypto_ex import *

PORT_ENC = 8501
PORT_DEC = 9501
SUBNET_MASK = '255.255.255.0'
COMM_PORT = '/dev/ttyUSB0'

ctk.set_appearance_mode(
    "Light")  #"System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme(
    "green")  # Themes: "blue" (standard), "green", "dark-blue"

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
        _app.comm_port = _app.entry_serial_port.get()
        device = serial.Serial(port=_app.comm_port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.5) #0.5sec
    except serial.serialutil.SerialException as e:
        print('시리얼 예외 발생: ', e)
    else:
        while not current_thread().stopped():
            data = device.read(1024)
            if data:
                _app.plaintext_textbox.insert("0.0", data.decode())
                print('수신: ', data)
                device.reset_input_buffer()
                device.write('READY_0\n'.encode())
                break
                #print(data)
            elif not data:
                print('수신: No Data')
            elif _app.data_to_send:
                _written = device.write(_app.data_to_send.encode())
                _app.data_to_send = None
                time.sleep(0.2)
                device.reset_input_buffer()

                print(f"written: {_written}")
                msg = f"{_written}바이트 전송 완료"
                _app.label_data2send.configure(text=msg)

        device.close()
        device = None

def init_enc_server(_app):
    try:
        host = _app.entry_server_ip.get()
        port = _app.entry_enc_port.get()
        _app.enc_server_socket = socket.socket()
        _app.enc_server_socket.bind((host, int(port)))
        _app.enc_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _app.enc_server_socket.listen(100)
    except Exception as e:
        _app.enc_server_socket = None
        print(e)
        tkinter.messagebox.showerror("Error", "암호화 서버 초기화에 실패하였습니다.")
        return None
    else:
        while True:
            #_app.label_enc_status.configure(text="암호화서버 접속 대기 중")
            #_app.label_enc_status.configure(fg_color="light green")
            print("\n\nWaiting for encrytion client connection...")
            conn, address = _app.enc_server_socket.accept()  # accept new connection
            print("Connected from: " + str(address))

            while True:
                # receive data stream. 
                # it won't accept data packet greater than 1024 bytes
                print("conn.recv(1024)...")
                data = conn.recv(1024)
                if not data:
                    #_app.label_enc_status.configure(text="암호화서버 중지됨")
                    #_app.label_enc_status.configure(fg_color="grey")
                    # break if data is not received or client closed connection
                    break
                print("Data received from client: ")
                print(data)
                if data.isalpha:
                    data = data.decode()
                _app.plaintext_textbox.insert("0.0", f"평문: {data}")
                _app.plaintext_textbox.insert("0.0", '\n')

                key = _app.entry_key.get()
                keyb = key.encode()
                keyb = keyb + KEY[len(keyb):]

                ciphertext, tag, nonce = enc_aes(keyb, data.encode())
                tnc = tag + nonce + ciphertext
                _app.plaintext_textbox.insert("0.0", "암호문: ")
                _app.plaintext_textbox.insert("1.6", tnc)
                _app.plaintext_textbox.insert("0.0", '\n\n')

                conn.send(tnc)  # send data to the client
                print("cipher text sent to client: ")


            conn.close()  # close the connection

def init_dec_server(_app):
    try:
        host = _app.entry_server_ip.get()
        port = _app.entry_dec_port.get()
        _app.dec_server_socket = socket.socket()
        _app.dec_server_socket.bind((host, int(port)))
        _app.dec_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _app.dec_server_socket.listen(100)
    except Exception as e:
        _app.dec_server_socket = None
        print(e)
        tkinter.messagebox.showerror("Error", "복호화 서버 초기화에 실패하였습니다.")
        return None
    else:
        while True:
            #_app.label_dec_status.configure(text="암호화서버 접속 대기 중")
            #_app.label_dec_status.configure(fg_color="light green")
            print("\n\nWaiting for decrypt client connection...")
            conn, address = _app.dec_server_socket.accept()  # accept new connection
            print("Connected from: " + str(address))

            while True:
                print("conn.recv(1024)...")
                tnc = conn.recv(1024)
                if not tnc:
                    #_app.label_dec_status.configure(text="복호화서버 중지됨")
                    #_app.label_dec_status.configure(fg_color="grey")
                    break
                print("Data received from decrypt client: ")
                print(tnc)
                _app.receive_textbox.insert("0.0", tnc)
                _app.receive_textbox.insert("0.0", '\n')

                key = _app.entry_key.get()
                keyb = key.encode()
                keyb = keyb + KEY[len(keyb):]

                tag, nonce, ciphertext = tnc[:16], tnc[16:32], tnc[32:]
                plaintext = dec_aes(keyb, ciphertext, tag, nonce)
                _app.receive_textbox.insert("0.0", plaintext)
                _app.receive_textbox.insert("0.0", '\n\n')

                conn.send(plaintext)  # send data to the client
                print("plaintext sent to client: ")


            conn.close()  # close the connection


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.comm_port = ''
        self.comm_thread=None
        self.cipher = "AES"
        self.enc_server_socket = None

        self.receive_plaintext_thread = None
        self.receive_ciphertext_thread = None
        self.data_to_send = None

        self.title("데이터암호화 모듈 테스트 프로그램")
        self.geometry(f"{1150}x{780}")

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=160, corner_radius=0)  #,
        self.sidebar_frame.grid(row=0, column=0, rowspan=50, sticky="nsew")

        self.send_frame = ctk.CTkFrame( self, width=220, corner_radius=0, fg_color='transparent')
        self.send_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")

        self.receive_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color='transparent')
        self.receive_frame.grid(row=0, column=2, rowspan=3, sticky="nsew")

        #self.sidebar_frame.grid_rowconfigure(2, weight=1)
        self.send_frame.grid_rowconfigure(2, weight=1)
        self.receive_frame.grid_rowconfigure(2, weight=1)


        self.option_button = ctk.CTkButton(self.sidebar_frame, fg_color='#CC6600', hover_color='#AA4400',
                                         command=self.read_option_event)
        self.option_button.configure(text="설정 읽어오기")
        self.option_button.grid(row=0, column=0, padx=10, pady=(40, 1), sticky="nw")

        self.label_serial = ctk.CTkLabel(self.sidebar_frame, text="시리얼 통신 포트")
        self.label_serial.grid(row=1, column=0, padx=10, pady=(20, 1), sticky="nw")

        self.entry_serial_port = ctk.CTkEntry(self.sidebar_frame)#, placeholder_text="COM2")
        self.entry_serial_port.grid(row=2, column=0, padx=10, pady=1, sticky="nw")
        self.entry_serial_port.insert(0, COMM_PORT)

        self.label_network = ctk.CTkLabel(self.sidebar_frame, text="단말 네트워크 설정")
        self.label_network.grid(row=9, column=0, padx=10, pady=(30,1), sticky="nw")

        self.label_ip = ctk.CTkLabel(self.sidebar_frame, text="IP")
        self.label_ip.grid(row=10, column=0, padx=15, pady=(1,0), sticky="nw")
        self.switch_var = ctk.StringVar(value="NO-DHCP")
        self.dhcp = ctk.CTkSwitch(self.sidebar_frame, text="DHCP", command=self.switch_event,
                                   variable=self.switch_var, onvalue="DHCP", offvalue="NO-DHCP")
        self.dhcp.grid(row=10, column=0, padx=80, pady=(1,0), sticky="nw")

        self.entry_server_ip = ctk.CTkEntry(self.sidebar_frame)
        self.entry_server_ip.grid(row=11, column=0, padx=10, pady=0, sticky="nw")

        self.label_subnet = ctk.CTkLabel(self.sidebar_frame, text="subnet mask")
        self.label_subnet.grid(row=12, column=0, padx=15, pady=(1,0), sticky="nw")
        self.entry_subnet = ctk.CTkEntry(self.sidebar_frame, placeholder_text=f"{SUBNET_MASK}")
        self.entry_subnet.grid(row=13, column=0, padx=10, pady=0, sticky="nw")

        self.label_port = ctk.CTkLabel(self.sidebar_frame, text="복호화포트")
        self.label_port.grid(row=15, column=0, padx=10, pady=(20,1), sticky="nw")
        self.entry_port = ctk.CTkEntry(self.sidebar_frame, placeholder_text=f"{PORT_DEC}")
        self.entry_port.grid(row=16, column=0, padx=10, pady=1, sticky="nw")

        #self.label_dec_status = ctk.CTkLabel(self.sidebar_frame, fg_color='grey', text="복호화 서버 중지됨")
        #self.label_dec_status.grid(row=17, column=0, padx=10, pady=(10,1), sticky="nw")

        self.label_key = ctk.CTkLabel(self.sidebar_frame, text="암호화 키(8-16자리)")
        self.label_key.grid(row=30, column=0, padx=10, pady=(30,1), sticky="nw")
        self.entry_key = ctk.CTkEntry(self.sidebar_frame, fg_color="#00c177", text_color='white', placeholder_text="12345678")
        self.entry_key.grid(row=31, column=0, padx=10, pady=1, sticky="nw")

        self.label_cipher = ctk.CTkLabel(self.sidebar_frame, text="암호화 방식:")  #,
        self.label_cipher.grid(row=32, column=0, padx=10, pady=1, sticky="nw")

        self.cipher_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["AES"],
            command=self.change_cipher_event)
        self.cipher_optionemenu.grid(row=33, column=0, padx=10, pady=(0, 10), sticky="nw")

        self.option_button = ctk.CTkButton(self.sidebar_frame, fg_color='#CC6600', hover_color='#AA4400',
                                         command=self.apply_option_event)
        self.option_button.configure(text="설정 저장")
        self.option_button.grid(row=34, column=0, padx=10, pady=(30, 1), sticky="nw")

        #=================================================================================
        # create textbox
        #self.file_button = ctk.CTkButton(master=self.inputfile_frame,
        #                                 command=self.load_file_event)
        self.send_button = ctk.CTkButton(self.send_frame, command=self.send_button_event)
        self.send_button.configure(text="암호화 요청 데이터와 응답 암호문")
        self.send_button.grid(row=0, column=0, padx=30, pady=(15, 5), sticky="nswe")

        self.clear_button = ctk.CTkButton(self.send_frame, command=self.clear_button_event)

        self.clear_button.configure(text="내용 지우기")
        self.clear_button.grid(row=0, column=1, padx=30, pady=(15, 5), sticky="nswe")
        self.label_data2send = ctk.CTkLabel(self.send_frame, text="")  #,
        #fg_color='blue')
        self.label_data2send.grid(row=1, column=0, padx=20, pady=(1, 5), sticky="nw")

        self.plaintext_textbox = ctk.CTkTextbox(self.send_frame, width=450)
        self.plaintext_textbox.grid(row=2, column=0, columnspan=2, padx=(20, 20), pady=(1, 55), sticky="nsew")

        #=================================================================================
        # create textbox
        self.receive_button = ctk.CTkButton(self.receive_frame,
                                            command=self.receive_button_dummy_event)
        #self.receive_button = ctk.CTkLabel(self.receive_frame, text="수신 데이터")

        self.receive_button.configure(text="복호화 요청 데이터와 응답 평문", bg_color='#889933', fg_color='#889933')
        self.receive_button.grid(row=0, column=0, padx=30, pady=(15, 5), sticky="nswe")

        self.label_filename = ctk.CTkLabel(self.receive_frame, text="")  #,
        #fg_color='blue')
        self.label_filename.grid(row=1, column=0, padx=10, pady=(1, 5), sticky="nw")

        self.receive_textbox = ctk.CTkTextbox(self.receive_frame, width=420)#, border_color='blue', bg_color='blue')
        self.receive_textbox.grid(row=2, column=0, padx=(20, 20), pady=(1, 55), sticky="nsew")
        #self.receive_textbox.configure(bg_color='blue', fg_color='blue', border_color='blue')

    def load_file_event(self):
        self.filename = fdlg.askopenfilename()
        file_contents = None
        with open(self.filename, 'r') as f:
            file_contents = f.read()
        file_info = f'{self.filename} : {len(file_contents)} bytes'
        self.label_filename.configure(text=file_info)
        self.plaintext_textbox.insert("0.0", file_contents)

    def send_button_event(self):
        return

    def switch_event(self):
        print("switch toggled, current value:", self.switch_var.get())

    def apply_option_event(self):
        self.init_server_thread()

    def read_option_event(self):
        self.read_options_thread()

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

    def init_server_thread(self):
        if self.receive_plaintext_thread:
            self.receive_plaintext_thread.stop()
            self.receive_plaintext_thread.join()
            self.receive_plaintext_thread = None

        self.receive_plaintext_thread = StoppableThread(target=init_enc_server,args=(self,))
        self.receive_plaintext_thread.start()

        if self.receive_ciphertext_thread:
            self.receive_ciphertext_thread.stop()
            self.receive_ciphertext_thread.join()
            self.receive_ciphertext_thread = None

        self.receive_ciphertext_thread = StoppableThread(target=init_dec_server,args=(self,))
        self.receive_ciphertext_thread.start()

    def read_options_thread(self):
        if self.read_options_thread:
            self.read_options_thread.stop()
            self.read_options_thread.join()
            self.read_options_thread = None

        self.read_options_thread = StoppableThread(target=receive_serial,args=(self,))
        self.read_options_thread.start()

    def receive_button_dummy_event(self):
        pass

    def clear_button_event(self):
        self.plaintext_textbox.delete("1.0", "end-1c")
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
    #app.config(cursor='watch')

    #CTkMessagebox(title="Info", message="This is a CTkMessagebox!")
    tkinter.messagebox.showinfo("Info", "This is a tkinter.messagebox!")

    with open("k2_config.txt", "r") as f:
        lines = f.readlines()
        comm_port = lines[0].split("comm:")[1].strip()
        dhcp = lines[1].split("dhcp:")[1].strip()
        ip = lines[2].split("ip:")[1].strip()
        subnet = lines[3].split("subnet:")[1].strip()
        port = lines[4].split("port:")[1].strip()
        key = lines[5].split("key:")[1].strip()

    app.entry_serial_port.insert(0, comm_port)
    #app.switch_var = ctk.StringVar(value="NO-DHCP")
    if dhcp == "true":
        app.switch_var.set("DHCP")
    else:
        app.switch_var.set("NO-DHCP")
    app.entry_server_ip.insert(0, ip)
    app.entry_subnet.insert(0, subnet)
    app.entry_port.insert(0, port)
    app.entry_key.insert(0, key)

    #app.init_server_thread()
    #app.init_comm_thread()

    app.mainloop()