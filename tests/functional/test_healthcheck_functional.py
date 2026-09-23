import datetime
import time
from unittest.mock import MagicMock, patch

from app.HealthCheck import HealthCheck

SETTINGS = (
    "settings:\n"
    "  interfaces:\n"
    "    - wg0\n"
    "  frequency_check: 5\n"
    "  timeout: 1\n"
    "  clients:\n"
    "    alice: \"10.0.0.2/32\"\n"
    "  telegram:\n"
    "    bot_token: \"123:ABC\"\n"
    "    chat_id: \"42\"\n"
    "  email:\n"
    "    smtp_host: \"smtp.example.com\"\n"
    "    from_addr: \"wireprobe@example.com\"\n"
    "    to_addrs:\n"
    "      - \"admin@example.com\"\n"
)


def wg_dump_line(allowed_ip, handshake_ts):
    fields = [
        "pubkey==",
        "psk==",
        "10.1.2.3:51820",
        allowed_ip,
        str(handshake_ts),
        "1024",
        "2048",
        "off",
    ]
    return "\t".join(fields) + "\n"


def build_health_check(tmp_path):
    config_file = tmp_path / "settings.yml"
    config_file.write_text(SETTINGS)
    return HealthCheck(settings_file=str(config_file))


@patch("app.HealthCheck.os.popen")
@patch("app.Notifications.Email.smtplib.SMTP")
@patch("app.Notifications.Telegram.urllib.request.urlopen")
def test_client_connect_and_disconnect_triggers_all_notifiers(mock_urlopen, mock_smtp, mock_popen, tmp_path):
    mock_response = MagicMock()
    mock_response.read.return_value = b"ok"
    mock_urlopen.return_value.__enter__.return_value = mock_response
    smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp_instance

    health_check = build_health_check(tmp_path)

    now_ts = int(time.mktime(datetime.datetime.now().timetuple()))
    mock_popen.return_value.readlines.return_value = [wg_dump_line("10.0.0.2/32", now_ts)]

    health_check.check_once()

    assert health_check.is_connected_client_list["alice"] is True
    assert mock_urlopen.call_count == 1
    assert b"tunnel+is+up" in mock_urlopen.call_args[0][1]
    connect_message = smtp_instance.send_message.call_args[0][0]
    assert "tunnel is up" in connect_message.get_content()

    old_ts = now_ts - (60 * 10)
    mock_popen.return_value.readlines.return_value = [wg_dump_line("10.0.0.2/32", old_ts)]

    health_check.check_once()

    assert health_check.is_connected_client_list["alice"] is False
    assert mock_urlopen.call_count == 2
    assert b"seems+down" in mock_urlopen.call_args[0][1]
    disconnect_message = smtp_instance.send_message.call_args[0][0]
    assert "potentially seems down" in disconnect_message.get_content()


@patch("app.HealthCheck.os.popen")
@patch("app.Notifications.Email.smtplib.SMTP")
@patch("app.Notifications.Telegram.urllib.request.urlopen")
def test_unknown_peer_is_ignored(mock_urlopen, mock_smtp, mock_popen, tmp_path):
    mock_response = MagicMock()
    mock_response.read.return_value = b"ok"
    mock_urlopen.return_value.__enter__.return_value = mock_response
    smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp_instance

    health_check = build_health_check(tmp_path)

    now_ts = int(time.mktime(datetime.datetime.now().timetuple()))
    mock_popen.return_value.readlines.return_value = [wg_dump_line("10.0.0.99/32", now_ts)]

    health_check.check_once()

    assert health_check.is_connected_client_list["alice"] is False
    mock_urlopen.assert_not_called()
    smtp_instance.send_message.assert_not_called()
