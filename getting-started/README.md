# Getting Started

To build the architecture for the Elastic Data Lake, you'll need these components:

* Logstash
* HAProxy (or equivalent)
* S3 Data Store
* Elastic Cluster

Here is the architecture we're building:

![](../images/architecture.png)

## Prerequisites

This guide depends on you having an S3 store and Elasticsearch cluster already running.  We'll use [Elastic Cloud](https://elastic.co) to run our Elasticsearch cluster and [Minio](https://www.digitalocean.com/community/tutorials/how-to-set-up-an-object-storage-server-using-minio-on-ubuntu-18-04) as an S3 data store (or any S3-compliant service).

## Step 1 - Logstash

Identify the host you want to run Logstash.  Depending on the volume of ingest you anticipate, you may want to run Logstash on multiple hosts (or containers).  It scales easily so putting HAProxy in front of it (which we'll do next) will make it easy to add more capacity.

Follow these instructions to get Logstash up and running:

[https://www.elastic.co/guide/en/logstash/current/installing-logstash.html](https://www.elastic.co/guide/en/logstash/current/installing-logstash.html)

### Centralized Pipeline Management

We'll configure Logstash to use Centralized Pipeline Management so that we can manage its pipelines from Kibana.  Add the following configuration to `/etc/logstash/logstash.yml`:

```
#
# X-Pack Management
#
xpack.management.enabled: true
xpack.management.pipeline.id:
  - "distributor"
  - "dead-letter-archive"
  - "dead-letter-reindex"
  - "dead-letter-structure"
  - "haproxy-filebeat-module-archive"
  - "haproxy-filebeat-module-reindex"
  - "haproxy-filebeat-module-structure"
  - "haproxy-metricbeat-module-archive"
  - "haproxy-metricbeat-module-reindex"
  - "haproxy-metricbeat-module-structure"
  - "system-filebeat-module-archive"
  - "system-filebeat-module-reindex"
  - "system-filebeat-module-structure"
  - "utilization-archive"
  - "utilization-reindex"
  - "utilization-structure"
xpack.management.elasticsearch.cloud_id: <cloud-id>
xpack.management.elasticsearch.cloud_auth: <user:password>
```

You may trim the `pipeline.id` list if you are not going to be collecting what's listed.

## Step 2 - HAProxy

Identify the host you want to run HAProxy.  Many Linux distributions support installation from the standard distribution.

In Ubuntu, run:

```
$ sudo apt install haproxy
```

In Redhat, run:

```
$ sudo yum install haproxy
```

A sample configuration file is provided: [haproxy.cfg](haproxy.cfg)