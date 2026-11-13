"""Synthetic end-to-end subprocess tests for offline Contacts CLI.

Every subprocess uses a disposable private SQLite path, with no personal data
or real export locations, and must reject overwrite, unsafe inputs and silent
rich-field loss.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

from goreecloud_contacts.core import make_backup, make_vcards

A = {
    "id":"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    "name":"Zoë García","phone":"+1 555 0100",
    "email":"zoe@example.invalid","organization":"GoreeCloud",
    "favorite":True,
}
B = {
    "id":"bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    "name":"André North","phone":"","email":"",
    "organization":"","favorite":False,
}


class OfflineCliTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix="gc-contacts-cli-")
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        self.private=self.root/"private"
        self.private.mkdir(mode=0o700)
        self.db=self.private/"contacts.sqlite3"
        self.fixture=self.root/"synthetic.json"
        self.fixture.write_text(make_backup([A,B]),encoding="utf8")
        self.env=os.environ.copy()
        self.env.update({"PYTHONDONTWRITEBYTECODE":"1","PYTHONNOUSERSITE":"1"})

    def run_cli(self,*args,code=0):
        result=subprocess.run(
            [sys.executable,"-m","goreecloud_contacts.cli",
             "--db",str(self.db),*map(str,args)],
            env=self.env,text=True,capture_output=True,timeout=8)
        self.assertEqual(result.returncode,code,result.stdout+" / "+result.stderr)
        return result

    def test_validators_do_not_create_database(self):
        self.assertIn("2 contact records",self.run_cli(
            "verify-backup","--input",self.fixture).stdout)
        vcf=self.root/"synthetic.vcf"
        vcf.write_text(make_vcards([A,B]),encoding="utf8",newline="")
        self.assertIn("2 contact records",self.run_cli(
            "verify-vcard","--input",vcf).stdout)
        self.assertFalse(self.db.exists(),"File validation must not open local SQLite")

    def test_status_check_backup_and_restore_are_private_and_explicit(self):
        self.assertIn("0 local contacts",self.run_cli("status").stdout)
        self.run_cli("restore","--input",self.fixture,code=2)
        self.assertIn("0 local contacts",self.run_cli("status").stdout)
        self.assertIn("2 contacts imported",self.run_cli(
            "restore","--input",self.fixture,"--yes").stdout)
        self.assertIn("2 local contacts; 1 favorites",self.run_cli("status").stdout)
        self.assertIn("integrity and contact schema: OK",self.run_cli("check").stdout)
        backup=self.root/"backup.json"
        self.run_cli("backup","--output",backup,code=2)
        self.assertFalse(backup.exists())
        self.assertIn("NOT encrypted",self.run_cli(
            "backup","--output",backup,"--acknowledge-plaintext").stdout)
        self.assertEqual(stat.S_IMODE(backup.stat().st_mode),0o600)
        self.assertEqual(backup.read_text(),make_backup([A,B]))
        result=self.run_cli("backup","--output",backup,
                            "--acknowledge-plaintext",code=1)
        self.assertNotIn(A["name"],result.stderr)
        self.assertEqual(backup.read_text(),make_backup([A,B]))
        conflict=self.run_cli("restore","--input",self.fixture,"--yes",code=1)
        self.assertNotIn(A["name"],conflict.stderr)
        self.assertIn("2 local contacts; 1 favorites",self.run_cli("status").stdout)

    def test_vcard_import_requires_lossy_format_acknowledgement_and_no_overwrite(self):
        vcf=self.root/"synthetic.vcf"
        vcf.write_text(make_vcards([A,B]),encoding="utf8",newline="")
        self.run_cli("import-vcard","--input",vcf,"--yes",code=2)
        self.assertFalse(self.db.exists())
        result=self.run_cli("import-vcard","--input",vcf,"--yes",
                            "--accept-limited-fields")
        self.assertIn("favorites not restored",result.stdout)
        self.assertIn("2 local contacts; 0 favorites",self.run_cli("status").stdout)
        self.run_cli("import-vcard","--input",vcf,"--yes",
                     "--accept-limited-fields",code=1)
        self.assertIn("2 local contacts; 0 favorites",self.run_cli("status").stdout)
        out=self.root/"limited.vcf"
        self.run_cli("export-vcard","--output",out,"--acknowledge-plaintext")
        self.assertEqual(stat.S_IMODE(out.stat().st_mode),0o600)
        self.assertEqual(out.read_text(),make_vcards([A,B]).replace("\r\n","\n"))

    def test_reject_bidi_unexpected_fields_symlink_and_hidden_logs(self):
        from goreecloud_contacts.core import ContactStore
        rich=self.root/"rich.json"
        rich.write_text('{"format":"goreecloud.contacts.v1",'
                        '"contacts":[{"notes":"private"}]}',encoding="utf8")
        result=self.run_cli("restore","--input",rich,"--yes",code=1)
        self.assertNotIn("notes",result.stderr)
        self.assertFalse(self.db.exists(),"Rejected JSON must not initialize SQLite")
        symlink=self.root/"link.json"
        symlink.symlink_to(self.fixture)
        self.run_cli("verify-backup","--input",symlink,code=1)
        self.assertFalse(self.db.exists())
        self.run_cli("status")
        self.assertTrue(self.db.exists())
        self.assertEqual(stat.S_IMODE(self.db.stat().st_mode),0o600)

if __name__=="__main__":
    unittest.main()
