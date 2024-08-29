import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(33, GPIO.OUT)

while True:
   GPIO.output(33, GPIO.HIGH)
   sleep(1)
   GPIO.output(33, GPIO.LOW)
   sleep(1)

