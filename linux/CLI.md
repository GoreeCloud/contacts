# GoreeCloud Contacts — offline Linux CLI (development)

The **GoreeCloud Contacts CLI** works with the same user-private SQLite database as the native GTK4 Linux client. No server, account login, Android Contacts Provider, telemetry, background job, networking or automatic synchronization is used. Commands are explicit and synchronous.

Run from the repository root with `PYTHONPATH=linux /usr/bin/python3 -m goreecloud_contacts.cli` followed by the command below, or use the guarded user installer `python3 linux/install_user.py` to install `~/.local/bin/goreecloud-contacts-cli` alongside the GTK launcher (the installer refuses overwrites).

| Command | Purpose | Consent |
| --- | --- | --- |
| `status` | Count local contacts and favorites; no contact details printed | None |
| `check` | Check SQLite integrity and validate portable fields | None |
| `verify-backup --input /trusted/file.json` | Validate JSON format v1, without opening the database | None |
| `verify-vcard --input /trusted/file.vcf` | Validate limited vCard 3.0, without opening the database | None |
| `preflight-restore --input /trusted/file.json` | Check JSON ID conflicts and capacity against existing private SQLite with no import | None |
| `preflight-vcard --input /trusted/file.vcf` | Check limited vCard visible-detail duplicates and capacity without importing | None |
| `backup --output /private/new-backup.json --acknowledge-plaintext` | Exclusive-create private JSON backup | Explicit acknowledgement |
| `export-vcard --output /private/new-contacts.vcf --acknowledge-plaintext` | Exclusive-create limited vCard | Explicit acknowledgement |
| `restore --input /trusted/file.json --yes` | Atomic import; refuses duplicate IDs and never overwrites | Explicit action |
| `import-vcard --input /trusted/file.vcf --yes --accept-limited-fields` | Atomic strict import; rejects unsupported rich properties and duplicate visible records | Explicit consent to limited format |

The `--db /private/data/contacts.sqlite3` global option must precede the command, for testing or a deliberately chosen local private store. Omit it to use the desktop client’s normal XDG location. `status` and `check` initialize the local private store if none exists; file-only `verify-*` commands do **not** create or open SQLite. The CLI returns a nonzero exit code and a general error without printing raw contact data on failure. Preflight checks inputs before opening private storage. If the database is absent, no directory or SQLite database is created; if present, it is opened SQLite read-only, without schema DDL or contact mutation. Only aggregate incoming/existing counts are printed. Preflight can become stale if another process edits the directory; the final import repeats checks within a write transaction.

**Privacy:** JSON backups and vCards are plaintext, despite owner-only (0600) creation. Use trusted encrypted storage for archives; never upload them to an untrusted service. Exports refuse existing filenames or symlinks, require an explicit acknowledgement, and never overwrite files. The local SQLite database is not encrypted by this application. Names, phones, emails and organizations are personally identifying data—avoid placing their values in terminal command-line arguments, shell history or logs. The CLI deliberately does not expose add/edit commands that would require sensitive values on a command line.

**Interoperability:** JSON v1 preserves exactly the six portable fields, including favorite flags. The limited vCard export/import profile covers one name, phone, email, and organization and **does not retain favorites** or rich contacts. Rich vCard properties are rejected rather than silently discarded. The native Android app remains a separate permission-gated Contacts Provider client; there is no shared live directory or CardDAV/Mesh integration.

**Development tests:** run `PYTHONPATH=linux /usr/bin/python3 -m unittest discover -s linux/tests -p 'test_*.py'`. The CLI subprocess tests use disposable synthetic contacts and check explicit consent, private file modes, conflict rollback, symlink refusal, no inadvertent database creation during file verification, and absence of PII in error messages. The installed GTK/XDG smoke also executes the installed CLI launcher against a disposable SQLite database.

**Release maturity:** development source and automated tests, not an installed or signed Stable release. Back up your data before manually updating the source; future migrations require independent review, backup/restore testing, and acceptance.
