from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('episode/<slug:slug>/', views.episode_detail, name='episode_detail'),
    path('episodes/', views.episode_list, name='episode_list'),
    path('<slug:slug>/', views.entry_detail, name='entry_detail'),
]
