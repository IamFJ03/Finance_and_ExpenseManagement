from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum, Count, Q, DecimalField, Value
from django.db.models.functions import TruncMonth, Coalesce
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import Category, Transaction, Budget, SavingGoal
from rest_framework.exceptions import ValidationError
from django.utils.dateparse import parse_date
from .serializers import CategorySerializer, TransactionSerializer, BudgetSerializer, SavingGoalSerializer

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

class SavingGoalViewSet(viewsets.ModelViewSet):
    serializer_class = SavingGoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavingGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)

class FinancialSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_transaction = Transaction.objects.filter(
            user = request.user
        )

        total_income = user_transaction.filter(
            transaction_types = 'income'
        ).aggregate(total = Sum('amount'))['total'] or 0

        total_expense = user_transaction.filter(
            transaction_types = 'expense'
        ).aggregate(total = Sum('amount'))['total'] or 0

        balance = total_income - total_expense

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance
        })

class MonthlySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        monthly_data = Transaction.objects.filter(
            user = request.user
        ).annotate(
            month = TruncMonth('transaction_date')
        ).values(
            'month',
            'transaction_types'
        ).annotate(
            total = Sum('amount')
        ).order_by('month')

        return Response(monthly_data)

class CategorySummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        category = Transaction.objects.filter(
            user = request.user,
            transaction_types = 'expense'
        ).values(
            'category__name'
        ).annotate(
            total_expense = Sum('amount')
        ).order_by(
            '-total_expense'
        )

        return Response(category)

class BudgetComparisonView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')

        if not month:
            raise ValidationError({
                'month': 'Please provide month in YYYY-MM-DD format.'
            })

        selected_month = parse_date(month)

        if not selected_month or selected_month.day !=1:
            raise ValidationError({
                'month': 'Enter a valid month using YYYY-MM-01 format.'
            })

        budget_data = Budget.objects.filter(
            user = request.user,
            month = selected_month
        ).annotate(
            actual_spending = Coalesce(
                Sum(
                    'category__transactions__amount',
                    filter = Q(
                        category__transactions__user=request.user,
                        category__transactions__transaction_types='expense',
                        category__transactions__transaction_date__year=selected_month.year,
                        category__transactions__transaction_date__month=selected_month.month
                    )
                ),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )

        result = []

        for budget in budget_data:

            remaining_budget = budget.amount - budget.actual_spending
            result.append({
                'category': budget.category.name,
                'budget_amount': budget.amount,
                'actual_spending': budget.actual_spending,
                'remaining_budget': remaining_budget,
                'exceeded': budget.actual_spending > budget.amount
            })

        return Response(result)
