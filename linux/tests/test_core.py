import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

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
