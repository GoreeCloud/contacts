import {InvalidContact, MAX_BUNDLE_BYTES, parseBackup, makeBackup, makeVCard, validateContact, searchContacts, selectExportContacts} from './model.mjs';
import {openStore} from './store.mjs';
import {parseVCard,visibleIdentity} from './vcard.mjs';
const byId = id => document.getElementById(id);
const inputFile = byId('importFile'), cardFile=byId('importCardFile'), editor = byId('editorDialog'), form = byId('editorForm');
let db = null, records = [], editingId = null, editingOriginal = null, deleteOriginal = null, activeFilter = 'all', busy = false;
let noticeTimer = null;
let pendingLocalRefresh = false;
// Same-origin/browser-profile invalidation only: broadcast a constant marker,
// never a name, ID, phone, email, backup, token or contact object.
const localChanges = typeof BroadcastChannel === 'function' ?
  new BroadcastChannel('goreecloud-contacts-web-v1-changes') : null;
function notice(message) {
  const el=byId('announcer');
  el.textContent=message; el.classList.add('visible');
  clearTimeout(noticeTimer); noticeTimer=setTimeout(()=>el.classList.remove('visible'),4700);
}
function enabled(value) {
  for(const id of ['newContact','emptyAdd','importBackup','importCard','exportBackup','exportCard','exportScope']) byId(id).disabled=!value;
}
function element(tag, className, text) {
  const node=document.createElement(tag);
  if(className) node.className=className;
  if(text !== undefined) node.textContent=text;
  return node;
}
function button(label, mark, className, handler) {
  const b=element('button',className,mark);
  b.type='button'; b.setAttribute('aria-label',label);
  b.title=label; b.addEventListener('click',handler);
  return b;
}
function render() {
  const visible=searchContacts(records,byId('searchInput').value).filter(c=>activeFilter==='all'||c.favorite);
  byId('countLabel').textContent=records.length===1?'1 contact saved locally':records.length+' contacts saved locally';
  const list=byId('contactList'); list.replaceChildren();
  for(const c of visible) {
    const row=element('article','person');
    row.setAttribute('role','listitem');
    const initial=element('div','avatar',Array.from(c.name.trim())[0].toLocaleUpperCase());
    initial.setAttribute('aria-hidden','true');
    const detail=element('div','');
    detail.append(element('p','person-name',c.name),element('p','person-meta',c.organization||c.email||'Personal contact'));
    const contact=element('div','person-contact',c.phone||c.email||'');
    const actions=element('div','person-actions');
    const star=button((c.favorite?'Remove ':'Add ') + c.name + (c.favorite?' from favorites':' to favorites'),
      c.favorite?'★':'☆', 'icon-button'+(c.favorite?' is-favorite':''),()=>{
        mutate(async()=>{ await db.save({...c,favorite:!c.favorite},false,c); notice(c.favorite?'Removed from favorites':'Added to favorites'); });
      });
    const edit=button('Edit '+c.name,'✎','icon-button',()=>openEditor(c));
    const remove=button('Delete '+c.name,'×','icon-button',()=>{deleteOriginal=c;byId('deleteTitle').textContent='Delete '+c.name+'?';byId('deleteDialog').showModal();});
    actions.append(star,edit,remove);
    row.append(initial,detail,contact,actions);list.append(row);
  }
  const showEmpty=visible.length===0;byId('emptyState').hidden=!showEmpty;
  if(showEmpty) {
    const none=records.length===0;
    byId('emptyTitle').textContent=none?'Make this space yours.':'No matching contacts.';
    byId('emptyMessage').textContent=none?'Add a contact to start your private directory.':'Try another search or switch the filter.';
    byId('emptyAdd').hidden=!none;
  }
}
async function reload() { records=await db.list();render(); }
function refreshAfterPeerChange() {
  if(!db)return;
  if(busy) { pendingLocalRefresh=true; return; }
  reload().catch(()=>notice('Unable to refresh local contacts'));
}
if(localChanges) {
  localChanges.onmessage=event=>{
    if(event.data==='changed') refreshAfterPeerChange();
  };
}
document.addEventListener('visibilitychange',()=>{
  if(!document.hidden) refreshAfterPeerChange();
});
async function mutate(action) {
  if(!db||busy)return;
  busy=true;
  try {
    await action();
    localChanges?.postMessage('changed'); // Only after the write committed.
    await reload();
  }
  catch (error) {notice(error instanceof InvalidContact?error.message:'Unable to complete action; existing data was kept');}
  finally {
    busy=false;
    if(pendingLocalRefresh) {
      pendingLocalRefresh=false;
      refreshAfterPeerChange();
    }
  }
}
function openEditor(c=null) {
  editingId=c?.id??null;
  editingOriginal=c?{...c}:null;
  form.reset();
  byId('editorTitle').textContent=c?'Edit contact':'New contact';
  byId('formError').hidden=true;
  for(const name of ['name','phone','email','organization']) form.elements.namedItem(name).value=c?.[name]??'';
  form.elements.namedItem('favorite').checked=c?.favorite??false;
  editor.showModal();byId('contactName').focus();
}
form.addEventListener('submit',event=>{
  event.preventDefault();
  if(busy)return;
  const c={id:editingId??crypto.randomUUID(),name:form.elements.namedItem('name').value,
    phone:form.elements.namedItem('phone').value,email:form.elements.namedItem('email').value,
    organization:form.elements.namedItem('organization').value,
    favorite:form.elements.namedItem('favorite').checked};
  let checked;
  try {checked=validateContact(c);}
  catch(error){byId('formError').textContent=error.message;byId('formError').hidden=false;return;}
  mutate(async()=>{
    await db.save(checked,!editingId,editingOriginal);editor.close();notice(editingId?'Contact updated':'Contact added');
  });
});
for(const id of ['cancelEditor','discardEditor']) byId(id).addEventListener('click',()=>editor.close());
byId('newContact').addEventListener('click',()=>openEditor());
byId('emptyAdd').addEventListener('click',()=>openEditor());
byId('cancelDelete').addEventListener('click',()=>byId('deleteDialog').close());
byId('confirmDelete').addEventListener('click',()=>{
  const selected=deleteOriginal;byId('deleteDialog').close();deleteOriginal=null;
  mutate(async()=>{await db.remove(selected.id,selected);notice('Contact deleted');});
});
byId('searchInput').addEventListener('input',()=>{if(db)render();});
window.addEventListener('focus',refreshAfterPeerChange);
function changeFilter(name) {
  activeFilter=name;
  for(const [id,on] of [['allFilter',name==='all'],['favoritesFilter',name==='favorites']]) {
    byId(id).setAttribute('aria-pressed',String(on));
    byId(id).classList.toggle('active',on);
  }
  if(db)render();
}
byId('allFilter').addEventListener('click',()=>changeFilter('all'));
byId('favoritesFilter').addEventListener('click',()=>changeFilter('favorites'));
function download(text,fileName,mimeType) {
  const objectURL=URL.createObjectURL(new Blob([text],{type:mimeType}));
  const anchor=document.createElement('a');anchor.href=objectURL;anchor.download=fileName;
  anchor.click();setTimeout(()=>URL.revokeObjectURL(objectURL),1000);
}
// An inactive browser tab can have stale UI state after another tab edits
// IndexedDB. Exports must capture a validated database snapshot, not cached UI state.
async function exportFresh({consent, serialize, fileName, mimeType, success}) {
  if(!db||busy)return;
  busy=true;
  try {
    // The scope is an explicit choice independent of search, tab or filter.
    // Both all-contact and favorites-only exports read the current IndexedDB.
    const scope=byId('exportScope').value;
    const current=await db.list();
    const selected=selectExportContacts(current,scope);
    records=current;
    render();
    if(scope==='favorites' && selected.length===0) {
      notice('No favorites available for export');return;
    }
    const encoded=serialize(selected); // Validate every record before asking.
    const label=scope==='favorites'?'Favorites only':'All contacts';
    const count=selected.length===1?'1 contact':selected.length+' contacts';
    if(!confirm(consent+'\nExport scope: '+label+' ('+count+').'))return;
    download(encoded,fileName,mimeType);
    notice(success);
  } catch {
    notice('Export failed; no contact file was prepared');
  } finally {
    busy=false;
    if(pendingLocalRefresh) {
      pendingLocalRefresh=false;
      refreshAfterPeerChange();
    }
  }
}
byId('exportBackup').addEventListener('click',()=>exportFresh({
  consent:'This backup is unencrypted. Save it only to storage you trust. Export your local contacts?',
  serialize:makeBackup,
  fileName:'goreecloud-contacts-backup.json',
  mimeType:'application/json',
  success:'Backup prepared locally'
}));
byId('exportCard').addEventListener('click',()=>exportFresh({
  consent:'Export names, phones, emails, and organizations as vCard? Favorites are not included.',
  serialize:makeVCard,
  fileName:'goreecloud-contacts.vcf',
  mimeType:'text/vcard;charset=utf-8',
  success:'vCard export prepared locally'
}));
byId('importBackup').addEventListener('click',()=>{if(db)inputFile.click();});
byId('importCard').addEventListener('click',()=>{if(db)cardFile.click();});
async function readStrictText(file) {
  if(file.size > MAX_BUNDLE_BYTES) throw new InvalidContact('File exceeds the 2 MiB size limit');
  try { return new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer()); }
  catch { throw new InvalidContact('Invalid UTF-8 contact file'); }
}
cardFile.addEventListener('change',async()=>{
  const file=cardFile.files?.[0];cardFile.value='';
  if(!file||!db||busy)return;
  let incoming;
  try {
    incoming=parseVCard(await readStrictText(file));
    const known=new Set(records.map(visibleIdentity));
    const staged=new Set();
    for(const c of incoming) {
      const key=visibleIdentity(c);
      if(known.has(key)||staged.has(key)) {
        throw new InvalidContact('Duplicate visible contact details; no import performed');
      }
      staged.add(key);
    }
  } catch(error) {
    notice(error instanceof InvalidContact?error.message:'Unable to read vCard file');
    return;
  }
  const preview=incoming.slice(0,3).map(c=>c.name).join(', ');
  if(!confirm('Import '+incoming.length+' limited vCards into this browser?\n'
    +'Preview: '+preview+(incoming.length>3?' …':'')+'\n'
    +'Only names, single phones, emails and organizations are supported. '
    +'Favorites and rich details are not included. Existing contacts will not be overwritten.'))return;
  mutate(async()=>{
    const count=await db.importNew(incoming,{rejectVisibleDuplicates:true});
    notice(count+' limited vCards imported locally');
  });
});
inputFile.addEventListener('change',async()=>{
  const file=inputFile.files?.[0];inputFile.value='';
  if(!file||!db||busy)return;
  if(file.size>MAX_BUNDLE_BYTES){notice('Backup exceeds the 2 MiB size limit');return;}
  let incoming;
  try {
    incoming=parseBackup(await readStrictText(file));
    const known=new Set(records.map(x=>x.id));
    if(incoming.some(x=>known.has(x.id))) {
      notice('Import stopped: matching contact IDs exist. Export a backup and resolve duplicates first.');return;
    }
  } catch(error){notice(error instanceof InvalidContact?error.message:'Unable to read that file');return;}
  if(!confirm('Import '+incoming.length+' contacts into this browser profile? This will not overwrite existing contacts.'))return;
  mutate(async()=>{const count=await db.importNew(incoming);notice(count+' contacts imported');});
});
enabled(false);
openStore().then(async opened=>{
  db=opened; await reload(); enabled(true);
}).catch(()=>{
  byId('countLabel').textContent='Private browser storage unavailable';
  byId('emptyState').hidden=false;
  byId('emptyTitle').textContent='Storage is unavailable';
  byId('emptyMessage').textContent='Open this app in a supported browser profile with IndexedDB enabled. No contacts were changed.';
  byId('emptyAdd').hidden=true;
  notice('Contacts are read-only until browser storage is available');
});
