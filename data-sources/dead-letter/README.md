# Dead Letter

The Dead Letter data source is a catch-all for unclassified data
in your Data Lake.  Ideally, the `distributor` pipeline in Logstash
is properly funneling your data to its own directory in your Data
Lake.  If the `distributor` doesn't see a matching tag on incoming
data, it will send the data to this data source.


The term "Dead Letter" refers to a piece of mail that cannot be
delivered to an address or returned to the sender. [Read
More](https://en.wikipedia.org/wiki/Dead_letter_mail)
