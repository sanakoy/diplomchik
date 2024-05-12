from collections import defaultdict
from itertools import groupby

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import Coalesce, TruncMonth, ExtractMonth, ExtractYear
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.db.models import Sum, Count
from django.http import HttpResponse, JsonResponse
import locale
from django.views.decorators.csrf import csrf_exempt


from datetime import datetime

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import *
from .models import Category, Operation
from .serializers import CategorySerializer, CategorySerializer1

current_month = datetime.now().month # для того, чтобы изначально выводилась статистика по текущему месяцу
current_year = datetime.now().year
# menu = {
#     'menus': [
#         {'title': 'Расходы', 'url_name': 'index', 'slug': 'spending'},
#         {'title': 'Доходы', 'url_name': 'index', 'slug': 'profit'},
#         {'title': 'Статистика', 'url_name': 'statistic', 'operation': 'spending', 'year': current_year, 'month': current_month},
#         {'title': 'Профиль', 'url_name': 'users:profile'},
#         {'title': 'Выйти', 'url_name': 'users:logout'},
#     ]
# }

menu =  [
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
    print('menu', menu)
    print('grouped_operation', grouped_operation)
    print('operation', operation)
    print('month', month)
    print('year', year)
    print('months_year', sorted_months_by_year)
    print('total', total)

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
        if form.is_valimd():
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


def spending(request):
    cats = Category.objects.filter(user=request.user, is_profit=True)
    for cat in cats:
        if cat.date_upd_cat_sum:
            if cat.date_upd_cat_sum.month != current_month:
                cat.cat_sum = 0 #обнуление суммы с нового месяца
                cat.date_upd_cat_sum = datetime.now()
                cat.plan = None
                cat.save()
        else:
            print("Дата обновления не установлена для категории с id:", cat.id)


    return render(request, "moneycheck/operation.html", {'menu': menu, 'current_url': request.build_absolute_uri})


def upd_cat_sum(id):
    cat = Category.objects.get(pk=id)
    total = Operation.objects.filter(kod_cat=cat) \
        .filter(date__month=current_month) \
        .filter(date__year=current_year) \
        .aggregate(total_sum=Sum('sum'))['total_sum']
    cat.cat_sum = total if total != None else 0
    cat.date_upd_cat_sum = datetime.now()
    cat.save()




# class CategoryAPIView(generics.ListAPIView):
#     serializer_class = CategorySerializer
#
#     def get_queryset(self):
#         # Получаем текущего пользователя
#         user = self.request.user
#         # Фильтруем категории по пользователю
#         # queryset = Category.objects.filter(user=user).annotate(total_operation=Sum('operation__sum'))
#         queryset = Category.objects.filter(user=user)
#         return queryset


class CategoryAPIView(APIView):
    def get(self, request):
        current_url = request.build_absolute_uri()
        print(current_url)
        if current_url == "http://127.0.0.1:8000/api/category/spending/":
            is_profit = False
            operation = "spending"
        else:
            is_profit = True
            operation = "profit"
        data = []
        all_operation = Operation.objects.filter(kod_cat__is_profit=is_profit).filter(
            kod_cat__user=request.user).filter(date__month=current_month).filter(date__year=current_year).order_by('-date')

        cats_sum = {}
        for i in all_operation:
            if i.kod_cat.name not in cats_sum.items():
                cats_sum[i.kod_cat.name] = all_operation.filter(kod_cat=i.kod_cat).aggregate(total_sum=Sum('sum'))['total_sum']

        print("cats: ", cats_sum)
        total = all_operation.aggregate(total_sum=Sum('sum'))['total_sum']
        if total == None:
            total = 0.0

        categories = Category.objects.filter(user=request.user, is_profit=is_profit)
        for category in categories:
            serializer_data = CategorySerializer1(category).data

                # Получаем связанный объект Plan и его precent
            plan = category.plan

            # Если план существует, получаем precent, иначе присваиваем None
            plan_precent = plan.precent if plan else None
            plan_sum = plan.plan_sum if plan else None

                # Добавляем precent в данные категории
            serializer_data['precent'] = plan_precent
            serializer_data['plan_sum'] = plan_sum


            data.append(serializer_data)

                # Возвращаем ответ
        return Response({'cats': data,
                         'total': total,
                         'operation': operation,
                         'cats_sum': cats_sum,})


@csrf_exempt
def add_operation_api(request):
    if request.method == 'POST':
        sum = request.POST.get('sum')
        comment = request.POST.get('comment')
        cat = request.POST.get('cat_id')
        str_date = request.POST.get('opDate')
        print('json', request.POST)
        # try:
        category = Category.objects.get(pk=cat)
        formate_dat = datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.%fZ')
        Operation.objects.create(sum=sum, comment=comment, date=formate_dat, kod_cat=category)
        upd_cat_sum(cat)
        category = Category.objects.get(pk=cat)

        total = category.cat_sum
        if category.plan_id != None:
            plan = Plan.objects.get(pk=category.plan_id)
            if total == None:
                precent = 0
            else:
                precent = total / plan.plan_sum * 100
            plan.precent = round(precent, 1)
            plan.save()
    return JsonResponse({'message': 'Operation saved successfully'})


@csrf_exempt
def add_plan_api(request):
    if request.method == 'POST':
        sum = request.POST.get('sum')
        cat = request.POST.get('cat_id')
        category = Category.objects.get(pk=cat)

        # total = Operation.objects.filter(kod_cat=category).aggregate(total_sum=Sum('sum'))['total_sum']
        total = category.cat_sum
        if total == None:
            precent = 0
        else:
            precent = total / int(sum) * 100
        plan = Plan.objects.create(precent=round(precent, 1), plan_sum=sum)
        category.plan = plan
        category.save()
        print('json', request.POST)

    return JsonResponse({'message': 'Plan saved successfully', 'plan_id': plan.id})



@csrf_exempt
def ed_plan_api(request):
    if request.method == 'POST':
        sum = request.POST.get('sum')
        plan_id = request.POST.get('plan_id')
        cat_id = request.POST.get('cat_id')
        print('json', request.POST)
        try:
            plan = Plan.objects.get(pk=plan_id)
            # total = Operation.objects.filter(kod_cat=cat_id).aggregate(total_sum=Sum('sum'))['total_sum']
            category = Category.objects.get(pk=cat_id)
            total = category.cat_sum
            if total == None:
                precent = 0
            else:
                precent = total / int(sum) * 100
            plan.plan_sum = sum
            plan.precent = round(precent, 1)
            plan.save()
        except ObjectDoesNotExist:
            print('ашипка')
        return JsonResponse({'message': 'Plan saved successfully', 'plan_id': plan.id})
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)


