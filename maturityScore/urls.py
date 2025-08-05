from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('userinputs/', views.userinputs, name='userinputs'),  # Yes/No form
    path('result/', views.calculate_score, name='calculate_score'),  # JSON response
     path('check-score/', views.check_score, name='check_score'),
    path("generate-table/", views.generate_table, name="generate_table"),


]
