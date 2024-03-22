from collections import defaultdict
from itertools import groupby
from django.db.models.functions import Coalesce, TruncMonth, ExtractMonth, ExtractYear
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.db.models import Sum, Count
from django.http import HttpResponse
import locale

from datetime import datetime

from .forms import *
from .models import Category, Operation

current_month = datetime.now().month # для того, чтобы изначально выводилась статистика по текущему месяцу
current_year = datetime.now().year
menu = [
    {'title': 'Расходы', 'url_name': 'index', 'slug': 'spending'},
    {'title': 'Доходы', 'url_name': 'index', 'slug': 'profit'},
    {'title': 'Статистика', 'url_name': 'statistic', 'operation': 'spending', 'year': current_year, 'month': current_month},
    {'title': 'Профиль', 'url_name': 'users:profile'},
    {'title': 'Выйти', 'url_name': 'users:logout'},
]
def index(request, operation):
    if operation == 'spending':
        is_profit = False
        title = 'расходы'
    elif operation == 'profit':
        is_profit = True
        title = 'доходы'

    categories = Category.objects.filter(is_profit=is_profit).filter(user=request.user).annotate(total_operation=Sum('operation__sum'))
    total = Operation.objects.filter(kod_cat__is_profit=is_profit).filter(kod_cat__user=request.user).aggregate(total_sum=Sum('sum'))['total_sum']
    if total == None:
        total = 0.0

    for c in categories:
        if c.plan != None:
            if c.total_operation != None:
                c.plan.precent = c.total_operation / c.plan.plan_sum * 100
                c.save()
    context = {
        'categories': categories,
        'menu': menu,
        'total': total,
        'operation': operation,
        'title': title,
    }

    return render(request, "moneycheck/index.html", context=context)

def statistic(request, operation, year, month):
    if operation == 'spending':
        is_profit = False

    elif operation == 'profit':
        is_profit = True

    all_operation = Operation.objects.filter(kod_cat__is_profit=is_profit).filter(kod_cat__user=request.user).filter(date__month=month).filter(date__year=year).order_by('-date')
    total = all_operation.aggregate(total_sum=Sum('sum'))['total_sum']
    if total == None:
        total = 0.0
    grouped_operation = {}
    for day, day_operation in groupby(all_operation, key=lambda x: x.date.strftime('%d %B')):
        grouped_operation[day] = list(day_operation)

    operations_for_month = Operation.objects.filter(kod_cat__is_profit=is_profit).filter(kod_cat__user=request.user)

    unique_years = operations_for_month.annotate(year=ExtractYear('date')).values_list('year', flat=True).distinct()

    # Создаем словарь, в котором ключами будут годы, а значениями - списки месяцев для каждого года
    months_by_year = defaultdict(list)

    # Извлекаем уникальные месяцы для каждого года и добавляем их в соответствующий список месяцев
    for year in unique_years:
        unique_months_for_year = operations_for_month.filter(date__year=year).annotate(
            month=ExtractMonth('date')).values_list('month', flat=True).distinct()
        months_by_year[year] = sorted(unique_months_for_year, reverse=True)

    # Теперь отсортируем словарь по ключам (годам) в порядке убывания
    sorted_months_by_year = dict(sorted(months_by_year.items(), reverse=True))

    # Выведем словарь, где ключи это года, а значения это списки уникальных месяцев для каждого года
    print(sorted_months_by_year)

    context = {
        'menu': menu,
        'grouped_operation': grouped_operation,
        'operation': operation,
        'month': month,
        'year': year,
        'title': 'Статистика',
        # 'months': months,
        'months_year': sorted_months_by_year,
        'total': total,
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
            Operation.objects.create(**data)
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
            form = AddOperationCatForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = request.user
                print(request.user)
                instance.save()
                redirect_url = reverse('index', kwargs={'operation': 'spending'})
                return redirect(redirect_url)
        else:
            form = AddOperationCatForm
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
    money = get_object_or_404(Operation, pk=id)
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
            total = Operation.objects.filter(kod_cat=cat_id).aggregate(total_sum=Sum('sum'))['total_sum']
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