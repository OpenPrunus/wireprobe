from app.HealthCheck import HealthCheck
from app.Notifications.Telegram import Telegram
from app.Notifications.Email import Email

BASE_SETTINGS = (
    "settings:\n"
    "  interfaces:\n"
    "    - wg0\n"
    "  frequency_check: 5\n"
    "  timeout: 1\n"
    "  clients:\n"
    "    alice: \"10.0.0.2/32\"\n"
)

TELEGRAM_SETTINGS = (
    "  telegram:\n"
    "    bot_token: \"123:ABC\"\n"
    "    chat_id: \"42\"\n"
)

EMAIL_SETTINGS = (
    "  email:\n"
    "    smtp_host: \"smtp.example.com\"\n"
    "    from_addr: \"wireprobe@example.com\"\n"
    "    to_addrs:\n"
    "      - \"admin@example.com\"\n"
)


def write_settings(tmp_path, content):
    config_file = tmp_path / "settings.yml"
    config_file.write_text(content)
    return str(config_file)


def test_no_notification_channel_configured(tmp_path):
    health_check = HealthCheck(settings_file=write_settings(tmp_path, BASE_SETTINGS))

    assert health_check.notifiers == []


def test_only_email_configured(tmp_path):
    health_check = HealthCheck(settings_file=write_settings(tmp_path, BASE_SETTINGS + EMAIL_SETTINGS))

    assert len(health_check.notifiers) == 1
    assert isinstance(health_check.notifiers[0], Email)


def test_only_telegram_configured(tmp_path):
    health_check = HealthCheck(settings_file=write_settings(tmp_path, BASE_SETTINGS + TELEGRAM_SETTINGS))

    assert len(health_check.notifiers) == 1
    assert isinstance(health_check.notifiers[0], Telegram)


def test_both_channels_configured(tmp_path):
    health_check = HealthCheck(
        settings_file=write_settings(tmp_path, BASE_SETTINGS + TELEGRAM_SETTINGS + EMAIL_SETTINGS)
    )

    assert [type(notifier) for notifier in health_check.notifiers] == [Telegram, Email]


def test_is_connected_client_list_is_not_shared_between_instances(tmp_path):
    settings_file = write_settings(tmp_path, BASE_SETTINGS)
    first = HealthCheck(settings_file=settings_file)
    first.is_connected_client_list["alice"] = True

    second = HealthCheck(settings_file=settings_file)

    assert second.is_connected_client_list["alice"] is False
