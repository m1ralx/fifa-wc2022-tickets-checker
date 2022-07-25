from datetime import datetime
from subprocess import call
from typing import List, Generator
from dataclasses import dataclass

from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from countries import COUNTRIES


@dataclass(frozen=True)
class Category:
    quality: int
    price: int


@dataclass
class Match:
    match_number: int
    host_team: str
    opposing_team: str
    match_date: str
    match_time: str
    stadium: str
    available_categories: List[Category]

    @classmethod
    def from_dict(cls, data) -> 'Match':
        match = Match(**data)
        match.available_categories = [Category(**c) for c in match.available_categories]
        return match

    @classmethod
    def from_html(cls, html_content: str) -> 'Match':
        document = BeautifulSoup(html_content, 'html.parser')
        
        match_number = int(document.find(class_='round').text.split()[1])

        host_team = document.find(class_='team host').text.strip()
        opposing_team = document.find(class_='team opposing').text.strip()

        match_date = document.find(class_='day').text.strip()
        match_time = document.find(class_='time').text.strip()
        stadium = document.find(class_='location').find(class_='site').text.strip()
        
        available_categories = list(cls._extract_available_categories(document))

        return Match(
            match_number=match_number,
            host_team=host_team,
            opposing_team=opposing_team,
            match_date=match_date,
            match_time=match_time,
            stadium=stadium,
            available_categories=available_categories,
        )
    
    @staticmethod
    def _extract_available_categories(document: BeautifulSoup) -> Generator[Category, None, None]:
        for elem in document.select('[class*=seat_category_end]'):
            category = elem.select_one('[class*=category]')
            if category.select_one('[class=category_unavailable_overlay]') is not None:
                continue
            tariff = elem.select_one('[class*=tariff]').text.strip()
            if tariff != 'Ticket Price':
                continue

            quality = int(category.text.strip().split()[1])
            price = int(elem.find(class_='int_part').text)
            
            yield Category(quality, price)

    def is_available(self) -> bool:
        return len(self.available_categories) > 0
    
    def as_keyboard(self) -> InlineKeyboardMarkup:
        from fifa_provider import MatchesProvider

        m = self
        keyboard = []

        host = m.host_team
        if m.host_team in COUNTRIES:
            host = f'{host} {COUNTRIES[m.host_team].icon}'
        opposing = m.opposing_team
        if m.opposing_team in COUNTRIES:
            opposing = f'{COUNTRIES[m.opposing_team].icon} {opposing}'

        keyboard.append([
            InlineKeyboardButton(host, callback_data='host'),
            InlineKeyboardButton(opposing, callback_data='opposing'),
        ])
        match_date = datetime.strptime(m.match_date.split(', ')[1], '%d %B %Y').strftime('%d-%m-%Y')
        date = f'📅 {match_date} {m.match_time}'
        keyboard.append([InlineKeyboardButton(date, callback_data='date')])
        location = f'🏟 {m.stadium} 🏟'
        keyboard.append([InlineKeyboardButton(location, callback_data='stadium')])
        categories = ', '.join([f'Cat {c.quality}' for c in m.available_categories])
        categories = f'🎫 {categories}'
        url = MatchesProvider.URL_TEMPLATE.format(MatchesProvider.PERFORMANCE_IDS_RANGE_START + m.match_number - 1)
        keyboard.append([InlineKeyboardButton(categories, url=url)])

        return InlineKeyboardMarkup(keyboard)

    def __str__(self) -> str:
        """
            ```
            +---------------------------------+
            | Game 2 | Senegal vs Netherlands |   <-- header
            +---------------------------------|
            | Monday, 21 November 2022 13:00  |   <-- date
            +---------------------------------|
            |        Al Thumama Stadium       |   <-- location
            +---------------------------------|
            |              Cat1               |   <-- categories
            +---------------------------------+
            ```
            [Open](https://....)
        """
        from fifa_provider import MatchesProvider

        m = self
        
        header = f'Game {m.match_number} | {m.host_team} vs {m.opposing_team}'
        date = f'{m.match_date} {m.match_time}'
        location = m.stadium
        categories = ', '.join([f'Cat {c.quality}' for c in m.available_categories])
        url = MatchesProvider.URL_TEMPLATE.format(MatchesProvider.PERFORMANCE_IDS_RANGE_START + m.match_number - 1)
        url = f'[Open]({url})'

        width = max((
            len(header),
            len(date),
            len(location)
        ))
        
        def pad(row: str):
            diff = width - len(row)
            left_padding = diff // 2
            right_padding = diff - left_padding
            left_padding += 1
            right_padding += 1

            row = row.ljust(len(row) + left_padding, '\t')
            return row.rjust(len(row) + right_padding, '\t')

        header = pad(header)
        date = pad(date)
        location = pad(location)
        categories = pad(categories)
        url = pad(url)
        
        horizonal_line = '+' + ('-' * (width + 2)) + '+\n'

        return (
            '```\n' +
            horizonal_line + 
            f'|{header}|\n' + 
            horizonal_line + 
            f'|{date}|\n' + 
            horizonal_line + 
            f'|{location}|\n' + 
            horizonal_line + 
            f'|{categories}|\n' + 
            horizonal_line +
            '```\n' +
            url
        )


class GetMatchResult:
    def __init__(self, match: Match = None, error: str = None) -> None:
        self.match = match
        self._error = error
    
    @classmethod
    def success(cls, match: Match) -> 'GetMatchResult':
        return cls(match)
    
    @classmethod
    def error(cls, error: str) -> 'GetMatchResult':
        return cls(error=error)
    
    def is_error(self) -> bool:
        return self._error is not None
