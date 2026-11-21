from django.urls import path,include
from .views import CategoryViewSet, TransactionViewSet, BudgetViewSet
from rest_framework.routers import DefaultRouter

router  = DefaultRouter()

router.register('categories', CategoryViewSet, basename='category')
router.register('transactions', TransactionViewSet, basename='transaction')
router.register('budgets', BudgetViewSet, basename="budget")

urlpatterns = [
    path('api/', include(router.urls)),
]