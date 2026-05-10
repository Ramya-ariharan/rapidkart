from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics


from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer

)

import random

from .models import DeliveryOTP,User

# Create your views here.


class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({

            'refresh': str(refresh),

            'access': str(refresh.access_token),

            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role
            }
        })



class SendOTPView(generics.GenericAPIView):

    serializer_class = SendOTPSerializer

    def post(self, request):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        phone = serializer.validated_data['phone']

        otp = str(
            random.randint(100000, 999999)
        )

        DeliveryOTP.objects.create(
            phone=phone,
            otp=otp
        )

        return Response({

            'message': 'OTP sent successfully',

            'otp': otp
        })

class VerifyOTPView(generics.GenericAPIView):

    serializer_class = VerifyOTPSerializer

    def post(self, request):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        phone = serializer.validated_data['phone']

        otp = serializer.validated_data['otp']

        otp_obj = DeliveryOTP.objects.filter(
            phone=phone,
            otp=otp,
            is_verified=False
        ).last()

        if not otp_obj:

            return Response({

                'error': 'Invalid OTP'

            }, status=400)

        if otp_obj.is_expired():

            return Response({

                'error': 'OTP expired'

            }, status=400)

        otp_obj.is_verified = True
        otp_obj.save()

        user = User.objects.get(
            phone=phone
        )

        refresh = RefreshToken.for_user(user)

        return Response({

            'message': 'Login successful',

            'refresh': str(refresh),

            'access': str(refresh.access_token),

            'user': {

                'id': user.id,

                'phone': user.phone,

                'role': user.role
            }
        })