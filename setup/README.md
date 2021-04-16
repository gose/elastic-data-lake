# Setup

To build the architecture for the Elastic Data Lake, you'll need these components:

* Logstash
* HAProxy (or equivalent)
* S3 Data Store (or equivalent)
* Elastic Cluster

Here is the architecture we're building:

![](../images/architecture.png)

## Prerequisites

This guide depends on you having an S3 store and Elasticsearch cluster already running.  We'll use [Elastic Cloud](https://elastic.co) to run our Elasticsearch cluster and [Minio](https://www.digitalocean.com/community/tutorials/how-to-set-up-an-object-storage-server-using-minio-on-ubuntu-18-04) as an S3 data store (or any S3-compliant service).

## Step 1 - Logstash

Identify the host you want to run Logstash.  Depending on the volume of ingest you anticipate, you may want to run Logstash on multiple hosts (or containers).  It scales easily so putting HAProxy in front of it (which we'll do next) will make it easy to add more capacity.

Follow these instructions to get Logstash up and running:

[https://www.elastic.co/guide/en/logstash/current/installing-logstash.html](https://www.elastic.co/guide/en/logstash/current/installing-logstash.html)

Next, create a [Logstash keystore](https://www.elastic.co/guide/en/logstash/current/keystore.html) to store sensitive information and variables:

```
$ export LOGSTASH_KEYSTORE_PASS=mypassword
$ sudo -E /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash create
```

**Note:**  Store this password somewhere safe.  You will also need to add it to the environment that starts the Logstash process.

We'll use the keystore to fill in variables about our Elasticsearch cluster:

```
$ sudo -E /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add ES_ENDPOINT
$ sudo -E /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add ES_USERNAME
$ sudo -E /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add ES_PASSWORD
```

The `ES_ENDPOINT` value should be a full domain with `https` prefix and `:9243` port suffix.  For example:

```
https://elasticsearch.my-domain.com:9243
```

We'll also use the keystore to fill in variables about our S3 bucket:

```
$ sudo -E /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add S3_ENDPOINT
$ sudo -E /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add S3_BUCKET
$ sudo -E /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add S3_ACCESS_KEY
$ sudo -E /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add S3_SECRET_KEY
$ sudo -E /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add S3_DATE_DIR
$ sudo -E /usr/share/logstash/bin/logstash-keystore --path.settings /etc/logstash add S3_TEMP_DIR
```

The `S3_DATE_DIR` variable is used to organize your data into `date/time` directories in the Data Lake.  For example, `data-source/2021-01-01/13-04` will contain data collected January 1, 2021 during the minute 1:04PM GMT.  Organizing your data in this manner gives you good granularity in terms of identifying what time windows you may want to re-index in the future.  It allows you to reindex data from a year, month, day, hour, or minute interval.

The recommended value for `S3_DATE_DIR` is:

```
%{+YYYY}-%{+MM}-%{+dd}/%{+HH}-%{+mm}
```

The `S3_TEMP_DIR` variable should point to a directory where Logstash can temporarily store events.  Since this directory will contain events, you may need to make it secure so that only the Logstash process can read it (in addition to write to it).

If Logstash is running on an isolated host, you may set it to:

```
/tmp/logstash
```

### Ansible Pipeline Management

We'll configure Logstash using Ansible.  Ansible is a popular software provisioning tool that makes deploying configuration updates to multiple servers a breeze.  If you can SSH into a host, you can use Ansible to push configuration to it.

Create a directory to hold the Logstash configuration we'll be pushing to each Logstash host.

```
$ mkdir logstash
$ vi playbook-logstash.yml 
```

Add the following content to your Logstash Ansible playbook.

**Note:** Replace `node-1` and `node-2` with the names of your Logstash hosts.

```
---
- hosts: node-1:node-2
  become: yes
  gather_facts: no

  tasks:
    - name: Copy in pipelines.yml
      template:
        src: "pipelines.yml"
        dest: "/etc/logstash/pipelines.yml"
        mode: 0644

    - name: Remove existing pipelines
      file:
        path: "/etc/logstash/conf.d"
        state: absent

    - name: Copy in pipelines
      copy:
        src: "conf.d"
        dest: "/etc/logstash/"

    - name: Restart Logstash
      service:
        name: logstash
        state: restarted
        enabled: true

```

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
