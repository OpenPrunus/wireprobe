from app.Config.Config import Config


def test_load_yaml_config(tmp_path):
    config_file = tmp_path / "settings.yml"
    config_file.write_text("settings:\n  timeout: 5\n  clients:\n    foo: \"10.0.0.2/32\"\n")

    config = Config.load_yaml_config(config_path=str(config_file))

    assert config == {"settings": {"timeout": 5, "clients": {"foo": "10.0.0.2/32"}}}
