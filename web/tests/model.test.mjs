import test from 'node:test';
import assert from 'node:assert/strict';
import {FORMAT, InvalidContact, validateContact, validateCollection, parseBackup, makeBackup, makeVCard, searchContacts} from '../model.mjs';
const a={id:'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',name:'Zoë García',phone:'+1 (205) 555-0100',email:'zoe@example.invalid',organization:'GoreeCloud',favorite:true};
const b={id:'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',name:'André North',phone:'',email:'',organization:'',favorite:false};
test('strict roundtrip backup, Unicode and local search',()=>{
  assert.deepEqual(parseBackup(makeBackup([b,a])),[a,b]);
  assert.equal(JSON.parse(makeBackup([a,b])).format,FORMAT);
  assert.equal(searchContacts([a,b],'zoe')[0].name,'Zoë García');
  assert.equal(searchContacts([a,b],'205')[0].id,a.id);
  assert.equal(searchContacts([a,b],'')[0].id,a.id);
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
test('supplementary Unicode uses portable scalar limits, not UTF-16 code units',()=>{
  const maxName = '😀'.repeat(160);
  const maxPhone = '🪁'.repeat(80);
  const maxEmail = '🪁'.repeat(254);
  const maxOrg = '🚀'.repeat(160);
  const allowed = validateContact({...a,name:maxName,phone:maxPhone,
    email:maxEmail,organization:maxOrg});
  assert.equal([...allowed.name].length,160);
  assert.deepEqual(parseBackup(makeBackup([allowed])),[allowed]);
  assert.match(makeVCard([allowed]),/BEGIN:VCARD/);
  for (const [key,limit,symbol] of [['name',160,'😀'],['phone',80,'🪁'],
    ['email',254,'🪁'],['organization',160,'🚀']]) {
    assert.throws(()=>validateContact({...a,[key]:symbol.repeat(limit+1)}),
      InvalidContact);
  }
  assert.throws(()=>validateContact({...a,name:'😀'.repeat(159)+'\uD800'}),
    InvalidContact);
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
