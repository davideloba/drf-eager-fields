# DRF Eager Fields

This library provides a dynamically fields selection and prefetching at the same time, in order to improve the response performance in Django REST Framework.

## Overview

This library has the primary scope to handle the eager loading while providing a dynamic, nested, run-time selection of the fields to display.
It's similiar to [drf-dynamic-fields](https://github.com/dbrgn/drf-dynamic-fields) and [drf-flex-fields](https://github.com/rsinger86/drf-flex-fields) great libraries, with the main aim of improving the poor database perfomances achieved when the fields to return are evaluted runtime and thus it's not possible to hardcode a prefetchable queryset.
It uses the capabaility of the "Prefetch" class of Django ORM to build the queryset on the fly.
> I'd liked to name this library *dfr-extra-fields* but the name had been already stolen :disappointed: :smile:

Features:
- dynamical nested fields selection
- dynamical nested fields exclusion
- optional Json to represent the wanted response structure
- works with model serializers and standard ones
- setup the response inside the view for a complete serializers reusability
- **prefetching of dynamically selected fields to decouple the number of queries from the number of rows (fix the N+1 problem)**
- custom prefetch queryset to filter the related dataset in the serializer definition

## Install
    pip install drf-eager-fields


## Quick example

Imagine that you have a customer API that returns all its orders and, inside each order, the related article. Our customer View queryset is *Customer.objects.all()*

``GET /api/customers/1``

    (number of queries: hundreds)

    "id": 1,  # unnecessary
    "name" : "Mario",
    "countries": [1],  # unnecessary
    "orders": [
        {   
            "id": 1,  # unnecessary
            "code": "DFGHJ",
            "created_at: '2020-11-29 20:04:53'
            "article": {
                "id": 1,  # unnecessary
                "code": "PIZZA"
                "customer": 1  # unnecessary
            }
        },
        {
            "id": 2,  # unnecessary
            "code": "BNMVC",
            created_at: '2020-12-01 21:12:07'
            "article": {
                ...
            }
        },
        ... many other orders (and articles) here ...
        {
            "id": 199,  # unnecessary
            "code": "QSDER",
            created_at: '2021-02-01 19:48:43'
            "article": {...}
        }
    ]

This response has two problems: unwanted fields (we don't want ids, any customer's data except for the name,) and speed, because we have camed across the N+1 problems.

### Standard solution
We can fix those issues by modifying the queryset in the view, adding all the prefetch stuff and creating another custom serializer to remove to annoing unnecessary fields. We must do this every time we want to return an even sligthly different response. In this case we want the article inside order, but in another case we just want the plain order's data without any other nested field, such as article.

### Drf-Eager-Fields

Using the *drf-eager-fields* you can achieve this result without modifying the view or the serializer.

### Default response

``GET /api/customers/1``

    "id": 1
    "name": "Mario"

### Custom response

``GET /api/customers/1?extra=orders.article,customer&fields=name,orders.created_at,orders.customer.name,orders.article.code``

    (number of queries: 3)

    "name" : "Mario",
    "orders": [
        {   
            "code": "DFGHJ",
            "created_at: '2020-11-29 20:04:53'
            "article": {
                "code": "PIZZA"
            }
        },
        {
            "code": "BNMVC",
            created_at: '2020-12-01 21:12:07'
            "article": {...}
        },
        ... other orders here ...
        {
            "code": "QSDER",
            created_at: '2021-02-01 19:48:43'
            "article": {
                ...
            }
        }
    ]

## Usage

First of all, you need to have your serializer extend the eager mixing class and, if you want to use the extra fields, you must set the `extra` class property.
> `extra` dictionary is defined as a function with the **@classproperty** decorator, to allow the import of nested serializers and avoiding the circular import issue. Until you face that problem, you can handle the `extra` property as a normal class attribute.

This is an example of the eager serializers:

    # article_serializer.py
    class ArticleSerializer(EagerFieldsMixin, serializers.ModelSerializer):

        class Meta:
            models = models.Article
            fields = ('id', 'code')
        
        @classproperty
        def extra(self):
            from .customer_serializers import CustomerSerializer
            return {
                "customer": {
                    "field": CustomerSerializer(),
                    "prefetch": True # see below
                }
            }
    
    # customer_serializer.py
    class CustomerSerializer(EagerFieldsMixin, serializers.ModelSerializer):

        class Meta:
            models = models.Customer
            fields = ('id', 'name')
        
        @classproperty
        def extra(self):
            from .countries_serializers import CountrySerializer
            return {
                "countries": {
                    "field": CountrySerializer(many=True),
                    "prefetch": True # see below
                }
            } 


``GET /api/articles/``

the standard response is, as usual:

    [
        {
            "id": 1,
            "code": "TNT"
        },
        {
            "id": 2,
            "code": "PIZZA"
        }
    ]

if you just want the article's code, you can request it explictly with the ``fields`` parameter

``GET /api/articles/?fields=code``

or excluding the id with the ``exclude`` parameter

``GET /api/articles/?exclude=id``


    [
        {
            "code": "TNT"
        },
        {
            "code": "PIZZA"
        }
    ]

If you want to add an extra fields, which is defined in the ``extra`` property, do this

