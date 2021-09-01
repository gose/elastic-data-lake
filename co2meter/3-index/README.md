# Elasticsearch Settings

Run the following commands in Dev Tools inside Kibana.

### Index Template

We use a `strict` mapping.  Any changes requires re-indexing from the Data Lake.

```
PUT _index_template/co2meter
{
  "template": {
    "settings": {
      "number_of_replicas": "1"
    },
    "mappings": {
      "dynamic": false,
      "_source": {
        "enabled": true,
        "includes": [],
        "excludes": []
      },
      "_routing": {
        "required": false
      },
      "properties": {
        "@timestamp": {
          "type": "date",
          "index": true,
          "ignore_malformed": false,
          "doc_values": true,
          "store": false
        },
        "co2_ppm": {
          "type": "integer",
          "index": true,
          "ignore_malformed": false,
          "coerce": true,
          "doc_values": true,
          "store": false
        },
        "hostname": {
          "type": "keyword",
          "index": true,
          "eager_global_ordinals": false,
          "norms": false,
          "split_queries_on_whitespace": false,
          "doc_values": true,
          "store": false,
          "index_options": "docs"
        },
        "location": {
          "type": "keyword",
          "index": true,
          "eager_global_ordinals": false,
          "norms": false,
          "split_queries_on_whitespace": false,
          "doc_values": true,
          "store": false,
          "index_options": "docs"
        },
        "source": {
          "type": "text"
        },
        "temp_c": {
          "type": "float"
        },
        "temp_f": {
          "type": "float"
        }
      }
    }
  },
  "index_patterns": [
    "co2meter-*"
  ]
}
```

```
PUT /co2meter-2020-*/_settings
{
  "settings": {
    "index.routing.allocation.require.box_type": "warm"
  }
}
```
