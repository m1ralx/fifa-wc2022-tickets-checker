import os
from typing import List

from telegram import InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder

from models import Match


class Bot:
    READ_TIMEOUT = 60
    WRITE_TIMEOUT = 60
    CONNECT_TIMEOUT = 60

    def __init__(self, ):
        token = os.getenv('API_TOKEN')
        self._bot = ApplicationBuilder().token(token).build().bot
        self._user_id = os.getenv('USER_ID')
        self._channel_id = os.getenv('CHAT_ID')

    async def _send_message_to_user(self, text: str, keyboard: InlineKeyboardMarkup = None):
        await self._send_message(self._user_id, text, keyboard)

    async def _send_message_to_channel(self, text: str, keyboard: InlineKeyboardMarkup = None):
        await self._send_message(self._channel_id, text, keyboard)

    async def _send_message(self, recipient_id: int, text: str, keyboard: InlineKeyboardMarkup = None):
        await self._bot.send_message(
            recipient_id,
            text,
            parse_mode='MarkdownV2',
            reply_markup=keyboard,
            read_timeout=self.READ_TIMEOUT,
            write_timeout=self.WRITE_TIMEOUT,
            connect_timeout=self.CONNECT_TIMEOUT,
        )

    async def report_error(self, error: str):
        await self._send_message_to_user('```\nTicketsChecker got error:\n{}```'.format(error))
    
    async def report_matches(self, matches: List[Match]):
        report_func = self._send_message_to_user
        if os.getenv('SEND_TO_CHANNEL') == 'true':
            report_func = self._send_message_to_channel
        for m in matches:
            await report_func(f'`Update for match №{m.match_number}`', m.as_keyboard())
