from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home_estudiante/', views.home_estudiante, name='home_estudiante'),
    path('logout/', views.logout_view, name='logout'),
]
