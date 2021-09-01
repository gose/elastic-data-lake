# CO2 Monitoring

Steps:

1. Read from a CO2 monitor and write the output to a log file.
2. Collect the log file with Filebeat.

https://www.co2meter.com/collections/desktop/products/co2mini-co2-indoor-air-quality-monitor

```
filebeat.inputs:
- type: log
  enabled: true
  tags: ["co2meter"]
  paths:
    - /var/log/co2meter.log
```

