from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("moneycheck.urls")),
    # path('users/', include('users.urls', namespace='users')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('admin/', admin.site.urls),

]
