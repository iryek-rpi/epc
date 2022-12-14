'''Serial communication test'''
import threading
import time

import serial

BAUD = 115200
PORT = '/dev/ttyUSB0'

ser = serial.Serial(port=PORT,
                    baudrate=BAUD,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=5)

line = ''
alive = True
endcommand = False


def readthread(ser):
    '''read from seral port'''
    global line
    global endcommand

    print('readthread init')

    while alive:
        try:
            for c in ser.read():
                line += (chr(c))
                if line.startswith('['):
                    if line.endswith(']'):
                        print('receive data=' + line)
                        if line == '[end]':
                            endcommand = True
                            print('end command\n')
                        # line reset
                        line = ''
                        ser.write('ok'.encode())
                else:
                    line = ''
        except Exception as e:
            print(f'read exception: {e}')

    print('thread exit')

    ser.close()


PLATFORM = 'DESKTOP2'


def main():
    global endcommand

    thread = threading.Thread(target=readthread, args=(ser, ))
    thread.daemon = True
    thread.start()

    if PLATFORM == 'DESKTOP':
        for count in range(0, 10):
            strcmd = '[test' + str(count) + ']'
            print('send data=' + strcmd)
            strencoding = strcmd.encode()
            ser.write(strencoding)
            time.sleep(1)

        strcmd = '[end]'
        ser.write(strcmd.encode())
        print('send data=' + strcmd)

    else:
        while True:
            time.sleep(1)
            if endcommand is True:
                break

    print('main exit')
    alive = False
    exit()


main()