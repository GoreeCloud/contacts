import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {parseBackup, makeBackup} from '../model.mjs';
const fixture=readFileSync(new URL('../../shared/fixtures/contacts-v1.json',import.meta.url),'utf8');
test('shared golden JSON accepted and round trips',()=>{
  const contacts=parseBackup(fixture);
  assert.equal(contacts.length,2);
  assert.equal(contacts[0].name,'Zoë García');
  assert.equal(contacts[1].name,'André North');
  assert.deepEqual(parseBackup(makeBackup(contacts)),contacts);
});
