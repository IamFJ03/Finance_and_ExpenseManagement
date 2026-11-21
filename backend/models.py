from django.db import models
from django.conf import settings
# Create your models here.

class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ("expense", "Expense")
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    name = models.CharField(max_length=100)

    category_type = models.CharField(max_length=100, choices=CATEGORY_TYPES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
            ('income', 'Income'),
            ("expense", "Expense")
        ]

    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('upi', 'Upi'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='transactions'
    )

    transaction_types = models.CharField(
        max_length=100,
        choices=TRANSACTION_TYPES
    )

    payment_method = models.CharField(
        max_length=100,
        choices=PAYMENT_METHODS
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    description = models.TextField(blank=True)

    transaction_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_types} - {self.amount}"