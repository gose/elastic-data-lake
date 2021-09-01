#!/usr/bin/env python3

import datetime
import fcntl
import json
import sys
import time

def decrypt(key,  data):
    cstate = [0x48,  0x74,  0x65,  0x6D,  0x70,  0x39,  0x39,  0x65]
    shuffle = [2, 4, 0, 7, 1, 6, 5, 3]
    phase1 = [0] * 8
    for i, o in enumerate(shuffle):
        phase1[o] = data[i]
    phase2 = [0] * 8
    for i in range(8):
        phase2[i] = phase1[i] ^ key[i]
    phase3 = [0] * 8
    for i in range(8):
        phase3[i] = ( (phase2[i] >> 3) | (phase2[ (i-1+8)%8 ] << 5) ) & 0xff
    ctmp = [0] * 8
    for i in range(8):
        ctmp[i] = ( (cstate[i] >> 4) | (cstate[i]<<4) ) & 0xff
    out = [0] * 8
    for i in range(8):
        out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xff
    return out

def hd(d):
    return " ".join("%02X" % e for e in d)

if __name__ == "__main__":
    key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]
    fp = open("/dev/hidraw0", "a+b", 0)
    set_report = [0] + [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]
    fcntl.ioctl(fp, 0xC0094806, bytearray(set_report))

    values = {}

    co2_ppm = 0
    temp_c = 1000
    i = 0

    while True:
        i += 1
        if i == 10:
            break
        data = list(fp.read(8))
        decrypted = decrypt(key, data)
        if decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]:
            print(hd(data), " => ", hd(decrypted),  "Checksum error")
        else:
            op = decrypted[0]
            val = decrypted[1] << 8 | decrypted[2]
            values[op] = val
            # http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf
            if 0x50 in values:
                co2_ppm = values[0x50]
            if 0x42 in values:
                temp_c = values[0x42] / 16.0 - 273.15

    temp_f = (temp_c * 9 / 5) + 32
    output = {
        "@timestamp":  datetime.datetime.utcnow().isoformat(),
        "hostname": "node-21",
        "location": "office",
        "co2_ppm": co2_ppm,
        "temp_c": float("%2.2f" % temp_c),
        "temp_f": float("%2.2f" % temp_f),
        "source": "CO2 Meter"
    }
    print(json.dumps(output))
