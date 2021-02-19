# Structuring Your Data

Elastic is a search engine.  It's optimized to help you find information in large sets of data.  It does this by *indexing* the data you send it.  If you wanted to find information in a large book, you would turn to the *index* to see *where* in the book certain keywords are mentioned.  When you send data into Elastic, the data is indexed in a similar manner so users can quickly search large corpuses of data for it.

Understand how index-based datastores think about data will help when it comes to put data into them.  Occassionally, users ask why Elastic doesn't do joins, or provide query-time structuring of data.  It's not so much that Elastic doesn't provide those behaviors, it does, it just doesn't provide them in the traditional way.  Joins, for example, happen at ingest.  Since Elastic is optimized for information retrieval, it's not designed to store data in a first-order, normalized manner as that takes time to resolve or dereference when a query comes in.  The same goes for query-time structuring.  If we want to make information retrieval *fast*, we want an architecture that makes those trade-offs and optimizes for user experience (i.e., search speed).  Elastic does let you structure at query-time with [scripted fields](https://www.elastic.co/guide/en/kibana/current/scripted-fields.html) and [runtime fields](https://www.elastic.co/guide/en/elasticsearch/reference/current/runtime.html), but be aware of the trade-offs they introduce.

Once we're thinking about structuring data before sending it to Elasticsearch to index it, it's time to think about how to structure it.  You have a few options:


* [Logstash filters](https://www.elastic.co/guide/en/logstash/current/filter-plugins.html)
* [Ingest node pipelines](https://www.elastic.co/guide/en/elasticsearch/reference/current/ingest.html)
* [Beats processors](https://www.elastic.co/guide/en/beats/filebeat/current/defining-processors.html)
* 3rd party ETL tools
* Custom scripts

Options are good, and you have many, but we're going to focus on using Logstash filters in this guide.  Logstash filters are a mature way to structure data and provide a relatively simple, yet scalable, toolchain to handle millions of events per second.  Your requirements might sway you to another method of structuring your data, and that's perfectly fine.

## Why Structure Data

You can either let Elastic *interpret* the type of data your sending in (called [Dynamic mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html#mapping-dynamic)) or you can tell Elastic *explicitly* what type of data you're sending in (called [Explicit mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html#mapping-explicit)).  It's up to you and both choices have pros and cons.  As an opinionated guide, we recommend explicitly mapping your data.  The reasons being, explicit mappings help:

* Keep your cluster size "lean"
* Improve your cluster's performance
* Provide the best user query experience

The cons to using explicity mappings are:

* Takes extra time on ingest to define a Mapping
* If data changes, you have to update the Mapping

As with any engineering problem, tradeoffs come at a cost, but we believe these are worth it.  There are many ELK users who use dynamic mappings every day and love that behavior.  You are more than welcome to stray from the advice of this guide.  But we're here to give you our opinion, as seasoned Elastic practictioners.

The goal of structuring data is to align it to a [Mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html) contained in an [Index Template](), for a given data source.  If you are familiar with building tables in traditional SQL databases, you can think of Mappings and Index Templates as a database schema for a table.  They define what *type* of data to expect.  Telling Elastic what type of data to expect helps it store your data in the optimal data structures on disk and in memory, and know how to responsd to user queries with fast and efficient retrieval.

The ELK Stack uses a "[Schema on Write](https://www.elastic.co/blog/schema-on-write-vs-schema-on-read)" architecture compared to a "Schema on Read" architecture.  Since data is more often queried than it is written (usually, way more), we only want to parse the data once, and not pay the computational cost of structuring it on the fly each time a user queries it.  Doing so gives Elastic the optimal approach to structuring your data on disk for fast and efficient retrieval when a user queries it.

## Logstash Filters

Logstash processes data using pipelines.  Logstash pipelines can be built a number of ways.  Below is one method for iteratively building them.  It's outlined in 3 steps:

1. Print events to `stdout` to verify we can read them
2. Add a [Logstash Filter](https://www.elastic.co/guide/en/logstash/current/filter-plugins.html) to the `filter` block to modify the structure
3. Repeat Step #2 until your records are structured

The goal is to build a series of filters inside the `filter` block, which will turn the unstructured or semi-structured data into a structured format.

One approach to following these steps is to setup three terminals, side-by-side, and open the following in each:

* Terminal 1 - Source record that we'll use to reference existing structure
* Terminal 2 - The conf.d/test.yml pipeline so we can slowly add `filters`
* Terminal 3 - Shell to run Logstash which will reflect their new structure

![Image of workflow](images/workflow.png)

In the above example, you can see the raw record on the left, the filter chain in the middle, and the structured output on the right.  Building a `filter` chain in Logstash is largely an exercise in referencing the [Logstash Filters](https://www.elastic.co/guide/en/logstash/current/filter-plugins.html) documentation to see what is available, how they behave, and options they take.

Start with an empty filter chain:

```
filter {
}
```

Verify that the `stdout` output plugin is able to print records to `stdout` without any filtering.  Then add your first filter:

```
filter {
    add_field => {
    	"foo" => "bar"
    }
}
```

When you save the `test.yml` file, Logstash will pick up the change and re-run the filters in the file.  This should give you an "iteration loop" to run over and over as you build your `filter` chain.

Logstash has the ability to [add conditionals and use variables](https://www.elastic.co/guide/en/logstash/current/event-dependent-configuration.html).  Once you become familiar with the syntax, you'll find it quite powerful with regards to pulling apart data and structuring it the way you want it.

## Structure for Mappings

The goal of structuring our data is to align it to our [Mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html), for a given data source.  If you are familiar with building tables in traditional SQL databases, then think of Mappings like database schemas.  They define what *type* of data an index will hold in Elasticsearch, or what *type* of data a table will hold in a SQL database.

The [Field data types](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html) supported by Elasticsearch are very similar to those you'd find when building a schema for a database.  The types help the datastore understand how to deal with the data your storing.  In the case of Elasticsearch, the types help tell the system how you intend to *retrieve* a given field.  Do you want to search it?  Then use the *analyzed* [text field type](https://www.elastic.co/guide/en/elasticsearch/reference/current/text.html).  Do you want to simply filter it?  Then use a type from the [keyword type family](https://www.elastic.co/guide/en/elasticsearch/reference/current/keyword.html).

## Index Template

The [Index Template](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-templates.html) is where the Mappings are defined for a given Index in Elasticsearch.  An [Index](https://www.elastic.co/blog/what-is-an-elasticsearch-index) is what Elasticsearch uses to logically store your data.   