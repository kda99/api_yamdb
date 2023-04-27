from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginAPISerializer


class LoginAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = LoginAPISerializer(data = data)
            if serializer.is_valid():
                email = serializer.data['email']
                password = serializer.data['password']
                user = authenticate(email=email, password=password)
                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    return {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
            return Response(
                'status': 400,
                'message': "Invalid password",
                'data': {},
            )