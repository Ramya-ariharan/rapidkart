from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User

        fields = [
            'id',
            'email',
            'phone',
            'password',
            'role'
        ]

    def create(self, validated_data):

        password = validated_data.pop('password')

        user = User(**validated_data)

        user.set_password(password)

        user.save()

        return user




class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField()

    def validate(self, data):

        user = authenticate(
            email=data['email'],
            password=data['password']
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials"
            )

        data['user'] = user

        return data
    
class SendOTPSerializer(serializers.Serializer):

    phone = serializers.CharField(
        max_length=15
    )

    def validate_phone(self, value):

        user = User.objects.filter(
            phone=value,
            role='delivery_partner'
        ).first()

        if not user:

            raise serializers.ValidationError(
                "Delivery partner not found"
            )

        return value
    

class VerifyOTPSerializer(serializers.Serializer):

    phone = serializers.CharField(
        max_length=15
    )

    otp = serializers.CharField(
        max_length=6
    )