# wireprobe

A WireGuard tunnel health probe. Monitors `wg show <iface> dump` handshakes
and notifies via Telegram/email when a client's tunnel goes up or down.

## Layout

- `wireprobe/` — the actual package + `fabfile.py`. Entry point is `fab run`,
  invoked from *inside* this directory (fab auto-discovers `fabfile.py` in
  cwd, and `fabfile.py` imports `app.HealthCheck` as a top-level `app`
  package, not `wireprobe.app`).
- `wireprobe/app/HealthCheck.py` — main loop (`check()`) / single-pass logic
  (`check_once()`, extracted for testability).
- `wireprobe/app/Notifications/` — `Base.Notifier` (shared connect/disconnect
  formatting), `Telegram`, `Email`. Both are optional in `settings.yml`;
  `HealthCheck` instantiates whichever sections are present.
- `tests/unit/`, `tests/functional/` — pytest, run via `pytest -v` from repo
  root (`pytest.ini` sets `pythonpath = wireprobe`).
- `packaging/systemd/` — unit for a manual/pip install.
- `packaging/deb/` — `build.sh <version> <output-dir>` builds a `.deb` via
  `fpm` (staging dir → `/usr/lib/wireprobe`, `/usr/bin/wireprobe` wrapper,
  `/etc/wireprobe`, systemd unit, postinst/prerm for the `wireprobe` system
  user).
- `packaging/apt/` — `aptly`-based signed APT repo, published to `gh-pages`
  by `.github/workflows/publish-apt-repo.yml`. See
  `packaging/apt/README.md` for the one-time GPG key / Pages setup (repo
  owner only — never handle that private key in an agent session).

## Commands

```shell
python3 -m pip install -r requirements.txt pytest flake8
pytest -v
flake8 wireprobe --count --select=E9,F63,F7,F82 --show-source --statistics
./packaging/deb/build.sh 0.0.0-test /tmp/out   # needs fpm (ruby gem)
```

## CI (`.github/workflows/`)

- `ci.yml` — lint, tests, `python -m build`, `.deb` build validation (once,
  py3.12 leg only) on every push/PR to `main`.
- `python-publish.yml` — on release published: publish to PyPI, build the
  `.deb` and attach it to the release.
- `publish-apt-repo.yml` — on release published or manual `workflow_dispatch`:
  rebuilds the whole APT repo from the current release's `.deb` + every
  `.deb` ever attached to a past release (GitHub Releases is the durable
  source of truth; nothing about the repo state persists between CI runs),
  signs it, force-pushes to `gh-pages`.

## Known gotchas (hit these already, don't re-debug from scratch)

- `reprepro` cannot hold multiple versions of the same package in one
  distribution (`includedeb` replaces); that's why this repo uses `aptly`
  instead, which can.
- `reprepro`/`aptly` both reject a bare `Architectures: all` — need a real
  arch too (`amd64 arm64` here), since the packages are `Architecture: all`.
- `actions/checkout` defaults to a shallow, tag-less clone. Any step that
  needs `git describe --tags` (manual-run version detection here) needs
  `fetch-depth: 0`. A failed `git describe` inside `x=$(cmd)` does **not**
  trip `set -e` — check the exit status explicitly (`if ! x=$(cmd); then`).
- GPG signing in CI needs loopback pinentry (`allow-loopback-pinentry` in
  `gpg-agent.conf`, `pinentry-mode loopback` in `gpg.conf`) — headless
  runners have no interactive pinentry, and signing fails with
  `gpg: skipped ...: Unusable secret key` otherwise.
- `gpg --list-secret-keys <email>` matches *every* key with that email in
  the keyring, not just the one you just generated. Filter by the key's
  name/comment instead, and sanity-check there's exactly one match before
  exporting — a stale/expired key silently winning this lookup is exactly
  what caused the "Unusable secret key" failure above, twice.
