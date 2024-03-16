from django.urls import path

from . import views

urlpatterns = [
    path("index/<slug:operation>/", views.index, name="index"),
    path("add/<int:cat_id>/",views.add, name="add"),
    path("addcat/<slug:operation>", views.addcat, name="addcat"),
    path("statistic/<slug:operation>/<int:month>", views.statistic, name="statistic"),
    path("deletecat/<int:cat_id>", views.deletecat, name="deletecat"),
    path("delete/<int:id>", views.delete, name="delete"),
    path("plancat/<int:cat_id>/", views.plancat, name="plancat"),
]