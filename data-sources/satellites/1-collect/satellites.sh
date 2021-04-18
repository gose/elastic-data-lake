#!/bin/bash

if pgrep -f "python3 /home/ubuntu/python/satellites/satellites.py" > /dev/null
then
    echo "Already running."
else
    echo "Not running.  Restarting..."
    /home/ubuntu/python/satellites/satellites.py >> /var/log/satellites.log
fi
