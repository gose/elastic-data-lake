#!/bin/bash
  
if [ $# -eq 0 ]; then
    echo "Usage: run.sh <pipeline.yml>"
    exit
fi

echo "Running pipeline: $1 ..."
/usr/share/logstash/bin/logstash --config.reload.automatic \
  --path.data tmp \
  --path.settings settings \
  -f $1
