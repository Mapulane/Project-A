#!/usr/bin/python3
"""
Python Practical Template
Keegan Crankshaw
Readjust this Docstring as follows:
Names: Mapulane Makhaba
Student Number:MKHMAP005
Prac: 1
Date: 25 June 2019
"""

# import Relevant Librares
import RPi.GPIO as GPIO
import time
from time import gmtime, strftime
from datetime import datetime, time
from time import sleep
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import spidev
from time import sleep
import sys
import threading
from blynk import run_blynk
#import RPi.GPIO as GPIO

date1 = datetime.now()

spi_max_speed = 4 * 1000000 # 4 MHz
Resolution = 2**10 # 10 bits for the MCP 4911
CE = 1 # CE0 or CE1, select SPI device on bus
# setup and open an SPI channel
spi = spidev.SpiDev()
spi.open(0,CE)
spi.max_speed_hz = spi_max_speed


FMT = '%H:%M:%S'
StartTime = ""
tdelta = ""
waitT = 1
a = 1
dc = 0
p= ' '
c = ' ' 
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
flag = False
flag2 = False
#  Buttons to display 
def StartStop(channel):
	#print("Start/Stop pressed")
	global flag
	flag = not flag
	#print(flag)

def Alarm(channel):
        global c 
	c = ' '
def ChangeInterval(channel):
	global waitT,a
	b = a %3
	
	s = [1, 3, 5]
	waitT = s[b]
	a=a+1
	if a>2:
	    a=0
def ResetSysTime(channel):

	global  StartTime
        StartTime = strftime("%H:%M:%S", gmtime())

def setup():
	global p
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(18, GPIO.OUT)
	p = GPIO.PWM(18,1)
	#set output pin


	#set input pin
	GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(27,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	GPIO.setup(22,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(23,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	#set up interrupts
	GPIO.add_event_detect(17,GPIO.FALLING, callback = StartStop, bouncetime=200)
	GPIO.add_event_detect(27,GPIO.FALLING, callback = Alarm, bouncetime=200)
	GPIO.add_event_detect(22,GPIO.FALLING, callback = ChangeInterval, bouncetime=200)
        GPIO.add_event_detect(23,GPIO.FALLING, callback = ResetSysTime, bouncetime=200)

def date_diff_in_Seconds(dt2, dt1):
  timedelta = dt2 - dt1
  return timedelta.days * 24 * 3600 + timedelta.seconds

def readADC(): 
    global mcp
    adc0 = mcp.read_adc(0)
    adc1 = mcp.read_adc(1)
    adc2 = mcp.read_adc(2)
    #print(type(adc0))
    return  [adc0,adc1,adc2]
def pulseWidth():
   global c,p
   if c == '*':
   	p.start(10)
   else:
    	p.start(0)
  # print(type(p))
def setOutput(val):
    global spi
    # lowbyte has 6 data bits
    # B7, B6, B5, B4, B3, B2, B1, B0
    # D5, D4, D3, D2, D1, D0,  X,  X
    lowByte = val << 2 & 0b11111100
    # highbyte has control and 4 data bits
    # control bits are:
    # B7, B6,   B5, B4,     B3,  B2,  B1,  B0
    # W  ,BUF, !GA, !SHDN,  D9,  D8,  D7,  D6
    # B7=0:write to DAC, B6=0:unbuffered, B5=1:Gain=1X, B4=1:Output is active
    highByte = ((val >> 6) & 0xff) | 0b0 << 7 | 0b0 << 6 | 0b1 << 5 | 0b1 << 4
    # by using spi.xfer2(), the CS is released after each block, transferring the
    # value to the output pin.

    #print("Highbyte = {0:8b}".format(highByte))
    #print("Lowbyte =  {0:8b}".format(lowByte))
    spi.xfer2([highByte, lowByte])

def getstartTime():
	global  StartTime 
	StartTime = strftime("%H:%M:%S", gmtime())

def SystemTime():
	global tdelta
	global StartTime

	s1 = (strftime("%H:%M:%S", gmtime()))
        tdelta = datetime.strptime(s1, FMT) - datetime.strptime(StartTime, FMT)	

def currentTime():
	return strftime("%H:%M:%S", gmtime())

def programStart():
	getstartTime()
	

def trigAlarm():
	global c, date1, flag2
	if ((dc< 0.65) or (dc> 2.65)) and (not flag2):
	   date1 = datetime.now()
	   flag2 = not flag2
	   c = '*'
	elif (dc < 0.65 or dc > 2.65):
	   date2 = datetime.now()
	   if date_diff_in_Seconds(date2, date1) > 180:
	  	c = '*'
		date1 = datetime.now()
	   else: 	
		c = ' '

# Logic that you write
def main():
	global dc,c,waitT
	setup()
	print('_'*68)
	print("| RTC Time | Sys Timer | Humidity | Temp | Light | DAC out | Alarm |")
	print('_'*68)
	while (not flag):
		sleep(0.5)
	programStart()
	while flag:
	   sleep(waitT)
	   #SystemTime()
	   
	   adcOutput = readADC()
	   hum = 3.3*adcOutput[0]/1023
	   temp = 3.3*adcOutput[1]/1023
	   temp = temp - 0.5
	   temp = int(temp//0.01)
	   dc = hum*adcOutput[2]/1023
	   dcO = int(dc*1023/3.3)
	   setOutput(dcO)
	   SystemTime()
	   trigAlarm()
	   print('| '+ currentTime() + ' | ' + str(tdelta) +'   | '  + '%1.1f' % hum + ' V    | ' + str(temp) + ' C | ' + str(adcOutput[2]) + '   | '  + '%1.2f'% dc + '    | ' + c + '     |' )
	   if c == '*':
		a = 'ON'
	   else:
		a ='OFF'
	   h =str( currentTime() + ' ' + str(tdelta) +' '  + '%1.1f' % hum + 'V ' + str(temp) + ' ' + str(adcOutput[2]) + ' '  + '%1.2f' % dc + 'V ' + a )
           #print(h)
	   threading.Thread(target=run_blynk(h)).start()
	   pulseWidth()
	print('_'*68)
	GPIO.cleanup()
	sys.exit()
# Only run the functions if 
if __name__ == "__main__":
    # Make sure the GPIO is stopped correctly
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print("Exiting gracefully")
        # Turn off your GPIOs here
        GPIO.cleanup()
    except Exception as e:
        GPIO.cleanup()
        #print("Some other error occurred")
        print(e.message)
GPIO.cleanup()

