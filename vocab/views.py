from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from vocab.models import Entry, Episode, Review


def index(request):
    return render(request, 'vocab/index.html')


def entry_detail(request, slug):
    return TemplateResponse(request, 'vocab/entry_detail.html', {
        'entry': get_object_or_404(Entry.objects.all(), slug=slug)
    })


def episode_detail(request, slug):
    episode = get_object_or_404(Episode.objects.all(), slug=slug)
    return TemplateResponse(request, 'vocab/episode_detail.html', {
        'episode': episode,
        'review_endpoint': reverse('episode_review', args=[episode.pk]),
    })


def episode_list(request):
    episodes = Episode.objects.order_by('-id')
    paginator = Paginator(episodes, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'vocab/episode_list.html', {
        'page_obj': page_obj,
    })


@login_required
@require_POST
def mark_episode_as_reviewed(request, episode_id):
    try:
        Review.objects.create(user=request.user, episode_id=episode_id)
    except DatabaseError as e:
        print(f'Error saving the review: {e}')

    return HttpResponse(
        'Episode {episode_id} successfully marked reviewed by {request.user.username}',
        content_type='text/plain',
    )
