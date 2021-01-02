# Elastic Data Lake

<img src="images/elk-data-lake.png" align="right" height="100" width="150" style="margin-top: -25px;" />

The Elastic Data Lake provides a methodology for collecting and
analyzing data with Elastic.

It presents a series of steps towards operating a data collection
& analysis environment using the Elastic Stack.  The framework
supports all kinds of data from logs to operational data, and
business data.

This guide provides a harness to build this pattern at your
organization.  No actual data is collected in this repository.  Its
purpose is to provide guidance and assets to help you onboard data.

## Architecture

Below is an archicture diagram of the data flow used in this
framework.  It uses Logstash to send a copy of the data you're
collecting to both Elasticsearch and your Data Lake, in parallel.
The Data Lake provides long-term durable storage for your raw data,
and Elastic provides an indexed store so that you can analyze your
data in near real-time.

In the event that you need to pull old data in or re-run raw data,
Logstash will retrieve it from the Data Lake and drop it in the
necessary pipeline for indexing in Elastic.  From there you can
analyze it with Elastic's rich set of visualization tools.

![](images/architecture.png)

Furthermore, the framework provides metering with HAProxy at key
points in the data flow.  This provides insight into our ingestion
volume at the point of entry, into the Data Lake, and into Elastic
for analysis.

## Setup

Follow the [Getting Started](/getting-started) guide to get your
Data Lake up and running.  It covers setting up Minio or leveraging
a Cloud object store like AWS S3, Google Cloud Storage, or Microsoft
Azure Storage.  There are also directions for configuring Logstash
and HAProxy since they are key components in this architecture.

## Onboarding Data

If you have data you'd like to collect & analize, follow these
steps.  Each step will provide the appropriate assets or guidance
for your data set.  If you build assets for a data source, we
encourage you to contribute back to the community via the
[Contribution](#contribute) section below.

![](images/onboarding-data.png)

Check the [/data-sources](/data-sources) directory to see if the
data source you want to collect already has the necessary assets
provided.  Some popular data sources (e.g., common log files) or
public data sources (e.g., wikipedia) have already been built and
you may wish to level them as-is or as a starting point.

The assets provided for a given data source cover these steps:

### Step 1 - Collect Data

Ingesting data can be accomplished in number of ways.  Based on
where your data resides, you may have a few options.  Most commonly,
data can be written to a file where Filebeat can be used to ship
the data in.  There a other Elastic Beats that specialize in
collecting data from various sources, like a network interface or
by polling a service API.  You can also pull in data from a database
or message queue like Kafka.

### Step 2 - Process Data

Processing data is handled by Logstash.  It copies our incoming
data to both Elasticsearch and a Data Lake / S3 repository.  Each
data set gets its own pipeline so it's clear what's going on with
it.  Logstash pipelines are easy to manage, copy around, and can
be committed to a source control repository.  They are key though
to structure your data though before having Elasticsearch index it.

### Step 3 - Index Data

Indexing the data in Elasticsearch is a step that involves providing
an "index template" to the engine so that the data coming is
appropriately indexed for fast retreival.  In the previous step,
we prepared the data specifically so they would match up to a
"schema", since that's what Elasticsearch uses to make searches
fast.

### Step 4 - Visualize Data

Visualizing data in Kibana is where the insight, information, and
answers come out, from all the work put into the previous steps.
It's where your hard work pays off when you're able to uncover new
insights in the data.  You'll use it to ask questions of the data
you collected, get answers and then form new questions to ask.
Rinse and repeat and you have a powerful search engine that you can
use to turn out insight after insight from your data.

## Data Sources

When it comes time to putting data in our Data Lake, we'll identify
it by name.  Since the same data set could be represented a number
of different ways, we'll accommodate that by putting assets for
that data source in an aptly named directory.

![](images/data-source-assets.png)

For example, let's say you want to collect & analyze data (logs or
metrics) from the popular HAProxy service.  There are a few ways
to do that and this diagram demonstrates how.  You could use the
official Elastic modules provided in Filebeat and Metricbeat.  Or
maybe you're running an older version of HAProxy and need to roll
your own.  You'd first check the [/data-sources](/data-sources)
directory for any directories with the word "haproxy" in the name.
We want to see if anyone has already done what you're trying to do,
or if someone has come close.  If so, great, you can try out their
work to see if it suits your needs.  If not, you can follow the
steps in this guide to collect & parse HAProxy to meet your needs.

Generally, the assets for each data source follow a particular
naming convention.  The goal here is to make it clear what piece
is involved in touching a particular data flow.  This naming
convention will help you know what data source is being collected,
what Logstash Pipeline is processing it, what Index Template is
indexing it, what Elasticsearch Index it's stored in, what Data
Lake / S3 directory it's archived in, and what Elastic Dashboard
visualizes it.

## Data Lake

The long-term archival of the data we're collecting will have the
following folder structure.  Each data source has its own directory
and data collected for that data source is stored in a subdirectory
named after the date it was collected.  This gives us a clean way
of seeing what data we collected and when.

```
<data-source-name>:
<day-of-year>/	<day-of-year>/	<day-of-year>/
```

For example:

```
authlog:
2020-12-29/	2020-12-30/	2020-12-31/

haproxy:
2020-12-29/	2020-12-30/	2020-12-31/

my-custom-log:
2020-12-29/	2020-12-30/	2020-12-31/

product-catalog:
2020-12-29/	2020-12-30/	2020-12-31/

syslog:
2020-12-29/	2020-12-30/	2020-12-31/

unclassified:
2020-12-29/	2020-12-30/	2020-12-31/

wikipedia:
2020-11-01/	2020-12-01/	2021-01-01/
```

If you're using Filebeat modules or other Elastic Beats (e.g.,
Metricbeat,  Packetbeat, etc), there are pipelines to nicely isolate
those data streams in the Data Lake as well.  Filebeat is assumed
to be the default ingest mechanism unless otherwise stated in the
directory name of the data source, like so:

```
authlog.module:
2020-12-29/	2020-12-30/	2020-12-31/

haproxy.module:
2020-12-29/	2020-12-30/	2020-12-31/

metricbeat.system.module:
2020-12-29/	2020-12-30/	2020-12-31/

metricbeat.postgresql.module:
2020-12-29/	2020-12-30/	2020-12-31/

packetbeat:
2020-12-29/	2020-12-30/	2020-12-31/

syslog.module:
2020-12-29/	2020-12-30/	2020-12-31/
```

To recap:

* `authlog` contains raw logs collected by Filebeat
* `authlog.module` contains logs collected by the Filebeat `system` module
* `metricbeat.system.module` contains logs collected by the Metricbeat `system` module
* `wikipedia` contains documents from Wikipedia
* `product-catalog` contains documents from a product catalog

You can adjust this layout structure by modifying the archive
pipelines accordingly.

## Contribute

If you have a data source you've parsed, built a pipeline for, an
index template, and a dashboard, you are welcome to share it with
the community.  Please submit an Issue with the assets or a Pull
Request.
