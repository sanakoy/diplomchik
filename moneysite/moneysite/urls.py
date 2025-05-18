from django.contrib import admin
from django.urls import include, path

from moneycheck.views import MenuAPIView, CategoryAPIView, StatisticAPIView

urlpatterns = [
    path("", include("moneycheck.urls")),
    # path('users/', include('users.urls', namespace='users')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('admin/', admin.site.urls),
    # path('api/category/', CategoryAPIView.as_view()),
    path('api/category/spending/', CategoryAPIView.as_view()),
    path('api/category/profit/', CategoryAPIView.as_view()),
    path('api/menu/', MenuAPIView.as_view()),
    path('api/statistic/<slug:operation>/<int:year>/<int:month>/', StatisticAPIView.as_view()),

]
