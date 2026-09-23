import logging
from unittest.mock import MagicMock, patch

from app.Notifications.Telegram import Telegram


def make_settings_file(tmp_path):
    config_file = tmp_path / "settings.yml"
    config_file.write_text(
        "settings:\n"
        "  telegram:\n"
        "    bot_token: \"123:ABC\"\n"
        "    chat_id: \"42\"\n"
    )
    return str(config_file)


def test_init_reads_bot_token_and_chat_id(tmp_path):
    telegram = Telegram(make_settings_file(tmp_path), logging.getLogger("test"))

    assert telegram.bot_token == "123:ABC"
    assert telegram.chat_id == "42"


@patch("app.Notifications.Telegram.urllib.request.urlopen")
def test_send_notification_posts_expected_payload(mock_urlopen, tmp_path):
    mock_response = MagicMock()
    mock_response.read.return_value = b"ok"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    telegram = Telegram(make_settings_file(tmp_path), logging.getLogger("test"))
    telegram.send_notification("hello world")

    called_url, called_data = mock_urlopen.call_args[0]
    assert called_url == "https://api.telegram.org/bot123:ABC/sendMessage"
    assert b"chat_id=42" in called_data
    assert b"text=hello" in called_data


@patch("app.Notifications.Telegram.urllib.request.urlopen")
def test_notify_connected_sends_formatted_message(mock_urlopen, tmp_path):
    mock_response = MagicMock()
    mock_response.read.return_value = b"ok"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    telegram = Telegram(make_settings_file(tmp_path), logging.getLogger("test"))
    telegram.notify_connected(client_name="alice")

    called_data = mock_urlopen.call_args[0][1]
    assert b"tunnel+is+up" in called_data
