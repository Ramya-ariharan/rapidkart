from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer


class CartView(generics.RetrieveAPIView):

    serializer_class = CartSerializer

    def get_object(self):

        cart, created = Cart.objects.get_or_create(
            user=self.request.user
        )

        return cart
    
    
class AddToCartView(generics.CreateAPIView):

    def post(self, request):

        user = request.user

        product_id = request.data.get('product_id')

        quantity = int(request.data.get('quantity', 1))

        cart, _ = Cart.objects.get_or_create(
            user=user
        )

        product = Product.objects.get(
            id=product_id
        )

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:

            item.quantity += quantity

        else:

            item.quantity = quantity

        item.save()

        return Response({
            "message": "Added to cart successfully"
        })


class RemoveCartItemView(generics.DestroyAPIView):

    def post(self, request):

        item_id = request.data.get('item_id')

        CartItem.objects.filter(
            id=item_id
        ).delete()

        return Response({
            "message": "Item removed"
        })