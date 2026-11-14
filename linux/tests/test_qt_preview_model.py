"""No-GUI, no-network tests of the read-only Qt Quick Contacts preview model."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from goreecloud_contacts.core import ContactError, new_contact, validate
from goreecloud_contacts.qt_preview_model import filter_contacts


class PreviewModelTests(unittest.TestCase):
    def setUp(self):
        self.a = new_contact("Álpha Example", "555 0100", "alpha@invalid.example", "GoreeCloud", True)
        self.b = new_contact("Beta Example", "555 0200", "beta@invalid.example", "Other", False)

    def test_favorite_first_and_stable_sort(self):
        self.assertEqual([c["id"] for c in filter_contacts([self.b, self.a])],
                         [self.a["id"], self.b["id"]])
        self.assertEqual([c["id"] for c in filter_contacts([self.a, self.b], favorites_only=True)],
                         [self.a["id"]])

    def test_unicode_fold_and_all_searchable_fields(self):
        for word in ("alpha", "555 0100", "alpha@invalid.example", "GoreeCloud"):
            with self.subTest(word=word):
                self.assertEqual([c["id"] for c in filter_contacts([self.b, self.a], word)],
                                 [self.a["id"]])

    def test_bounded_input_and_strict_domain_validation(self):
        with self.assertRaises(ContactError):
            filter_contacts([self.a], "x" * 161)
        with self.assertRaises(ContactError):
            filter_contacts([self.a], favorites_only=1)
        bad = dict(self.a, name="")
        with self.assertRaises(ContactError):
            filter_contacts([bad])

    def test_does_not_mutate_contacts(self):
        initial = dict(self.a)
        self.assertEqual(filter_contacts([self.a])[0], validate(self.a))
        self.assertEqual(self.a, initial)


if __name__ == "__main__":
    unittest.main()
