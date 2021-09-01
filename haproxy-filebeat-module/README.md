We'll use the Filebeat HAProxy module to grab the HAProxy log file.

You can grab it without the module, but only one method works at a
time for Filebeat to read the file (you can't enable both).

We'll use the Filebeat HAProxy module since it cleanly persists the
HAProxy log file messages while also providing the appropriate metadata
for the other module artifacts: Ingest Pipeline, Kibana Dashboard, etc.

```
$ filebeat module enable haproxy
$ cat /etc/filebeat/modules.d/haproxy.yml
- module: haproxy
  log:
    enabled: true
    var.input: file
```
We should still be able to use the data collected by the module with
the "raw" HAProxy data source adapter [here](/data-sources/haproxy).

Since Beats Modules come with the ability to load the out-of-the-box
assets using the beat, you can leverage that method as described below.

Load Index Template

[https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-template.html](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-template.html)

Load Kibana Dashboards

[https://www.elastic.co/guide/en/beats/filebeat/current/load-kibana-dashboards.html](https://www.elastic.co/guide/en/beats/filebeat/current/load-kibana-dashboards.html)
