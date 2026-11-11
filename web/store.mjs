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
  save(contact, isNew) {
    const entry = validateContact(contact);
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
          if (!found.result) { tx.abort(); return; }
          os.put(entry);
        };
      }
    });
  }
  remove(id) {
    if (typeof id !== 'string') throw new InvalidContact('Invalid contact ID');
    return new Promise((resolve,reject) => {
      const tx = this.db.transaction('contacts','readwrite');
      tx.objectStore('contacts').delete(id);
      tx.oncomplete = () => resolve();
      tx.onabort = () => reject(new Error('Contact deletion failed'));
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
