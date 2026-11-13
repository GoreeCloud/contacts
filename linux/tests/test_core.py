import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from goreecloud_contacts.core import (
    ContactError, ContactStore, FORMAT, parse_backup, make_backup, make_vcards,
    validate, validate_collection, new_contact, read_backup_file, write_new_file
)

A = dict(id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", name="Zoë García",
         phone="+1 (205) 555-0100", email="zoe@example.invalid",
         organization="GoreeCloud", favorite=True)
B = dict(id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb", name="André North",
         phone="", email="", organization="", favorite=False)
FIXTURE = Path(__file__).resolve().parents[2] / "shared/fixtures/contacts-v1.json"

class ContactsCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / "private"
        self.folder.mkdir(mode=0o700)
        self.file = self.folder / "contacts.sqlite3"

    def test_shared_fixture_and_roundtrip(self):
        fixture=FIXTURE.read_text(encoding="utf-8")
        contacts=parse_backup(fixture)
        self.assertEqual(contacts,[A,B])
        self.assertEqual(parse_backup(make_backup(contacts)),[A,B])
        self.assertEqual(json.loads(make_backup(contacts))["format"],FORMAT)
        self.assertIn("VERSION:3.0\r\n",make_vcards(contacts))
        self.assertNotIn("favorite",make_vcards(contacts))
        self.assertEqual(make_vcards([]),"")
        lines=make_vcards([dict(A,name="É"*90)]).split("\r\n")
        self.assertTrue(all(len(line.encode("utf8"))<=75 for line in lines))
        self.assertIn("\r\n ",make_vcards([dict(A,name="É"*90)]))

    def test_synthetic_crud_search_favorites_and_permissions(self):
        store=ContactStore(self.file)
        self.addCleanup(store.close)
        store.save(B,is_new=True)
        store.save(A,is_new=True)
        self.assertEqual(store.list(),[B,A])
        self.assertEqual(store.filtered("zoe")[0]["name"],"Zoë García")
        self.assertEqual(store.filtered("205")[0]["id"],A["id"])
        self.assertEqual(store.filtered(favorites_only=True),[A])
        changed=dict(B,name="Updated Name",favorite=True)
        store.save(changed,is_new=False,expected=B)
        self.assertTrue(store.filtered(favorites_only=True)[0]["favorite"])
        store.delete(A["id"],expected=A)
        self.assertEqual(store.list(),[changed])
        self.assertEqual(stat.S_IMODE(self.folder.stat().st_mode),0o700)
        self.assertEqual(stat.S_IMODE(self.file.stat().st_mode),0o600)

    def test_atomic_import_conflicts_do_not_replace_existing(self):
        store=ContactStore(self.file)
        self.addCleanup(store.close)
        store.save(A,is_new=True)
        with self.assertRaises(ContactError):
            store.import_new([B,A])
        self.assertEqual(store.list(),[A])
        self.assertEqual(store.import_new([B]),1)
        self.assertEqual(len(store.list()),2)
        with self.assertRaises(ContactError):
            store.save(B,is_new=True)
        self.assertEqual(store.list(),[A,B])

    def test_concurrent_edit_and_delete_fail_closed_on_stale_records(self):
        store=ContactStore(self.file)
        other=ContactStore(self.file)
        self.addCleanup(store.close)
        self.addCleanup(other.close)
        store.save(A,is_new=True)
        previous=store.list()[0]
        latest=dict(A,name="Updated by another Linux window")
        other.save(latest,is_new=False,expected=previous)
        with self.assertRaises(ContactError):
            store.save(dict(A,name="stale update"),is_new=False,expected=previous)
        with self.assertRaises(ContactError):
            store.delete(A["id"],expected=previous)
        self.assertEqual(store.list(),[latest])
        store.delete(A["id"],expected=latest)
        self.assertEqual(store.list(),[])

    def test_separate_process_stale_edits_and_imports_cannot_overwrite(self):
        """Two genuine OS processes share only synthetic private SQLite data.

        Preflight is advisory, not a transaction reservation; actual imports
        must recheck conflicts under BEGIN IMMEDIATE after another process
        commits. No real account, contacts, device or network access.
        """
        store=ContactStore(self.file)
        self.addCleanup(store.close)
        store.save(A,is_new=True)
        previous=store.list()[0]
        latest=dict(previous,name="Other process committed")
        worker = """
import json,sys
from goreecloud_contacts.core import ContactStore
db=ContactStore(sys.argv[1])
try:
    command=sys.argv[2]
    incoming=json.loads(sys.argv[3])
    if command=='edit':
        db.save(incoming,is_new=False,expected=json.loads(sys.argv[4]))
    elif command=='import':
        db.import_new(incoming,reject_visible_duplicates=bool(int(sys.argv[4])))
    else:
        raise RuntimeError('Unsupported synthetic test action')
finally:
    db.close()
"""
        def invoke(action,incoming,condition):
            args=[sys.executable,"-c",worker,str(self.file),action,
                  json.dumps(incoming,ensure_ascii=False),
                  json.dumps(condition,ensure_ascii=False)
                  if action=="edit" else str(int(condition))]
            process=subprocess.run(args,capture_output=True,text=True,timeout=12)
            self.assertEqual(process.returncode,0,
                "Synthetic child process failed (no contact details logged)")

        invoke("edit",latest,previous)
        with self.assertRaises(ContactError):
            store.save(dict(previous,name="stale parent update"),
                       is_new=False,expected=previous)
        with self.assertRaises(ContactError):
            store.delete(previous["id"],expected=previous)
        self.assertEqual(store.list(),[latest])

        from goreecloud_contacts.core import check_import
        self.assertEqual(check_import([B],store.list()),1)
        invoke("import",[B],False)
        with self.assertRaises(ContactError):
            store.import_new([B])
        self.assertEqual(store.list(),[latest,B])

        # Different IDs, identical visible contact details: a stale vCard
        # preflight can pass then become a conflict in another process.
        staged=dict(B,id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
                    name="Synthetic New Visible",email="new@example.invalid")
        competitor=dict(staged,id="dddddddd-dddd-4ddd-8ddd-dddddddddddd")
        self.assertEqual(check_import([staged],store.list(),
                                      reject_visible_duplicates=True),1)
        invoke("import",[competitor],True)
        with self.assertRaises(ContactError):
            store.import_new([staged],reject_visible_duplicates=True)
        self.assertNotIn(staged["id"],{c["id"] for c in store.list()})
        self.assertIn(competitor["id"],{c["id"] for c in store.list()})
        self.assertEqual(len(store.list()),3)

    def test_reject_bad_input_surrogates_bidi_hidden_fields_and_unsafe_files(self):
        for bad in (
            dict(A,notes="secret"),dict(A,name="A\r\nFN:fake"),
            dict(A,name="A\u202eB"),dict(A,name="A\u2066B"),
            dict(A,name="\ud800"),dict(A,favorite=1),dict(A,name=""),
            dict(A,name="X"*161),dict(A,id="../bad"),
        ):
            with self.assertRaises(ContactError):
                validate(bad)
        with self.assertRaises(ContactError):
            validate_collection([A,A])
        with self.assertRaises(ContactError):
            parse_backup('{"format":"goreecloud.contacts.v1","contacts":[],"evil":"secret"}')
        with self.assertRaises(ContactError):
            parse_backup("X" * (2*1024*1024+1))
        with self.assertRaises(ContactError):
            parse_backup("not json")
        unsafe = Path(self.temp.name)/"public"
        unsafe.mkdir(mode=0o755)
        with self.assertRaises(ContactError):
            ContactStore(unsafe/"data.db")
        secret=self.folder/"secret.db"
        secret.write_text("placeholder")
        secret.chmod(0o644)
        with self.assertRaises(ContactError):
            ContactStore(secret)
        target=self.folder/"target.db"
        target.write_text("dummy")
        link=self.folder/"link.db"
        link.symlink_to(target)
        with self.assertRaises(ContactError):
            ContactStore(link)

    def test_interrupted_export_never_leaves_a_partial_plaintext_file(self):
        for failure, expected in (
            (OSError("synthetic full disk"), ContactError),
            (KeyboardInterrupt(), KeyboardInterrupt),
        ):
            with self.subTest(failure=type(failure).__name__):
                location=self.folder/("interrupted-"+type(failure).__name__+".json")
                with patch("goreecloud_contacts.core.os.fsync",
                           side_effect=failure):
                    with self.assertRaises(expected):
                        write_new_file(location,make_backup([A]))
                self.assertFalse(location.exists(),
                                 "Interrupted export left a partial sensitive backup")
        target=self.folder/"protected-existing.json"
        target.write_text("preserve existing synthetic file")
        symlink=self.folder/"export-symlink.json"
        symlink.symlink_to(target)
        with self.assertRaises(ContactError):
            write_new_file(symlink,"attempt overwrite")
        self.assertEqual(target.read_text(),"preserve existing synthetic file")

    def test_explicit_file_export_is_exclusive_and_private(self):
        location=self.folder/"backup.json"
        text=make_backup([A])
        write_new_file(location,text)
        self.assertEqual(stat.S_IMODE(location.stat().st_mode),0o600)
        self.assertEqual(read_backup_file(location),[A])
        with self.assertRaises(ContactError):
            write_new_file(location,"X")
        self.assertEqual(location.read_text(),text)
        bad=self.folder/"symlink.json"
        bad.symlink_to(location)
        with self.assertRaises(ContactError):
            read_backup_file(bad)

if __name__=="__main__":
    unittest.main()
