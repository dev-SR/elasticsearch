import json
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


def bulk_indexing(create_index=False):
    if create_index:
        ProductDocument.init()
        print('Index created')

    with open('product\data.json', 'r') as file:
        data = json.load(file)

    for product in data:
        # print(product)
        prod = ProductDocument(
            title=product['title'],
            description=product['description'],
            price=product['price'],
            category=product['category'],
            brand=product['brand'],
            quantity=product['quantity'],
            filters=[Filter(name=filter['name'], value=filter['value']) for filter in product['filters']]
        )
        prod.save(using=es)
    print('Bulk indexing done')
