import numpy as np
import RPi.GPIO as GPIO
import datetime,time,os

calibration = 0.2
pin = 23
sleep_time = 58.5

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

rain = 0.
def cb(channel):
    global rain
    rain += calibration

GPIO.add_event_detect(pin,GPIO.FALLING,callback=cb,bouncetime=300)

start = datetime.datetime.now()
prev_min = 0
sleep = 0.98
rain_list=[]
path = '/home/pi/data/cimms/rain'
if not os.path.exists(path):
    os.makedirs(path)

while True:
    end = datetime.datetime.now()
    cur_min = end.minute
    if cur_min == prev_min:
        rain_list.append(rain)
    else:
        if len(rain_list) > 0:
            fname = os.path.join(path,'rain_%4d%02d%02d.csv' %
                (start.year,start.month,start.day))
            fd = open(fname,'a+')
            fd.write(','.join([str(start),str(round(sum(rain_list),2)),
                str(round(max(rain_list),2)),
                str(len(rain_list)),str(sum(r > 0. for r in rain_list)),'\n']))
            fd.close()
        rain_list = [rain]
        prev_min = cur_min
    rain = 0.
    time.sleep(sleep)


