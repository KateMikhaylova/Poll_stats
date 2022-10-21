from telethon import TelegramClient
from telethon.tl.types import Channel, Message, MessageMediaPoll
from telethon.tl.functions.messages import GetHistoryRequest

from typing import List, Dict, NoReturn, Optional, Union

import sys
from math import floor


class PollStats:
    def __init__(self, client: TelegramClient):
        """
        :param client: TelegramClient
        """
        self.client = client
        self.channel = None
        self.chat = 'me'

    def get_channels(self) -> Optional[NoReturn]:
        """
        Saves PythonTalk entity to channel attribute and PythonTalk Chat entity to chat attribute
        :return: None
        """
        for dialog in self.client.iter_dialogs():
            if type(dialog.entity) == Channel and dialog.entity.id == 1659266585:
                self.chat = dialog.entity
            if type(dialog.entity) == Channel and dialog.entity.id == 1434699043:
                self.channel = dialog.entity
        if self.channel is None:
            print('Вы не подписаны на канал PythonTalk')
            sys.exit()

    async def get_polls(self) -> List[Message]:
        """
        Gets all quizzes from PythonTalk channel
        :return: list of telegram messages
        """
        offset_msg = 0
        limit_msg = 100

        polls = []

        while True:
            history = await self.client(GetHistoryRequest(peer=self.channel,
                                                          offset_id=offset_msg,
                                                          offset_date=None,
                                                          add_offset=0,
                                                          limit=limit_msg,
                                                          max_id=0,
                                                          min_id=0,
                                                          hash=0
                                                          ))

            if not history.messages:
                return polls

            messages = history.messages
            for message in messages:
                if type(message) == Message and type(message.media) == MessageMediaPoll and message.media.poll.quiz:
                    polls.append(message)

            offset_msg = messages[-1].id

    def calculate_result(self, polls_list: List[Message]) -> Union[Dict[str, int], NoReturn]:
        """
        Calculates quantity of answered quizzes and quantity of correctly answered quizzes
        :param polls_list: list of telegram messages
        :return: dict with results
        """
        total_answers = 0
        correct_answers = 0

        for poll in polls_list:
            if poll.media.results and poll.media.results.results:
                total_answers += 1
                correct = True
                for option in poll.media.results.results:
                    if option.chosen != option.correct:
                        correct = False
                if correct:
                    correct_answers += 1

        if not total_answers:
            print('Вы еще не поучаствовали ни в одной викторине')
            sys.exit()

        return {'total': total_answers, 'correct': correct_answers}

    def create_template(self, result: Dict[str, int]) -> str:
        """
        Creates text template based on results
        :param result: dict with total answered and total correct info
        :return: template string to be sent
        """
        grade = floor((result['correct'] / result['total']) * 10)

        templates = {0: 'Я начинающий, но очень перспективный разработчик/аналитик. Пожелайте мне удачи.',
                     1: 'Я учусь изо всех сил. Уже скоро улучшу результат',
                     2: 'Я хорошо изучил уже несколько тем, чем дальше, тем больше будет правильных ответов',
                     3: 'Я с питоном все еще на "вы", но кое-что знаю и умею.',
                     4: 'Я много стараюсь, и получается уже совсем неплохо.',
                     5: 'Я уже за экватором изучения питона.',
                     6: 'Я упорно двигаюсь к цели, правильных ответов уже прилично больше половины',
                     7: 'Я с питоном уже на "ты", но он все еще может меня удивить.',
                     8: 'Я очень близко к идеалу. Пару тем подтянуть и готово!',
                     9: 'Я знаю все! Всего-то пару раз случайно не туда нажалось. Честно!',
                     10: 'Я Олег Булыгин🙂, если это не мой акк, поздравляю, вы меня раскрыли.'}

        if (result['total']) >= 10:
            return f'''Из {result["total"]} квизов {result["correct"]} правильно🙂.\n{templates[grade]}'''

        else:
            templates[10] = '100% ответов правильно, но это меньше, чем за половину квизов.\nНадо перепроверить, когда отвечу на все'
            return f'''Из {result["total"]} квизов {result["correct"]} правильно🙂.\n{templates[grade]}'''

    async def send_result(self, text: str) -> None:
        """
        Sends result message to PythonTalk Chat, if user is in it, otherwise to user saved messages
        :param text: result template
        :return: None
        """
        await self.client.send_message(self.chat, text)
