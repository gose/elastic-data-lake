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
purpose is to provide guidance and assets to help you onboard and
analyze data.

## Architecture

Below is an archicture diagram of the data flow used in this
framework.  It uses Logstash to send a copy of the data you're
collecting to both Elasticsearch and your Data Lake, in parallel.
The Data Lake provides long-term durable storage for your raw data,
and Elastic provides an indexed store so that you can analyze your
data in near real-time.

In the event that you need to pull old data in or re-run raw data,
a Logstash pipeline will retrieve it from the Data Lake and drop
it in the necessary pipeline for indexing in Elasticsearch.

![](images/architecture.png)

Furthermore, the framework provides metering with HAProxy at key
points in the data flow.  This provides insight into our ingestion
volume at the point of entry, into the Data Lake, and into Elastic.
These measurements are often used to gauge the voluem of data the
system is handling.

Follow the [Getting Started](/getting-started) guide to get your
Data Lake up and running.  It covers setting up Minio or leveraging
a Cloud object store like AWS S3, Google Cloud Storage, or Microsoft
Azure Storage.  There are also directions for configuring Logstash
and HAProxy since they are key components in this architecture.

## Onboarding Data

Once your arhitecture is setup, follow these steps to onboard data.
Each step will provide the appropriate assets or guidance to ingest
data for a data source.  If you build assets for a data source, we
encourage you to contribute back to the community via the
[Contribution](#contribute) section below.

![](images/onboarding-data.png)

Check the [/data-sources](/data-sources) directory to see if the
data source you want to collect already has the necessary assets
provided.  Some popular data sources (e.g., common log files) or
public data sources (e.g., wikipedia) have already been built and
you may wish to leverage them as-is or as a starting point.

The assets provided for a given data source cover these steps:

### Step 1 - Collect Data

Ingesting data can be accomplished in number of ways.  Based on
where your data resides, you may have a few options.  Most commonly,
data can be written to a file where Filebeat can be used to ship
the data in.  There a other Elastic Beats that specialize in
collecting data from various sources, like a network interface or
by polling a service API.  You can also pull in data from a database
or message queue like Kafka.

If your data source is listed in [/data-sources](/data-sources),
follow the steps in the `1-collect/` directory.  The README in that
directory should outline the steps to collect data and send it to Logstash
to be processed.

If your data source is not listed, see [Creating a Data Sources](#creating-a-data-sources).

### Step 2 - Process Data

Processing data is handled by Logstash.  It copies your incoming
data to both Elasticsearch and your Data Lake.  Each
data set gets its own pipeline so it's clear what's going on with
it.  Logstash pipelines are easy to manage, copy around, and can
be committed to a source control repository.  They are key though
to structuring your data before having Elasticsearch index it.

If your data source is listed in [/data-sources](/data-sources),
follow the steps in the `2-process/` directory.  The README in that
directory should outline the steps to process data in Logstash
and provide example pipelines.

If your data source is not listed, see [Creating a Data Sources](#creating-a-data-sources).

### Step 3 - Index Data

Indexing the data in Elasticsearch is a step that involves providing
an "index template" to Elasticsearch so that the data coming is
appropriately typed.  In the previous step, we prepared the data 
specifically so it would match up to a "mapping" (a.k.a., "schema")
as defined in your Index Template.

If your data source is listed in [/data-sources](/data-sources),
follow the steps in the `3-index/` directory.  The README in that
directory should outline the mapping considerations that were made 
and provide an example.

If your data source is not listed, see [Creating a Data Sources](#creating-a-data-sources).

### Step 4 - Visualize Data

Visualizing data in Kibana is where the insight, information, and
answers come out, from all the work put into the previous steps.
It's where your hard work pays off when you're able to uncover new
insights in the data.  You'll use it to ask questions of the data
you collected, get answers and then form new questions to ask.
Rinse and repeat and you have a powerful search engine that you can
use to turn out insight after insight from your data.

If your data source is listed in [/data-sources](/data-sources),
follow the steps in the `4-visualize/` directory.  The README in that
directory should outline what visualizations are provide and direction
on how to import them into Kibana.

If your data source is not listed, see [Creating a Data Sources](#creating-a-data-sources).

## Creating a Data Sources

The data sources you wish to collect may already be in [/data-sources](/data-sources).
If they are, that's great, you have a nice starting point.  If they aren't,
this guide will walk you through creating them.  In general, a data source 
might have several variations as different needs come into play.

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
Lake directory it's archived in, and what Elastic Dashboard
visualizes it.

1. Create a directory named for your data (e.g., my-custom-data).

	```
	$ mkdir data-sources/my-custom-data
	$ cd data-sources/my-custom-data
	```

2. Create the following subdirectories inside it:

	```
	$ mkdir 1-collect 2-process 3-index 4-visualize
	$ ls
	1-collect/	2-process/	3-index/	4-visualize/
	```

3. Add your assets to the appropriate subdirectory.

	```
	README.md
	1-collect/filebeat.yml.snippet
	2-process/my-custom-data-archive.pipeline
	2-process/my-custom-data-reindex.pipeline
	2-process/my-custom-data-structure.pipeline
	3-index/my-custom-data-index-template.json
	4-visualize/my-custom-data-dashboard.ndjson
	```

4. Open an Issue or submit a Pull Request to have your data source added to this repo.

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

You can adjust this layout structure by modifying the archive
pipelines accordingly.

## Contribute

If you have a data source you've parsed, built a pipeline for, an
index template, and a dashboard, you are welcome to share it with
the community.  Please submit an Issue with the assets or a Pull
Request.

