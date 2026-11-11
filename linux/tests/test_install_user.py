import os
from pathlib import Path
import stat
import tempfile
import unittest

from install_user import install

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
            self.assertTrue(wrapper.exists())
            self.assertEqual(stat.S_IMODE(wrapper.stat().st_mode),0o700)
            desktop=data/"applications"/"org.goreecloud.Contacts.desktop"
            self.assertIn(str(wrapper),desktop.read_text())
            self.assertFalse((data/"goreecloud"/"contacts"/"contacts.sqlite3").exists())
            with self.assertRaises(ValueError):
                install(data,bins)
            self.assertTrue(package.exists())
            self.assertTrue(desktop.exists())

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
