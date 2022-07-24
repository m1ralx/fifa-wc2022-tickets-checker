import os
import logging
import traceback

import requests
from requests.adapters import HTTPAdapter, Retry

from models import Match, GetMatchResult

logger = logging.getLogger()


class MatchesProvider:
    URL_TEMPLATE = 'https://fcfs-intl.fwc22.tickets.fifa.com/secure/selection/event/seat/performance/{}/lang/en'
    TOTAL_MATCHES_COUNT = 64
    PERFORMANCE_IDS_RANGE_START = 101437163855
    PERFORMANCE_IDS_RANGE_END = PERFORMANCE_IDS_RANGE_START + TOTAL_MATCHES_COUNT

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers['User-Agent'] = os.getenv('USER_AGENT')
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504],
        )
        self._session.mount('http://', HTTPAdapter(max_retries=retries))
        self._session.mount('https://', HTTPAdapter(max_retries=retries))

        self.current_performance_id = self.PERFORMANCE_IDS_RANGE_START

    def __iter__(self) -> 'MatchesProvider':
        self.current_performance_id = self.PERFORMANCE_IDS_RANGE_START
        return self
    
    def __next__(self) -> GetMatchResult:
        if self._current_match_number > self.TOTAL_MATCHES_COUNT:
            raise StopIteration
        
        result = self._fetch()
        self.current_performance_id += 1
        return result
    
    def _fetch(self) -> GetMatchResult:
        try:
            logger.info('fetching match №%d', self._current_match_number)
            response = self._session.get(self.URL_TEMPLATE.format(self.current_performance_id))

            if response.status_code != 200:
                error = 'match_number: {}. Bad response status code: {}'.format(self._current_match_number, response.status_code)
                logger.error(error)
                return GetMatchResult.error(error)

            match = Match.from_html(response.content)
            return GetMatchResult.success(match)
        
        except Exception as exc:
            logger.exception('match_number: {}'.format(self._current_match_number))
            return GetMatchResult.error('match_number: {}. Exception: {}'.format(self._current_match_number, traceback.format_exc()))

    @property
    def _current_match_number(self) -> int:
        return self.current_performance_id - self.PERFORMANCE_IDS_RANGE_START + 1
