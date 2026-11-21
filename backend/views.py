from django.shortcuts import render
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Category, Transaction, Budget
from .serializers import CategorySerializer, TransactionSerializer, BudgetSerializer

# Create your views here.

@api_view(['POST'])
def register(request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response(
                {"message":"All Fields are Required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"message": "User Already Exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        User.objects.create_user(
            username = request.data.get("username"),
            email = request.data.get("email"),
            password = request.data.get("password")
        )

        return Response(
            {"message": "User Registered Successfully"},
            status=status.HTTP_201_CREATED
        )

@api_view(['POST'])
def login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(
        username=username,
        password=password
    )

    if user is not None:

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Login Successfull",
                "refresh": str(refresh),
                "access": str(refresh.access_token)
             },
            status=status.HTTP_200_OK
        )

    return Response(
        {"message": "Invalid Username or Password"},
        status=status.HTTP_401_UNAUTHORIZED
    )

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user = self.request.user).select_related('category')

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user = self.request.user)

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)