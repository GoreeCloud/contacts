from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
class Nodes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.scripts=[]
        self.links=[]
        self.inline_handlers=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if "id" in d:
            self.ids.append(d["id"])
        if tag=="script":
            self.scripts.append(d)
        if tag=="link":
            self.links.append(d)
        for k,v in attrs:
            if k.lower().startswith("on"):
                self.inline_handlers.append((k,v))

class MarkupTests(unittest.TestCase):
    def test_accessible_ui_and_first_party_asset_boundary(self):
        text=(ROOT/"index.html").read_text(encoding="utf-8")
        parser=Nodes()
        parser.feed(text)
        self.assertEqual(len(parser.ids),len(set(parser.ids)),"Duplicate accessible IDs")
        self.assertEqual(parser.inline_handlers,[])
        self.assertEqual(parser.scripts,[{"type":"module","src":"./main.mjs"}])
        self.assertIn({"rel":"stylesheet","href":"./gc-ui/tokens.css"},parser.links)
        self.assertIn({"rel":"icon","type":"image/svg+xml","href":"./assets/goreecloud-logo.svg"},parser.links)
        for token in ('role="status"','aria-live="polite"','aria-label="Contact filters"',
                      'id="editorDialog"','id="deleteDialog"','id="contactList"',
                      'autocomplete="off"',"connect-src 'none'","form-action 'none'",
                      'id="importCard"','id="importCardFile"'):
            self.assertIn(token,text)
        self.assertNotIn('http://',text)
        self.assertNotIn('https://',text)

if __name__=="__main__":
    unittest.main()
