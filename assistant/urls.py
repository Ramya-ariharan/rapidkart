from django.urls import path

from .views import (
    ShoppingAssistantView
)


urlpatterns = [

    path(
        'shopping-assistant/',
        ShoppingAssistantView.as_view()
    )
]