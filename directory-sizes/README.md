# Monitoring Directory Sizes

<img src="logo.png" alt="DHT22" width="350" align="right">

Keeping an eye on the growth of your Data Lake is useful for a few reasons:

1. See how fast each data source is growing on disk
2. Keep an eye on how much space you have available
3. Better understand the cost of storing each data source

We'll use a Python script to query the size of each directory in our Data Lake (via NFS mount) in addition to recording the total size and space available for use.  Our script will write to stdout which we'll redirect to a log file.  From there, Filebeat will pick it up and send it to Elastic.

![Dashboard](dashboard.png)

Let's get started.

## Step #1 - Collect Data

Create a Python script at `~/bin/directory-sizes.py` with the following contents (adjusting any values as you see fit):

```python
#!/usr/bin/env python3

import datetime
import json
import os

path = "/mnt/data-lake"

def get_size(start_path = path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp): # skip symbolic links
                total_size += os.path.getsize(fp)
    return total_size

if __name__ == "__main__":
    if os.path.ismount(path):
        # Get size of each directory
        for d in os.listdir(path):
            size_bytes = get_size(path + "/" + d)
            output = {
                "@timestamp": datetime.datetime.utcnow().isoformat(),
                "dir": d,
                "bytes": size_bytes
            }
            print(json.dumps(output))

        # Get total, available, and free space
        statvfs = os.statvfs(path)
        output = {
            "@timestamp": datetime.datetime.utcnow().isoformat(),
            "total_bytes": statvfs.f_frsize * statvfs.f_blocks,     # Size of filesystem in bytes
            "free_bytes": statvfs.f_frsize * statvfs.f_bfree,       # Free bytes total
            "available_bytes": statvfs.f_frsize * statvfs.f_bavail, # Free bytes for users
            "mounted": True
        }
        print(json.dumps(output))
    else:
        output = {
            "@timestamp": datetime.datetime.utcnow().isoformat(),
            "mounted": False
        }
        print(json.dumps(output))
```

Try running the script from the command line:

```bash
chmod a+x ~/bin/directory-sizes.py
~/bin/directory-sizes.py
```

The output should look like the following:

```json
{"@timestamp": "2021-09-06T14:46:37.376487", "dir": "nginx", "bytes": 1445406508}
{"@timestamp": "2021-09-06T14:46:39.673445", "dir": "system-metricbeat-module", "bytes": 62265436549}
{"@timestamp": "2021-09-06T14:46:39.683812", "dir": "flights", "bytes": 5943006981}
{"@timestamp": "2021-09-06T14:46:41.122360", "dir": "haproxy-metricbeat-module", "bytes": 15443596238}
{"@timestamp": "2021-09-06T14:46:41.122731", "dir": "weather-historical", "bytes": 137599636}
...
```

Once you're able to successfully run the script, create a log file for its output:

```bash
sudo touch /var/log/directory-sizes.log
sudo chown ubuntu.ubuntu /var/log/directory-sizes.log
```

Create a logrotate entry so the log file doesn't grow unbounded:

```
sudo vi /etc/logrotate.d/directory-sizes
```

Add the following content:

```
/var/log/directory-sizes.log {
  weekly
  rotate 12
  compress
  delaycompress
  missingok
  notifempty
  create 644 ubuntu ubuntu
}
```

Add the following entry to your crontab:

```
* * * * * sudo /home/ubuntu/bin/directory-sizes.py >> /var/log/directory-sizes.log 2>&1
```

Verify output by tailing the log file for a few minutes:

```
$ tail -f /var/log/directory-sizes.log
```

If you're seeing output scroll each minute then you are successfully collecting data!

## Step #2 - Archive Data

Once your data is ready to archive, we'll use Filebeat to send it to Logstash which will in turn sends it to S3.

Add the following to the Filebeat config `/etc/filebeat/filebeat.yml` on the host logging your DHT22 data:

```yaml
filebeat.inputs:
  - type: log
    enabled: true
    tags: ["directory-sizes"]
    paths:
      - /var/log/directory-sizes.log
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

At this point, we should have DHT22 data flowing into Logstash.  By default however, our `distributor` pipeline in Logstash will put any unrecognized data in our Data Lake / S3 bucket called `NEEDS_CLASSIFIED`.  To change this, we're going to update the `distributor` pipeline to recognize the DHT22 data feed.

Add the following conditional to your `distributor.yml` file:

```
} else if "directory-sizes" in [tags] {
    pipeline {
        send_to => ["directory-sizes-archive"]
    }
}
```

Create a Logstash pipeline called `directory-sizes-archive.yml` with the following contents:

```
input {
    pipeline {
        address => "directory-sizes-archive"
    }
}
filter {
}
output {
    s3 {
        #
        # Custom Settings
        #
        prefix => "directory-sizes/%{+YYYY}-%{+MM}-%{+dd}/%{+HH}"
        temporary_directory => "${S3_TEMP_DIR}/directory-sizes-archive"
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
sudo mv directory-sizes-archive.yml /etc/logstash/conf.d/
```

Add the pipeline to your `/etc/logstash/pipelines.yml` file:

```
- pipeline.id: "directory-sizes-archive"
  path.config: "/etc/logstash/conf.d/directory-sizes-archive.conf"
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

Create a new pipeline called `directory-sizes-index.yml` with the following content:

```
input {
    pipeline {
        address => "directory-sizes-index"
    }
}
filter {
    json {
        source => "message"
    }
    json {
        source => "message"
    }
    date {
        match => ["timestamp", "ISO8601"]
    }
    mutate {
        remove_field => ["timestamp", "message"]
        remove_field => ["tags", "agent", "input", "log", "path", "ecs", "@version"]
    }
}
output {
    elasticsearch {
        #
        # Custom Settings
        #
        id => "directory-sizes-index"
        index => "directory-sizes-%{+YYYY.MM.dd}"
        hosts => "${ES_ENDPOINT}"
        user => "${ES_USERNAME}"
        password => "${ES_PASSWORD}"
    }
}
```

Put this pipeline in your Logstash configuration directory so it gets loaded in whenever Logstash restarts:

```bash
sudo mv directory-sizes-index.yml /etc/logstash/conf.d/
```

Add the pipeline to your `/etc/logstash/pipelines.yml` file:

```
- pipeline.id: "directory-sizes-index"
  path.config: "/etc/logstash/conf.d/directory-sizes-index.conf"
```

Append your new pipeline to your tagged data in the `distributor.yml` pipeline:

```
} else if "directory-sizes" in [tags] {
    pipeline {
        send_to => ["directory-sizes-archive", "directory-sizes-index"]
    }
}
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

Download this dashboard:  [directory-sizes.ndjson](directory-sizes.ndjson)

Jump back into Kibana:

1. Select "Stack Management" from the menu
2. Select "Saved Objects"
3. Click "Import" in the upper right

Once it's been imported, click on "Temperature DHT22".

![Dashboard](dashboard.png)

Congratulations!  You should now be looking at temperature data from your DHT22 in Elastic.

