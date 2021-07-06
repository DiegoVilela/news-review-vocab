import re
import requests
from collections import namedtuple
from datetime import datetime
from bs4 import BeautifulSoup
from django.utils.text import slugify

from vocab.models import Episode

URL_BASE = 'https://www.bbc.co.uk/learningenglish/english/course/newsreview/unit-'

UnitInfo = namedtuple('UnitInfo', ['unit', 'starting_episode', 'ending_episode'])


class NewsReview:
    def __init__(self):
        self.session = requests.Session()
        self._episodes = []
        self._dates = []
        self._next_unit = True

    def _parse_dates(self, bs: BeautifulSoup):
        items = bs.find_all('span', class_='date')
        for date in items:
            self._dates.append(datetime.strptime(str(date.string), '%d %b %Y'))

        idx = len(self._dates) - len(self._episodes)
        for episode in self._episodes:
            try:
                episode.date = self._dates[idx]
                idx += 1
            except IndexError as e:
                print(f'Error: {e}')

    def _get_unit_from_episode_id(self, ep_id):
        if ep_id <= 0:
            raise Exception('Invalid episode_id.')
        elif 1 <= ep_id <= 109:
            unit = int(ep_id / 10 + 1)
        elif 110 <= ep_id <= 139:
            unit = int(ep_id / 10)
        else:  # >= 140
            unit = int(ep_id / 10 - 1)
        return unit

    def _get_unit_info(self, unit=None, episode_id=None):
        """Return a UnitInfo object as per the BBC site."""

        if episode_id:
            unit = self._get_unit_from_episode_id(episode_id)

        start = (unit * 10) - 9  # 71
        end = start + 9  # 80
        if unit == 10:
            end = 99
        elif unit == 11:
            start = 100
            end = 119
        elif unit == 12:
            start = unit * 10
            end = start + 9
        elif unit == 13:
            start = unit * 10
            end = 149
        elif unit >= 14:
            start = (unit * 10) + 10
            end = start + 9

        return UnitInfo(unit, start, end)

    def _remove_links(self, bs: BeautifulSoup):
        for el in bs(('p', 'h3')):
            if el.find('a', href=True):
                el.decompose()

    def _isRelevant(self, text: str):
        if text.startswith('_'):
            return False

        to_exclude = {
            'Downloads',
            'More',
            'Did you like that? Why not try these?',
            'Watch the video and complete the activity',
            'To do',
            "Try our quiz to see how well you've learned today's language.",
        }

        if text in to_exclude:
            return False

        return True

    def _get_episode_content(self, sections):
        content = []
        for section in sections:
            for line in section.stripped_strings:
                line_text = str(line)
                if self._isRelevant(line_text):
                    content.append(line)

        return content[1:]

    def _parse_episode(self, content, episode_id: int):
        bs = BeautifulSoup(content, features="html5lib")
        self._remove_links(bs)
        sections = bs.find_all('div', class_=re.compile('widget widget-richtext'))
        headline = sections[0].find('h3').string
        headline = str(headline)
        ep_content = self._get_episode_content(sections)
        ep_content = '\n'.join(ep_content)
        ep_content = ep_content.replace(u'\xa0', u' ')
        episode = Episode(
            id=episode_id,
            headline=headline,
            slug=slugify(headline),
            raw_content=ep_content,
        )
        return episode

    def _get_episode(self, episode_id, unit):
        # Due to BBC bug
        if episode_id == 1:
            return False

        url_ep = f'{URL_BASE}{unit}/session-{episode_id}'
        try:
            print(f'Getting episode {episode_id} ...')
            response = self.session.get(url_ep)
            response.raise_for_status()
            if response.status_code == 404:
                print(f'Episode {episode_id} was not published yet.')
            return self._parse_episode(response.content, episode_id)
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return False

    def _get_episodes(self, unit: int, from_ep: int = None):
        # Uses a unit to get episode dates, otherwise, one
        # more request would be necessary for each episode
        # as their pages don't have their dates
        unit_info = self._get_unit_info(unit)
        start = from_ep or unit_info.starting_episode
        end = unit_info.ending_episode

        for episode_id in range(start, end + 1):
            episode = self._get_episode(episode_id, unit)
            if not episode:
                self._next_unit = False
                return self._episodes
            self._episodes.append(episode)
        return self._episodes

    def get_unit(self, unit: int, from_ep: int = None):
        """Return all episodes of a given BBC News Review unit.

        Example: get_unit(7)
        The following URL would be used to fetch episodes and their respective dates.
        https://www.bbc.co.uk/learningenglish/english/course/newsreview/unit-7
        """

        episodes = self._get_episodes(unit, from_ep)
        url_unit = f'{URL_BASE}{unit}/'
        response = self.session.get(url_unit)
        if response.ok:
            page = BeautifulSoup(response.content, features="html5lib")
            self._parse_dates(page)
            self._episodes = []
            self._dates = []

        return episodes

    def pull(self):
        """Synchronize database with BBC News Review.

        Return a list of episodes if any were added.
        """

        # Initial set up. None Episode on the database
        from_episode_id = 2  # Not 1 because of a bug on BBC website
        unit = 1

        # Update. There are Episodes in the database
        if Episode.objects.exists():
            from_episode_id = Episode.objects.last().pk + 1
            unit = self._get_unit_info(episode_id=from_episode_id).unit

        # Run the fetching and parsing
        result = []

        while episodes := self.get_unit(1, None):
            for episode in episodes:
                result.append(episode)
            unit += 1
            # After the first iteration, get_unit() will return complete units.
            # To do that, the parameter `from_episode_id` MUST be `None`.
            from_episode_id = None
            if not self._next_unit:
                break

        return result
