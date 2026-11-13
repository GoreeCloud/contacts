"""Cross-language portable Contacts contract for web and native Linux.

Node is needed only for this test, not for the installed Linux client.
"""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from goreecloud_contacts.core import parse_backup,make_backup,make_vcards
from goreecloud_contacts.vcard import parse_vcards

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

    @unittest.skipUnless(shutil.which("node"),"Node needed for cross-language development check")
    def test_supplementary_unicode_boundaries_are_lossless_across_both_apps(self):
        records=[{
            "id":"eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
            "name":"😀"*160, "phone":"🪁"*80, "email":"",
            "organization":"🚀"*160, "favorite":True,
        }]
        js = r'''
import {parseBackup,makeBackup,makeVCard} from './web/model.mjs';
import {parseVCard} from './web/vcard.mjs';
const source=JSON.parse(process.argv[1]);
const backup=makeBackup(source);
const card=makeVCard(source);
const recovered=parseVCard(card,()=> 'ffffffff-ffff-4fff-8fff-ffffffffffff');
process.stdout.write(JSON.stringify({backup,card,recovered}));
'''
        result=subprocess.run(["node","--input-type=module","--eval",js,
                               json.dumps(records,ensure_ascii=False)],
                              cwd=ROOT,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr[-350:])
        output=json.loads(result.stdout)
        self.assertEqual(output["backup"],make_backup(records))
        self.assertEqual(output["card"],make_vcards(records))
        self.assertEqual(parse_backup(output["backup"]),records)
        recovered=parse_vcards(output["card"],
                              lambda:"ffffffff-ffff-4fff-8fff-ffffffffffff")
        self.assertEqual(output["recovered"],recovered)

    @unittest.skipUnless(shutil.which("node"),"Node needed for cross-language development check")
    def test_web_and_linux_vcard_import_recover_same_limited_fields(self):
        js = r"""
import {readFileSync} from 'node:fs';
import {parseBackup,makeVCard} from './web/model.mjs';
import {parseVCard} from './web/vcard.mjs';
const contacts=parseBackup(readFileSync('./shared/fixtures/contacts-v1.json','utf8'));
const ids=['cccccccc-cccc-4ccc-8ccc-cccccccccccc','dddddddd-dddd-4ddd-8ddd-dddddddddddd'];
let i=0;
process.stdout.write(JSON.stringify(parseVCard(makeVCard(contacts),()=>ids[i++])));
"""
        process=subprocess.run(["node","--input-type=module","--eval",js],
                               cwd=ROOT,capture_output=True,text=True,timeout=10)
        self.assertEqual(process.returncode,0,process.stderr[-350:])
        source=parse_backup(FIXTURE.read_text(encoding="utf-8"))
        ids=iter(("cccccccc-cccc-4ccc-8ccc-cccccccccccc",
                  "dddddddd-dddd-4ddd-8ddd-dddddddddddd"))
        expected=parse_vcards(make_vcards(source),lambda: next(ids))
        self.assertEqual(json.loads(process.stdout),expected)

if __name__=="__main__":
    unittest.main()
