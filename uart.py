import serial
import time

port = serial.Serial("/dev/ttyAMA0", baudrate=921600, timeout=3.0)

while True:
	port.write(b"?")
	rcv = str(port.read(12))
	print("Received: " + rcv)
	time.sleep(2.0)



