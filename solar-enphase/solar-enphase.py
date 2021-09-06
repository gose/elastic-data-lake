#!/usr/bin/env python3
  
import urllib.request
import urllib.parse
import datetime

def main():
    # The Enphase API endpoints are detailed here:
    #   https://developer.enphase.com/docs
    # Most of them don't need to be called more than once a day.

    now = datetime.datetime.utcnow()

    # Run once per day
    if now.hour == 0 and now.minute == 0:
        url = "https://api.enphaseenergy.com/api/v2/systems/<your_site_id>/energy_lifetime?key=<your_key>&user_id=<your_user_id>"
        f = urllib.request.urlopen(url)
        print(f.read().decode("utf-8"))

        url = "https://api.enphaseenergy.com/api/v2/systems/<your_site_id>/inventory?key=<your_key>&user_id=<your_user_id>"
        f = urllib.request.urlopen(url)
        print(f.read().decode("utf-8"))

    # Run once per hour
    if now.minute == 0:
        url = "https://api.enphaseenergy.com/api/v2/systems/<your_site_id>/summary?key=<your_key>&user_id=<your_user_id>"
        f = urllib.request.urlopen(url)
        print(f.read().decode("utf-8"))

    # Run every 10 minutes 
    if now.minute % 10 == 0:
        # Get the status of each inverter
        url = "https://api.enphaseenergy.com/api/v2/systems/inverters_summary_by_envoy_or_site?key=<your_key>&user_id=<your_user_id>&site_id=<your_site_id>"
        f = urllib.request.urlopen(url)
        print(f.read().decode("utf-8"))

        # The `stats` endpoint updates, at most, once every 5 minutes.
        # It isn't reliable though, so you can't expect a new reading every 5 minutes.
        # Due to this, we'll track all of it and use an enrich lookup in Logstash to 
        # see if the 5-minute reading was already inserted into Elasticsearch.
        # {
        #   "end_at": 1613239200,
        #   "devices_reporting": 20,
        #   "powr": 159,  # Average power produced during this interval, measured in Watts.
        #   "enwh": 13    # Energy produced during this interval, measured in Watt hours.
        # }
        url = "https://api.enphaseenergy.com/api/v2/systems/<your_site_id>/stats?key=<your_key>&user_id=<your_user_id>"
        f = urllib.request.urlopen(url)
        print(f.read().decode("utf-8"))

if __name__ == "__main__":
    main()
