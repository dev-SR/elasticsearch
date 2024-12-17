from django.http import JsonResponse
from django.conf import settings
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch
from rest_framework import status
from rest_framework import viewsets
from .models import Product, Category, Brand, Attribute, AttributeValue
from .serializers import ProductSerializer, CategorySerializer, BrandSerializer, AttributeSerializer, AttributeValueSerializer
from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework import serializers
from .search import ProductDocument, es
import json


class FiltersSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=255)


class CustomProductSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    category = serializers.CharField(max_length=255)
    brand = serializers.CharField(max_length=255)
    filters = FiltersSerializer(many=True)


# class CustomView(APIView):
#     def get(self, request):
#         # Get the main search query
#         search_term = request.GET.get('q', '')

#         # Extract all query parameters excluding 'q'
#         query_params = request.GET.copy()
#         query_params.pop('q', None)

#         # Extract specific filters for category and brand
#         category_filter = query_params.pop('category', None)
#         brand_filter = query_params.pop('brand', None)

#         # Build the multi_match query if search_term is provided
#         search_queries = []
#         if search_term:
#             search_queries.append(
#                 {
#                     "multi_match": {
#                         "query": search_term,
#                         "fields": [
#                             "title",
#                             "description",
#                             "all_filters"
#                         ],
#                         "type": "phrase_prefix"
#                     }
#                 }
#             )

#         # Build dynamic nested filters
#         filter_options = []
#         for filter_name, filter_values in query_params.lists():
#             nested_filter = {
#                 "nested": {
#                     "path": "filters",
#                     "query": {
#                         "bool": {
#                             "must": [
#                                 {
#                                     "term": {
#                                         "filters.name": filter_name
#                                     }
#                                 }
#                             ],
#                             "should": [
#                                 {
#                                     "term": {
#                                         "filters.value": value
#                                     }
#                                 } for value in filter_values
#                             ],
#                             "minimum_should_match": 1
#                         }
#                     }
#                 }
#             }
#             filter_options.append(nested_filter)

#         # Add category filter if present
#         if category_filter:
#             category_filter_clause = {
#                 "term": {
#                     "category": category_filter[0] if len(category_filter) == 1 else category_filter
#                 }
#             }
#             filter_options.append(category_filter_clause)

#         # Add brand filter if present
#         if brand_filter:
#             brand_filter_clause = {
#                 "term": {
#                     "brand": brand_filter[0] if len(brand_filter) == 1 else brand_filter
#                 }
#             }
#             filter_options.append(brand_filter_clause)

#         # Build the bool query dynamically
#         bool_query = {}
#         if search_queries:
#             bool_query["must"] = search_queries
#         if filter_options:
#             bool_query["filter"] = filter_options

#         # Build the facets aggregation
#         facets_agg = {
#             "facets": {
#                 "nested": {
#                     "path": "filters"
#                 },
#                 "aggs": {
#                     "names": {
#                         "terms": {
#                             "field": "filters.name"
#                         },
#                         "aggs": {
#                             "values": {
#                                 "terms": {
#                                     "field": "filters.value"
#                                 }
#                             }
#                         }
#                     }
#                 }
#             }
#         }

#         # Construct the Elasticsearch query body
#         body = {
#             "size": 2,  # Adjust the size as needed
#             "query": {
#                 "bool": bool_query
#             },
#             "aggs": facets_agg
#         }

#         # Execute the search
#         print(body)
#         response = es.search(index="product", body=body)
#         return Response(response)

class CustomView(APIView):
    def get(self, request):
        # Get the main search query
        search_term = request.GET.get('q', '')

        # Extract all query parameters excluding 'q'
        query_params = request.GET.copy()
        query_params.pop('q', None)
        # check if the query_params is empty
        if not query_params:
            print("query_params is empty")

        # Extract specific filters for category and brand
        category_filter = query_params.pop('category', None)
        brand_filter = query_params.pop('brand', None)

        # Build the multi_match query if search_term is provided
        search_queries = None
        if search_term:
            search_queries = [(
                {
                    "multi_match": {
                        "query": search_term,
                        "fields": [
                            "title",
                            "description",
                            "all_filters"
                        ],
                        "type": "phrase_prefix"
                    }
                }
            )]

        # Build dynamic nested filters
        nested_filter_options = []

        for filter_name, filter_values in query_params.lists():
            nested_filter = {
                "nested": {
                    "path": "filters",
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "term": {
                                        "filters.name": filter_name
                                    }
                                }
                            ],
                            "should": [
                                {
                                    "term": {
                                        "filters.value": value
                                    }
                                } for value in filter_values
                            ],
                            "minimum_should_match": 1
                        }
                    }
                }
            }
            nested_filter_options.append(nested_filter)

        # Add category filter if present
        if category_filter:
            category_filter_clause = {
                "term": {
                    "category": category_filter[0] if len(category_filter) == 1 else category_filter
                }
            }
            nested_filter_options.append(category_filter_clause)

        # Add brand filter if present
        if brand_filter:
            brand_filter_clause = {
                "term": {
                    "brand": brand_filter[0] if len(brand_filter) == 1 else brand_filter
                }
            }
            nested_filter_options.append(brand_filter_clause)

        # Build the facets aggregation
        facets_agg = {
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

        # Construct the Elasticsearch query body
        body = {
            "size": 2,  # Adjust the size as needed
        }
        if search_queries:
            body["query"] = {
                "bool": {
                    "must": search_queries
                }
            }
        if nested_filter_options:
            body["post_filter"] = {
                "bool": {
                    "filter": nested_filter_options
                }
            }

            body["aggs"] = {
                "aggs_all_filters": {
                    "filter": {
                        "bool": {
                            "filter": nested_filter_options
                        }
                    },
                    "aggs": facets_agg
                }
            }
            if len(list(query_params.lists())) > 1:
                for filter_name, filter_values in query_params.lists():
                    nested_other_filter_options = []
                    for filter_name_others, filter_values in query_params.lists():
                        if filter_name != filter_name_others:
                            nested_filter = {
                                "nested": {
                                    "path": "filters",
                                    "query": {
                                        "bool": {
                                            "must": [
                                                {
                                                    "term": {
                                                        "filters.name": filter_name_others
                                                    }
                                                }
                                            ],
                                            "should": [
                                                {
                                                    "term": {
                                                        "filters.value": value
                                                    }
                                                } for value in filter_values
                                            ],
                                            "minimum_should_match": 1
                                        }
                                    }
                                }
                            }
                            nested_other_filter_options.append(nested_filter)

                    key = f"aggs_{filter_name}"
                    body["aggs"][key] = {
                        "filter": {
                            "bool": {
                                "filter": nested_other_filter_options
                            }
                        },
                        "aggs": {
                            "facets": {
                                "nested": {
                                    "path": "filters"
                                },
                                "aggs": {
                                    "agg_special": {
                                        "filter": {
                                            "match": {
                                                "filters.name": filter_name
                                            }
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
                        }
                    }

        # Execute the search
        print(body)
        response = es.search(index="product", body=body)
        return Response(response)

    def post(self, request):
        # print(request.data)
        serializer = CustomProductSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            prod = ProductDocument(
                title=validated_data['title'],
                description=validated_data['description'],
                price=validated_data['price'],
                category=validated_data['category'],
                brand=validated_data['brand'],
                quantity=validated_data['quantity'],
                filters=[{
                    'name': filter['name'],
                    'value': filter['value']
                } for filter in validated_data['filters']]
            )
            r = prod.save()
            return Response({"result": f"{r}"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer


class AttributeValueViewSet(viewsets.ModelViewSet):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
