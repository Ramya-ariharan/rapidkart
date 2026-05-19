from rest_framework import serializers
from .models import UserEvent

class UserEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvent
        fields = ['event_type', 'product', 'search_query', 'metadata']

    def validate(self, data):
        # search events must have a query
        if data['event_type'] == 'search' and not data.get('search_query'):
            raise serializers.ValidationError("search_query is required for search events")

        # non-search events must have a product
        if data['event_type'] != 'search' and not data.get('product'):
            raise serializers.ValidationError("product is required for view/click/purchase events")

        return data