@csrf_exempt
def del_plan_api(request):
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        print('json', request.POST)
        try:
            plan = Plan.objects.get(pk=plan_id)
            plan.delete()
        except ObjectDoesNotExist:
            print('ашипка')
        return JsonResponse({'message': 'Plan saved successfully', 'plan_id': plan.id})
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)

@csrf_exempt
def add_cat_api(request):
    if request.method == 'POST':
        name = request.POST.get('cat_name')
        image = request.POST.get('cat_image')
        operation = request.POST.get('operation')
        if operation == 'spending':
            is_profit = False
        else:
            is_profit = True
        date = datetime.now()
        print('json', request.POST)
        Category.objects.create(name=name, user=request.user, date_upd_cat_sum=date, cat_sum=0, image_url=image, is_profit=is_profit)
    return JsonResponse({'message': 'Добавление категории'})

@csrf_exempt
def ed_cat_api(request):
    if request.method == 'POST':
        name = request.POST.get('cat_name')
        id = request.POST.get('cat_id')
        image = request.POST.get('cat_image')
        print('json', request.POST)
        category = Category.objects.get(pk=id)
        category.name = name
        if image != '':
            category.image_url = image
        category.save()
    return JsonResponse({'message': 'Редактирование категории'})

@csrf_exempt
def del_cat_api(request):
    if request.method == 'POST':
        print('json', request.POST)
        id = request.POST.get('cat_id')
        category = Category.objects.get(pk=id)
        category.delete()
    return JsonResponse({'message': 'Категория удалена'})

class MenuAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response(menu)


def vue_statistic(request, operation, year, month):
    return render(request, "moneycheck/vue_statistic.html", context={'menu': menu})

class StatisticAPIView(APIView):

    def get(self, request, operation, year, month):
        operation = operation
        month = month
        year = year
        if operation == 'spending':
            is_profit = False

        elif operation == 'profit':
            is_profit = True

        all_operation = Operation.objects.filter(kod_cat__is_profit=is_profit).filter(
            kod_cat__user=request.user).filter(date__month=month).filter(date__year=year).order_by('-date')

        cats_sum = {}
        for i in all_operation:
            if i.kod_cat.name not in cats_sum.items():
                cats_sum[i.kod_cat.name] = all_operation.filter(kod_cat=i.kod_cat).aggregate(total_sum=Sum('sum'))['total_sum']


        print("cats: ", cats_sum)
        total = all_operation.aggregate(total_sum=Sum('sum'))['total_sum']
        if total == None:
            total = 0.0
        grouped_operation = {}
        for day, day_operation in groupby(all_operation, key=lambda x: x.date.strftime('%d %B')):
            day_operations_serialized = [{'id': op.id, 'sum': op.sum, 'comment': op.comment, 'kod_cat': op.kod_cat.name} for op in day_operation]
            grouped_operation[day] = day_operations_serialized
            print(type(grouped_operation[day]))

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


        return Response({
            'grouped_operation': grouped_operation,
            'operation': operation,
            'month': month,
            'year': year,
            'months_year': sorted_months_by_year,
            'total': total,
            'cats_sum': cats_sum,
        })

@csrf_exempt
def ed_operation_api(request):
    if request.method == 'POST':
        sum = request.POST.get('opSum')
        comment = request.POST.get('opComment')
        id = request.POST.get('opId')
        str_date = request.POST.get('opDate')
        print(str_date)
        print('json', request.POST)
        # try:
        operation = Operation.objects.get(pk=int(id))
        operation.sum = sum
        operation.comment = comment
        operation.date = datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.%fZ')
        operation.save()
        category = Category.objects.get(pk=operation.kod_cat.id)
        upd_cat_sum(category.id)

        total = category.cat_sum
        if category.plan_id != None:
            plan = Plan.objects.get(pk=category.plan_id)
            if total == None:
                precent = 0
            else:
                precent = total / plan.plan_sum * 100
            plan.precent = round(precent, 1)
            plan.save()
    return JsonResponse({'message': 'Operation saved successfully'})

@csrf_exempt
def del_operation_api(request):
    if request.method == 'POST':
        id = request.POST.get('opId')
        print('json', request.POST)
        try:
            operation = Operation.objects.get(pk=id)
            category = Category.objects.get(pk=operation.kod_cat.id)
            operation.delete()
            upd_cat_sum(category.id)
            total = category.cat_sum
            if category.plan_id != None:
                plan = Plan.objects.get(pk=category.plan_id)
                if total == None:
                    precent = 0
                else:
                    precent = total / plan.plan_sum * 100
                plan.precent = round(precent, 1)
                plan.save()
        except ObjectDoesNotExist:
            print('ашипка')
        return JsonResponse({'message': 'Plan saved successfully', 'op_id': operation.id})
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)