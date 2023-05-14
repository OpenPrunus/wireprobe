import datetime
import os
import time
from .Config.Config import Config
from .Notifications.Telegram import Telegram


class HealthCheck:
    """
    HealthCheck class
    """
    is_connected_client_list = {}
    client_list = {}
    interfaces = []
    timeout = 1
    frequency_check = 5
    telegram = None

    def __init__(self, settings_file=""):
        """
        Construct HealthCheck Object
        :param settings_file: Path to the setting file
        :return:
        """
        if not settings_file:
            settings_file = config_path=os.path.join(os.path.dirname(__file__), "../settings.yml")
        settings = Config.load_yaml_config(config_path=settings_file)
        self.timeout = settings['settings']["timeout"]
        self.frequency_check = settings["settings"]["frequency_check"]
        self.client_list = {v: k for k, v in settings["settings"]["clients"].items()}
        for client in self.client_list:
            self.is_connected_client_list[self.client_list[client]] = False
        self.telegram = Telegram(settings_file)
        self.interfaces = settings['settings']['interfaces']
        print(self.client_list)
        print(self.is_connected_client_list)

    def check(self):
        """
        Check method
        :return:
        """

        while True:
            time.sleep(self.frequency_check)
            for current_interface in self.interfaces:
                result = os.popen("wg show {interface} dump | tail -n +2".format(interface=current_interface)).readlines()

                for line in result:
                    result_line_list = line.split("\t")
                    print(result_line_list[5])
                    if result_line_list[3] not in self.client_list:
                        continue
                    current_client_name = self.client_list[result_line_list[3]]
                    print("current client : " + current_client_name)
                    now = datetime.datetime.now()
                    last_seen = datetime.datetime.fromtimestamp(int(result_line_list[4]))
                    d1_ts = time.mktime(now.timetuple())
                    d2_ts = time.mktime(last_seen.timetuple())
                    minutes_diff = (d1_ts - d2_ts) / 60
                    print(now, last_seen, now - last_seen, minutes_diff)
                    if minutes_diff > self.timeout and self.is_connected_client_list[current_client_name]:
                        self.is_connected_client_list[current_client_name] = False
                        self.telegram.notify_disconnected(client_name=current_client_name)
                    elif minutes_diff < self.timeout and not self.is_connected_client_list[current_client_name]:
                        self.is_connected_client_list[current_client_name] = True
                        self.telegram.notify_connected(client_name=current_client_name)
