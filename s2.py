# sender.py
import time
import serial

ser = serial.Serial(port='/dev/ttyUSB0',
                    baudrate=115200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)
ser2 = serial.Serial(port='/dev/ttyUSB1',
                     baudrate=115200,
                     parity=serial.PARITY_NONE,
                     stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS,
                     timeout=1)
msg = ""
i = 0
while True:
    i += 1
    print(f"Counter {i} - Hello from Raspberry Pi")
    ser.write(f'hello-{i}'.encode('utf-8'))
    ser2.write(f'hello-{i*10}'.encode('utf-8'))
    time.sleep(2)