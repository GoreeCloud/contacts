import test from 'node:test';
import assert from 'node:assert/strict';
import {FORMAT, InvalidContact, validateContact, validateCollection, parseBackup, makeBackup, makeVCard, searchContacts, selectExportContacts} from '../model.mjs';
const a={id:'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',name:'Zoë García',phone:'+1 (205) 555-0100',email:'zoe@example.invalid',organization:'GoreeCloud',favorite:true};
const b={id:'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',name:'André North',phone:'',email:'',organization:'',favorite:false};
test('strict roundtrip backup, Unicode and local search',()=>{
  assert.deepEqual(parseBackup(makeBackup([b,a])),[a,b]);
  assert.equal(JSON.parse(makeBackup([a,b])).format,FORMAT);
  assert.equal(searchContacts([a,b],'zoe')[0].name,'Zoë García');
  assert.equal(searchContacts([a,b],'205')[0].id,a.id);
  assert.equal(searchContacts([a,b],'')[0].id,a.id);
});
test('opt-in export scope minimizes disclosure and refuses unknown scopes',()=>{
  assert.deepEqual(selectExportContacts([b,a],'all'),[b,a]);
  assert.deepEqual(selectExportContacts([b,a],'favorites'),[a]);
  assert.equal(parseBackup(makeBackup(selectExportContacts([b,a],'favorites'))).length,1);
  assert.equal(makeVCard(selectExportContacts([b],'favorites')),'');
  assert.throws(()=>selectExportContacts([a,b],'some other scope'),InvalidContact);
  assert.throws(()=>selectExportContacts([{...a,notes:'secret'}],'favorites'),InvalidContact);
  assert.deepEqual([a,b],[a,b],'Selection must not mutate source records');
});
test('no injected fields, duplicate IDs, unsafe Unicode or malformed backups',()=>{
  for(const rec of [
    {...a,notes:'PRIVATE'}, {...a,id:'../bad'}, {...a,name:'A\nFN:injected'},
    {...a,name:'A\u202EB'}, {...a,name:'A\u2066B'},
    {...a,name:'A\u200eB'}, {...a,email:'x'.repeat(255)},
    {...a,favorite:'true'}, {...a,name:''}, {...a,name:'a'.repeat(161)},
    {...a,name:'\uD800'}, Object.assign(Object.create({}),a),
  ]) assert.throws(()=>validateContact(rec),InvalidContact);
  assert.throws(()=>validateCollection([a,a]),InvalidContact);
  assert.throws(()=>parseBackup(JSON.stringify({format:FORMAT,contacts:[a],extra:'secret'})),InvalidContact);
  assert.throws(()=>parseBackup('{"format":"unknown","contacts":[]}'),InvalidContact);
  assert.throws(()=>parseBackup('{invalid'),InvalidContact);
  assert.throws(()=>parseBackup('x'.repeat(2*1024*1024+1)),InvalidContact);
  assert.throws(()=>parseBackup('{"format":"goreecloud.contacts.v1","contacts":[],"__proto__":{}}'),InvalidContact);
});
test('vCard escaping, line folding and intentionally limited export',()=>{
  const c={...a,name:'Comma, Semi; Back\\ Slash'};
  const raw=makeVCard([c]);
  assert.match(raw,/VERSION:3\.0\r\n/);
  assert.match(raw,/FN:Comma\\, Semi\\; Back\\\\ Slash/);
  assert.ok(raw.endsWith('END:VCARD\r\n'));
  assert.ok(!raw.includes('favorite'));
  const long=makeVCard([{...a,name:'É'.repeat(90)}]);
  for(const line of long.split('\r\n').filter(Boolean)) {
    assert.ok(Buffer.byteLength(line,'utf8')<=75,'Overwide folded vCard line');
  }
  assert.ok(long.includes('\r\n '));
  assert.equal(makeVCard([]),'');
});

import {sameContact} from '../store.mjs';
test('stale update matcher detects other-tab changes without exposing data',()=>{
  assert.equal(sameContact(a,{...a}),true);
  assert.equal(sameContact(a,{...a,phone:'new phone'}),false);
  assert.equal(sameContact(a,{...a,name:'\u202Espoof'}),false);
});
