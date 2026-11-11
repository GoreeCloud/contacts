import {InvalidContact, MAX_BUNDLE_BYTES, parseBackup, makeBackup, makeVCard, validateContact, searchContacts} from './model.mjs';
import {openStore} from './store.mjs';
const byId = id => document.getElementById(id);
const inputFile = byId('importFile'), editor = byId('editorDialog'), form = byId('editorForm');
let db = null, records = [], editingId = null, deleteId = null, activeFilter = 'all', busy = false;
let noticeTimer = null;
function notice(message) {
  const el=byId('announcer');
  el.textContent=message; el.classList.add('visible');
  clearTimeout(noticeTimer); noticeTimer=setTimeout(()=>el.classList.remove('visible'),4700);
}
function enabled(value) {
  for(const id of ['newContact','emptyAdd','importBackup','exportBackup','exportCard']) byId(id).disabled=!value;
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
        mutate(async()=>{ await db.save({...c,favorite:!c.favorite},false); notice(c.favorite?'Removed from favorites':'Added to favorites'); });
      });
    const edit=button('Edit '+c.name,'✎','icon-button',()=>openEditor(c));
    const remove=button('Delete '+c.name,'×','icon-button',()=>{deleteId=c.id;byId('deleteTitle').textContent='Delete '+c.name+'?';byId('deleteDialog').showModal();});
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
async function mutate(action) {
  if(!db||busy)return;
  busy=true;
  try {await action();await reload();}
  catch (error) {notice(error instanceof InvalidContact?error.message:'Unable to complete action; existing data was kept');}
  finally {busy=false;}
}
function openEditor(c=null) {
  editingId=c?.id??null;
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
    await db.save(checked,!editingId);editor.close();notice(editingId?'Contact updated':'Contact added');
  });
});
for(const id of ['cancelEditor','discardEditor']) byId(id).addEventListener('click',()=>editor.close());
byId('newContact').addEventListener('click',()=>openEditor());
byId('emptyAdd').addEventListener('click',()=>openEditor());
byId('cancelDelete').addEventListener('click',()=>byId('deleteDialog').close());
byId('confirmDelete').addEventListener('click',()=>{
  const id=deleteId;byId('deleteDialog').close();deleteId=null;
  mutate(async()=>{await db.remove(id);notice('Contact deleted');});
});
byId('searchInput').addEventListener('input',()=>{if(db)render();});
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
byId('exportBackup').addEventListener('click',()=>{
  if(!db)return;
  if(!confirm('This backup is unencrypted. Save it only to storage you trust. Export your local contacts?'))return;
  try {download(makeBackup(records),'goreecloud-contacts-backup.json','application/json');notice('Backup prepared locally');}
  catch(error){notice(error.message);}
});
byId('exportCard').addEventListener('click',()=>{
  if(!db)return;
  if(!confirm('Export names, phones, emails, and organizations as vCard? Favorites are not included.'))return;
  try {download(makeVCard(records),'goreecloud-contacts.vcf','text/vcard;charset=utf-8');notice('vCard export prepared locally');}
  catch(error){notice(error.message);}
});
byId('importBackup').addEventListener('click',()=>{if(db)inputFile.click();});
inputFile.addEventListener('change',async()=>{
  const file=inputFile.files?.[0];inputFile.value='';
  if(!file||!db||busy)return;
  if(file.size>MAX_BUNDLE_BYTES){notice('Backup exceeds the 2 MiB size limit');return;}
  let incoming;
  try {
    incoming=parseBackup(await file.text());
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
