#!/usr/bin/env python3
import RPi.GPIO as GPIO
import tsys01
import ms5837
import pickle
import time
import os
import math
import configparser
import sys

BURN = 33
data_rec = 16

samp_count = 1

NumSamples = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BURN, GPIO.OUT)
GPIO.setup(data_rec, GPIO.OUT)
GPIO.output(BURN, 0)
GPIO.output(data_rec, 1)

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def abortMission(configLoc):

    abortConfig = configparser.ConfigParser()
    abortConfig.read(configLoc)
    abortConfig.set('Mission','Abort','1')
    with open(config,'wb') as abortFile:
        abortConfig.write(abortFile)

    GPIO.output(IO328, 0)
    os.system('sudo python /home/pi/Documents/Minion_scripts/Recovery_Sampler.py &')

data_config = configparser.ConfigParser()
data_config.read('/home/pi/Documents/Minion_scripts/Data_config.ini')

configDir = data_config['Data_Dir']['Directory']
configLoc = '{}/Minion_config.ini'.format(configDir)
config = configparser.ConfigParser()
config.read(configLoc)
MAX_Depth = float(config['Mission']['Max_Depth'])
MAX_Depth = MAX_Depth*100.4  # Convert from meters to mBar
Abort = str2bool(config['Mission']['Abort'])
iniImg = str2bool(config['Sampling_scripts']['Image'])
iniTpp = str2bool(config['Sampling_scripts']['TempPres'])
iniTmp = str2bool(config['Sampling_scripts']['Temperature'])
iniO2  = str2bool(config['Sampling_scripts']['Oxybase'])
iniAcc = str2bool(config['Sampling_scripts']['ACC_100Hz'])

if Abort == True:
        GPIO.output(IO328, 0)
        os.system('sudo python /home/pi/Documents/Minion_scripts/Recovery_Sampler.py &')


firstp = open("/home/pi/Documents/Minion_scripts/timesamp.pkl","rb")
samp_time = pickle.load(firstp)

for dataNum in os.listdir('{}/minion_data/INI/'.format(configDir)):
    if dataNum.endswith('_TEMPPRES-INI.txt'):
        samp_count = samp_count + 1

samp_time = "{}-{}".format(samp_count, samp_time)

Stime = float(config['Initial_Samples']['hours'])
Srate = float(config['Initial_Samples']['TempPres_sample_rate'])    

file_name = "{}/minion_data/INI/{}_TEMPPRES-INI.txt".format(configDir, samp_time)

Sf = 1/Srate

TotalSamples = Stime*60*60*Srate

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
if sensor.read():
    Pres_ini = sensor.pressure()
else:
    Pres_ini = "Broken"

print("Pressure: {} Bar").format(Pres_ini)

print("Temperature: %.2f C") % (sensor.temperature(ms5837.UNITS_Centigrade))

time.sleep(1)

file = open(file_name,"a+")

if iniTmp == True:

    file.write("T+P MS5837_30BA and TempTSYS01 @ %s\r\n" % samp_time)
    file.write("Pressure(mbar), Temp(C), TempTSYS01(C) \r\n")

else:

    file.write("T+P MS5837_30BA @ %s\r\n" % samp_time)
    file.write("Pressure(mbar),Temp(C) \r\n")

file.close()

if __name__ == '__main__':

    if Pres_ini == "Broken":
        file.write("Sensor Malfunction! Returning to surface.")
        abortMission(configLoc)

    else:

        if iniImg == True:
            os.system('sudo python /home/pi/Documents/Minion_scripts/Minion_image_IF.py &')

        if iniO2 == True:
            os.system('sudo python /home/pi/Documents/Minion_scripts/OXYBASE_RS232_IF.py &')

        if iniAcc == True:
            os.system('sudo python /home/pi/Documents/Minion_scripts/ACC_100Hz_IF.py &')

        # Spew readings
        while(NumSamples <= TotalSamples):

            if sensor.read():
                print("P: %0.1f mbar  %0.3f atm\tT: %0.2f C") % (
                sensor.pressure(), # Default is mbar (no arguments)
                sensor.pressure(ms5837.UNITS_atm), # Request psi
                sensor.temperature()) # Default is degrees C (no arguments)

            else:
                print('Sensor ded')
                file.write('Sensor fail')
                abortMission(configLoc)
              
            Pres_ini = sensor.pressure()

            if Pres_ini >= MAX_Depth:
                file.write("Minion Exceeded Depth Maximum!")
                abortMission(configLoc)
            
            file = open(file_name,"a")

            if iniTmp == True:

                if not sensor_temp.read():
                    print("Error reading sensor")
                    iniTmp = False
                    exit(1)

                print("Temperature_accurate: %0.2f C" % sensor_temp.temperature())

                file.write("{},{},{}\n".format(sensor.pressure(), sensor.temperature(),sensor_temp.temperature()))

            else:

                file.write("{},{}\n".format(sensor.pressure(), sensor.temperature()))

            NumSamples = NumSamples + 1

            time.sleep(Sf)

        file.close()
        GPIO.output(data_rec, 0)
