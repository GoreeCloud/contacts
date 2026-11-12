#!/usr/bin/env python3
"""Installed native Contacts launcher smoke under disposable XDG paths.

Uses the real per-user installer and GTK4 executable under Xvfb, with desktop
portals disabled ONLY for headless CI so a host portal's own D-Bus/FUSE services
cannot stall application activation. No account, personal data, network service,
or persistent installation is touched.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import signal
import sqlite3
import stat
import subprocess
import tempfile
import time

from install_user import install
from goreecloud_contacts.core import ContactStore, new_contact


def launch_and_verify(launcher: Path, environment: dict, db: Path, expected: int):
    process = subprocess.Popen(
        ["xvfb-run", "-a", str(launcher)],
        env=environment, cwd=str(launcher.parent.parent),
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, start_new_session=True,
    )
    try:
        deadline = time.monotonic() + 18
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise AssertionError("Installed native Contacts executable exited unexpectedly")
            if db.is_file():
                with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as connection:
                    try:
                        count=connection.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
                    except sqlite3.OperationalError:
                        count=None  # The app may still be finishing schema initialization.
                if count == expected:
                    break
            time.sleep(0.15)
        else:
            raise AssertionError("Installed GTK app did not open the expected private SQLite store")
        assert process.poll() is None, "GTK app exited after opening its local store"
        time.sleep(0.4)
        assert process.poll() is None
    finally:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=6)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=6)


def smoke():
    if not shutil.which("xvfb-run"):
        raise RuntimeError("Required real native GTK Xvfb runner missing")
    with tempfile.TemporaryDirectory(prefix="gc-contacts-user-install-") as scratch:
        root = Path(scratch)
        app_files = root / "appfiles"
        bin_root = root / "bin"
        home = root / "home"
        data = root / "data"
        config = root / "config"
        cache = root / "cache"
        runtime = root / "runtime"
        for directory in (home, data, config, cache, runtime):
            directory.mkdir(mode=0o700)

        install(app_files, bin_root)
        launcher = bin_root / "goreecloud-contacts"
        desktop = app_files / "applications" / "org.goreecloud.Contacts.desktop"
        package = app_files / "goreecloud" / "contacts-linux" / "goreecloud_contacts"
        assert launcher.is_file() and os.access(launcher, os.X_OK)
        assert (package / "app.py").is_file()
        assert (package / "vcard.py").is_file()
        assert (package / "assets" / "logo.svg").is_file()
        desktop_text = desktop.read_text(encoding="utf8")
        assert str(launcher) in desktop_text
        assert str(package / "assets" / "logo.svg") in desktop_text

        environment = os.environ.copy()
        environment.update({
            "HOME": str(home),
            "XDG_DATA_HOME": str(data),
            "XDG_CONFIG_HOME": str(config),
            "XDG_CACHE_HOME": str(cache),
            "XDG_RUNTIME_DIR": str(runtime),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "GDK_BACKEND": "x11",
            "GTK_USE_PORTAL": "0",
            "GIO_USE_VFS": "local",
            "NO_AT_BRIDGE": "1",
            "GSETTINGS_BACKEND": "memory",
        })
        environment.pop("PYTHONPATH", None)  # The installed wrapper must set its own package path.
        environment["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/dev/null"  # Deny host/user D-Bus access.
        private = data / "goreecloud" / "contacts"
        database = private / "contacts.sqlite3"

        launch_and_verify(launcher, environment, database, expected=0)
        assert stat.S_IMODE(private.stat().st_mode) == 0o700
        assert stat.S_IMODE(database.stat().st_mode) == 0o600
        assert private.stat().st_uid == os.getuid()
        assert database.stat().st_uid == os.getuid()
        assert not (home / ".local" / "share" / "goreecloud").exists(), (
            "App unexpectedly wrote to HOME default data folder"
        )

        # After a complete app shutdown, create only a synthetic test record.
        store = ContactStore(database)
        try:
            store.save(new_contact("Synthetic Offline Install Test",
                                   email="synthetic@example.invalid"), is_new=True)
        finally:
            store.close()

        launch_and_verify(launcher, environment, database, expected=1)
        with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as connection:
            assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            assert connection.execute("SELECT COUNT(*) FROM contacts").fetchone()[0] == 1
        print("GOREECLOUD_CONTACTS_INSTALLED_GTK_XDG_RESTART_SQLITE_PASS")


if __name__ == "__main__":
    smoke()
