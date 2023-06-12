import sys
import time
import threading
from threading import Thread
from threading import current_thread
import logging

import json
import serial
import tkinter
import tkinter.filedialog as fdlg
import tkinter.messagebox
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import socket

from crypto_ex import *

# config a logger using default logger
logging.basicConfig(filename='app.log', filemode='w', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


PORT_ENC = 8501
PORT_DEC = 9501
SUBNET_MASK = '255.255.255.0'
COMM_PORT = '/dev/ttyUSB0'
GATEWAY = '192.168.0.1'

ctk.set_appearance_mode(
    "Light")  #"System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme(
    "green")  # Themes: "blue" (standard), "green", "dark-blue"

OPTIONS = {
    'comm_port': COMM_PORT,
    'dhcp': 0,
    'ip': '',
    'gateway': '',
    'subnet': SUBNET_MASK,
    'port': '',
    'key': '1234567890'
}

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

def read_device_options(_app):

    try:
        _app.comm_port = _app.entry_serial_port.get()
        device = serial.Serial(port=_app.comm_port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.6, write_timeout=0.3) #0.5sec
    except serial.serialutil.SerialException as e:
        #_app.config(cursor='watch')
        CTkMessagebox(title="Info", message=f"시리얼 연결 오류: COM 포트({_app.comm_port})를 확인하세요.")
        #CTkMessagebox(title="Info", message="단말에서 설정값을 읽어오고 있습니다. 잠시만 기다려주세요.")
        #tkinter.messagebox.showinfo("Info", "This is a tkinter.messagebox!")
        logging.debug('시리얼 예외 발생: ', e)
    else:
        #while not current_thread().stopped() or not app.stop_thread:
        device.write('CNF_REQ\n'.encode())
        msg = device.readline()

        if msg:
            logging.debug(f'수신: {msg}')
            msg = msg.decode('utf-8')
            msg = msg.strip()
            logging.debug(f'수신 decoded: {msg}')
            if msg.startswith('CNF_JSN') and msg.endswith('CNF_END'):
                msg = msg[7:-7]
                _app.plaintext_textbox.insert("0.0", msg)
                options = json.loads(msg)
                apply_options(options, _app)
                logging.debug(f'수신: {msg}')
                device.reset_input_buffer()
        else:
            logging.debug('수신: No Data')
            CTkMessagebox(title="Info", message=f"단말에서 정보를 읽어올 수 없습니다.")

    finally:
        device.close()
        device = None

def write_device_options(_app):

    try:
        _app.comm_port = _app.entry_serial_port.get()
        device = serial.Serial(port=_app.comm_port, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.6, write_timeout=0.3) #0.5sec
    except serial.serialutil.SerialException as e:
        CTkMessagebox(title="Info", message=f"시리얼 연결 오류: COM 포트({_app.comm_port})를 확인하세요.")
        logging.debug('시리얼 예외 발생: ', e)
    else:
        options = read_ui_options(_app)
        str_options = json.dumps(options)

        msg = bytes(f"CNF_WRT{str_options}CNF_END\n", encoding='utf-8')
        written=device.write(msg)
        logging.debug(f'송신: {msg}')
        logging.debug(f'송신: {written} bytes')
        time.sleep(0.3)
    finally:
        device.close()
        device = None

def apply_options(options, _app):
    #app.entry_serial_port.insert(0, options["comm_port"])
    if options['dhcp']:
        _app.switch_var.set("DHCP")
    else:
        _app.switch_var.set("NO-DHCP")
    _app.entry_ip.delete(0, "end")
    _app.entry_ip.insert(0, options["ip"])
    _app.entry_subnet.delete(0, "end")
    _app.entry_subnet.insert(0, options["subnet"])
    _app.entry_gateway.delete(0, "end")
    _app.entry_gateway.insert(0, options["gateway"])
    _app.entry_port.delete(0, "end")
    _app.entry_port.insert(0, options["port"])
    _app.entry_key.delete(0, "end")
    _app.entry_key.insert(0, options["key"])

def read_ui_options(_app):

    options = {}
    options['comm_port'] = _app.entry_serial_port.get()
    if app.switch_var.get() == "DHCP":
        options['dhcp'] = 1
    else:
        options['dhcp'] = 0
    options['ip'] = app.entry_ip.get()
    options['subnet'] = app.entry_subnet.get()
    options['gateway'] = app.entry_gateway.get()
    options['port'] = app.entry_port.get()
    options['key'] = app.entry_key.get()

    return options

