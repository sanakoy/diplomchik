from collections import defaultdict
from itertools import groupby
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import render
from django.db.models import Sum, Q, FilteredRelation
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import *
from .models import Category, Operation
from .serializers import CategorySerializer1
from asgiref.sync import sync_to_async


current_month = datetime.now().month # для того, чтобы изначально выводилась статистика по текущему месяцу
current_year = datetime.now().year


menu =  [
        {'title': 'Расходы', 'url_name': 'index', 'slug': 'spending'},
        {'title': 'Доходы', 'url_name': 'index', 'slug': 'profit'},
        {'title': 'Статистика', 'url_name': 'statistic', 'operation': 'spending', 'year': current_year, 'month': current_month},
        {'title': 'Профиль', 'url_name': 'users:profile'},
        {'title': 'Выйти', 'url_name': 'users:logout'},
    ]

menu_dict = {
        'spending': {'title': 'Расходы', 'url_name': 'index', 'slug': 'spending'},
        'profit': {'title': 'Доходы', 'url_name': 'index', 'slug': 'profit'},
        'statistic': {'title': 'Статистика', 'url_name': 'statistic', 'operation': 'spending', 'year': current_year, 'month': current_month},
        'profile': {'title': 'Профиль', 'url_name': 'users:profile'},
        'logout': {'title': 'Выйти', 'url_name': 'users:logout'},
}



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


    return render(request, "moneycheck/operation.html", {'menu': menu_dict, 'current_url': request.build_absolute_uri})


def upd_cat_sum(id):
    cat = Category.objects.get(pk=id)
    total = Operation.objects.filter(kod_cat=cat) \
        .filter(date__month=current_month) \
        .filter(date__year=current_year) \
        .aggregate(total_sum=Sum('sum'))['total_sum']
    cat.cat_sum = total if total != None else 0
    cat.date_upd_cat_sum = datetime.now()
    cat.save()


# class CategoryAPIView(APIView):
    # def get(self, request):
    #     current_url = request.build_absolute_uri()
    #     if current_url == "http://127.0.0.1:8003/api/category/spending/":
    #         is_profit = False
    #         operation = "spending"
    #         operation_rus = "Расходы"
    #     else:
    #         is_profit = True
    #         operation = "profit"
    #         operation_rus = "Доходы"

    #     now = datetime.now()
    #     current_year = now.year
    #     current_month = now.month

    #     # --- ЗАПРОС 1 ---
    #     # Точный аналог FastAPI: outerjoin с условием внутри ON.
    #     # FilteredRelation принудительно добавляет условие в ON clause LEFT OUTER JOIN'а.
    #     categories_query = Category.objects.filter(
    #         user=request.user,
    #         is_profit=is_profit
    #     ).annotate(
    #         current_operations=FilteredRelation(
    #             'operation',
    #             condition=Q(
    #                 operation__date__year=current_year,
    #                 operation__date__month=current_month
    #             )
    #         )
    #     ).annotate(
    #         calculated_cat_sum=Sum('current_operations__sum')
    #     ).order_by('date_create')
        
    #     # Выполняем запрос в БД (аналог rows = (await session.execute(query)).all())
    #     categories = list(categories_query)

    #     # --- ЗАПРОС 2 ---
    #     # Точный аналог FastAPI: подгружаем планы отдельным запросом через ID (selectinload)
    #     cat_ids = [cat.id for cat in categories]
        
    #     # select_related('plan') сделает LEFT JOIN к планам для нужных ID
    #     cats_with_plans = Category.objects.select_related('plan').filter(id__in=cat_ids)
        
    #     # Создаем мапу {cat_id: plan} как в FastAPI (plans_map)
    #     plans_map = {cat.id: cat.plan for cat in cats_with_plans}

    #     # --- ПИТОНОВСКАЯ ЛОГИКА ---
    #     data = []
    #     cats_sum = {}
    #     total = 0.0

    #     for category in categories:
    #         # Парсим сумму (cat_sum из Запроса 1)
    #         sum_val = float(category.calculated_cat_sum) if category.calculated_cat_sum else 0.0
    #         cats_sum[category.name] = sum_val
    #         total += sum_val

    #         # Забираем план из мапы Запроса 2
    #         plan = plans_map.get(category.id)

    #         # Сериализуем
    #         serializer_data = CategorySerializer1(category).data
    #         serializer_data['cat_sum'] = sum_val
    #         serializer_data['precent'] = plan.precent if plan else None
    #         serializer_data['plan_sum'] = plan.plan_sum if plan else None

    #         data.append(serializer_data)

    #     return Response({
    #         'cats': data,
    #         'total': total,
    #         'operation': operation,
    #         'cats_sum': cats_sum,
    #     })
