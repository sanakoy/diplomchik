from django.urls import path

from . import views

urlpatterns = [
    path("index/<slug:operation>/", views.index, name="index"),
    path("add/<int:cat_id>/",views.add, name="add"),
    path("addcat/<slug:operation>", views.addcat, name="addcat"),
    path("statistic/<slug:operation>/<int:year>/<int:month>/", views.vue_statistic, name="statistic"),
    path("deletecat/<int:cat_id>", views.deletecat, name="deletecat"),
    path("delete/<int:id>", views.delete, name="delete"),
    path("plancat/<int:cat_id>/", views.plancat, name="plancat"),
    path("spending/", views.spending, name="spending"),
    path("profit/", views.spending, name='profit'),
    path('api/add-operation/', views.add_operation_api),
    path('api/ed-operation/', views.ed_operation_api),
    path('api/del-operation/', views.del_operation_api),
    path('api/add-plan/', views.add_plan_api),
    path('api/ed-plan/', views.ed_plan_api),
    path('api/del-plan/', views.del_plan_api),
    path('api/add-cat/', views.add_cat_api),
    path('api/ed-cat/', views.ed_cat_api),
    path('api/del-cat/', views.del_cat_api),
    path("vue_statistic/", views.vue_statistic, name="vue_statistic")

]