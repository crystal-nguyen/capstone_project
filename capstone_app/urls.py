from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="demo_home"),
    path('dashboard/',views.dashboard, name='demo_dashboard'),
    path('test/',views.test, name='demo_test'),
]