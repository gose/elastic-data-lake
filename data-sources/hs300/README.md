# Monitoring Power with HS300

<img src="hs300.png" alt="HS300" width="200" align="right">

The Kasa Smart Wi-Fi Power Strip is a consumer-grade power strip that allows you to query the electrical properties of each outlet.  For example:

* Voltage
* Current
* Watts
* Watts per hour

More information about this device can be found here:

[https://www.kasasmart.com/us/products/smart-plugs/kasa-smart-wi-fi-power-strip-hs300](https://www.kasasmart.com/us/products/smart-plugs/kasa-smart-wi-fi-power-strip-hs300)

The HS300 is queried with a Python3 script.  The script is designed to run from a cron job where its output is redirected to a log file.  From there, Filebeat picks it up and sends it into Elasticsearch.

Many data center grade PSUs also provide ways to query individual outlet metrics.  A similar script could be written to extract this information in a commercial setting.

## Step #1 - Collect Data

Install the following Python module that knows how to query the power strip:

```
$ pip3 install pyhs100
```

Find the IP address of the power strip:

```
$ pyhs100 discover | grep IP
Host/IP: 192.168.1.5
```

Try querying the power strip:

```
$ /home/ubuntu/.local/bin/pyhs100 --ip 192.168.1.5 emeter
```

You should see output similar to:

```
{0: {'voltage_mv': 112807, 'current_ma': 239, 'power_mw': 24620, 'total_wh': 12}, 1: {'voltag_mv': 112608, 'current_ma': 243, 'power_mw': 23948, 'total_wh': 12}, 2: {'voltage_mv': 112608, 'current_ma': 238, 'power_mw': 23453, 'total_wh': 11}, 3: {'voltage_mv': 112509, 'current_ma': 70, 'power_mw': 5399, 'total_wh': 4}, 4: {'voltage_mv': 112409, 'current_ma': 93, 'power_mw': 3130, 'total_wh': 1}, 5: {'voltage_mv': 109030, 'current_ma': 78, 'power_mw': 5787, 'total_wh': 2}}
```

This is not properly formatted JSON, but the script included with this data source will help clean it up.

After you've verified that you can query the power strip, download the following script and open it in your favorite editor:

[hs300.py](hs300.py)

Modify the script with the following:

* Change the IP addresses to match that of your power strip(s)
* Change the directory location of the `pyhs100` command
* Change the names of each outlet in the `hosts` dictionary
* Change the "location" argument in the `query_power_strip()` function calls

Try running the script from the command line:

```
$ chmod a+x ~/bin/hs300.py
$ ~/bin/hs300.py
{"@timestamp": "2021-02-08T14:32:11.611868", "outlets": [{"outlet": 0, "name": "node-1", "volts": 112.393, "amps": 0.254, "watts": 25.425, "label": "office"}, ...]}
```

The output will include a JSON-formatted of each power outlet's metrics.  When pretty-printed, this will look like:

```
{
  "@timestamp": "2021-02-08T14:32:11.611868",
  "outlets": [
	   {
	      "outlet": 0, 
	      "name": "node-1",
	      "volts": 112.393,
	      "amps": 0.254,
	      "watts": 25.425,
	      "label": "office"
		},
		...
	]
}
```

Once you're able to successfully query the power strip, create a log file for its output:

```
$ sudo touch /var/log/hs300.log
$ sudo chown ubuntu.ubuntu /var/log/hs300.log
```

Create a logrotate entry so the log file doesn't grow unbounded:

```
$ sudo vi /etc/logrotate.d/hs300
```

Add the following content:

```
/var/log/hs300.log {
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
* * * * * /home/ubuntu/bin/hs300.py >> /var/log/hs300.log 2>&1
```

Verify output by tailing the log file for a few minutes:

```
$ tail -f /var/log/hs300.log
```

Tell Filebeat to send events in it to Elasticsearch, by editing `/etc/filebeat/filebeat.yml`:

```
filebeat.inputs:
- type: log
  enabled: true
  tags: ["hs300"]
  paths:
    - /var/log/hs300.log
```

Restart Filebeat:

```
$ sudo systemctl restart filebeat
```

We now have a reliable collection method that will queue the HS300 data on disk in a log file, read the log file as it is written to, and send the power stats to Elasticsearch in near real-time.  Filebeat will manage all the domain-specific logic of handing it off to Logstash in a reliable manner, dealing with retries, backoff logic, and more.  Our next step is to process the data in Logstash.

## Step #2 - Process Data

Once Filebeat is sending in data, we need to tell Logstash what to do with it.  By default, our `distributor` pipeline will put any unrecognized data in a Data Lake bucket called `NEEDS_CLASSIFIED`.  To change this, we're going to update the `distributor` pipeline to recognize the HS300 data feed and create two pipelines that know how to handle it (i.e., properly structure it for Elasticsearch and archive it in the Data Lake).

If you're doing this in environment with multiple Logstash instances, please adapt the instruction below to your workflow for deploying updates.  There is an [Ansible example]() if you'd like to learn more about it as a deployment model.

### Index Pipeline

Create a pipeline called `hs300-index` in your Logstash pipeline directory:

```
$ sudo vi /etc/logstash/conf.d/hs300-index.yml
```

Add the following content:

```
input {
    pipeline {
        address => "hs300-index"
    }
}
filter {
    mutate {
        remove_field => ["log", "input", "agent", "tags", "@version", "ecs", "host"]
        gsub => [
            "message", "@timestamp", "ts"
        ]
    }
    json {
        source => "message"
        skip_on_invalid_json => true
    }
    if "_jsonparsefailure" in [tags] {
        drop { }
    }
    split {
        field => "outlets"
    }
    ruby {
        code => "
            event.get('outlets').each do |k, v|
                event.set(k, v)
            end
            event.remove('outlets')
        "
    }
    if "_rubyexception" in [tags] {
      drop { }
    }
    mutate {
        remove_field => ["message", "@timestamp"]
    }
    date {
        match => ["ts", "YYYY-MM-dd'T'HH:mm:ss.SSSSSS"]
        timezone => "UTC"
        target => "@timestamp"
    }
    mutate {
        remove_field => ["ts"]
    }
}
output {
    elasticsearch {
        #
        # Custom Settings
        #
        id => "hs300-index"
        index => "hs300-%{+YYYY.MM.dd}"
        hosts => "${ES_ENDPOINT}"
        user => "${ES_USERNAME}"
        password => "${ES_PASSWORD}"
    }
}
```

The `filter` chain in this pipeline was built by following the [Building Logstash Filters](2-process/README.md) guide.

### Archive Pipeline

Create a pipeline called `hs300-archive` in your Logstash pipeline directory:

```
$ sudo vi /etc/logstash/conf.d/hs300-archive.yml
```

Add the following content:

```
input {
    pipeline {
        address => "hs300-archive"
    }
}
filter {
}
output {
    s3 {
        #
        # Custom Settings
        #
        prefix => "hs300/${S3_DATE_DIR}"
        temporary_directory => "${S3_TEMP_DIR}/hs300-archive"
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
        time_file => 1
        # encoding => "gzip"
        additional_settings => {
            force_path_style => true
            follow_redirects => false
        }
    }
}
```

We're not going to `gzip` encode the log messages to our Data Lake because it already does that for us.  If your Data Lake is not already compressing your data, then you will want to uncomment the `encoding` line.

*Note:*  Popular services like AWS S3 do not compress your data for you, so be sure to compress your data before sending it there.  These services will compress the data users have stored, but it's done unbeknownst to the user.  They are saving money by doing this, but charging you for storing the uncompressed size of your data.  So be sure to compress your data before using one of the popular Cloud storage services.

### Update Logstash Pipelines.yml

Tell Logstash about our new pipelines in the `pipelines.yml` file:

```
$ sudo vi /etc/logstash/pipelines.yml
```

Add the two pipelines we just created:

```
- pipeline.id: "hs300-archive"
  path.config: "/etc/logstash/conf.d/hs300-archive.conf"
- pipeline.id: "hs300-index"
  path.config: "/etc/logstash/conf.d/hs300-index.conf"
```

*Note:*  Do not restart Logstash yet.

### Distributor Pipeline

Edit the `distributor` pipeline to recognize the `hs300` tagged data coming in:

**Important**:  Before doing this, be sure your Logstash instances have the `hs300-index` pipeline _and_ the `hs300-archive` pipeline deployed!  If they are not, Logstash will start logging an error message indicating it failed to hand-off messages to the appropriate pipelines.

```
$ sudo vi /etc/logstash/conf.d/distributor.yml
```

Add the following conditional:

```
	...
	} else if "hs300" in [tags] {
        pipeline {
            send_to => ["hs300-archive"] #, "hs300-index"]
        }
    } ...
```

We have purposefully commented out the `hs300-index` pipeline so no data is sent to it.  That's because we have to create an Index Template first (which we'll do in Step #3 below).  For now though, we can tell Logstash to start collecting HS300 data and archiving it in the Data Lake.

Restart Logstash so these changes take effect:

```
$ sudo systemctl restart logstash
```

It's generally good practice to watch the Logstash log file as it's being restarted for any errors:

```
$ tail -f /var/log/logstash/logstash-plain.log
```

It can take a minute or two for Logstash to fully start, so be patient.

## Step #3 - Index Data

Once Logstash is correctly processing the data, we need to tell Elasticsearch how to index it.

## Step #4 - Visualize Data

Once Elasticsearch is indexing the data, we want to visualize it in Kibana.