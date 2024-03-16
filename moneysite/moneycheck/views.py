from itertools import groupby
from django.db.models.functions import Coalesce, TruncMonth, ExtractMonth
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.db.models import Sum, Count
from django.http import HttpResponse
import locale

from datetime import datetime

from .forms import *
from .models import Category, Spending

current_month = datetime.now().month # для того, чтобы изначально выводилась статистика по текущему месяцу
menu = [
    {'title': 'Расходы', 'url_name': 'index', 'slug': 'spending'},
    {'title': 'Доходы', 'url_name': 'index', 'slug': 'profit'},
    {'title': 'Статистика', 'url_name': 'statistic', 'slug1': 'spending', 'slug2': current_month},
]
def index(request, operation):
    if operation == 'spending':
        is_profit = False
        title = 'расходы'
    elif operation == 'profit':
        is_profit = True
        title = 'доходы'

    categories = Category.objects.filter(is_profit=is_profit).annotate(total_spending=Sum('spending__sum'))
    total = Spending.objects.filter(kod_cat__is_profit=is_profit).aggregate(total_sum=Sum('sum'))['total_sum']
    context = {
        'categories': categories,
        'menu': menu,
        'total': total,
        'operation': operation,
        'title': title,
    }

    return render(request, "moneycheck/index.html", context=context)

def statistic(request, operation, month):
    if operation == 'spending':
        is_profit = False

    elif operation == 'profit':
        is_profit = True

    all_operation = Spending.objects.filter(kod_cat__is_profit=is_profit).filter(date__month=month).order_by('-date')

    grouped_operation = {}
    for day, day_operation in groupby(all_operation, key=lambda x: x.date.strftime('%d %B')):
        grouped_operation[day] = list(day_operation)

    operations_for_month = Spending.objects.filter(kod_cat__is_profit=is_profit)

    unique_months = operations_for_month.annotate(month=ExtractMonth('date')).values_list('month', flat=True).distinct()
    months = [m for m in unique_months if m != None and m != month] # получаем все месяцы

    context = {
        'menu': menu,
        'grouped_operation': grouped_operation,
        'operation': operation,
        'month': current_month,
        'title': 'Статистика',
        'months': months,
    }

    return render(request, "moneycheck/statistic.html", context=context)
def add(request, cat_id):
    if request.method == 'POST':
        form = AddMoneyForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            category = Category.objects.get(pk=cat_id)
            data['kod_cat'] = category
            # print(form.cleaned_data)
            Spending.objects.create(**data)
            if category.is_profit:
                redirect_url = reverse('index', kwargs={'operation': 'profit'})
            elif not category.is_profit:
                redirect_url = reverse('index', kwargs={'operation': 'spending'})
            return redirect(redirect_url)
    form = AddMoneyForm()
    category = Category.objects.get(pk=cat_id)

    context = {
        'title': 'Занесите расходы',
        'category': category,
        'form': form
    }
    return render(request, "moneycheck/form.html", context=context)

def addcat(request, operation):
    if operation == 'spending':
        if request.POST:
            form = AddSpendingCatForm(request.POST)
            if form.is_valid():
                form.save()
                redirect_url = reverse('index', kwargs={'operation': 'spending'})
                return redirect(redirect_url)
        else:
            form = AddSpendingCatForm
    elif operation == 'profit':
        if request.POST:
            form = AddProfitCatForm(request.POST)
            if form.is_valid():
                form.save()
                redirect_url = reverse('index', kwargs={'operation': 'profit'})
                return redirect(redirect_url)
        else:
            form = AddProfitCatForm

    context = {
        'title': 'Добавьте категорию',
        'form': form,
    }

    return render(request, "moneycheck/form.html", context=context)


def deletecat(request, cat_id):
    category = get_object_or_404(Category, pk=cat_id)
    category.delete() # Удаляем объект из базы данных
    if category.is_profit == False:
        redirect_url = reverse('index', kwargs={'operation': 'spending'})
    else:
        redirect_url = reverse('index', kwargs={'operation': 'profit'})

    return redirect(redirect_url)

def delete(request, id):
    money = get_object_or_404(Spending, pk=id)
    money.delete()
    print(money.date.month)
    month = money.date.month
    if money.kod_cat.is_profit == False:
        redirect_url = reverse('statistic', kwargs={'operation': 'spending', 'month': month})
        return redirect(redirect_url)
    elif money.kod_cat.is_profit == True:
        redirect_url = reverse('statistic', kwargs={'operation': 'profit', 'month': month})
        return redirect(redirect_url)


def plancat(request, cat_id):
    if request.method == 'POST':
        form = PlanCatForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            category = Category.objects.get(pk=cat_id)
            total = Spending.objects.filter(kod_cat=cat_id).aggregate(total_sum=Sum('sum'))['total_sum']
            print(data['plan_sum'], type(data['plan_sum']))
            if total == None:
                precent = 0
            else:
                precent = total / data['plan_sum'] * 100

            data['precent'] = precent
            plan = Plan.objects.create(**data)
            category.plan = plan
            category.save()
            if category.is_profit:
                redirect_url = reverse('index', kwargs={'operation': 'profit'})
            elif not category.is_profit:
                redirect_url = reverse('index', kwargs={'operation': 'spending'})
            return redirect(redirect_url)
    form = PlanCatForm()

    context = {
        'title': 'Назначьте план',
        'form': form
    }
    return render(request, "moneycheck/form.html", context=context)