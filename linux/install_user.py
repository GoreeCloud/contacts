#!/usr/bin/env python3
"""Guarded, per-user native GTK app installation (no root privileges).

Never touches personal Contacts SQLite data or upgrades an existing install.
Reinstall/upgrade requires deliberate review; this script refuses overwrites.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import shutil
import stat
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "goreecloud_contacts"
APP_ID = "org.goreecloud.Contacts"


def safe_new_file(path: Path, contents: str, mode: int):
    """Exclusively create one private file, removing any incomplete write on failure.

    Existing files are never opened or overwritten. A failed flush/fsync must
    not leave an executable or desktop entry with truncated contents.
    """
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = None
    created = False
    try:
        fd = os.open(path, flags, mode)
        created = True
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            fd = None  # File object now owns the descriptor.
            handle.write(contents)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        if created:
            try:
                path.unlink()
            except OSError:
                # Propagate the original failure; the installer can still report
                # an incomplete entry that requires manual review.
                raise RuntimeError("Incomplete installer file could not be removed")
        raise


def install(data_root: Path, bin_root: Path):
    data_root = Path(os.path.abspath(os.fspath(data_root)))
    bin_root = Path(os.path.abspath(os.fspath(bin_root)))
    if any(p.is_symlink() for p in (data_root,bin_root)):
        raise ValueError("Refusing symlinked installation directories")
    app_parent = data_root / "goreecloud"
    destination = app_parent / "contacts-linux"
    desktop_dir = data_root / "applications"
    desktop = desktop_dir / (APP_ID + ".desktop")
    launcher = bin_root / "goreecloud-contacts"
    cli_launcher = bin_root / "goreecloud-contacts-cli"
    if any(path.exists() or path.is_symlink()
           for path in (destination,desktop,launcher,cli_launcher)):
        raise ValueError("Existing Contacts installation detected; no files were overwritten")
    for path in (app_parent,desktop_dir,bin_root):
        path.mkdir(parents=True,exist_ok=True,mode=0o700)
        info=path.stat(follow_symlinks=False)
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
            raise ValueError("Installation directories must belong to this user")
        if path.is_symlink():
            raise ValueError("Refusing symlinked installation directory")
    if not SOURCE.is_dir() or any(p.is_symlink() for p in SOURCE.rglob("*")):
        raise ValueError("Source directory invalid or contains a symlink")
    stage = Path(tempfile.mkdtemp(prefix=".contacts-stage-",dir=app_parent))
    created = []
    try:
        shutil.copytree(SOURCE,stage/"goreecloud_contacts",
                        ignore=shutil.ignore_patterns("__pycache__","*.pyc"),
                        symlinks=False)
        os.chmod(stage,0o700)
        os.rename(stage,destination)
        created.append(destination)
        quoted = shlex.quote(str(destination))
        wrapper = ("#!/bin/sh\n" +
                   "export PYTHONPATH=" + quoted + "\n" +
                   "exec /usr/bin/python3 -m goreecloud_contacts.app \"$@\"\n")
        safe_new_file(launcher,wrapper,0o700)
        created.append(launcher)
        cli_wrapper = ("#!/bin/sh\n" +
                       "export PYTHONPATH=" + quoted + "\n" +
                       "exec /usr/bin/python3 -m goreecloud_contacts.cli \"$@\"\n")
        safe_new_file(cli_launcher,cli_wrapper,0o700)
        created.append(cli_launcher)
        text = (
            "[Desktop Entry]\nType=Application\nName=GoreeCloud Contacts\n"
            "GenericName=Contact Manager\nComment=Private offline-first personal contacts\n"
            'Exec="' + str(launcher).replace("\\","\\\\").replace('"','\\"') + '"\n'
            "Terminal=false\nIcon=" + str(destination / "goreecloud_contacts" / "assets" / "logo.svg") + "\nCategories=Office;Utility;\n"
            "StartupNotify=true\n"
        )
        safe_new_file(desktop,text,0o600)
        created.append(desktop)
    except Exception:
        # Roll back new installation files only. Do not touch Contacts data.
        for item in reversed(created):
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink(missing_ok=True)
        if stage.exists():
            shutil.rmtree(stage)
        raise
    print("Installed GoreeCloud Contacts GTK and offline CLI launchers and desktop entry.")
    print("Personal contact data was not read, moved or deleted.")


def main(argv=None):
    parser=argparse.ArgumentParser(description="Install standalone GoreeCloud Contacts native Linux preview")
    parser.add_argument("--data-root",type=Path,default=Path(os.environ.get(
        "XDG_DATA_HOME",str(Path.home()/".local"/"share"))))
    parser.add_argument("--bin-root",type=Path,default=Path(os.environ.get(
        "XDG_BIN_HOME",str(Path.home()/".local"/"bin"))))
    args=parser.parse_args(argv)
    try:
        install(args.data_root,args.bin_root)
    except (OSError,ValueError) as error:
        parser.exit(1,"Contacts installation refused: "+str(error)+"\n")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
