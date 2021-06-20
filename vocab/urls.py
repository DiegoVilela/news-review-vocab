from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:slug>/', views.entry_detail, name='entry_detail'),
    path('episode/<slug:slug>/', views.episode_detail, name='episode_detail'),
]
