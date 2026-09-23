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

### Debian package (.deb)

Every [release](https://github.com/OpenPrunus/wireprobe/releases) ships a `.deb` built by CI. It installs the app to `/usr/lib/wireprobe`, a `wireprobe` wrapper to `/usr/bin/wireprobe`, a `wireprobe` systemd service (enabled but not started), and creates the `wireprobe` system user.

You can either download it from a release and install it directly:

```shell
$ sudo apt install ./wireprobe_<version>_all.deb
```

or add the project's APT repository, signed and published by CI on GitHub Pages, to get updates via `apt upgrade`. It keeps every released version, so `apt install wireprobe=<version>` also works:

```shell
$ curl -fsSL https://openprunus.github.io/wireprobe/pubkey.gpg | sudo gpg --dearmor -o /usr/share/keyrings/wireprobe.gpg
$ echo "deb [signed-by=/usr/share/keyrings/wireprobe.gpg] https://openprunus.github.io/wireprobe/ stable main" | sudo tee /etc/apt/sources.list.d/wireprobe.list
$ sudo apt update
$ sudo apt install wireprobe
```

Either way, then:

```shell
$ sudo cp /etc/wireprobe/settings.yml.example /etc/wireprobe/settings.yml
# edit /etc/wireprobe/settings.yml with your configuration
$ sudo systemctl start wireprobe
```

Check status and logs with `systemctl status wireprobe` and `journalctl -u wireprobe -f`.

### Debian (dependencies for a pip install)

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

## Testing

```shell
$ python3 -m pip install -r requirements.txt pytest
$ pytest -v
```

Unit tests live in `tests/unit`, functional (end-to-end) tests in `tests/functional`. Both run in CI on every push/PR to `main`.

## Running as a systemd service (manual / pip install)

If you installed from PyPI or a source checkout instead of the `.deb` (which already wires this up, see above), a unit file is provided in [packaging/systemd/wireprobe.service](packaging/systemd/wireprobe.service).

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