#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import os
import math
import configparser
import sys

data_rec = 16

ps_test = "pgrep -a python"

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(data_rec, GPIO.OUT)
GPIO.output(data_rec, 1)

data_config = configparser.ConfigParser()
data_config.read('/home/pi/Documents/Minion_scripts/Data_config.ini')

configDir = data_config['Data_Dir']['Directory']
configLoc = '{}/Minion_config.ini'.format(configDir)
config = configparser.ConfigParser()
config.read(configLoc)

iniImg = str2bool(config['Sampling_scripts']['Image'])
iniTpp = str2bool(config['Sampling_scripts']['TempPres'])
iniTmp = str2bool(config['Sampling_scripts']['Temperature'])
iniO2  = str2bool(config['Sampling_scripts']['Oxybase'])
iniAcc = str2bool(config['Sampling_scripts']['ACC_100Hz'])

scriptNames = ["TempPres_IF.py","OXYBASE_RS232_IF.py","ACC_100Hz_IF.py"]

if __name__ == '__main__':

    if iniTpp == True:
        os.system('sudo python /home/pi/Documents/Minion_scripts/TempPres_IF.py &')

    if iniImg == True:
        os.system('sudo python /home/pi/Documents/Minion_scripts/Minion_image_IF.py &')

    if iniO2 == True:
        os.system('sudo python /home/pi/Documents/Minion_scripts/OXYBASE_RS232_IF.py &')

    if iniAcc == True:
        os.system('sudo python /home/pi/Documents/Minion_scripts/ACC_100Hz_IF.py &')

    while(any(x in os.popen(ps_test).read() for x in scriptNames)) == True:

        time.sleep(10)
        print("Extended Sampling")

    GPIO.output(data_rec, 0)
    exit(0)
