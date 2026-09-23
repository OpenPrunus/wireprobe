import pytest

from app.Notifications.Base import Notifier


class RecordingNotifier(Notifier):
    def __init__(self):
        self.sent = []

    def send_notification(self, message):
        self.sent.append(message)


def test_send_notification_not_implemented():
    with pytest.raises(NotImplementedError):
        Notifier().send_notification("hello")


def test_notify_connected_formats_message():
    notifier = RecordingNotifier()

    notifier.notify_connected(client_name="alice")

    assert notifier.sent == ["🐉 Wireguard: alice tunnel is up"]


def test_notify_disconnected_formats_message():
    notifier = RecordingNotifier()

    notifier.notify_disconnected(client_name="alice")

    assert notifier.sent == ["🐉 Wireguard: alice tunnel potentially seems down"]
