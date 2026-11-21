from rest_framework import serializers
from .models import Category, Transaction, Budget, SavingGoal

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'category',
            'transaction_types',
            'payment_method',
            'amount',
            'description',
            'transaction_date',
            'created_at'
        ]

        read_only_fields = ['id', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Amount must be greater then 0"
            )

        return value

    def validate_category(self, value):

        request = self.context.get('request')

        if value.user!=request.user:
            raise serializers.ValidationError(
                "You cannot use another user's category"
            )

        return value

    def validate(self, attrs):
        category = attrs.get(
            'category',
            self.instance.category if self.instance else None
        )

        transaction_types = attrs.get(
            'transaction_types',
            self.instance.transaction_types if self.instance else None
        )

        if category and transaction_types:
            if category.category_type != transaction_types:
                raise serializers.ValidationError({
                    "category": "Category type must match transaction type."
                })

        return attrs

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'category', 'amount', 'month', 'created_at']
        read_only_fields = ['id','user', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater then 0")

        return value

    def validate_category(self, value):

        request = self.context.get('request')

        if value.user != request.user:
            raise serializers.ValidationError("You cannot use another user's category")

        return value

    def validate(self, value):
        category = value.get(
            'category',
            self.instance.category if self.instance else None
        )

        if category:
            if category.category_type != "expense":
                raise serializers.ValidationError(
                    {"category": "Must be of expense"}
                )

        return value

class SavingGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingGoal
        fields = ['id', 'user', 'name', 'target_amount', 'saved_amount', 'target_date', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Target amount cannot be 0 or less then 0")

        return value

    def validate_saved_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Saved amount cannot be below 0")

        return value

    def validate(self, attrs):
        saved_amount = attrs.get(
            'saved_amount',
            self.instance.saved_amount if self.instance else 0
        )

        target_amount = attrs.get(
            'target_amount',
            self.instance.target_amount if self.instance else None
        )

        if target_amount is not None and target_amount < saved_amount:
            raise serializers.ValidationError(
                {"saved_amount": "Saved Amount cannot exceed target amount"}
            )

        return attrs