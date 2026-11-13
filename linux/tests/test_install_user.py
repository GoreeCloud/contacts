import os
from pathlib import Path
import stat
import tempfile
import unittest

from install_user import install, safe_new_file
from unittest.mock import patch

class InstallTests(unittest.TestCase):
    def test_user_install_owns_only_new_app_code_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            data=root/"data"
            bins=root/"bin"
            install(data,bins)
            package=data/"goreecloud"/"contacts-linux"/"goreecloud_contacts"/"app.py"
            self.assertTrue(package.is_file())
            wrapper=bins/"goreecloud-contacts"
            cli=bins/"goreecloud-contacts-cli"
            self.assertTrue(wrapper.exists())
            self.assertTrue(cli.exists())
            self.assertIn("goreecloud_contacts.cli",cli.read_text())
            self.assertEqual(stat.S_IMODE(cli.stat().st_mode),0o700)
            self.assertEqual(stat.S_IMODE(wrapper.stat().st_mode),0o700)
            desktop=data/"applications"/"org.goreecloud.Contacts.desktop"
            self.assertIn(str(wrapper),desktop.read_text())
            self.assertFalse((data/"goreecloud"/"contacts"/"contacts.sqlite3").exists())
            with self.assertRaises(ValueError):
                install(data,bins)
            self.assertTrue(package.exists())
            self.assertTrue(desktop.exists())

    def test_partial_file_write_cleanup_and_existing_file_preservation(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            target=root/"launcher"
            with patch("install_user.os.fsync",
                       side_effect=OSError("synthetic disk sync failure")):
                with self.assertRaises(OSError):
                    safe_new_file(target,"#!/bin/sh\nexec true\n",0o700)
            self.assertFalse(target.exists(), "Incomplete launchers must be removed")
            target.write_text("original")
            with self.assertRaises(FileExistsError):
                safe_new_file(target,"malicious overwrite",0o700)
            self.assertEqual(target.read_text(),"original")

    def test_desktop_write_failure_rolls_back_only_new_code(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            data=root/"data"
            bins=root/"bin"
            personal=data/"goreecloud"/"contacts"
            personal.mkdir(parents=True,mode=0o700)
            sentinel=personal/"synthetic.sqlite3"
            sentinel.write_bytes(b"preserve this synthetic existing file")
            # GTK and CLI wrapper fsync succeed, desktop entry fsync then fails.
            with patch("install_user.os.fsync",
                       side_effect=[None,None,OSError("synthetic desktop fsync failure")]):
                with self.assertRaises(OSError):
                    install(data,bins)
            self.assertFalse((bins/"goreecloud-contacts").exists())
            self.assertFalse((bins/"goreecloud-contacts-cli").exists())
            self.assertFalse((data/"applications"/"org.goreecloud.Contacts.desktop").exists())
            self.assertFalse((data/"goreecloud"/"contacts-linux").exists())
            self.assertEqual(sentinel.read_bytes(),b"preserve this synthetic existing file")

    def test_existing_cli_launcher_blocks_install_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            bins=root/"bin"
            bins.mkdir(mode=0o700)
            existing=bins/"goreecloud-contacts-cli"
            existing.write_text("existing private CLI")
            with self.assertRaises(ValueError):
                install(root/"data",bins)
            self.assertEqual(existing.read_text(),"existing private CLI")
            self.assertFalse((bins/"goreecloud-contacts").exists())
            self.assertFalse((root/"data"/"goreecloud"/"contacts-linux").exists())

    def test_symlinked_installation_root_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            real=root/"real"
            real.mkdir()
            link=root/"link"
            link.symlink_to(real,target_is_directory=True)
            with self.assertRaises(ValueError):
                install(link,root/"bin")
            self.assertFalse((root/"bin"/"goreecloud-contacts").exists())

if __name__=="__main__":
    unittest.main()
