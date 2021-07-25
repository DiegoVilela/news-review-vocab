from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('review/<int:episode_id>', views.mark_episode_as_reviewed, name='episode_review'),
    path('episode/<slug:slug>/', views.episode_detail, name='episode_detail'),
    path('episodes/', views.episode_list, name='episode_list'),
    path('<slug:slug>/', views.entry_detail, name='entry_detail'),
]
