import serial
import time

class FtsMotorController():
    def __init__(self,port='COM3'):
        self.port = port
        self.ser = serial.Serial(port,baudrate=9600,timeout=0.1)
    def get_position(self):
        self.ser.write('RP\n')
        time.sleep(0.01)
        message = ''
        new_char = None
        while new_char != '\r':
            new_char = self.ser.read(1)
            if new_char == '':
                print "timed out while reading"
                break
            message += new_char
        try:
            counts = float(message)
            return counts
        except ValueError:
            raise ValueError("Couldn't parse: %s" % message)

    def send_position_command(self,counts):
        self.ser.write('P=%d G\n' % counts)
        time.sleep(0.01)

    def go_to_position(self,commanded_counts,timeout=30):
        start_time = time.time()
        self.send_position_command(commanded_counts)
        while time.time() - start_time < timeout:
            try:
                current = self.get_position()
#                print "current:", current
                if current == commanded_counts:
                    return
            except ValueError:
                pass
        raise Exception("Timed out waiting to get to commanded position")