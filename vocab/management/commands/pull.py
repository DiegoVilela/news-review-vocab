from django.core.management import BaseCommand, CommandError
from django.db import DatabaseError

from vocab.bbc import NewsReview
from vocab.models import Episode
from vocab.youtube import service, Video


def similarity(a: list, b: list):
    if not a or not b:
        return 0

    smaller = a
    bigger = b
    if len(b) > len(a):
        smaller = b
        bigger = a

    count = 0
    for i in smaller:
        if i in bigger:
            count += 1

    return round(count / len(smaller) * 100)


def get_videos():

    videos = service.videos
    # To better match the list from BBC
    placeholder = Video(None, None, None)
    videos.insert(6, placeholder)
    videos.insert(179, placeholder)
    return videos


def get_episodes():
    episodes = list(Episode.objects.order_by('-id'))
    # To better match the list from Youtube
    episodes.insert(170, Episode())
    return episodes


class Command(BaseCommand):
    help = 'Fetch and save episodes from BBC News Review.'

    def _update_episodes_from_bbc(self):
        self.stdout.write('Fetching episodes from BBC News Review.')
        handler = NewsReview()
        result = handler.pull()
        if result:
            try:
                for episode in result:
                    episode.save()
            except DatabaseError as e:
                raise CommandError(e)

        self.stdout.write(self.style.SUCCESS('All episodes in sync with BBC.'))

    def _update_videos_sequentially(self):
        self.stdout.write('Fetching video ids from Youtube.')
        videos = get_videos()
        episodes = get_episodes()

        for idx, episode in enumerate(episodes):
            video = videos[idx]
            cleaned_episode = service.clean(episode.headline).split()

            if similarity(video.headline, cleaned_episode) < 50:
                # episode.video = service.get_video_id(episode.headline, episode.date)
                print(f'{video.headline}\n{cleaned_episode}')
                print('Similarity: ', similarity(video.headline, cleaned_episode), '-' * 80, idx, '\n')
            else:
                episode.video = video.video_id
                try:
                    episode.save(update_fields=['video'])
                except DatabaseError as e:
                    raise CommandError(e)

        total = Episode.objects.count()
        without_video = Episode.objects.filter(video__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(f'{total = } {without_video = }'))

    def handle(self, *args, **options):
        self._update_episodes_from_bbc()

        if not Episode.objects.exists():
            self._update_videos_sequentially()

        if episodes_missing_video := Episode.objects.filter(video__isnull=True):
            self.stdout.write('Fetching missing video ids from Youtube.')
            for episode in episodes_missing_video:
                if video_id := service.get_video_id(episode.headline, episode.date):
                    episode.video = video_id
                else:
                    episode.video = f'{episode.id} ?'
                episode.save(update_fields=['video'])

            self.stdout.write(self.style.SUCCESS('All videos in sync with Youtube.'))
