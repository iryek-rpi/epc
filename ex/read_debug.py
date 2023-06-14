import sys
import serial
import logging
import time

#create default logger
#logging.basicConfig(level=logging.DEBUG)
#write to a log file and console at the same time
logging.basicConfig(filename='app.log', filemode='w', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


COMM_PORT = '/dev/ttyACM0'

if __name__ == "__main__":
    if sys.argv[1:]:
        COMM_PORT = sys.argv[1]

    logging.debug(f"시리얼 포트: {COMM_PORT}\n")

    try:
        device = serial.Serial(port=COMM_PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.5)
    except serial.serialutil.SerialException as e:
        print('시리얼 예외 발생: ', e)
    else:
        while 1:
            data = device.readline()
            if data:
                logging.debug(f"수신: {data}")
            time.sleep(0.3)

        device.close()
        device = None
