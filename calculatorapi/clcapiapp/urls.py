from django.urls import path
from . import views

urlpatterns = [
    path('<str:numberid>/', views.get_numbers, name='get_numbers'),
]
