import urllib.request
import urllib.parse
import os
from ..Config.Config import Config


class Telegram:
    """
    Telegram notification class
    """
    connect_alert = "🐉 Wireguard: {} is now connected"
    disconnect_alert = "🐉 Wireguard: {} is now disconnected"
    parse_mode = "MarkdownV2"
    bot_token = ""
    chat_id = ""
    url_notify_telegram = "https://api.telegram.org/bot{}/sendMessage"

    def __init__(self, settings_file):
        """
        Constructor Telegram
        :param bot_token: The token of the bot
        :param chat_id: The chan telegram id
        """
        if not settings_file:
            settings = Config.load_yaml_config(config_path=os.path.join(os.path.dirname(__file__), "settings.yml"))
        else:
            settings = Config.load_yaml_config(config_path=settings_file)
        self.bot_token = settings['settings']['telegram']['bot_token']
        self.chat_id = settings['settings']['telegram']['chat_id']
        print(self.bot_token, self.chat_id)

    def send_notification(self, message):
        """
        Notify method
        :param message: Message to send to telegram
        :return:
        """
        data = urllib.parse.urlencode({'chat_id': self.chat_id, 'text': message, 'parse_mode': self.parse_mode}).encode('ascii')
        with urllib.request.urlopen(self.url_notify_telegram.format(self.bot_token), data) as f:
            print(f.read().decode('utf-8'))

    def notify_connected(self, client_name):
        """
        Notify connected method to send message connection to telegram
        :param client_name: Name of the client ti display
        :return:
        """
        self.send_notification(self.connect_alert.format(client_name))

    def notify_disconnected(self, client_name):
        """
        Notify disconnected method to send message disconnection to telegram
        :param client_name: Name of the client ti display
        :return:
        """
        self.send_notification(self.disconnect_alert.format(client_name))
