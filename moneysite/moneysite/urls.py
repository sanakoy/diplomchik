from django.contrib import admin
from django.urls import include, path

from moneycheck.views import CategoryAPIView

urlpatterns = [
    path("", include("moneycheck.urls")),
    # path('users/', include('users.urls', namespace='users')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('admin/', admin.site.urls),
    path('api/category/', CategoryAPIView.as_view()),
]
