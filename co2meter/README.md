# CO2 Monitoring

<img src="/Users/gose/elastic/data-lake/co2meter/co2meter.png" alt="satellites" width="300" align="right">

The [CO2Mini](https://www.co2meter.com/collections/desktop/products/co2mini-co2-indoor-air-quality-monitor?variant=308811055) is an indoor air quality monitor that displays the CO2 level of the room it's in.  It's often used in home and office settings since it's been shown that elevated CO2 levels can cause [fatigue](https://pubmed.ncbi.nlm.nih.gov/26273786/) and [impair decisions](https://newscenter.lbl.gov/2012/10/17/elevated-indoor-carbon-dioxide-impairs-decision-making-performance/).  The CO2Mini connects to a computer via USB where it can be read programmatically.

## Step #1 - Collect Data

Create a new python script called `~/bin/co2meter.py` with the following contents:

​	[co2meter.py](co2meter.py)

The script was originally written by [Henryk Plötz](https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us) and has only a few minor edits so it works with Python3.  

Take a few minutes to familiarize yourself with the script.  There are a couple of labels you can change near the bottom.  Adjust the values of `hostname` and `location` to suit your needs.

With your CO2Mini plugged in, try running the script:

```bash
chmod a+x ~/bin/co2monitor.py
sudo ~/bin/co2monitor.py
```

We'll run our script with `sudo`, but you could add a `udev` rule to give your user permission to `/dev/hidraw0`.

You should see output on `stdout` similar to:

```json
{"@timestamp": "2021-09-01T20:38:06.353614", "hostname": "node", "location": "office", "co2_ppm": 438, "temp_c": 27.79, "temp_f": 82.02, "source": "CO2 Meter"}
```

Once you confirm the script is working, you can redirect its output to a log file:

```bash
sudo touch /var/log/co2monitor.log
sudo chown ubuntu.ubuntu /var/log/co2monitor.log
```

Create a logrotate entry so the log file doesn't grow unbounded:

```bash
sudo vi /etc/logrotate.d/co2monitor
```

Add the following logrotate content:

```
/var/log/co2monitor.log {
  weekly
  rotate 12
  compress
  delaycompress
  missingok
  notifempty
  create 644 ubuntu ubuntu
}
```

Add the following entry to your crontab with `crontab -e`:

```
* * * * * /home/ubuntu/bin/co2monitor.py >> /var/log/co2monitor.log 2>&1
```

Verify output by tailing the log file for a few minutes (since cron is only running the script at the start of each minute):

```bash
tail -f /var/log/co2monitor.log
```

If you're seeing output scroll each minute then you are successfully collecting data!

## Step #2 - Archive Data

Once your data is ready to archive, we'll use Filebeat to send it to Logstash which will in turn sends it to S3.

Add the following to the Filebeat config `/etc/filebeat/filebeat.yml` on the host logging your weather data:

```yaml
filebeat.inputs:
  - type: log
    enabled: true
    tags: ["co2meter"]
    paths:
      - /var/log/co2meter.log
```

This tells Filebeat where the log file is located and it adds a tag to each event.  We'll refer to that tag in Logstash so we can easily isolate events from this data stream.

Restart Filebeat:

```bash
sudo systemctl restart filebeat
```

You may want to tail syslog to see if Filebeat restarts without any issues:

```bash
tail -f /var/log/syslog | grep filebeat
```

At this point, we should have CO2 Monitor data flowing into Logstash.  By default however, our `distributor` pipeline in Logstash will put any unrecognized data in our Data Lake / S3 bucket called `NEEDS_CLASSIFIED`.  To change this, we're going to update the `distributor` pipeline to recognize the weather station data feed.

Add the following conditional to your `distributor.yml` file:

```
} else if "co2meter" in [tags] {
    pipeline {
        send_to => ["co2meter-archive"]
    }
}
```

Create a Logstash pipeline called `co2monitor-archive.yml` with the following contents:

```
input {
    pipeline {
        address => "co2monitor-archive"
    }
}
filter {
}
output {
    s3 {
        #
        # Custom Settings
        #
        prefix => "co2monitor/%{+YYYY}-%{+MM}-%{+dd}/%{+HH}"
        temporary_directory => "${S3_TEMP_DIR}/co2monitor-archive"
        access_key_id => "${S3_ACCESS_KEY}"
        secret_access_key => "${S3_SECRET_KEY}"
        endpoint => "${S3_ENDPOINT}"
        bucket => "${S3_BUCKET}"

        #
        # Standard Settings
        #
        validate_credentials_on_root_bucket => false
        codec => json_lines
        # Limit Data Lake file sizes to 5 GB
        size_file => 5000000000
        time_file => 60
        # encoding => "gzip"
        additional_settings => {
            force_path_style => true
            follow_redirects => false
        }
    }
}
```

Put this pipeline in your Logstash configuration directory so it gets loaded whenever Logstash restarts:

```bash
sudo mv co2monitor-archive.yml /etc/logstash/conf.d/
```

Add the pipeline to your `/etc/logstash/pipelines.yml` file:

```
- pipeline.id: "co2meter-archive"
  path.config: "/etc/logstash/conf.d/co2meter-archive.conf"
```

And finally, restart the Logstash service:

```bash
sudo systemctl restart logstash
```

While Logstash is restarting, you can tail it's log file in order to see if there are any configuration errors:

```bash
sudo tail -f /var/log/logstash/logstash-plain.log
```

After a few seconds, you should see Logstash shutdown and start with the new pipeline and no errors being emitted.

Check your cluster's Stack Monitoring to see if we're getting events through the pipeline:

![Stack Monitoring](archive.png)

Check your S3 bucket to see if you're getting data directories created for the current date & hour with data:

![MinIO](minio.png)

If you see your data being stored, then you are successfully archiving!

## Step #3 - Index Data

Once Logstash is archiving the data, next we need to index it with Elastic.

We'll use Elastic's [Dynamic field mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-field-mapping.html) feature to automatically create the right [Field data types](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html) for the data we're sending in.  

Using the [Logstash Toolkit](http://github.com/gose/logstash-toolkit), the following filter chain has been built that can parse the raw JSON coming in.

Create a new pipeline called `co2monitor-index.yml` with the following content:

```
input {
    pipeline {
        address => "co2meter-index"
    }
}
filter { 
    json {
        source => "message"
    }
    json {
        source => "message"
    }
    mutate {
        remove_field => ["message", "agent", "host", "input", "log", "host", "ecs", "@version"]
    }
}
output {
    elasticsearch {
        #
        # Custom Settings
        #
        id => "co2meter-index"
        index => "co2meter-%{+YYYY.MM.dd}"
        hosts => "${ES_ENDPOINT}"
        user => "${ES_USERNAME}"
        password => "${ES_PASSWORD}"
    }
}
```

Put this pipeline in your Logstash configuration directory so it gets loaded in whenever Logstash restarts:

```bash
sudo mv co2monitor-index.yml /etc/logstash/conf.d/
```

Add the pipeline to your `/etc/logstash/pipelines.yml` file:

```
- pipeline.id: "co2monitor-index"
  path.config: "/etc/logstash/conf.d/co2monitor-index.conf"
```

And finally, restart the Logstash service:

```bash
sudo systemctl restart logstash
```

While Logstash is restarting, you can tail it's log file in order to see if there are any configuration errors:

```bash
sudo tail -f /var/log/logstash/logstash-plain.log
```

After a few seconds, you should see Logstash shutdown and start with the new pipeline and no errors being emitted.

Check your cluster's Stack Monitoring to see if we're getting events through the pipeline:

![Indexing](index.png)

## Step #4 - Visualize Data

Once Elasticsearch is indexing the data, we want to visualize it in Kibana.

![Dashboard](dashboard.png)

Download this dashboard:  [co2monitor.ndjson](co2monitor.ndjson)

Jump back into Kibana:

1. Select "Stack Management" from the menu
2. Select "Saved Objects"
3. Click "Import" in the upper right

Congratulations!  You should now be looking at data from your weather station in Elastic.
