import test from 'node:test';
import assert from 'node:assert/strict';
import {makeVCard, InvalidContact} from '../model.mjs';
import {parseVCard,visibleIdentity} from '../vcard.mjs';
const a={id:'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',name:'Zoë García',phone:'+1 (205) 555-0100',email:'zoe@example.invalid',organization:'GoreeCloud',favorite:true};
const b={id:'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',name:'André, North; East \\ West',phone:'',email:'',organization:'',favorite:false};
const ids=['cccccccc-cccc-4ccc-8ccc-cccccccccccc','dddddddd-dddd-4ddd-8ddd-dddddddddddd'];
function fromFile(text){let i=0;return parseVCard(text,()=>ids[i++]);}
test('limited export/import roundtrip retains represented fields',()=>{
  const result=fromFile(makeVCard([a,b]));
  assert.equal(result.length,2);
  assert.equal(result[0].name,a.name);
  assert.equal(result[1].name,b.name);
  assert.deepEqual(result.map(c=>c.id),ids);
  assert.equal(result[0].favorite,false);
  assert.equal(visibleIdentity(result[0]),visibleIdentity(a));
  assert.equal(fromFile(makeVCard([a]).replaceAll('\r\n','\n'))[0].name,a.name);
});
test('UTF8 line folding and escaped punctuation',()=>{
  const long={...a,name:'É'.repeat(90)+' Semi; Comma, Back\\ Slash'};
  assert.equal(fromFile(makeVCard([long]))[0].name,long.name);
});
test('reject rich fields, unknown properties, malformed and injected text',()=>{
  const good=makeVCard([a]);
  const variants=[
    '',good.replace('END:VCARD','PHOTO;ENCODING=b:SECRET\r\nEND:VCARD'),
    good.replace('END:VCARD','NOTE:private\r\nEND:VCARD'),
    good.replace('END:VCARD','TEL:duplicate\r\nEND:VCARD'),
    good.replace('VERSION:3.0','VERSION:4.0'),
    good.replace('VERSION:3.0','VERSION:3.0\r\nVERSION:3.0'),
    good.replace('N:Zoë García;;;;','N:Structured;Name;;;'),
    good.replace('FN:Zoë García','FN:Zoë\\nGarcía'),
    good.replace('FN:Zoë García','FN:Zoë\u202eGarcía'),
    good.replace('FN:Zoë García','FN;CHARSET=UTF-8:Zoë García'),
    good.replace('END:VCARD',''),
    ' '+good,
    good.replace('\r\n','\r'),
    good.replace('FN:Zoë García','FN:Comma,Unescaped'),
    good.replace('FN:Zoë García','FN:Zoë\\qGarcía')
  ];
  for(const broken of variants) assert.throws(()=>fromFile(broken),InvalidContact);
  assert.throws(()=>fromFile(good.repeat(30000)),InvalidContact);
});
test('ID factory cannot create invalid or duplicate IDs',()=>{
  assert.throws(()=>parseVCard(makeVCard([a]),()=> 'bad'),InvalidContact);
  assert.throws(()=>parseVCard(makeVCard([a,b]),()=> ids[0]),InvalidContact);
});
