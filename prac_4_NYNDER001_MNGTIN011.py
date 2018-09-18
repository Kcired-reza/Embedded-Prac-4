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