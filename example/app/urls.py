from django.urls import path

from . import views


urlpatterns = [
    path("articles/", views.ArticleList.as_view(), name="articles-list"),
    path("articles/<int:pk>/", views.ArticleDetail.as_view(), name="article-detail"),
    path("lazy/articles/", views.LazyArticleList.as_view(), name="lazy-articles-list"),
    path("customers/", views.CustomerList.as_view(), name="customers-list"),
    path("customers/<int:pk>/", views.CustomerDetail.as_view(), name="customer-detail"),
    path(
        "lazy/customers/<int:pk>/",
        views.LazyCustomerDetail.as_view(),
        name="lazy-customer-deail",
    ),
]
