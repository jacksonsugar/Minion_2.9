#!/usr/bin/python3
import RPi.GPIO as GPIO
import tsys01
import ms5837
import time
import os
import serial
import configparser
import pickle

NumSamples = 0

samp_count = 1

def str2bool(v):
    return v.lower() in ("yes","true",'1','t')

data_config = configparser.ConfigParser()
data_config.read('/home/pi/Documents/Minion_scripts/Data_config.ini')

configDir = data_config['Data_Dir']['Directory']

config = configparser.ConfigParser()
configloc = '{}/Minion_config.ini'.format(configDir)

config.read(configloc)

iniTpp = str2bool(config['Sampling_scripts']['TempPres'])
iniTmp = str2bool(config['Sampling_scripts']['Temperature'])

Stime = config['Data_Sample']['Minion_sample_time']

try :
    float(test_string)
    Stime = float(Stime)
except :
    Stime = float(.25)

Srate = float(config['Data_Sample']['Minion_sample_rate'])

Sf = 1/Srate

TotalSamples = Stime*60*Srate

firstp = open("/home/pi/Documents/Minion_scripts/timesamp.pkl","rb")
samp_time = pickle.load(firstp)

for dataNum in os.listdir('{}/minion_data/'.format(configDir)):
    if dataNum.endswith('_TEMPPRES.txt'):
        samp_count = samp_count + 1

samp_time = "{}-{}".format(samp_count, samp_time)

file_name = "{}/minion_data/{}_TEMPPRES.txt".format(configDir, samp_time)

if iniTmp == True:

    sensor_temp = tsys01.TSYS01()

    # We must initialize the sensor before reading it
    if not sensor_temp.init():
        print("Error initializing sensor")
        exit(1)

sensor = ms5837.MS5837_30BA() # Default I2C bus is 1 (Raspberry Pi 3)

if not sensor.init():
        print("Sensor could not be initialized")
        exit(1)

# We have to read values from sensor to update pressure and temperature
if not sensor.read():
    print("Sensor read failed!")
    exit(1)

print("Pressure: %.2f atm  %.2f Torr  %.2f psi") % (
sensor.pressure(ms5837.UNITS_atm),
sensor.pressure(ms5837.UNITS_Torr),
sensor.pressure(ms5837.UNITS_psi))

print("Temperature: %.2f C") % (sensor.temperature(ms5837.UNITS_Centigrade))

freshwaterDepth = sensor.depth() # default is freshwater
sensor.setFluidDensity(ms5837.DENSITY_SALTWATER)
saltwaterDepth = sensor.depth() # No nead to read() again
sensor.setFluidDensity(1000) # kg/m^3
print("Depth: %.3f m (saltwater)") % (saltwaterDepth)

# fluidDensity doesn't matter for altitude() (always MSL air density)
print("MSL Relative Altitude: %.2f m") % sensor.altitude() # relative to Mean Sea Level pressure in air

time.sleep(1)

file = open(file_name,"a+")

if iniTmp == True:

    file.write("T+P INI @ %s\r\n" % samp_time)
    file.write("Pressure(mbar), Temp(C), TempTSYS01(C) \r\n")

else:

    file.write("T+P INI @ %s\r\n" % samp_time)
    file.write("Pressure(mbar),Temp(C) \r\n")

file.close()


# Spew readings
while NumSamples <= TotalSamples:

    if sensor.read():
        print("P: %0.1f mbar  %0.3f atm\tT: %0.2f C") % (
        sensor.pressure(), # Default is mbar (no arguments)
        sensor.pressure(ms5837.UNITS_atm), # Request psi
        sensor.temperature()) # Default is degrees C (no arguments)

    else:
        print('Sensor ded')
        file.write('Sensor fail')
        exit(1)

    file = open(file_name,"a")

    if iniTmp == True:

        if not sensor_temp.read():
            print("Error reading sensor")
            file.write("Error reading TSYS01, disabling.")
            iniTmp = False

        print("Temperature_accurate: %0.2f C" % sensor_temp.temperature())

        file.write("{},{},{}\n".format(sensor.pressure(), sensor.temperature(),sensor_temp.temperature()))

    else:

        file.write("{},{}\n".format(sensor.pressure(), sensor.temperature()))

    NumSamples = NumSamples + 1

    time.sleep(Sf)

file.close()
