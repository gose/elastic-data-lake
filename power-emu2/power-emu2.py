#! /usr/bin/env python3

import datetime
import json
import os
import platform
import serial
import sys
import time
import xml.etree.ElementTree as et

data = {}
data['message'] = "Starting"
d = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
data['timestamp'] = d

Y2K = 946684800

try:
    dev = '/dev/ttyACM1'
    emu2 = serial.Serial(dev, 115200, timeout=1)
    data['status'] = "connected"
except:
    data['status'] = "could not connect"
    print(json.dumps(data), flush=True)
    exit()

print(json.dumps(data), flush=True)

while True:
    try:
        msg = emu2.readlines()
    except:
        data = {}
        data['message'] = "error"
        d = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        data['timestamp'] = d
        print(json.dumps(data))
        exit()

    if msg == [] or msg[0].decode()[0] != '<':
        continue

    msg = ''.join([line.decode() for line in msg])

    try:
        tree = et.fromstring(msg)
        #print(msg)
    except:
        continue

    data = {}
    data['message'] = tree.tag

    if tree.tag == 'InstantaneousDemand':
        # Received every 15 seconds
        ts = int(tree.find('TimeStamp').text, 16)
        t = ts + Y2K # ts + Y2K = Unix Epoch Time
        d = datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%SZ")
        data['timestamp'] = d
        power = int(tree.find('Demand').text, 16)
        power *= int(tree.find('Multiplier').text, 16)
        power /= int(tree.find('Divisor').text, 16)
        power = round(power, int(tree.find('DigitsRight').text, 16))
        data['demand_kW'] = power
    elif tree.tag == 'PriceCluster':
        # Received every 1-2 minutes
        ts = int(tree.find('TimeStamp').text, 16)
        t = ts + Y2K # ts + Y2K = Unix Epoch Time
        d = datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%SZ")
        data['timestamp'] = d
        #data['price'] = int(tree.find('Price').text, 16)
        #data['trailing'] = int(tree.find('TrailingDigits').text, 16)
        data['price_cents_kWh'] = int(tree.find('Price').text, 16)
        data['price_cents_kWh'] /= 1000
        data['currency'] = int(tree.find('Currency').text, 16)
        # Currency uses ISO 4217 codes
        # US Dollar is code 840
        data['tier'] = int(tree.find('Tier').text, 16)
        st = int(tree.find('StartTime').text, 16)
        st = st + Y2K # st + Y2K = Unix Epoch Time
        d = datetime.datetime.fromtimestamp(st).strftime("%Y-%m-%dT%H:%M:%SZ")
        data['start_time'] = d
        data['duration'] = int(tree.find('Duration').text, 16)
    elif tree.tag == 'CurrentSummationDelivered':
        # Received every 3-5 minutes
        ts = int(tree.find('TimeStamp').text, 16)
        t = ts + Y2K # ts + Y2K = Unix Epoch Time
        d = datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%SZ")
        data['timestamp'] = d
        data['summation_delivered'] = int(tree.find('SummationDelivered').text, 16)
        data['summation_received'] = int(tree.find('SummationReceived').text, 16)
        energy = int(tree.find('SummationDelivered').text, 16)
        energy -= int(tree.find('SummationReceived').text, 16)
        energy *= int(tree.find('Multiplier').text, 16)
        energy /= int(tree.find('Divisor').text, 16)
        energy = round(energy, int(tree.find('DigitsRight').text, 16))
        data['meter_kWh'] = energy
    elif tree.tag == 'TimeCluster':
        # Received every 15 minutes
        ts = int(tree.find('UTCTime').text, 16)
        t = ts + Y2K # ts + Y2K = Unix Epoch Time
        d = datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%SZ")
        data['timestamp'] = d
        ts = int(tree.find('LocalTime').text, 16)
        t = ts + Y2K # ts + Y2K = Unix Epoch Time
        d = datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%dT%H:%M:%S")
        data['local_time'] = d
    else:
        for child in tree:
            if child:
                value = int(child.text, 16) if child.text[:2] == '0x' else child.text
                data['unknown'] = value

    print(json.dumps(data), flush=True)
