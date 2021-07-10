import os
import re
from collections import namedtuple
from datetime import datetime, time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEVELOPER_KEY = os.environ.get('YOUTUBE_DEVELOPER_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE_CHANNEL = 'UCHaHD477h-FeBbVh9Sh7syA'

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


def get_error_msg(e: HttpError):
    return f'An HTTP error {e.resp.status} occurred: {e.content}'


class _Youtube:
    def __init__(self):
        self._service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                              developerKey=DEVELOPER_KEY)
        self._page_count = 1
        self._page_token = ''
        self.videos = []

    def fetch_all(self):
        try:
            while page := self._get_videos_page():
                self._parse_videos_page(page)
        except HttpError as e:
            print(get_error_msg(e))
        return self.videos

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
            cleaned_headline = _Youtube.clean(video['snippet']['title'])
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

    def get_video_id(self, q: str, date: datetime):
        if not date:
            return None

        published_after = datetime.combine(date, time())
        video_id = None
        try:
            result = self._service.search().list(
                part='id',
                channelId=YOUTUBE_CHANNEL,
                maxResults=1,
                publishedAfter=f"{published_after.isoformat(timespec='seconds')}Z",
                q=q,
                type='video',
                videoDuration='medium',
                videoEmbeddable='true',
            ).execute()
            try:
                video_id = result['items'][0]['id']['videoId']
            except IndexError:
                video_id = None
        except HttpError as e:
            print(get_error_msg(e))

        return video_id


service = _Youtube()