``GET /api/articles/?extra=customer``


    [
        {
            "id": 1,
            "code": "TNT",
            "customer": {
                "id": 1,
                "name": "Willy"
            }
        },
        {
            "id": 2,
            "code": "PIZZA",
            "customer": {
                "id": 1,
                "name": "Mario"
            }
        }
    ]

With *dotted* notation, you can add the any nested extra fields previously defined in the serializers `extra` dict:

``GET /api/articles/?extra=customer.countries``


    [
        {
            "id": 1,
            "code": "TNT",
            "customer": {
                "id": 1,
                "name": "Willy",
                "countries": [
                    {
                        "id": 1,
                        "name": "USA"
                    }
                ]
            }
        },
        {
            "id": 2,
            "code": "PIZZA",
            "customer": {
                "id": 1,
                "name": "Mario",
                "countries": [
                    {
                        "id": 1,
                        "name": "USA"
                    },
                    {
                        "id": 2,
                        "name": "Italy"
                    },
                ]
            }
        }
    ]


> **Advice**: if you want the take the best from this library, put all your related fields inside the `extra` dictionary
and leave only the model's flat properties in the serializer.Meta 'fields' attribute. 


Of course, you can combine all the parameters to get your custom response

``GET /api/articles/?extra=customer.countries,fields=code,customer.name,customer.countries.name``



    [
        {
            "code": "TNT",
            "customer": {
                "name": "Willy",
                "countries": [
                    {
                        "name": "USA"
                    }
                ]
            }
        },
        {
            "code": "PIZZA",
            "customer": {
                "name": "Mario",
                "countries": [
                    {
                        "name": "USA"
                    },
                    {
                        "name": "Italy"
                    },
                ]
            }
        }
    ]

Once you are done with the eager serializer, make your view to extend the *EaderFieldsViewMixin* like this:

        Class ArticleView(EagerFieldsViewMixin, ListAPIView):
            queryset = Article.objects.all()  # one level queryset, no prefetching
            serializer_class = ArticleSerializer
            serializer_extra = 'customer.countries'
            serializer_fields = 'code,customer.name,customer.countries.name'
            serializer_exclude = ...

As you can see, you can set the serializer params directly from the view.
There are two ways more to do that:

- inside the request, as query params. This overrides the default parameters set in the view:

        GET /api/articles/?extra=customer,fields=code,customer.name,exclude=...

- inside the GET request, as **JSON in the body**. This JSON represent the wanted response structure and overrides other paramas set in view or in the query params string:

        {
            "fields" : {
                "code": null,
                "customer": {
                    "name": null
                }
            }
        }


## Prefetch
> With great power comes great responsibility. [Peter Parker]


The problem with the dynamic response, is how to eager loading (prefetching)
all the necessary data without leading ourself to the famous N+1 nightmare.
This library takes the capability of the Django *Prefetch* class to deal with it.
If you set the property "prefetch" in your `extra` dictionary, the queryset will be extended runtime to prefetch them.

    "countries": {
        "field": CountrySerializer(many=True),
        "prefetch": True
            # is equal to
        "prefetch": Prefetch("countries", queryset=CountrySerializer.Meta.model.objects.all())
    }

If you set the ``prefetch`` attribute in every serializer, this librarythis library will compose the prefetched queryset for you, even for the nested fields. :bomb:

> *Prefetch class* or *prefetch_related* is mandatory in Django to prefetching the related objects from the "many" side of the relationship (many-to-one and many-to-many). On the "one" side, you should use *select_related*. However I chose to use the *Prefetch class* for both, as recommended by Django documentation in cases where *you want to use a QuerySet that performs further prefetching on related models* or *you want to prefetch only a subset of the related objects.*

### One step further..
The prefetch attribute can accept a bool or a Prefetch object where you
can declare your queryset. Let me show you an example with the article API: image that you just want to show the related orders, but only the last 10 orders, and of course, prefetch them.

       @classproperty
        def extra(self):
            from .order_serializer import OrderSerializer

            return {
                "orders": {"field": OrderSerializer(many=True), "prefetch": True},
                "last_10_orders": {
                    "field": OrderSerializer(source="orders", many=True),
                    "prefetch": Prefetch(
                        "orders",
                        queryset=OrderSerializer.Meta.model.objects.filter(
                            id__in=Subquery(
                                OrderSerializer.Meta.model.objects.filter(
                                    article_id=OuterRef("article_id")
                                )
                                .order_by("-created_at")
                                .values_list("id", flat=True)[:10]
                            )
                        ).order_by("-created_at"),
                    ),
                },
            }

Now, if you call


``GET /api/articles/?extra=last_10_orders``

you will get only the last 10 prefetch orders, ordered by the date. :bomb: :bomb:
> Sorry for the complex queryset but, as far as I know, in Django you cannot limit the queryset directly if you want to keep it as queryset for further extension, so you have to nest a subquery to get the latest ids.

## Example and testing
You can run an example Django DRF application inside ``example`` folder

    $ python manage.py runserver 0.0.0.0:8000

In that folder, to run the tests

    $ python manage.py test

## Credits
- [drf-dynamic-fields](https://github.com/dbrgn/drf-dynamic-fields)
- [drf-flex-fields](https://github.com/rsinger86/drf-flex-fields)


## License

MIT license, see ``LICENSE`` file.
