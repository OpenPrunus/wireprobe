# wireprobe
A Wireguard Probe

## Installation

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
$ mv fabfile/settings.yml.example fabfile/settings.yml
```

Set your configrations in `fabile/settings.yml`

```shell
$ fab run
```

You can also set a different path for settings.yml

```shell
$ fab run -s /path/to/settings.yml
```

## Help

```shell
$ fab --help run
```