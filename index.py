import asyncio
import os
import logging
from datetime import datetime, timedelta
from typing import List
from itertools import zip_longest
import traceback

from fifa_provider import MatchesProvider
from repository import MatchesRepository
from reporter import Bot
from models import Match
from timestamp import get_timestamp

logger = logging.getLogger()


def handler(event, context):
    asyncio.run(main())
    return {
        "statusCode": 200,
        "body": 'OK',
    }


async def main():
    bot = Bot()

    actual_matches = await get_actual_matches(bot)
    await update_state(bot, actual_matches)


class FetchException(Exception):
    pass


class UpdateStateException(Exception):
    pass


async def get_actual_matches(bot: Bot) -> List[Match]:
    matches_provider = MatchesProvider()
    actual_matches = []
    for m in matches_provider:
        if m.is_error():
            await bot.report_error(m.error)
            raise FetchException('Failed to fetch actual matches')
        actual_matches.append(m.match)
    return actual_matches


async def update_state(bot: Bot, actual_matches: List[Match]):
    if os.getenv('UPDATE_STATE') != 'true':
        return
    try:
        repository = MatchesRepository()
        timestamp, current_matches = repository.get_current_matches()
        if timestamp < get_timestamp(datetime.now() - timedelta(hours=1)):
            await bot.report_error('last update more than 1h ago')
        updated_matches = get_updated_matches(current_matches, actual_matches)
        await bot.report_matches(updated_matches)
        now = datetime.now()
        repository.store_matches(now, actual_matches)
    except Exception as exc:
        logger.exception('failed to update state')
        await bot.report_error('failed to update state\n{}'.format(traceback.format_exc()))
        raise UpdateStateException('failed to update state') from exc

def get_updated_matches(current: List[Match], actual: List[Match]) -> List[Match]:
    updates = []
    for new, old in zip_longest(actual, current):
        if old is None and new.is_available():
            updates.append(new)
        elif len(set(new.available_categories) - set(old.available_categories)) > 0:
            updates.append(new)
    return updates


if __name__ == '__main__':
    asyncio.run(main())
