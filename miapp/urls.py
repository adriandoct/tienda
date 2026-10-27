from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('caja/', views.modulo_cajero, name='modulo_cajero'),
    path('caja/procesar-venta/', views.procesar_venta_cajero, name='procesar_venta_cajero'),
]
