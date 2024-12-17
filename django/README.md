# Django + ElasticSearch

## ElasticSearch-DSL

### Setup

1. Install elasticsearch-dsl

```bash
pip install elasticsearch-dsl
```

2. Define `search.py` file in an app

```python
from elasticsearch_dsl import Document, Text, Keyword, Float, Integer, Nested, InnerDoc
# from elasticsearch_dsl.connections import connections
# connections.create_connection(hosts='http://localhost:9200')
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts='http://localhost:9200')


class Filter(InnerDoc):
    name = Keyword(copy_to='all_filters')
    value = Keyword(copy_to='all_filters')


class ProductDocument(Document):
    title = Text(copy_to='all_filters')
    description = Text(copy_to='all_filters')
    price = Float()
    category = Keyword(copy_to='all_filters')
    brand = Keyword(copy_to='all_filters')
    quantity = Integer()
    filters = Nested(Filter)

    class Index:
        name = 'product'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }


def create_index():
    ProductDocument.init()
    print('Index created')

```

To create index run `crate_index()` function on Django shell

By running `python manage.py shell` you go into the Django shell and import your `search.py` with `from <app>.search import *` and then run `crate_index()` to create index.


## Faceting

 Facets help customers quickly discover their desired product based on specific attributes, such as size, color, price range, etc. This means that we can filter products based on their attributes. Facets are created by grouping products based on their attributes.

In, elasticsearch we can use aggregations - buckets grouping mechanism to create facets.

For the index mapping:

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

We can create facets using the following aggregation:

```sh
GET product/_search
{
  "aggs": {
        "facets": {
          "nested": {
            "path": "filters"
          },
          "aggs": {
            "names": {
              "terms": {
                "field": "filters.name"
              },
              "aggs": {
                "values": {
                  "terms": {
                    "field": "filters.value"
                  }
                }
              }
            }
          }
        }
      }
}
```

For example, since we haven't applied any filters yet, the result will following, listing all the attributes and their values:

 ```bash
Color:
    - Red (10)
    - Blue (5)
    - Green (3)
    - Gray (2)
    - Black (1)
RAM:
    - 4GB (10)
    - 8GB (5)
    - 16GB (3)
    - 32GB (2)
    - 64GB (1)
Storage:
    - 64GB (10)
    - 128GB (5)
    - 256GB (3)
    - 512GB (2)
    - 1TB (1)
```

Now let's say an user wants to filter products with the following attributes:

- Color: black

```sh
GET product/_search
{
    "size": 10,
    "query": {
        "bool": {
            "filter": [
                {
                    "nested": {
                        "path": "filters",
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "term": {
                                            "filters.name": "Color"
                                        }
                                    }
                                ],
                                "should": [
                                    {
                                        "term": {
                                            "filters.value": "red"
                                        }
                                    }
                                ],
                                "minimum_should_match": 1
                            }
                        }
                    }
                }
            ]
        }
    },
    "aggs": {
        "facets": {
            "nested": {
                "path": "filters"
            },
            "aggs": {
                "names": {
                    "terms": {
                        "field": "filters.name"
                    },
                    "aggs": {
                        "values": {
                            "terms": {
                                "field": "filters.value"
                            }
                        }
                    }
                }
            }
        }
    }
}
```

Response:

```bash
Color:
    - Red (10)
RAM:
    - 4GB (6)
    - 8GB (2)
Storage:
    - 64GB (4)
    - 128GB (3)
```

As show by the result facets are narrowed down to only the values that match the filter applied. But other `Color` values are not shown. This is not the expected behavior. We want to show all the options of the applied filter `Color` but other filters options should narrowed down to the values that match the filter applied `Color=red`. Like below:

```bash
Color:
    - Red (10)
    - Blue (5)
    - Green (3)
    - Gray (2)
    - Black (1)
RAM:
    - 4GB (6)
    - 8GB (2)
Storage:
    - 64GB (4)
    - 128GB (3)
```

Search i.e, `samsung` in amazon.com to obverse this behavior.


Therefore, we need to retain all the facets regardless of the filters applied. To do this we need to use a `global` aggregation to get all the facets.

So:

Before:


```bash
{
  "query": { search, filter },
  "aggs": { ... }
}
```


Now:


```bash
{
  "query: {search}
  "aggs": {
    "global_aggs_filters" : {
      "filter": { filter }, <---- here goes the "query"
      "aggs": { ... }    <---- and here the "aggs"
    }
  }
}
```

