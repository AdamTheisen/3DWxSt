#!/usr/bin/python
#Code to gather data from the CIMMS modified 3DPAWS sensor from UCAR
#Import general libraries
import time
import os
import datetime as dt

#Import Sensor Libraries
import Adafruit_MCP9808.MCP9808 as MCP9808
import Adafruit_HTU21D.HTU21D as HTU21D
import Adafruit_BMP.BMP280 as BMP280
import SI1145.SI1145 as SI1145

def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

def main():
    time = dt.datetime.now()
    #Get MCP9808 Temp Data
    try:
        mcp1 = MCP9808.MCP9808()
        mcp1.begin()
        mcp1_temp = mcp1.readTempC()
    except:
        try:
            mcp1 = MCP9808.MCP9808()
            mcp1.begin()
            mcp1_temp = mcp1.readTempC()
        except:
            mcp1_temp = -9999.

    try:
        mcp2 = MCP9808.MCP9808(address=0x19)#Pi Temp
        mcp2.begin()
        mcp2_temp = mcp2.readTempC()
    except:
        mcp2_temp = -9999.

    #Get HTU2D RH/Temp Data
    try:
        htu = HTU21D.HTU21D()
        htu_temp = htu.read_temperature()
        htu_rh = htu.read_humidity()
        htu_dp = htu.read_dewpoint()
    except:
        htu_temp = -9999.
        htu_rh = -9999.
        htu_dp = -9999.

    #Get BMP pressure and temp data
    try:
        bmp = BMP280.BMP280()
        bmp_temp = bmp.read_temperature()
        bmp_pressure = bmp.read_pressure()
        bmp_alt = bmp.read_altitude()
        bmp_slp = bmp.read_sealevel_pressure()
    except:
        bmp_temp = -9999.
        bmp_pressure = -9999.
        bmp_alt = -9999.
        bmp_slp = -9999.

    #Get UV data
    try:
        si = SI1145.SI1145()
        si_vis = si.readVisible()
        si_ir = si.readIR()
        si_uv = si.readUV()
        si_uv = si_uv/100.0
    except:
        si_vis = -9999.
        si_ir = -9999.
        si_uv = -9999.

    #Write Data out to files
    path = '/home/pi/data/cimms'
    #Check if directories exist, if not create them
    inst_dirs = ['mcp1','mcp2','htu','bmp','si','master']
    for d in inst_dirs:
        if not os.path.exists(os.path.join(path,d)):
            os.makedirs(os.path.join(path,d))

    data = [time]
    #Write Individual Files   
    #MCP9808 Main Sensor
    fname = os.path.join(path,inst_dirs[0],'mcp9808_1_%4d%02d%02d.csv' % 
        (time.year,time.month,time.day))
    fd = open(fname,'a+')
    fd.write(','.join([str(time),str(mcp1_temp)])+'\n')
    fd.close()
    #MCP9808 Logger Sensor
    fname = os.path.join(path,inst_dirs[1],'mcp9808_2_%4d%02d%02d.csv' % 
        (time.year,time.month,time.day))
    fd = open(fname,'a+')
    fd.write(','.join([str(time),str(mcp2_temp)])+'\n')
    fd.close()
    #HTU21D Humidity Sensor
    fname = os.path.join(path,inst_dirs[2],'htu21d_%4d%02d%02d.csv' % 
        (time.year,time.month,time.day))
    fd = open(fname,'a+')
    fd.write(','.join([str(time),str(htu_temp),str(htu_dp),str(htu_rh)])+'\n')
    fd.close()
    #BMP280 Pressure Sensor
    fname = os.path.join(path,inst_dirs[3],'bmp280_%4d%02d%02d.csv' % 
        (time.year,time.month,time.day))
    fd = open(fname,'a+')
    fd.write(','.join([str(time),str(bmp_temp),str(bmp_pressure),str(bmp_alt),
        str(bmp_slp)])+'\n')
    fd.close()
    #SI1145 UV Sensor
    fname = os.path.join(path,inst_dirs[4],'si1145_%4d%02d%02d.csv' % 
        (time.year,time.month,time.day))
    fd = open(fname,'a+')
    fd.write(','.join([str(time),str(si_vis),str(si_ir),str(si_uv)])+'\n')
    fd.close()

    #Write out all data to master file
    fname = os.path.join(path,inst_dirs[5],'cimms_wxst_%4d%02d%02d.csv' % 
        (time.year,time.month,time.day))
    fd = open(fname,'a+')
    fd.write(','.join([str(time),str(round(mcp1_temp,2)),str(round(mcp2_temp,2)),
        str(round(htu_temp,2)),str(round(htu_dp,2)),str(round(htu_rh,2)),
        str(round(bmp_temp,2)),str(round(bmp_pressure,2)),str(round(bmp_alt,2)),
        str(round(bmp_slp,2)),str(round(si_vis,2)),str(round(si_ir,2)),
        str(round(si_uv,2))])+'\n')
    fd.close()

main()
