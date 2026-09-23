import logging
from unittest.mock import MagicMock, patch

from app.Notifications.Email import Email


def make_settings_file(tmp_path, extra=""):
    config_file = tmp_path / "settings.yml"
    config_file.write_text(
        "settings:\n"
        "  email:\n"
        "    smtp_host: \"smtp.example.com\"\n"
        "    from_addr: \"wireprobe@example.com\"\n"
        "    to_addrs:\n"
        "      - \"admin@example.com\"\n" + extra
    )
    return str(config_file)


def test_init_defaults(tmp_path):
    email = Email(make_settings_file(tmp_path), logging.getLogger("test"))

    assert email.smtp_host == "smtp.example.com"
    assert email.smtp_port == 587
    assert email.use_tls is True
    assert email.from_addr == "wireprobe@example.com"
    assert email.to_addrs == ["admin@example.com"]


def test_init_coerces_single_to_addr_string(tmp_path):
    config_file = tmp_path / "settings.yml"
    config_file.write_text(
        "settings:\n"
        "  email:\n"
        "    smtp_host: \"smtp.example.com\"\n"
        "    from_addr: \"wireprobe@example.com\"\n"
        "    to_addrs: \"admin@example.com\"\n"
    )

    email = Email(str(config_file), logging.getLogger("test"))

    assert email.to_addrs == ["admin@example.com"]


@patch("app.Notifications.Email.smtplib.SMTP")
def test_send_notification_uses_starttls_by_default(mock_smtp, tmp_path):
    smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp_instance

    email = Email(
        make_settings_file(tmp_path, "    username: \"user\"\n    password: \"pass\"\n"),
        logging.getLogger("test"),
    )
    email.send_notification("hello world")

    mock_smtp.assert_called_once_with("smtp.example.com", 587)
    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_called_once_with("user", "pass")
    sent_message = smtp_instance.send_message.call_args[0][0]
    assert sent_message["From"] == "wireprobe@example.com"
    assert sent_message["To"] == "admin@example.com"
    assert sent_message.get_content().strip() == "hello world"


@patch("app.Notifications.Email.smtplib.SMTP_SSL")
def test_send_notification_uses_ssl_on_port_465(mock_smtp_ssl, tmp_path):
    smtp_instance = MagicMock()
    mock_smtp_ssl.return_value.__enter__.return_value = smtp_instance

    email = Email(make_settings_file(tmp_path, "    smtp_port: 465\n"), logging.getLogger("test"))
    email.send_notification("hello world")

    mock_smtp_ssl.assert_called_once_with("smtp.example.com", 465)
    smtp_instance.starttls.assert_not_called()


@patch("app.Notifications.Email.smtplib.SMTP")
def test_send_notification_skips_login_without_username(mock_smtp, tmp_path):
    smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = smtp_instance

    email = Email(make_settings_file(tmp_path), logging.getLogger("test"))
    email.send_notification("hello world")

    smtp_instance.login.assert_not_called()
