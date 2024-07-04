from rest_framework import status
from rest_framework.response import Response
from .serializers import UserSerializer, UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from .serializers import AddUserDetailSerializer, EmployeeDetailSerializer
from .models import UserDetail
from rest_framework.parsers import MultiPartParser

User = get_user_model()


class SignupView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, format=None):
        if request.user.role == 'ADMIN':
            serializer = UserCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            # Serialize the user object
            user_detail = UserDetail.objects.get(user=user)
            user_serializer = EmployeeDetailSerializer(user_detail)
            # Return the serialized user data along with the token
            return Response({'token': token.key, 'user': user_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'}, status=200)

class AddUserDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, email):
        if request.user.role == 'ADMIN':
            serializer = AddUserDetailSerializer(data=request.data)
            user = User.objects.get(email=email)
            print(request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
        
class UserDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'ADMIN':
            employees = UserDetail.objects.exclude(user__role='ADMIN')
            serializer = EmployeeDetailSerializer(employees, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)