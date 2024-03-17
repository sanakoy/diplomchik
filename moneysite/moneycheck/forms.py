from django import forms
from .models import *

class AddMoneyForm(forms.Form):
    sum = forms.FloatField(label='Сумма')
    comment = forms.CharField(max_length=255, label='Комментарий', required=False)

class AddOperationCatForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Название'}

class AddProfitCatForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {'name': 'Название'}

    def __init__(self, *args, **kwargs):
        super(AddProfitCatForm, self).__init__(*args, **kwargs)
        # Устанавливаем значение по умолчанию для поля is_profit
        self.instance.is_profit = True

class PlanCatForm(forms.Form):
    plan_sum = forms.FloatField(label='Сумма')