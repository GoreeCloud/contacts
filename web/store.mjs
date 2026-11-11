// Isolated, browser-profile IndexedDB database. No fetch, remote API or telemetry.
import {InvalidContact, MAX_CONTACTS, validateContact, validateCollection} from './model.mjs';
const DB = 'goreecloud-contacts-web-v1';
export function openStore() {
  return new Promise((resolve,reject) => {
    if (typeof indexedDB === 'undefined') {
      reject(new Error('Browser storage is unavailable')); return;
    }
    const req = indexedDB.open(DB,1);
    req.onupgradeneeded = () => {
      if (!req.result.objectStoreNames.contains('contacts')) {
        req.result.createObjectStore('contacts',{keyPath:'id'});
      }
    };
    req.onsuccess = () => resolve(new ContactStore(req.result));
    req.onerror = () => reject(new Error('Unable to open private browser storage'));
    req.onblocked = () => reject(new Error('Close other Contacts tabs to upgrade browser storage'));
  });
}
export function sameContact(a,b) {
  try { return JSON.stringify(validateContact(a)) === JSON.stringify(validateContact(b)); }
  catch { return false; }
}
export class ContactStore {
  constructor(db) { this.db = db; }
  close() { this.db.close(); }
  list() {
    return new Promise((resolve,reject) => {
      const tx = this.db.transaction('contacts','readonly');
      const req = tx.objectStore('contacts').getAll();
      req.onsuccess = () => {
        try { resolve(validateCollection(req.result)); }
        catch { reject(new Error('Stored contact records are invalid; no changes were made')); }
      };
      req.onerror = () => reject(new Error('Unable to read contacts'));
      tx.onabort = () => reject(new Error('Contact read transaction failed'));
    });
  }
  save(contact, isNew, expected = null) {
    const entry = validateContact(contact);
    const prior = isNew ? null : validateContact(expected);
    if (!isNew && prior.id !== entry.id) throw new InvalidContact('Contact identity changed');
    return new Promise((resolve,reject) => {
      const tx = this.db.transaction('contacts','readwrite'), os = tx.objectStore('contacts');
      tx.oncomplete = () => resolve();
      tx.onabort = () => reject(new Error('Contact was not saved'));
      if (isNew) {
        const count = os.count();
        count.onsuccess = () => {
          if (count.result >= MAX_CONTACTS) { tx.abort(); return; }
          os.add(entry); // Duplicate IDs abort transaction; existing record is not overwritten.
        };
      } else {
        const found = os.get(entry.id);
        found.onsuccess = () => {
          if (!found.result || !sameContact(found.result,prior)) { tx.abort(); return; }
          os.put(entry); // Refuse stale editor or another-tab overwrites.
        };
      }
    });
  }
  remove(id, expected) {
    const prior = validateContact(expected);
    if (id !== prior.id) throw new InvalidContact('Contact identity changed');
    return new Promise((resolve,reject) => {
      const tx = this.db.transaction('contacts','readwrite');
      const os = tx.objectStore('contacts');
      const current = os.get(id);
      current.onsuccess = () => {
        if (!current.result || !sameContact(current.result,prior)) { tx.abort(); return; }
        os.delete(id);
      };
      tx.oncomplete = () => resolve();
      tx.onabort = () => reject(new Error('Contact changed or deletion failed'));
    });
  }
  importNew(entries) {
    const contacts=validateCollection(entries);
    return new Promise((resolve,reject) => {
      const tx=this.db.transaction('contacts','readwrite'), os=tx.objectStore('contacts');
      tx.oncomplete=() => resolve(contacts.length);
      tx.onabort=() => reject(new Error('Import was rolled back; duplicate ID or storage limit'));
      const count=os.count();
      count.onsuccess=() => {
        if (count.result + contacts.length > MAX_CONTACTS) { tx.abort(); return; }
        for(const c of contacts) os.add(c); // Atomic: one conflicting ID rolls back every imported row.
      };
    });
  }
}
