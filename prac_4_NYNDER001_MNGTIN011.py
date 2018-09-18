import spidev
import time
import os
import sys

# Open SPI bus
spi = spidev.SpiDev()   # create spi object
spi.open(0,0)
spi.max_speed_hz = 1000000
# RPI has one bus (#0) and two devices (#0 & #1)


# function to read ADC data from a channel
def GetData(channel):   # channel must be an integer 0-7
    adc = spi.xfer2([1,(8+channel)<<4,0])   # sending 3 bytes
    data = ((adc[1]&3) << 8) + adc[2]
    return data


# function to convert data to voltage level,
# places: number of decimal places needed
def ConvertVolts(data,places):
    volts = (data * 3.3) / float(1023)
    volts = round(volts,places)
    return volts

# function to convert data to light percentage
def ConvertLight(data,places):
    light = (data * 100) / float(1023)
    light = round(light,places)
    return light

# function to convert data to temperature
def ConvertTemp(data,places):
    temp = (data * 100) / float(1023)
    temp = round(temp,places)
    return temp

tFreq = 0.5

# Frequency Switch
def onFreq(channel):
    global tFreq
    if tFreq == 0.5:
        tFreq = 1
    elif tFreq == 1:
        tFreq = 2
    else:
        tFreq = 0.5
        
monitor = True

# Stop Switch
def onStop(channel):
    global monitor
    if monitor == False:
        monitor = True
    else:
        monitor = False
    global tFreq
    if tFreq == 0.5:
        tFreq = 1
    elif tFreq == 1:
        tFreq = 2
    else:
        tFreq = 0.5
        
# Define switch pins
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

reset = 4
freq = 17
stop = 27
display = 22

GPIO.setup(reset, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(freq, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(stop, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(display, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#Interrupts
GPIO.add_event_detect(reset, GPIO.RISING, callback= onReset, bouncetime=500) # Reset Switch

GPIO.add_event_detect(freq, GPIO.RISING, callback= onFreq, bouncetime=500) # Frequency Switch 

GPIO.add_event_detect(stop, GPIO.RISING, callback= onStop, bouncetime=500) # Stop Switch

GPIO.add_event_detect(display, GPIO.RISING, callback= onDisplay, bouncetime=1000) # Display Switch