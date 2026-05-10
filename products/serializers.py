from rest_framework import serializers

from .models import (
    Category,
    Product,
    ProductImage
)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:

        model = Category

        fields = '__all__'


class ProductImageSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = ProductImage

        fields = [
            'id',
            'image'
        ]

class ProductSerializer(
    serializers.ModelSerializer
):

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    class Meta:

        model = Product

        fields = [
            'id',
            'category',
            'category_name',
            'name',
            'description',
            'price',
            'is_available',
            'images'
        ]
