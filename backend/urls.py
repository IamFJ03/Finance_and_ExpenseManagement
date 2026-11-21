from django.urls import path,include
from .views import CategoryViewSet, TransactionViewSet, BudgetViewSet, SavingGoalViewSet
from rest_framework.routers import DefaultRouter

router  = DefaultRouter()

router.register('categories', CategoryViewSet, basename='category')
router.register('transactions', TransactionViewSet, basename='transaction')
router.register('budgets', BudgetViewSet, basename="budget")
router.register('saving-goals', SavingGoalViewSet, basename="saving-goal")

urlpatterns = [
    path('api/', include(router.urls)),
]