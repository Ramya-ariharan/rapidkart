from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import UserEvent
from .serializers import UserEventSerializer

class TrackEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserEventSerializer(data=request.data)

        if serializer.is_valid():
            UserEvent.objects.create(
                user=request.user,
                **serializer.validated_data
            )
            return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)