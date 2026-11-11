from pathlib import Path
import tempfile
import unittest

from goreecloud_contacts.core import ContactError, make_vcards
from goreecloud_contacts.vcard import parse_vcards,read_vcards_file,visible_identity

A = dict(id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
         name="Zoë García",phone="+1 (205) 555-0100",
         email="zoe@example.invalid",organization="GoreeCloud",favorite=True)
B = dict(id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
         name="André, North; East \\ West",phone="",email="",organization="",favorite=False)

class VCardImportTests(unittest.TestCase):
    def test_limited_roundtrip_and_dropped_favorite_disclosure(self):
        ids=iter(("cccccccc-cccc-4ccc-8ccc-cccccccccccc",
                  "dddddddd-dddd-4ddd-8ddd-dddddddddddd"))
        data=parse_vcards(make_vcards([A,B]),lambda: next(ids))
        self.assertEqual(data[0]["name"],A["name"])
        self.assertEqual(data[1]["name"],B["name"])
        self.assertEqual(visible_identity(data[0]),visible_identity(A))
        self.assertFalse(data[0]["favorite"])
        self.assertFalse(data[1]["favorite"])
        self.assertEqual(len(parse_vcards(make_vcards([A]).replace("\r\n","\n"))),1)

    def test_duplicate_visible_records_never_partially_import(self):
        from goreecloud_contacts.core import ContactStore
        with tempfile.TemporaryDirectory() as folder:
            parent=Path(folder)/"private"
            parent.mkdir(mode=0o700)
            store=ContactStore(parent/"contacts.sqlite3")
            try:
                store.save(A,is_new=True)
                from_import=parse_vcards(make_vcards([A]))
                with self.assertRaises(ContactError):
                    store.import_new(from_import,reject_visible_duplicates=True)
                self.assertEqual(store.list(),[A])
                unique=dict(B,name="Different Name")
                same_fields_different_id=dict(unique,id="cccccccc-cccc-4ccc-8ccc-cccccccccccc")
                copies=parse_vcards(make_vcards([unique,same_fields_different_id]))
                with self.assertRaises(ContactError):
                    store.import_new(copies,reject_visible_duplicates=True)
                self.assertEqual(store.list(),[A])
                self.assertEqual(store.import_new(parse_vcards(make_vcards([unique])),
                                                 reject_visible_duplicates=True),1)
                self.assertEqual(len(store.list()),2)
            finally:
                store.close()

    def test_multibyte_folding_and_safe_file_read(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/"synthetic.vcf"
            long=dict(A,name="É"*90+" Semi; Comma, Back\\ Slash")
            target.write_bytes(make_vcards([long]).encode("utf8"))
            self.assertEqual(read_vcards_file(target)[0]["name"],long["name"])
            link=Path(folder)/"alias.vcf"
            link.symlink_to(target)
            with self.assertRaises(ContactError):
                read_vcards_file(link)

    def test_reject_unsupported_fields_and_malformed_inputs(self):
        good=make_vcards([A])
        variants=[
            "",good.replace("END:VCARD","PHOTO;ENCODING=b:SECRET\r\nEND:VCARD"),
            good.replace("END:VCARD","NOTE:private\r\nEND:VCARD"),
            good.replace("END:VCARD","TEL:duplicate\r\nEND:VCARD"),
            good.replace("VERSION:3.0","VERSION:2.1"),
            good.replace("VERSION:3.0","VERSION:3.0\r\nVERSION:3.0"),
            good.replace("N:Zoë García;;;;","N:Structured;Name;;;"),
            good.replace("FN:Zoë García","FN:Zoë\\nGarcía"),
            good.replace("FN:Zoë García","FN:Zoë\u202eGarcía"),
            good.replace("FN:Zoë García","FN;CHARSET=UTF-8:Zoë García"),
            good.replace("END:VCARD",""),
            " "+good,
            good.replace("\r\n","\r",1),
            good.replace("FN:Zoë García","FN:Comma,Unescaped"),
            good.replace("FN:Zoë García","FN:Zoë\\qGarcía")
        ]
        for data in variants:
            with self.subTest(broken=data[:36]),self.assertRaises(ContactError):
                parse_vcards(data)
        with self.assertRaises(ContactError):
            parse_vcards(good*30000)
        with self.assertRaises(ContactError):
            parse_vcards(make_vcards([A,B]),lambda: A["id"])
