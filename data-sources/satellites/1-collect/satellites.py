#!/usr/bin/env python3

import datetime, json, time
from skyfield.api import load, wgs84

def main():
    stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
    stations = load.tle_file(stations_url, reload=True)
    starlink_url = 'http://celestrak.com/NORAD/elements/starlink.txt'
    starlinks = load.tle_file(starlink_url, reload=True)

    while True:
        now = datetime.datetime.utcnow()
        ts = load.timescale()

        satellites = []
        output = {}
        output['@timestamp'] = now.strftime('%Y-%m-%dT%H:%M:%SZ')

        by_name = {station.name: station for station in stations}
        station = by_name['ISS (ZARYA)']
        satellite = {}
        satellite['name'] = 'ISS'
        satellite['sat_num'] = station.model.satnum
        geocentric = station.at(ts.now())
        subpoint = wgs84.subpoint(geocentric)
        geo_point = {}
        geo_point['lat'] = subpoint.latitude.degrees
        geo_point['lon'] = subpoint.longitude.degrees
        satellite['location'] = geo_point
        satellite['elevation'] = int(subpoint.elevation.m)
        satellites.append(satellite)

        for starlink in starlinks:
            try:
                geocentric = starlink.at(ts.now())
                subpoint = wgs84.subpoint(geocentric)
                satellite = {}
                satellite['name'] = starlink.name
                satellite['sat_num'] = starlink.model.satnum
                geo_point = {}
                geo_point['lat'] = subpoint.latitude.degrees
                geo_point['lon'] = subpoint.longitude.degrees
                satellite['location'] = geo_point
                satellite['elevation'] = int(subpoint.elevation.m)
                satellites.append(satellite)
            except:
                pass

        output['satellites'] = satellites
        print(json.dumps(output))

        time.sleep(3)

if __name__ == "__main__":
    main()
