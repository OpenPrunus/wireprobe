import logging
import os
import urllib.request
import urllib.parse

from ..Config.Config import Config
from .Base import Notifier


class Telegram(Notifier):
    """
    Telegram notification class
    """
    parse_mode = "MarkdownV2"
    bot_token = ""
    chat_id = ""
    url_notify_telegram = "https://api.telegram.org/bot{bot_token}/sendMessage"
    logger = None

    def __init__(self, settings_file, logger=None):
        """
        Constructor Telegram
        :param bot_token: The token of the bot
        :param chat_id: The chan telegram id
        """
        self.logger = logger
        if not settings_file:
            settings = Config.load_yaml_config(config_path=os.path.join(os.path.dirname(__file__), "settings.yml"))
        else:
            settings = Config.load_yaml_config(config_path=settings_file)
        self.bot_token = settings['settings']['telegram']['bot_token']
        self.chat_id = settings['settings']['telegram']['chat_id']
        self.logger.debug("bot_token = {bot_token}\n"
                          "chat_id = {chat_id}".format(bot_token=self.bot_token, chat_id=self.chat_id))

    def send_notification(self, message):
        """
        Notify method
        :param message: Message to send to telegram
        :return:
        """
        data = urllib.parse.urlencode({'chat_id': self.chat_id, 'text': message, 'parse_mode': self.parse_mode}).encode('ascii')
        with urllib.request.urlopen(self.url_notify_telegram.format(bot_token=self.bot_token), data) as f:
            self.logger.info(f.read().decode('utf-8'))
