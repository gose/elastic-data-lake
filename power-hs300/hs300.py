#!/usr/bin/env python3

import datetime
import json
import subprocess

def query_power_strip(ip_addr, label, hosts, outlets, time):
    output = subprocess.getoutput("/home/ubuntu/.local/bin/pyhs100 --ip " + ip_addr +
            " emeter | grep voltage")
    output = output.replace("'", "\"")
    output = output.replace("0:", "\"0\":")
    output = output.replace("1:", "\"1\":")
    output = output.replace("2:", "\"2\":")
    output = output.replace("3:", "\"3\":")
    output = output.replace("4:", "\"4\":")
    output = output.replace("5:", "\"5\":")

    try:
        json_output = json.loads(output)
        for i in range(0, 6):
            reading = {}
            reading["ip"] = ip_addr
            reading["label"] = label
            reading["outlet"] = i
            reading["name"] = hosts[i]
            reading["volts"] = json_output[f"{i}"]["voltage_mv"] / 1000
            reading["amps"] = json_output[f"{i}"]["current_ma"] / 1000
            reading["watts"] = json_output[f"{i}"]["power_mw"] / 1000
            # Record then erase, the stats from the meter only at the top of each hour.
            # This gives us a clean "watts/hour" reading every 1 hour.
            if time.minute == 0:
                reading["watt_hours"] = json_output[f"{i}"]["total_wh"]
                erase_output = subprocess.getoutput("/home/ubuntu/.local/bin/pyhs100 --ip " +
                        ip_addr + " emeter --erase")
            outlets.append(reading)
    except Exception as e:
        print(e)

def main():
    # This script is designed to run every minute.
    # If it's the top of the hour, the "watt_hours" are also queried,
    # which often makes the runtime of this script greater than 1 minute.
    # So we capture the time the script started because we'll likely write
    # to output after another invocation of this script.
    # Even though these events will be written "out of order",
    # recording the correct invocation time will be important.
    now = datetime.datetime.utcnow()
    outlets = []

    hosts = {
        0: "node-22",
        1: "5k-monitor",
        2: "node-17",
        3: "node-18",
        4: "node-21",
        5: "switch-8"
    }
    query_power_strip("192.168.1.81", "desk", hosts, outlets, now)

    hosts = {
        0: "node-1",
        1: "node-2",
        2: "node-3",
        3: "node-0",
        4: "switch-8-poe",
        5: "udm-pro"
    }
    query_power_strip("192.168.1.82", "office", hosts, outlets, now)

    hosts = {
        0: "node-9",
        1: "node-10",
        2: "node-6",
        3: "node-4",
        4: "node-5",
        5: "node-20"
    }
    query_power_strip("192.168.1.83", "basement", hosts, outlets, now)

    power = {
        "@timestamp": now.isoformat(),
        "outlets": outlets
    }

    print(json.dumps(power))

if __name__ == "__main__":
    main()