class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.comm_port = ''
        self.comm_thread=None
        self.cipher = "AES"
        self.enc_server_socket = None

        self.read_options_thread = None
        self.stop_thread = False

        self.receive_plaintext_thread = None
        self.receive_ciphertext_thread = None
        self.data_to_send = None

        self.title("데이터암호화 모듈 테스트 프로그램")
        self.geometry(f"{1350}x{700}")

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.options = OPTIONS

        self.sidebar_frame = ctk.CTkFrame(self, width=160, corner_radius=0)  #,
        self.sidebar_frame.grid(row=0, column=0, rowspan=50, sticky="nsew")

        self.send_frame = ctk.CTkFrame( self, width=220, corner_radius=0, fg_color='transparent')
        self.send_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")

        self.receive_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color='transparent')
        self.receive_frame.grid(row=0, column=2, rowspan=3, sticky="nsew")

        #self.sidebar_frame.grid_rowconfigure(2, weight=1)
        self.send_frame.grid_rowconfigure(6, weight=1)
        self.receive_frame.grid_rowconfigure(2, weight=1)


        self.option_button = ctk.CTkButton(self.sidebar_frame, fg_color='#CC6600', hover_color='#AA4400',
                                         command=self.read_option_event)
        self.option_button.configure(text="설정 읽어오기")
        self.option_button.grid(row=0, column=0, padx=10, pady=(40, 1), sticky="nw")

        self.label_serial = ctk.CTkLabel(self.sidebar_frame, text="시리얼 통신 포트")
        self.label_serial.grid(row=1, column=0, padx=10, pady=(20, 1), sticky="nw")

        self.entry_serial_port = ctk.CTkEntry(self.sidebar_frame)#, placeholder_text="COM2")
        self.entry_serial_port.grid(row=2, column=0, padx=(10,20), pady=1, sticky="nw")

        self.label_network = ctk.CTkLabel(self.sidebar_frame, text="단말 네트워크 설정")
        self.label_network.grid(row=9, column=0, padx=10, pady=(30,1), sticky="nw")

        self.label_ip = ctk.CTkLabel(self.sidebar_frame, text="IP")
        self.label_ip.grid(row=10, column=0, padx=15, pady=(1,0), sticky="nw")
        self.switch_var = ctk.StringVar(value="NO-DHCP")
        self.dhcp = ctk.CTkSwitch(self.sidebar_frame, text="DHCP", command=self.dhcp_event,
                                   variable=self.switch_var, onvalue="DHCP", offvalue="NO-DHCP")
        self.dhcp.grid(row=10, column=0, padx=80, pady=(1,0), sticky="nw")

        self.entry_ip = ctk.CTkEntry(self.sidebar_frame)
        self.entry_ip.grid(row=11, column=0, padx=10, pady=0, sticky="nw")

        self.label_gateway = ctk.CTkLabel(self.sidebar_frame, text="gateway")
        self.label_gateway.grid(row=12, column=0, padx=15, pady=(1,0), sticky="nw")
        self.entry_gateway = ctk.CTkEntry(self.sidebar_frame)
        self.entry_gateway.grid(row=13, column=0, padx=10, pady=0, sticky="nw")

        self.label_subnet = ctk.CTkLabel(self.sidebar_frame, text="subnet mask")
        self.label_subnet.grid(row=14, column=0, padx=15, pady=(1,0), sticky="nw")
        self.entry_subnet = ctk.CTkEntry(self.sidebar_frame )
        self.entry_subnet.grid(row=15, column=0, padx=10, pady=0, sticky="nw")

        self.label_port = ctk.CTkLabel(self.sidebar_frame, text="port")
        self.label_port.grid(row=16, column=0, padx=15, pady=(1,0), sticky="nw")
        self.entry_port = ctk.CTkEntry(self.sidebar_frame, placeholder_text=f"{PORT_DEC}")
        self.entry_port.grid(row=17, column=0, padx=10, pady=0, sticky="nw")

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
        # Send Frame
        self.clear_button = ctk.CTkButton(self.send_frame, width=20, command=self.clear_button_event)
        self.clear_button.configure(text="내용 지우기")
        self.clear_button.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="we")

        self.label_plaintext = ctk.CTkLabel(self.send_frame, text="평    문:")
        self.label_plaintext.grid(row=1, column=0, padx=20, pady=(40, 0), sticky="nw")
        self.entry_plaintext = ctk.CTkEntry(self.send_frame, width=500, placeholder_text="16자 이내의 암호화할 데이터를 입력하세요")
        self.entry_plaintext.grid(row=1, column=0, padx=70, pady=(40,0), sticky="nw")

        self.enc_button = ctk.CTkButton(self.send_frame, width=200, command=self.enc_button_event)
        self.enc_button.configure(text="암호화 요청", bg_color='#aa3333', fg_color='#bb3333')
        self.enc_button.grid(row=2, column=0, padx=20, pady=(30, 0))#, sticky="we")

        self.label_ciphertext = ctk.CTkLabel(self.send_frame, text="암호문:")
        self.label_ciphertext.grid(row=3, column=0, padx=20, pady=(30, 0), sticky="nw")
        self.entry_ciphertext = ctk.CTkTextbox(self.send_frame, width=500)
        self.entry_ciphertext.grid(row=3, column=0, padx=70, pady=(30,0), sticky="nw")

        self.dnc_button = ctk.CTkButton(self.send_frame, width=200, command=self.dec_button_event)
        self.dnc_button.configure(text="복호화 요청", fg_color='#555599')
        self.dnc_button.grid(row=4, column=0, padx=20, pady=(30, 0))#, sticky="we")

        self.label_dectext = ctk.CTkLabel(self.send_frame, text="복호문:")
        self.label_dectext.grid(row=5, column=0, padx=20, pady=(30, 0), sticky="nw")
        self.entry_dectext = ctk.CTkEntry(self.send_frame, width=500)
        self.entry_dectext.grid(row=5, column=0, padx=70, pady=(30,0), sticky="nw")

        #=================================================================================
        # create textbox
        self.history_button = ctk.CTkButton(self.receive_frame, command=self.history_clear_event)
        self.history_button.configure(text="처리 기록 삭제")#, bg_color='#889933', fg_color='#889933')
        self.history_button.grid(row=0, column=0, padx=30, pady=(15, 5), sticky="nswe")

        self.history_textbox = ctk.CTkTextbox(self.receive_frame, width=420)#, border_color='blue', bg_color='blue')
        self.history_textbox.grid(row=2, column=0, padx=(20, 20), pady=(40, 60), sticky="nsew")
        self.history_textbox.insert('0.0', "처리 기록\n")
        self.history_textbox.configure(state='disabled')
        #self.receive_textbox.configure(bg_color='blue', fg_color='blue', border_color='blue')

    def get_options(self):
        self.options['dhcp'] = self.switch_var.get()
        self.options['ip'] = self.entry_ip.get()
        self.options['port'] = self.entry_port.get()
        self.options['key'] = self.entry_key.get()
        self.options['gateway'] = self.entry_gateway.get()
        self.options['subnet'] = self.entry_subnet.get()
        return self.options
    
    def set_options(self, value):
        self.options = value

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

    def dhcp_event(self):
        if self.switch_var.get() == 'NO-DHCP':
            self.entry_ip.configure(state='disabled')
            self.entry_gateway.configure(state='disabled')
            self.entry_subnet.configure(state='disabled')
        else:
            self.entry_ip.configure(state='normal')
            self.entry_gateway.configure(state='normal')
            self.entry_subnet.configure(state='normal')
        print("switch toggled, current value:", self.switch_var.get())

    def apply_option_event(self):
        write_device_options(self)

    def read_option_event(self):
        #self.init_options_thread()
        read_device_options(self)

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

    def init_options_thread(self):
        if self.read_options_thread:
            self.read_options_thread.stop()
            self.read_options_thread.join()
            self.read_options_thread = None

        self.read_options_thread = StoppableThread(target=read_device_options,args=(self,))
        self.read_options_thread.start()

    def enc_button_event(self):
        #self.plaintext_textbox.delete("1.0", "end-1c")
        pass

    def dec_button_event(self):
        #self.plaintext_textbox.delete("1.0", "end-1c")
        pass

    def history_clear_event(self):
        self.history_textbox.configure(state='normal')
        self.history_textbox.delete("1.0", "end-1c")
        self.history_textbox.configure(state='disabled')

    def clear_button_event(self):
        self.plaintext_textbox.delete("1.0", "end-1c")

    def change_cipher_event(self, new_cipher: str):
        self.cipher = new_cipher

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)


if __name__ == "__main__":

    app = App()

    #with open("k2_config.txt", "r") as f:
    #    lines = f.readlines()
    #    comm_port = lines[0].split("comm:")[1].strip()
    #    dhcp = lines[1].split("dhcp:")[1].strip()
    #    ip = lines[2].split("ip:")[1].strip()
    #    subnet = lines[3].split("subnet:")[1].strip()
    #    port = lines[4].split("port:")[1].strip()
    #    key = lines[5].split("key:")[1].strip()

    #app.switch_var = ctk.StringVar(value="NO-DHCP")

    options = app.options
    comm_port = options['comm_port']
    dhcp = options['dhcp']
    ip = options['ip']
    subnet = options['subnet']
    port = options['port']
    key = options['key']

    app.entry_serial_port.insert(0, comm_port)
    if options['dhcp']:
        app.switch_var.set("DHCP")
    else:
        app.switch_var.set("NO-DHCP")
    app.entry_ip.insert(0, ip)
    app.entry_subnet.insert(0, subnet)
    app.entry_port.insert(0, port)
    app.entry_key.insert(0, key)

    app.mainloop()

    app.stop_thread = True