class CategoryAPIView(View):  # <-- View, не APIView
    async def get(self, request):
        current_url = request.build_absolute_uri()
        if "spending" in current_url:
            is_profit = False
            operation = "spending"
        else:
            is_profit = True
            operation = "profit"

        now = datetime.now()
        current_year = now.year
        current_month = now.month

        # Получаем user_id синхронно через sync_to_async — до любых ORM запросов
        get_user_id = sync_to_async(lambda: request.user.id)
        user_id = await get_user_id()

        @sync_to_async
        def get_categories():
            return list(
                Category.objects.filter(
                    user_id=user_id,  # <-- user_id вместо request.user
                    is_profit=is_profit
                ).annotate(
                    current_operations=FilteredRelation(
                        'operation',
                        condition=Q(
                            operation__date__year=current_year,
                            operation__date__month=current_month
                        )
                    )
                ).annotate(
                    calculated_cat_sum=Sum('current_operations__sum')
                ).order_by('date_create')
            )

        @sync_to_async
        def get_plans(cat_ids):
            cats_with_plans = Category.objects.select_related('plan').filter(id__in=cat_ids)
            return {cat.id: cat.plan for cat in cats_with_plans}

        categories = await get_categories()
        cat_ids = [cat.id for cat in categories]
        plans_map = await get_plans(cat_ids)

        data = []
        cats_sum = {}
        total = 0.0

        for category in categories:
            sum_val = float(category.calculated_cat_sum) if category.calculated_cat_sum else 0.0
            cats_sum[category.name] = sum_val
            total += sum_val

            plan = plans_map.get(category.id)

            # serializer_data = CategorySerializer1(category).data
            serializer_data = {"id" :category.id,
            "name" : category.name,
            "cat_sum" : category.cat_sum,
            "is_profit" : category.is_profit,
            "image_url" : category.image_url,
            "plan_id" : category.plan_id,  # plan_id вместо plan
            "user_id" : category.user_id}
            serializer_data['cat_sum'] = sum_val
            serializer_data['precent'] = plan.precent if plan else None
            serializer_data['plan_sum'] = plan.plan_sum if plan else None

            data.append(serializer_data)

        return JsonResponse({
            'cats': data,
            'total': total,
            'operation': operation,
            'cats_sum': cats_sum,
        })

@csrf_exempt
def add_operation_api(request):
    if request.method == 'POST':
        sum = request.POST.get('sum')
        comment = request.POST.get('comment')
        cat = request.POST.get('cat_id')
        str_date = request.POST.get('opDate')
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

        total = category.cat_sum
        if total == None:
            precent = 0
        else:
            precent = total / int(sum) * 100
        plan = Plan.objects.create(precent=round(precent, 1), plan_sum=sum)
        category.plan = plan
        category.save()

    return JsonResponse({'message': 'Plan saved successfully', 'plan_id': plan.id})



@csrf_exempt
def ed_plan_api(request):
    if request.method == 'POST':
        sum = request.POST.get('sum')
        plan_id = request.POST.get('plan_id')
        cat_id = request.POST.get('cat_id')
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
        date = timezone.now()
        Category.objects.create(name=name, user=request.user, date_create=date, date_upd_cat_sum=date, cat_sum=0, image_url=image, is_profit=is_profit)
    return JsonResponse({'message': 'Добавление категории'})

