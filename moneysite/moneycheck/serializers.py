from django.db.models import Sum
from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    precent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'cat_sum',  'is_profit', 'precent', 'user_id', 'plan_id']

    def get_precent(self, obj):
        # Получаем объект Plan, связанный с категорией
        plan = obj.plan
        # Возвращаем сумму плана, если он существует
        if plan:
            return plan.precent
        else:
            return None

    @classmethod
    def setup_eager_loading(cls, queryset):
        # Получаем общую сумму cat_sum для всех категорий
        total_sum = queryset.aggregate(total_sum=Sum('cat_sum'))['total_sum']
        # Создаем список, где первый элемент - словарь с общей суммой
        result = [{"total_sum": total_sum}]
        # Добавляем категории в список
        result += list(queryset.values())
        return result

class CategorySerializer1(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    cat_sum = serializers.FloatField(default=0)
    parent = serializers.IntegerField(default=None)
    is_profit = serializers.BooleanField(default=False)
    image_url = serializers.URLField(default=None)
    plan_id = serializers.IntegerField(default=None)  # plan_id вместо plan
    user_id = serializers.IntegerField()



