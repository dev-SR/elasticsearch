# Elasticsearch

- [Elasticsearch](#elasticsearch)
  - [Setup - Docker Compose for Elasticsearch and Kibana](#setup---docker-compose-for-elasticsearch-and-kibana)
  - [Index CRUD Operations](#index-crud-operations)
    - [Creating an Index](#creating-an-index)
    - [Listing all indices and mappings](#listing-all-indices-and-mappings)
    - [Deleting an Index](#deleting-an-index)
    - [Adding a Document](#adding-a-document)
    - [Retrieving Document](#retrieving-document)
    - [Updating a Document](#updating-a-document)
    - [Deleting a Document](#deleting-a-document)
  - [Basic Query](#basic-query)
    - [Get all documents](#get-all-documents)
    - [`match` query](#match-query)
    - [`multi-match` query](#multi-match-query)
    - [`term` query](#term-query)
    - [`range` query](#range-query)
    - [`bool` query](#bool-query)
  - [Aggregations and Grouping](#aggregations-and-grouping)
    - [Metrics aggregations](#metrics-aggregations)
      - [Single-value numeric Metrics aggregations](#single-value-numeric-metrics-aggregations)
        - [Multi-value numeric Metrics aggregations](#multi-value-numeric-metrics-aggregations)
    - [Bucket aggregations](#bucket-aggregations)
  - [Mapping](#mapping)
  - [Analyzer](#analyzer)

## Setup - Docker Compose for Elasticsearch and Kibana

Below is a simple example of a Docker Compose file for Elasticsearch and Kibana. You can create or copy this file using a text editor.

```yml
services:
  elasticsearch:
    image: elasticsearch:7.17.22
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - 9200:9200
    networks:
      - my-network

  kibana:
    image: kibana:7.17.22
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - 5601:5601
    depends_on:
      - elasticsearch
    networks:
      - my-network

networks:
  my-network:
    driver: bridge
```

Start Elasticsearch and Kibana by running the following command:

```bash
docker-compose up -d
```

This command starts the containers in the background. Elasticsearch can be accessed at `http://localhost:9200`, while Kibana is accessible at `http://localhost:5601`.

To stop the containers, you can use the following command in the same directory:

```bash
docker-compose stop
```

To remove the containers, you can use the following command:

```bash
docker-compose down
```

## Index CRUD Operations

### Creating an Index

ex1:

```sh
PUT /my_index
```

ex2- with settings and mappings:

```sh
PUT /my_index
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "age": { "type": "integer" }
    }
  }
}
```

Mapping is used to define the fields and their data types of the documents in the index.


### Listing all indices and mappings

```sh
GET /_cat/indices
GET index_name/_mapping
```

### Deleting an Index

```sh
DELETE /my_index
```

### Adding a Document

```sh
POST /my_index/_doc
{
  "name": "John Doe",
  "age": 30
}
```

Above will create a document with a random id while below will create a document with a specific id,1.

```sh
POST /my_index/_doc/1
{
  "name": "John Doe",
  "age": 30
}
```

Adding documents in bulk:

```sh
POST /my_index/_bulk
{"index": {"_id": "10000"}}
{"name": "John Doe", "age": 30}
{"index": {"_id": "200000"}}
{"name": "Jane Doe", "age": 25}

# or

POST /_bulk
{ "index": { "_index": "my_index", "_id": "1" } }
{ "name": "John Doe", "age": 30 }
{ "index": { "_index": "my_index", "_id": "2" } }
{ "name": "Jane Smith", "age": 25 }
{ "index": { "_index": "my_index", "_id": "3" } }
{ "name": "Alice Johnson", "age": 27 }

```

### Retrieving Document

```sh
GET /my_index/_doc/1
```

To retrieve multiple documents, you can use the `_mget` endpoint:

```sh
GET /my_index/_mget
{
  "docs": [
    {
      "_id": "1"
    },
    {
      "_id": "2"
    }
  ]
}
```

To retrieve all documents in an index, you can use the `_search` endpoint:

```sh
GET /my_index/_search
```

### Updating a Document

```sh
POST /my_index/_update/1
{
  "doc": {
    "age": 31
  }
}
```

### Deleting a Document

```sh
DELETE /my_index/_doc/1
```

Delete all documents in an index:

```sh
POST /my_index/_delete_by_query
{
  "query": {
    "match_all": {}
  }
}
```

## Basic Query

example index:

```sh
PUT /product
{
  "mappings": {
    "dynamic": true,
    "properties": {
      "title": {
        "type": "text",
        "copy_to": "all_filters"
      },
      "description": {
        "type": "text",
        "copy_to": "all_filters"
      },
      "price": {
        "type": "float"
      },
      "category": {
        "type": "keyword",
        "copy_to": "all_filters"
      },
      "brand": {
        "type": "keyword",
        "copy_to": "all_filters"
      },
      "quantity": {
        "type": "integer"
      },
      "filters": {
        "type": "nested",
        "properties": {
          "name": {
            "type": "keyword",
            "copy_to": "all_filters"
          },
          "value": {
            "type": "keyword",
            "copy_to": "all_filters"
          }
        }
      }
    }
  }
}
# https://www.elastic.co/guide/en/elasticsearch/reference/8.14/copy-to.html
# The copy_to parameter allows you to copy the values of multiple fields into a group field, which can then be queried as a single field. For example, the first_name and last_name fields can be copied to the full_name field as follows:

POST /product/_bulk
{ "index": { "_id": "1" } }
{ "title": "iPhone 13", "description": "Latest Apple smartphone", "price": 999.99, "category": "electronics", "brand": "Apple", "quantity": 50, "filters": [ {"name": "color", "value": "blue"}, {"name": "storage", "value": "128GB"} ] }
{ "index": { "_id": "2" } }
{ "title": "Samsung Galaxy S21", "description": "Flagship Samsung smartphone", "price": 899.99, "category": "electronics", "brand": "Samsung", "quantity": 100, "filters": [ {"name": "color", "value": "black"}, {"name": "storage", "value": "256GB"} ] }
{ "index": { "_id": "3" } }

#.........

```


### Get all documents

```sh
GET /my_index/_search

# or

GET /my_index/_search
{
  "from": 0
  "size": 10,
}

# or

GET /my_index/_search
{
  "query": {
    "match_all": {}
  },
  "size": 10,
  "from": 0
}
```

### `match` query

`match` query is used to search for documents all the matching words in the query string. By default, the `match` query uses the `OR` operator. For example:

```sh
GET product/_search
{
  "query": {
    "match": {
      "title": "apple iphone"
    }
  }
}
```

This query will return all documents where the `title` field contains the words `apple` or `iphone` case insensitive. So it will return documents with the title `Apple iPhone`, `apple iphone`, `Apple Watch`, `iPhone 13`, etc.

Therefore the default operator for the `match` query is `OR`. To change it to `AND`, you can use the `operator` parameter:

```sh
GET product/_search
{
  "query": {
    "match": {
      "title": {
        "query": "apple watch",
        "operator": "and"
      }
    }
  }
}
```

### `multi-match` query

`multi-match` query is used to search for documents that match the query string in multiple fields. For example:

```sh
GET product/_search
{
  "query": {
    "multi_match": {
      "query": "apple watch",
      "fields": ["title", "description"]
    }
  }
}
```

Individual fields can be boosted with the caret (^) notation:

```sh
GET product/_search
{
  "query": {
    "multi_match": {
      "query": "apple watch",
      "fields": ["title^3", "description"]
    }
  }
}
```

In the above example, the `title` field is boosted by a factor of 3.

### `term` query

`term` query is used to search for documents that contain an exact term in a field. For example:

```sh
GET product/_search
{
  "query": {
    "term": {
      "category": "electronics"
    }
  }
}

GET product/_search
{
  "query": {
    "term": {
      "category":{
        "value": "Electronics",
        "case_insensitive":true
      }
    }
  }
}
```

### `range` query

`range` query is used to search for documents that contain a range of values in a field. For example:

```sh
GET product/_search
{
  "query": {
    "range": {
      "price": {
        "gte": 100,
        "lte": 500
      }
    }
  }
}
```

### `bool` query

The Bool Query in Elasticsearch is used to combine multiple subqueries using Boolean logic, such as AND, OR, and NOT operations. It's particularly useful when you need to create more advanced and intricate queries by combining various conditions.

For condition keyword like `must`, `should`, `must_not`, and `filter` etc. are used.

1. `must` - The `must` clause is used to specify that the query must match all the conditions specified in the clause.


```sh
GET product/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "apple"
          }
        },
        {
          "match": {
            "title": "watch"
          }
        }
      ]
    }
  }
}
```

The above query will return documents where the `title` field contains both `apple` and `watch`.


2. `should` - The `should` clause is used to specify that the query should match at least one of the conditions specified in the clause.

example 2:

```sh
GET product/_search
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "title": "apple"
          }
        },
        {
          "match": {
            "title": "watch"
          }
        }
      ]
    }
  }
}
```

The above query will return documents where the `title` field contains either `apple` or `watch`.

3. `filter` is like `must` but does not calculate the relevance score, just filters the result based on the condition. Therefore, `filter` is faster than `must` and query clauses will be cached for future use.

```sh
GET product/_search
{
  "query": {
    "bool": {
      "filter": [
        {
          "match": {
            "title": "iphone"
          }
        },
        {
          "match": {
            "title": "apple"
          }
        },
        {
          "match": {
            "title": "pro"
          }
        }
      ]
    }
  }
}
```

The above query will return documents where the `title` field contains `apple`, `iphone`, and `pro`. So the logical operation is `AND` for the `filter` clause.


Combining multiple conditions:

```sh
GET product/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "iphone"
          }
        }
      ],
      "must_not": [
        {
          "match": {
            "title": "watch"
          }
        }
      ],
      "should": [
        {
          "match": {
            "title": "apple"
          }
        },
        {
          "match": {
            "title": "pro"
          }
        }
      ]
    }
  }
}
```

The above query will return documents where the `title` field contains `apple` and `iphone` but not `watch`.


## Aggregations and Grouping

### Metrics aggregations

Metrics aggregations are used to calculate metrics on fields in documents. Some of the commonly used metrics aggregations are:

- Single-value numeric Metrics aggregations
- Multi-value numeric Metrics aggregations

#### Single-value numeric Metrics aggregations

- `avg` - Calculates the average value of a numeric field.
- `sum` - Calculates the sum of a numeric field.
- `min` - Calculates the minimum value of a numeric field.
- `max` - Calculates the maximum value of a numeric field.
- `value_count` - Counts the number of values in a field.
- `cardinality` - Counts the number of unique values in a field.
- `stats` - Calculates the count, sum, min, max, and avg of a numeric field.

Syntax:

```sh
GET index/_search
{
  "aggs": {
    "agg_name": {
      "agg_type": {
        "field": "field_name"
      }
    }
  }
}
```


Example:


```sh
GET product/_search
{
  "size":0,
  "aggs": {
    "avg_price": {
      "avg": {
        "field": "price"
      }
    },
    "sum_price": {
      "sum": {
        "field": "price"
      }
    },
    "min_price": {
      "min": {
        "field": "price"
      }
    },
    "max_price": {
      "max": {
        "field": "price"
      }
    },
    "count_brand": {
      "value_count": {
        "field": "brand"
      }
    },
    "distinct_category": {
      "cardinality": {
        "field": "category"
      }
    },
    "stats_price": {
      "stats": {
        "field": "price"
      }
    }
  }
}
```

##### Multi-value numeric Metrics aggregations

- `percentiles` - Calculates the percentiles of a numeric field.
- `percentile_ranks` - Calculates the percentile ranks of a numeric field.
- `top_hits` - Returns the top documents per bucket.
- `extended_stats` - Calculates the count, sum, min, max, avg, and standard deviation of a numeric field.
- `geo_bounds` - Calculates the bounding box of a geo-point field.

Syntax:

```sh
GET index/_search
{
  "aggs": {
    "agg_name": {
      "agg_type": {
        "field": "field_name"
      }
    }
  }
}
```

Example:

```sh
GET product/_search
{
  "size":0,
  "aggs": {
    "percentiles_price": {
      "percentiles": {
        "field": "price"
      }
    },
    "percentile_ranks_price": {
      "percentile_ranks": {
        "field": "price",
        "values": [50, 75, 90]
      }
    },
    "extended_stats_price": {
      "extended_stats": {
        "field": "price"
      }
    }
  }
}
```

### Bucket aggregations

Bucket aggregations, as opposed to metrics aggregations, **can hold nested sub-aggregations**. These sub-aggregations will be aggregated for the buckets created by their "parent" bucket aggregation.

This is useful when you want to group documents based on a field value and then calculate metrics on those groups.

Some of the commonly used bucket aggregations are:

- `terms` - Groups documents based on the value of a field.
- `date_histogram` - Groups documents based on date intervals.
- `range` - Groups documents based on a range of values.
- `histogram` - Groups documents based on numeric intervals.
- `geo_distance` - Groups documents based on the distance from a geo-point.
- `filters` - Groups documents based on a filter.
- `nested` - Groups nested documents.
- `children` - Groups child documents.

Syntax:

```sh
GET index/_search
{
  "aggs": {
    "agg_name": {
      "agg_type": {
        "field": "field_name"
      }
    }
  }
}
```

Example group products based on category:

```sh
GET product/_search
{
  "size": 0,
  "aggs": {
    "groups_by_category": {
      "terms": {
        "field": "category",
        "min_doc_count": 1
      }
    }
  }
}
```

Example group products based on category, then get price stats for each category:

```sh
GET product/_search
{
  "size": 0,
  "aggs": {
    "groups_by_category": {
      "terms": {
        "field": "category",
        "min_doc_count": 1
      },
      "aggs": {
        "stats_price": {
          "stats": {
            "field": "price"
          }
        }
      }
    }
  }
}
```

Example group products based on category, then filter products with price greater than 500:

```sh
GET product/_search
{
  "size": 0,
  "aggs": {
    "groups_by_category": {
      "terms": {
        "field": "category",
        "min_doc_count": 1
      },
      "aggs": {
        "filter_price": {
          "filter": {
            "range": {
              "price": {
                "gte": 500
              }
            }
          }
        }
      }
    }
  }
}
#


GET product/_search
{
  "size": 0,
  "aggs": {
    "filter_price": {
      "filter": {
        "range": {
          "price": {
            "gte": 500
          }
        }
      },
      "aggs": {
        "groups_by_category": {
          "terms": {
            "field": "category"
          }
        }
      }
    }
  }
}

#

GET product/_search
{
  "size": 0,
  "aggs": {
    "filter_price": {
      "filter": {
        "match": {
          "title": "iphone"
        }
      },
      "aggs": {
        "stats": {
          "stats": {
            "field": "price"
          }
        }
      }
    }
  }
}
```

## Mapping

Mapping is used to define the fields and their data types of the documents in the index. It is important to define the mapping before adding documents to the index to ensure that the fields are correctly indexed and searchable.


```sh
PUT /product
{
  "mappings": {
    "dynamic": true,
    "properties": {
      "title": {
        "type": "text",
        "copy_to": "all_filters"
      },
      "description": {
        "type": "text",
        "copy_to": "all_filters"
      },
      "price": {
        "type": "double"
      },
      "category": {
        "type": "keyword",
        "copy_to": "all_filters"
      },
      "brand": {
        "type": "keyword",
        "copy_to": "all_filters"
      },
      "quantity": {
        "type": "integer"
      },
      "filters": {
        "type": "nested",
        "properties": {
          "name": {
            "type": "keyword",
            "copy_to": "all_filters"
          },
          "value": {
            "type": "keyword",
            "copy_to": "all_filters"
          }
        }
      }
    }
  }
}
```

## Analyzer

An analyzer is used to process the text before indexing it in Elasticsearch. It consists of three parts:

- Character filters: Used to preprocess the text before tokenization.
- Tokenizer: Used to break the text into tokens.
- Token filters: Used to modify the tokens before indexing.


```sh
PUT /my_index
{
  "settings": {
    "analysis": {
      "analyzer": {
        "my_analyzer": {
          "type": "custom",
          "char_filter": [],
          "tokenizer": "standard",
          "filter": ["lowercase"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "my_analyzer"
      }
    }
  }
}
```

In the above example, we define a custom analyzer called `my_analyzer` that uses the standard tokenizer and lowercase filter. We then apply this analyzer to the `title` field in the mapping.

You can test this new analyzer to make sure it is behaving correctly by using the analyze API:

```sh
GET /my_index/_analyze
{
  "analyzer": "my_analyzer",
  "text": "Hello World"
}
```

This will return the tokens generated by the analyzer:

```json

```

Usually, the same `analyzer` should be applied at index time and at search time, to ensure that the terms in the query are in the same format as the terms in the inverted index.

**Sometimes, though, it can make sense to use a different analyzer at search time**, such as when using the `edge_ngram` tokenizer for autocomplete or when using search-time synonyms.

```sh
PUT my-index-000001
{
  "settings": {
    "analysis": {
      "filter": {
        "my_filter": {
          "type": "edge_ngram",
          "min_gram": 1,
          "max_gram": 20
        }
      },
      "analyzer": {
        "my_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "my_filter"
          ]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "text": {
        "type": "text",
        "analyzer": "my_analyzer",
        "search_analyzer": "standard"
      }
    }
  }
}
```

In this example, we define an analyzer called `my_analyzer` that uses the `edge_ngram` filter during indexing and a search analyzer called `standard` during search. This is useful for autocomplete scenarios where you want to match partial words.

For example:

```sh
PUT my-index-000001/_doc/1
{
  "text": "Quick Brown Fox"
}

GET my-index-000001/_search
{
  "query": {
    "match": {
      "text": {
        "query": "Quick Br",
        "operator": "and"
      }
    }
  }
}
```

During indexing the term `Quick Brown Fox` will be tokenized into the following terms: `Q`, `Qu`, `Qui`, `Quic`, `Quick`, `B`, `Br`, `Bro`, `Brow`, `Brown`, `F`, `Fo`, `Fox`.

And during search, the query `Quick Br` will be tokenized into the terms `Quick` and `Br` (as per standard tokenizer), which will match the term `Quick Brown Fox`.

More:

- [https://www.elastic.co/guide/en/elasticsearch/reference/current/search-analyzer.html](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-analyzer.html)
- [https://www.elastic.co/guide/en/elasticsearch/guide/2.x/_index_time_search_as_you_type.html](https://www.elastic.co/guide/en/elasticsearch/guide/2.x/_index_time_search_as_you_type.html)


A complete example with mapping:

```sh
PUT /product
{
  "settings": {
    "analysis": {
      "filter": {
        "my_synonym_filter": {
          "type": "synonym",
          "synonyms_path": "analysis/synonym.txt"
        },
        "edge_ngram_filter": {
          "type": "edge_ngram",
          "min_gram": 2,
          "max_gram": 20
        }
      },
      "analyzer": {
        "product_indexing_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "asciifolding",
            "my_synonym_filter",
            "edge_ngram_filter"
          ]
        },
        "product_search_analyzer": {
          "type": "custom",
          "tokenizer": "keyword",
          "filter": [
            "lowercase",
            "asciifolding"
          ]
        }
      }
    }
  },
  "mappings": {
    "dynamic": true,
    "properties": {
      "title": {
        "type": "text",
        "copy_to": "all_filters",
        "analyzer": "product_indexing_analyzer",
        "search_analyzer": "product_search_analyzer"
      },
      "description": {
        "type": "text",
        "copy_to": "all_filters",
        "analyzer": "product_indexing_analyzer",
        "search_analyzer": "product_search_analyzer"
      },
      "price": {
        "type": "float"
      },
      "category": {
        "type": "keyword",
        "copy_to": "all_filters",
        "normalizer": "lowercase_normalizer"
      },
      "brand": {
        "type": "keyword",
        "copy_to": "all_filters",
        "normalizer": "lowercase_normalizer"
      },
      "quantity": {
        "type": "integer"
      },
      "filters": {
        "type": "nested",
        "properties": {
          "name": {
            "type": "keyword",
            "copy_to": "all_filters",
            "normalizer": "lowercase_normalizer"
          },
          "value": {
            "type": "keyword",
            "copy_to": "all_filters",
            "normalizer": "lowercase_normalizer"
          }
        }
      },
      "all_filters": {
        "type": "text",
        "analyzer": "product_indexing_analyzer",
        "search_analyzer": "product_search_analyzer"
      }
    }
  }
}
```

In this example, we define a custom analyzer called `product_indexing_analyzer` that uses the standard tokenizer and applies the following filters: `lowercase`, `asciifolding`, `my_synonym_filter`, and `edge_ngram_filter`, for indexing. We also define a custom analyzer called `product_search_analyzer` that uses the keyword tokenizer and applies the `lowercase` and `asciifolding` filters for searching.


Using an `edge_ngram` filter during indexing but not during search can be a very effective strategy for certain types of search functionalities, especially in e-commerce, where users often type partial terms or prefixes.

**Why This Works Well?**

1. **Efficient Prefix Search**: By using edge n-grams at index time, you generate all possible prefixes of your terms. This allows you to match user queries against these prefixes efficiently.
2. **Simplified Search Queries**: The search-time analyzer (`product_search_keyword_analyzer`) does not need to generate n-grams. It can search for the exact tokens, making the query process simpler and faster.
3. **Consistent Matching**: Users can type partial words or prefixes and still get relevant results. For example, a search for "iPh" can match "iPhone".
