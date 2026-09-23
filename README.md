# wireprobe

[![CI](https://github.com/OpenPrunus/wireprobe/actions/workflows/ci.yml/badge.svg)](https://github.com/OpenPrunus/wireprobe/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/wireprobe.svg)](https://pypi.org/project/wireprobe/)

A Wireguard Probe

## How it works

wireprobe polls the local WireGuard interfaces on a schedule and watches, for
each peer you've told it to care about, how long it's been since that peer's
last handshake. When that goes above a threshold it fires a "disconnected"
notification; when a handshake shows up again within the threshold, it fires
a "connected" one.

Concretely, on every tick:

1. It runs `wg show <interface> dump` for each configured interface — this
   dumps every peer's `AllowedIPs` and the timestamp of its last handshake.
2. For each peer line, it looks up the peer by matching `AllowedIPs` against
   the `clients` map in your config (see [Configuration](#configuration)
   below) — peers not listed there are ignored.
3. It computes `now - last_handshake` in minutes and compares it to
   `timeout`:
   - if it just crossed *above* `timeout` and the client was marked as up,
     it's marked down and every configured notifier fires
     `notify_disconnected`.
   - if it just crossed *below* `timeout` and the client was marked as down
     (which includes "never seen since this process started"), it's marked
     up and every notifier fires `notify_connected`.
4. It sleeps `frequency_check` seconds and repeats — forever, in the
   foreground (that's what the systemd units and `.deb` wrap).

A couple of things worth knowing:

- State is only kept in memory. A restart forgets who was up or down, so the
  first poll after a (re)start can send a spurious "connected" notification
  for every peer that happens to already be within `timeout` — it doesn't
  know that peer didn't just reconnect.
- Notifications go out to *every* channel you've configured (Telegram and/or
  email) on every state change — there's no per-channel filtering.
- Matching is purely on the `AllowedIPs` string reported by `wg show`, so it
  has to match exactly what's in `clients` (see below) — usually the peer's
  tunnel IP with a `/32`.

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

(Maintainers: see [packaging/apt/README.md](packaging/apt/README.md) for how the signing key and GitHub Pages publishing are set up.)

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

## Configuration

```shell
$ mv wireprobe/settings.yml.example wireprobe/settings.yml
```

then edit `wireprobe/settings.yml` (or `/etc/wireprobe/settings.yml` for the
`.deb`/systemd installs). Full example:

```yaml
settings:
  interfaces:
    - wg0                       # every "wg show <iface> dump" to poll
  frequency_check: 30           # seconds between polls
  timeout: 3                    # minutes of handshake silence before a peer is "down"

  clients:
    alice-laptop: "10.20.0.2/32"   # must match AllowedIPs from `wg show wg0 dump`
    bob-phone: "10.20.0.3/32"

  # Both notification channels are optional and independent — configure
  # either one, both, or neither (in which case state changes are only
  # logged, not notified).

  telegram:
    bot_token: "123456789:AAExampleTokenGoesHere"
    chat_id: "-1001234567890"

  email:
    smtp_host: "smtp.example.com"
    smtp_port: 587               # 465 -> implicit TLS (SMTPS); otherwise STARTTLS unless use_tls: false
    use_tls: true
    username: "wireprobe@example.com"   # omit to skip SMTP auth entirely
    password: "app-specific-password"
    from_addr: "wireprobe@example.com"
    to_addrs:                    # a single string also works, not just a list
      - "admin@example.com"
      - "oncall@example.com"
```

Field reference:

| Field | Meaning |
| --- | --- |
| `interfaces` | WireGuard interface names on this host to poll, as `wg show interfaces` lists them. |
| `frequency_check` | Seconds to sleep between polls. |
| `timeout` | Minutes since a peer's last handshake before it's considered disconnected. |
| `clients` | Maps a friendly name to a peer's `AllowedIPs` value — find it with `wg show <iface> dump` or `wg show <iface> allowed-ips`. |
| `telegram.bot_token` / `chat_id` | Create a bot via [@BotFather](https://t.me/BotFather); get the target `chat_id` by messaging the bot and checking `getUpdates`, or via [@userinfobot](https://t.me/userinfobot) for a personal chat. |
| `email.*` | Standard SMTP settings; see the notes above for `smtp_port`/`use_tls`/`username` behavior. |

Once configured:

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