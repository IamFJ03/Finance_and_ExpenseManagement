from django.urls import path,include
from .views import CategoryViewSet, TransactionViewSet
from rest_framework.routers import DefaultRouter

router  = DefaultRouter()

router.register('categories', CategoryViewSet, basename='category')
router.register('transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('api/', include(router.urls)),
]