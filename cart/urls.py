from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    RemoveCartItemView
)

urlpatterns = [

    path(
        '',
        CartView.as_view()
    ),

    path(
        'add/',
        AddToCartView.as_view()
    ),

    path(
        'remove/',
        RemoveCartItemView.as_view()
    ),
]