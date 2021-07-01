import os
import re
from collections import namedtuple

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


DEVELOPER_KEY = os.environ.get('YOUTUBE_DEVELOPER_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

Video = namedtuple('Video', ['headline', 'video_id', 'published_at'])

remove = {
    ' \'',
    '\' ',
    ':',
    ' -',
    '- ',
    'BBC News Review',
    'News Review',
    'Watch News Review',
    'BBC Learning English',
}
PATTERN = re.compile('|'.join(remove))


class Youtube:
    def __init__(self, load_all: bool = False):
        self._service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                              developerKey=DEVELOPER_KEY)
        self._page_count = 1
        self._page_token = ''
        self.videos = []
        if load_all:
            self.fetch_all()

    def fetch_all(self):
        try:
            while page := self._get_videos_page():
                self._parse_videos_page(page)
        except HttpError as e:
            print(f'An HTTP error {e.resp.status} occurred: {e.content}')

    def _get_videos_page(self):
        if self._page_count != 1:
            if not self._page_token:
                print('All videos were fetched.')
                return False

        return self._service.playlistItems().list(
            part='contentDetails,snippet',
            fields='nextPageToken,items(snippet(publishedAt,title,resourceId(videoId)))',
            maxResults=50,
            playlistId='PLcetZ6gSk968l1s4WuxwyhiyEUmg5GOZC',
            pageToken=self._page_token,
        ).execute()

    def _parse_videos_page(self, page):
        try:
            self._page_token = page['nextPageToken']
        except KeyError:
            self._page_token = False

        for video in page['items']:
            cleaned_headline = Youtube.clean(video['snippet']['title'])
            self.videos.append(Video(
                headline=cleaned_headline.split(),
                video_id=video['snippet']['resourceId']['videoId'],
                published_at=video['snippet']['publishedAt'],
            ))
        self._page_count += 1

    def __len__(self):
        return len(self.videos)

    @classmethod
    def clean(cls, text: str):
        return re.sub(PATTERN, '', text).lower()
