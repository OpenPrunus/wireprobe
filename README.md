# wireprobe
A Wireguard Probe

## Installation

### Pypi

```shell
$ python3 -m pip install wireprobe
```

and upgrading

```shell
$ python3 -m pip install wireprobe -U
```

### Debian

```shell
$ sudo apt install python3-urllib3 python3-requests python3-decorator python3-fabric python3-invoke python3-pyyaml-env-tag
```

### Python pip
```shell
python3 -m pip install -r requiremments
```

## Usage

```shell
$ mv wireprobe/settings.yml.example wireprobe/settings.yml
```

Set your configrations in `wireprobe/settings.yml`

```shell
$ cd wireprobe
$ fab run
```

For INFO logs

```shell
$ cd wireprobe
$ fab run -l 20
```

You can also set a different path for settings.yml

```shell
$ cd wireprobe
$ fab run -s /path/to/settings.yml
```

## Help

```shell
$ fab --help run
```

## Running as a systemd service

A unit file is provided in [packaging/systemd/wireprobe.service](packaging/systemd/wireprobe.service).

```shell
$ sudo useradd --system --no-create-home wireprobe
$ sudo mkdir -p /opt/wireprobe /etc/wireprobe
$ sudo cp -r . /opt/wireprobe
$ sudo python3 -m venv /opt/wireprobe/venv
$ sudo /opt/wireprobe/venv/bin/pip install -r /opt/wireprobe/requirements.txt fabric
$ sudo cp wireprobe/settings.yml.example /etc/wireprobe/settings.yml
# edit /etc/wireprobe/settings.yml with your configuration
$ sudo chown -R wireprobe:wireprobe /opt/wireprobe /etc/wireprobe
$ sudo cp packaging/systemd/wireprobe.service /etc/systemd/system/
$ sudo systemctl daemon-reload
$ sudo systemctl enable --now wireprobe
```

Check status and logs with `systemctl status wireprobe` and `journalctl -u wireprobe -f`.