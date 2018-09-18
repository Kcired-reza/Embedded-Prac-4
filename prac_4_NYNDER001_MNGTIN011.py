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

# Define sensor channels
light = 0
temp = 6
pot = 7

# Define arrays and counters
arrLight = []
arrTemp = []
arrPot = []
arrTime = []
arrTimer = []
count = 0

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

# Reset Switch
def onReset(channel):
    print("Reset")
    global arrLight
    global arrTemp
    global arrPot
    global arrTime
    global arrTimer
    global count
    global resetHours
    global resetMinutes
    global resetSeconds
    
    arrLight = []
    arrTemp = []
    arrPot = []
    arrTime = []
    arrTimer = []
    count = 0
    resetHours = getHours()
    resetMinutes = getMinutes()
    resetSeconds = getSeconds()
    global tFreq
    if tFreq == 0.5:
        tFreq = 1
    elif tFreq == 1:
        tFreq = 2
    else:
        tFreq = 0.5
        
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

import datetime
 
# Time functions
def getHours():
    date_time = datetime.datetime.now()
    time = date_time.time()
    hour = time.hour
    return hour
    
def getMinutes():
    date_time = datetime.datetime.now()
    time = date_time.time()
    minute = time.minute
    return minute

def getSeconds():
    date_time = datetime.datetime.now()
    time = date_time.time()
    second = time.second
    return second

# Initialise starting time
resetHours = getHours()
resetMinutes = getMinutes()
resetSeconds = getSeconds()
    
def getTime():
    date_time = datetime.datetime.now()
    time = date_time.time()
    if time.hour < 10:
        hour = "0" + str(time.hour)
    else:
        hour = str(time.hour)
        
    if time.minute < 10:
        minute = "0" + str(time.minute)
    else:
        minute = str(time.minute)

    if time.second < 10:
        second = "0" + str(time.second)
    else:
        second = str(time.second)
        
    strTime = hour + ':' +  minute + ':' + second
    return strTime
    
# Timer Function
def Timer():
    timerHours = getHours() - resetHours 
    timerMinutes = getMinutes() - resetMinutes
    timerSeconds = getSeconds() - resetSeconds

    if timerSeconds < 0:
        timerSeconds = timerSeconds + 60
        timerMinutes -= 1
        
    if timerMinutes < 0:
        timerMinutes += 60
        timerHours -= 1

    if timerHours < 0:
        timerHours += 24

    if timerHours < 10:
        hour = "0" + str(timerHours)
    else:
        hour = str(timerHours)
        
    if timerMinutes < 10:
        minute = "0" + str(timerMinutes)
    else:
        minute = str(timerMinutes)

    if timerSeconds < 10:
        second = "0" + str(timerSeconds)
    else:
        second = str(timerSeconds)
        
    strTime = hour + ':' +  minute + ':' + second
    return strTime

# Display Switch
def onDisplay(channel):
    print("Time     Timer    Pot   Temp  Light")
    for i in range(count):
        if i < 5:
            print(arrTime[i], arrTimer[i], arrPot[i], "V", arrTemp[i], "C", arrLight[i], "%")
    global tFreq
    if tFreq == 0.5:
        tFreq = 1
    elif tFreq == 1:
        tFreq = 2
    else:
        tFreq = 0.5
        
#Interrupts
GPIO.add_event_detect(reset, GPIO.RISING, callback= onReset, bouncetime=500) # Reset Switch

GPIO.add_event_detect(freq, GPIO.RISING, callback= onFreq, bouncetime=500) # Frequency Switch 

GPIO.add_event_detect(stop, GPIO.RISING, callback= onStop, bouncetime=500) # Stop Switch

GPIO.add_event_detect(display, GPIO.RISING, callback= onDisplay, bouncetime=1000) # Display Switch

try:
    while True:
        if monitor:
            # Read the data
            sensr_data = GetData (light)    # Measure light
            arrLight.append(ConvertLight(sensr_data,2))
            
            sensr_data = GetData (temp)     # Measure temp
            arrTemp.append(ConvertTemp(sensr_data,2))

            sensr_data = GetData (pot)      # Measure pot
            arrPot.append(ConvertVolts(sensr_data,2))

            arrTime.append(getTime())
            arrTimer.append(Timer())
            
            i = len(arrTimer) - 1
            print(arrTime[i], arrTimer[i], arrPot[i], "V", arrTemp[i], "C", arrLight[i], "%")
            count += 1
            if count > 5:
                count = 5
                arrLight.pop(0)
                arrTemp.pop(0)
                arrPot.pop(0)
                arrTime.pop(0)
                arrTimer.pop(0)
            # Wait before repeating loop
        time.sleep(tFreq)
except KeyboardInterrupt:
    spi.close()