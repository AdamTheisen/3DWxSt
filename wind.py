import Adafruit_ADS1x15
import RPi.GPIO as GPIO
import numpy as np
import time
import datetime as dt
import os

wind_spd = 0.
count = 1.

def get_wind_dir(adc):
    '''Function to get the wind direction from the ADC'''
    raw = adc.read_adc(0,gain=ADC_GAIN)
    adc_min = 269
    adc_max = 2047
    adc_range = adc_max - adc_min
    if (raw < adc_min):
        wdir = 0.
    elif (raw > adc_max):
        wdir = 360.
    else:
        adc_rel = raw - adc_min
        wdir = adc_rel*360.0/adc_range
    return round(wdir,2)

def get_wind_spd(wind, delta_t):
    '''Function to et the wind speed calculation'''
    count = 1.
    sensor_num = 2.
    #sample = 58.5 # Original value based on 1 minute average
    sample = delta_t
    sleep_time = 60
    cal_factor = 2.64
    offset = 0.0
    scale = cal_factor*(2.*3.14156*0.079)/(sensor_num*sample)
    wspd = wind*scale+offset
    return wspd

def wind_spd_cb(channel):
    global wind_spd
    wind_spd += count

if __name__ == "__main__":

    path = '/home/pi/data/cimms/wind'
    if not os.path.exists(path):
        os.makedirs(path)

    #Set up the ADC and GPIO
    adc = Adafruit_ADS1x15.ADS1015()
    ADC_GAIN=1
    pin = 22
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin,GPIO.FALLING,callback=wind_spd_cb,
        bouncetime=1)

    start = dt.datetime.now()

    wdir_list = []
    wspd_list = []
    sleep = 0.98
    prev_min = 0

    while True:
        end = dt.datetime.now()
        cur_min = end.minute
        delta_t = (end - start).total_seconds()
        wdir = get_wind_dir(adc)
        wspd = get_wind_spd(wind_spd,delta_t)

        if cur_min == prev_min:
            wdir_list.append(wdir)
            wspd_list.append(wspd)
        else:
            if len(wspd_list) > 0:
                #Write to file
                fname = os.path.join(path,'wind_%4d%02d%02d.csv' %
                    (start.year,start.month,start.day))
                fd = open(fname,'a+')
                fd.write(','.join([str(start),str(round(np.mean(wspd_list),2)),
                    str(round(max(wspd_list),2)),str(round(min(wspd_list),2)),
                    str(round(np.std(wspd_list),2)),
                    str(round(np.median(wspd_list),2)),str(len(wspd_list)),
                    str(round(np.mean(wdir_list),2)),
                    str(round(max(wdir_list),2)),str(round(min(wdir_list),2)),
                    str(round(np.std(wdir_list),2)),
                    str(round(np.median(wdir_list),2)),
                    str(len(wdir_list)),'\n']))
                fd.close()

            wdir_list=[wdir]
            wspd_list=[wspd]
            prev_min = cur_min

        #Reset Wind Speed
        wind_spd = 0.
        start = dt.datetime.now()

        time.sleep(sleep)

    fd.close()
    GPIO.cleanup()
