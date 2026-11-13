"""GoreeCloud Contacts offline Linux CLI.

Explicit, local-only backup, restore, verification and diagnostics. The CLI never
uses a network, telemetry, external command, Android Contacts Provider or Mesh.
No personal contact values are printed by default.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sqlite3
import sys

from .core import (
    ContactError, ContactStore, check_import, data_location, make_backup,
    make_vcards, read_backup_file, write_new_file,
)
from .vcard import read_vcards_file


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(
        prog="goreecloud-contacts-cli",
        description="Offline GoreeCloud Contacts backup and diagnostics (no account or network access).")
    p.add_argument("--db",type=Path,default=None,
                   help="Explicit private SQLite path; default is the app's XDG contact store")
    commands=p.add_subparsers(dest="action",required=True)
    commands.add_parser("status",help="Show only aggregate local contact and favorite counts")
    commands.add_parser("check",help="Check SQLite database integrity (no contact values printed)")
    for name,description in (
        ("backup","Export private six-field JSON backup (plaintext)"),
        ("export-vcard","Export limited vCard 3.0 (plaintext; favorites are not retained)"),
    ):
        q=commands.add_parser(name,help=description)
        q.add_argument("--output",type=Path,required=True)
        q.add_argument("--acknowledge-plaintext",action="store_true",required=True,
                       help="Confirm the exported file contains unencrypted personal contact details")
    for name,description in (
        ("restore","Restore strict JSON backup into the local store without replacing records"),
        ("import-vcard","Import restricted vCard 3.0; rejects rich fields and duplicate visible records"),
    ):
        q=commands.add_parser(name,help=description)
        q.add_argument("--input",type=Path,required=True)
        q.add_argument("--yes",action="store_true",required=True,
                       help="Confirm writing contacts to the local private store")
        if name=="import-vcard":
            q.add_argument("--accept-limited-fields",action="store_true",required=True,
                           help="Acknowledge that vCard cannot restore favorites or unsupported rich fields")
    for name in ("verify-backup","verify-vcard"):
        q=commands.add_parser(name,help="Validate a file without opening or changing the local database")
        q.add_argument("--input",type=Path,required=True)
    for name, description in (
        ("preflight-restore", "Check JSON conflicts and capacity without importing"),
        ("preflight-vcard", "Check limited vCard conflicts and capacity without importing"),
    ):
        q=commands.add_parser(name,help=description)
        q.add_argument("--input",type=Path,required=True)
    return p


def execute(args: argparse.Namespace) -> str:
    action=args.action
    if action in ("verify-backup","verify-vcard"):
        result=read_backup_file(args.input) if action=="verify-backup" else read_vcards_file(args.input)
        return f"Valid {len(result)} contact records; no local database accessed or modified"
    if action in ("preflight-restore","preflight-vcard"):
        incoming = (read_backup_file(args.input) if action=="preflight-restore"
                    else read_vcards_file(args.input))
        location = data_location(args.db)
        # Preflight of an absent store stays pure: no directory, SQLite file or
        # journal is created, and no private content is printed.
        if location.is_symlink() or location.parent.is_symlink():
            raise ContactError("Unsafe private storage path")
        current=[]
        if location.exists():
            store=ContactStore(location,readonly=True)
            try:
                current=store.list()
            finally:
                store.close()
        count=check_import(incoming,current,
                           reject_visible_duplicates=action=="preflight-vcard")
        kind="Limited vCard" if action=="preflight-vcard" else "JSON"
        return (f"{kind} preflight passed: {count} incoming contacts; "
                f"{len(current)} existing contacts; no import performed. "
                "Recheck required at actual import.")
    if action in ("backup","export-vcard") and not args.acknowledge_plaintext:
        raise ContactError("Export requires --acknowledge-plaintext")
    if action in ("restore","import-vcard") and not args.yes:
        raise ContactError("Import requires --yes")
    if action=="import-vcard" and not args.accept_limited_fields:
        raise ContactError("Limited vCard import requires --accept-limited-fields")

    # Parse untrusted input before opening/creating any private SQLite file.
    incoming=None
    if action=="restore":
        incoming=read_backup_file(args.input)
    elif action=="import-vcard":
        incoming=read_vcards_file(args.input)

    store=ContactStore(args.db)
    try:
        if action=="status":
            values=store.list()
            return f"{len(values)} local contacts; {sum(bool(x['favorite']) for x in values)} favorites"
        if action=="check":
            outcome=store.db.execute("PRAGMA integrity_check").fetchone()
            if not outcome or outcome[0]!="ok":
                raise ContactError("SQLite integrity check failed")
            store.list()  # Also validate every stored contact against the portable schema.
            return "Local SQLite integrity and contact schema: OK"
        if action=="backup":
            content=make_backup(store.list())
            write_new_file(args.output,content)
            return "Private JSON backup created; it is NOT encrypted"
        if action=="export-vcard":
            content=make_vcards(store.list())
            write_new_file(args.output,content)
            return "Limited vCard export created; favorites were NOT included; file is NOT encrypted"
        if action=="restore":
            count=store.import_new(incoming)
            return f"{count} contacts imported atomically (existing IDs never overwritten)"
        if action=="import-vcard":
            count=store.import_new(incoming,reject_visible_duplicates=True)
            return f"{count} limited vCards imported atomically (favorites not restored)"
        raise ContactError("Unsupported local Contacts operation")
    finally:
        store.close()


def main(argv=None) -> int:
    p=parser()
    options=p.parse_args(argv)
    try:
        message=execute(options)
    except (ContactError,sqlite3.Error,UnicodeError,OSError,ValueError):
        # No private contact fields, path, raw SQL exception or imported file content
        # should flow into terminal logs on errors.
        print("Contacts operation refused or failed; existing data was not intentionally replaced. "
              "Check local permissions, input format and contact conflicts.",file=sys.stderr)
        return 1
    print(message)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
