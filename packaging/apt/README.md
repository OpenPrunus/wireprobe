# APT repository — one-time setup

The `publish-apt-repo` workflow ([.github/workflows/publish-apt-repo.yml](../../.github/workflows/publish-apt-repo.yml))
builds and signs the APT repo on every published release, and publishes it to
the `gh-pages` branch. It needs a GPG signing key that only the repo owner
should generate — it is never handled by CI beyond importing it from a secret.

It uses `aptly` rather than `reprepro`: `aptly`'s local repo can hold several
versions of the same package at once, so `apt install wireprobe=0.3` keeps
working after `0.4` ships. Since CI runners are stateless, every run rebuilds
the repo from scratch out of the current release's `.deb` plus every `.deb`
attached to a past GitHub release (downloaded via `gh release download`) —
GitHub Releases is the durable source of truth, not any persisted `aptly`
state, so a lost `gh-pages` branch is always fully recoverable by re-running
the workflow.

## 1. Generate the signing key (locally, not in CI)

```shell
$ gpg --batch --passphrase '' --quick-generate-key \
    "wireprobe APT repo <prunus@ecuri.es>" rsa4096 sign never
$ KEY_ID=$(gpg --list-secret-keys --with-colons "wireprobe APT repo" | awk -F: '/^sec/ {print $5; exit}')
$ gpg --armor --export-secret-keys "$KEY_ID" > wireprobe-apt-private.asc
```

`sign never` means the key never expires; adjust if you'd rather rotate it
periodically. The empty passphrase is required so CI can sign non-interactively.

Filter the lookup by the key's name (`"wireprobe APT repo"`), not by the bare
email — if your keyring has other keys sharing that email address (personal
keys, old/expired ones, ...), searching by email matches all of them and
`awk ... exit` silently grabs whichever one `gpg` lists first, which may not
be the key you just generated. Double-check before exporting:

```shell
$ gpg --list-secret-keys --with-colons "wireprobe APT repo"
```

should print exactly one `sec:` line, with `u` (ultimate) as its second
field — not `e` (expired) or anything else.

## 2. Add it as a repository secret

GitHub → repo → Settings → Secrets and variables → Actions → New repository secret:

- Name: `APT_GPG_PRIVATE_KEY`
- Value: the full contents of `wireprobe-apt-private.asc`

Then delete `wireprobe-apt-private.asc` locally (or keep it offline somewhere safe, not in the repo).

## 3. Enable GitHub Pages

The workflow needs to run once (e.g. by publishing a release) to create the
`gh-pages` branch — Pages can't target a branch that doesn't exist yet.
After that first run: Settings → Pages → Source = "Deploy from a branch",
Branch = `gh-pages` / `(root)`.

The repo will then be reachable at `https://openprunus.github.io/wireprobe/`,
matching the URL used in the main [README](../../README.md#debian-package-deb).

## Notes

- To rotate the key: repeat step 1 with a new key, update the
  `APT_GPG_PRIVATE_KEY` secret, and re-publish (or re-run) the workflow —
  `pubkey.gpg` on the site is regenerated from the imported key every run, so
  clients need to re-import it after a rotation.
- Old releases that predate this workflow have no `.deb` asset to pick up;
  the repo's version history starts from whichever release first shipped one.
