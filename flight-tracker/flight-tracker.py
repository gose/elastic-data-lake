#!/usr/bin/env python3

import pyModeS as pms

from datetime import datetime, timedelta
from json import dumps
from pyModeS import common
from pyModeS.extra.rtlreader import RtlReader

class Flight:
    def __init__(self, hex_ident=None):
        self.hex_ident = hex_ident
        self.call_sign = None
        self.location = None
        self.altitude_ft = None
        self.speed_kts = None
        self.track_angle_deg = None
        self.vertical_speed_fpm = None
        self.speed_ref = None
        self.last_seen = None
        self.sent = False

    def has_info(self):
        return (#self.call_sign is not None and
            self.location is not None and
            self.altitude_ft is not None and
            self.track_angle_deg is not None and
            self.speed_kts is not None)

    def pretty_print(self):
        print(self.hex_ident, self.call_sign, self.location, self.altitude_ft, self.speed_kts,
                self.track_angle_deg, self.vertical_speed_fpm, self.speed_ref)

    def json_print(self):
        output = {
            "@timestamp": self.last_seen.isoformat(),
            "hex_code": self.hex_ident,
            "call_sign": self.call_sign,
            "location": {
                "lat": self.location[0],
                "lon": self.location[1]
                },
            "altitude_ft": self.altitude_ft,
            "speed_kts": self.speed_kts,
            "track_deg": int(self.track_angle_deg),
            "vertical_speed_fpm": self.vertical_speed_fpm,
            "speed_ref": self.speed_ref
        }
        print(dumps(output))


class ADSBClient(RtlReader):
    def __init__(self):
        super(ADSBClient, self).__init__()
        self.flights = {}
        self.lat_ref = <your_latitude>
        self.lon_ref = <your_longitude>
        self.i = 0

    def handle_messages(self, messages):
        self.i += 1
        for msg, ts in messages:
            if len(msg) != 28:  # wrong data length
                continue

            df = pms.df(msg)

            if df != 17:  # not ADSB
                continue

            if pms.crc(msg) !=0:  # CRC fail
                continue

            icao = pms.adsb.icao(msg)
            tc = pms.adsb.typecode(msg)
            flight = None

            if icao in self.flights:
                flight = self.flights[icao]
            else:
                flight = Flight(icao)

            flight.last_seen = datetime.now()

            # Message Type Codes:  https://mode-s.org/api/
            if tc >= 1 and tc <= 4:
                # Typecode 1-4
                flight.call_sign = pms.adsb.callsign(msg).strip('_')
            elif tc >= 9 and tc <= 18:
                # Typecode 9-18 (airborne, barometric height)
                flight.location = pms.adsb.airborne_position_with_ref(msg,
                        self.lat_ref, self.lon_ref)
                flight.altitude_ft = pms.adsb.altitude(msg)
                flight.sent = False
            elif tc == 19:
                # Typecode: 19
                # Ground Speed (GS) or Airspeed (IAS/TAS)
                # Output (speed, track angle, vertical speed, tag):
                (flight.speed_kts, flight.track_angle_deg, flight.vertical_speed_fpm,
                    flight.speed_ref) = pms.adsb.velocity(msg)

            self.flights[icao] = flight

            if self.i > 10:
                self.i = 0
                #print("Flights: ", len(self.flights))
                for key in list(self.flights):
                    f = self.flights[key]
                    if f.has_info() and not f.sent:
                        #f.pretty_print()
                        f.json_print()
                        f.sent = True
                    elif f.last_seen < (datetime.now() - timedelta(minutes=5)):
                        #print("Deleting ", key)
                        del self.flights[key]


if __name__ == "__main__":
    client = ADSBClient()
    client.run()