@csrf_exempt
def ed_cat_api(request):
    if request.method == 'POST':
        name = request.POST.get('cat_name')
        id = request.POST.get('cat_id')
        image = request.POST.get('cat_image')
        category = Category.objects.get(pk=id)
        category.name = name
        if image != '':
            category.image_url = image
        category.save()
    return JsonResponse({'message': 'Редактирование категории'})

@csrf_exempt
def del_cat_api(request):
    if request.method == 'POST':
        id = request.POST.get('cat_id')
        category = Category.objects.get(pk=id)
        category.delete()
    return JsonResponse({'message': 'Категория удалена'})

class MenuAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response(menu)


def vue_statistic(request, operation, year, month):
    return render(request, "moneycheck/vue_statistic.html", context={'menu': menu_dict})

class StatisticAPIView(APIView):
    def get(self, request, operation, year, month):
        is_profit = (operation == 'profit')

        now = datetime.now()
        current_month = now.month
        current_year = now.year

        # --- ЗАПРОС 1: Достаем все операции за месяц + категории ---
        # Использование select_related('kod_cat') решает проблему N+1 
        # при обращении к op.kod_cat.name и op.kod_cat.image_url
        operations = list(
            Operation.objects.filter(
                kod_cat__is_profit=is_profit,
                kod_cat__user=request.user,
                date__year=year,
                date__month=month
            ).select_related('kod_cat').order_by('-date')
        )

        # --- ПИТОНОВСКАЯ ЛОГИКА АГРЕГАЦИИ В ПАМЯТИ ---
        # Заменяет тяжелые .aggregate() в цикле и itertools.groupby
        grouped_operation = {}
        cats_sum = {}
        total = 0.0

        for op in operations:
            op_sum = float(op.sum) if op.sum else 0.0
            total += op_sum

            # Считаем сумму по категориям (cats_sum)
            cat_name = op.kod_cat.name
            cats_sum[cat_name] = cats_sum.get(cat_name, 0.0) + op_sum

            # Формируем кроссплатформенный ключ дня без ведущих нулей (например, "15 May")
            day_key = f"{op.date.day} {op.date.strftime('%B')}"

            # Группируем операции по дням (вместо itertools.groupby)
            if day_key not in grouped_operation:
                grouped_operation[day_key] = []
            
            grouped_operation[day_key].append({
                'id': op.id,
                'sum': op_sum,
                'comment': op.comment,
                'kod_cat': cat_name,
                'image_url': op.kod_cat.image_url
            })

        # --- ЗАПРОС 2: История месяцев и лет ---
        # Достаем все уникальные комбинации "год-месяц" ОДНИМ запросом.
        # Метод .values().distinct() заменяет вложенные циклы
        history_qs = Operation.objects.filter(
            kod_cat__is_profit=is_profit,
            kod_cat__user=request.user
        ).values('date__year', 'date__month').distinct().order_by('-date__year', '-date__month')

        months_by_year = defaultdict(list)
        for row in history_qs:
            y = row['date__year']
            m = row['date__month']
            if y is not None and m is not None:
                # В возвращаемом JSON ключи годов — это строки (например, "2026")
                months_by_year[str(y)].append(m)

        return Response({
            'grouped_operation': grouped_operation,
            'operation': operation,
            'month': month,
            'year': year,
            'months_year': dict(months_by_year),
            'total': total,
            'cats_sum': cats_sum,
            'current_month': current_month,
            'current_year': current_year,
        })

@csrf_exempt
def ed_operation_api(request):
    if request.method == 'POST':
        sum = request.POST.get('opSum')
        comment = request.POST.get('opComment')
        id = request.POST.get('opId')
        str_date = request.POST.get('opDate')
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
        try:
            operation = Operation.objects.get(pk=id)
            category = Category.objects.get(pk=operation.kod_cat.id)
            operation.delete()
            upd_cat_sum(category.id)
            category = Category.objects.get(pk=category.id)
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