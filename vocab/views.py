from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse

from vocab.models import Entry, Episode


def index(request):
    return render(request, 'vocab/index.html')


def entry_detail(request, slug):
    return TemplateResponse(request, 'vocab/entry_detail.html', {
        'entry': get_object_or_404(Entry.objects.all(), slug=slug)
    })


def episode_detail(request, slug):
    return TemplateResponse(request, 'vocab/episode_detail.html', {
        'episode': get_object_or_404(Episode.objects.all(), slug=slug)
    })


def episode_list(request):
    episodes = Episode.objects.order_by('-id')
    paginator = Paginator(episodes, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'vocab/episode_list.html', {
        'page_obj': page_obj,
    })
