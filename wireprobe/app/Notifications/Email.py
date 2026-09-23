import os
import smtplib
from email.message import EmailMessage

from ..Config.Config import Config
from .Base import Notifier


class Email(Notifier):
    """
    Email notification class
    """
    subject = "Wireprobe notification"
    smtp_host = ""
    smtp_port = 587
    use_tls = True
    username = ""
    password = ""
    from_addr = ""
    to_addrs = []
    logger = None

    def __init__(self, settings_file, logger=None):
        """
        Constructor Email
        :param settings_file: Path to the setting file
        :param logger: logger instance
        """
        self.logger = logger
        if not settings_file:
            settings = Config.load_yaml_config(config_path=os.path.join(os.path.dirname(__file__), "settings.yml"))
        else:
            settings = Config.load_yaml_config(config_path=settings_file)
        email_settings = settings['settings']['email']
        self.smtp_host = email_settings['smtp_host']
        self.smtp_port = email_settings.get('smtp_port', 587)
        self.use_tls = email_settings.get('use_tls', True)
        self.username = email_settings.get('username', "")
        self.password = email_settings.get('password', "")
        self.from_addr = email_settings['from_addr']
        to_addrs = email_settings['to_addrs']
        self.to_addrs = [to_addrs] if isinstance(to_addrs, str) else to_addrs
        self.logger.debug("smtp_host = {smtp_host}\n"
                          "smtp_port = {smtp_port}\n"
                          "from_addr = {from_addr}\n"
                          "to_addrs = {to_addrs}".format(
                            smtp_host=self.smtp_host,
                            smtp_port=self.smtp_port,
                            from_addr=self.from_addr,
                            to_addrs=self.to_addrs))

    def send_notification(self, message):
        """
        Notify method
        :param message: Message to send by email
        :return:
        """
        email_message = EmailMessage()
        email_message['Subject'] = self.subject
        email_message['From'] = self.from_addr
        email_message['To'] = ", ".join(self.to_addrs)
        email_message.set_content(message)

        smtp_class = smtplib.SMTP_SSL if self.smtp_port == 465 else smtplib.SMTP
        with smtp_class(self.smtp_host, self.smtp_port) as smtp:
            if self.use_tls and self.smtp_port != 465:
                smtp.starttls()
            if self.username:
                smtp.login(self.username, self.password)
            smtp.send_message(email_message)
        self.logger.info("Email notification sent to {to_addrs}".format(to_addrs=self.to_addrs))
