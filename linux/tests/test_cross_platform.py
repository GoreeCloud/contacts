"""Cross-language portable Contacts contract for web and native Linux.

Node is needed only for this test, not for the installed Linux client.
"""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from goreecloud_contacts.core import parse_backup,make_backup,make_vcards

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=ROOT/"shared"/"fixtures"/"contacts-v1.json"

class CrossPlatformContractTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"),"Node needed for cross-language development check")
    def test_js_and_python_emit_identical_json_and_vcard_bytes(self):
        js = r"""
import {readFileSync} from 'node:fs';
import {parseBackup,makeBackup,makeVCard} from './web/model.mjs';
const input=readFileSync('./shared/fixtures/contacts-v1.json','utf8');
const contacts=parseBackup(input);
process.stdout.write(JSON.stringify({backup:makeBackup(contacts),vcard:makeVCard(contacts)}));
"""
        process=subprocess.run(["node","--input-type=module","--eval",js],
                               cwd=ROOT,capture_output=True,text=True,timeout=10)
        self.assertEqual(process.returncode,0,process.stderr[-300:])
        result=json.loads(process.stdout)
        contacts=parse_backup(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(result["backup"],make_backup(contacts))
        self.assertEqual(result["vcard"],make_vcards(contacts))

if __name__=="__main__":
    unittest.main()
