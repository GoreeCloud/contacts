// GoreeCloud Contacts portable, no-network development contract v1.
// Manual JSON transfer preserves favorites. vCard 3.0 deliberately omits favorites.
export const FORMAT = 'goreecloud.contacts.v1';
export const MAX_CONTACTS = 5000;
export const MAX_BUNDLE_BYTES = 2 * 1024 * 1024;
const LIMITS = Object.freeze({name: 160, phone: 80, email: 254, organization: 160});
const KEYS = Object.freeze(['email','favorite','id','name','organization','phone']);
const UUID = /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/;
const UNSAFE = /[\u0000-\u001f\u007f-\u009f\u061c\u200e\u200f\u2028\u2029\u202a-\u202e\u2066-\u2069]/u;
const encoder = new TextEncoder();

export class InvalidContact extends Error {
  constructor(message) { super(message); this.name = 'InvalidContact'; }
}
function plainObject(value, exactKeys) {
  if (value === null || typeof value !== 'object' || Array.isArray(value) ||
      Object.getPrototypeOf(value) !== Object.prototype) throw new InvalidContact('Expected a plain object');
  const keys = Object.keys(value).sort();
  if (keys.length !== exactKeys.length || keys.some((key,i) => key !== exactKeys[i])) {
    throw new InvalidContact('Unexpected or missing fields');
  }
}
function field(name, value) {
  if (typeof value !== 'string') throw new InvalidContact('Invalid ' + name + ' type');
  const normalized = value.trim().normalize('NFC');
  if (normalized.length > LIMITS[name] || encoder.encode(normalized).length > LIMITS[name] * 4 ||
      UNSAFE.test(normalized) ||
      new TextDecoder('utf-8',{fatal:false}).decode(encoder.encode(normalized)) !== normalized) {
    throw new InvalidContact('Invalid ' + name + ' content');
  }
  if (name === 'name' && normalized.length === 0) throw new InvalidContact('Name is required');
  return normalized;
}
export function validateContact(value) {
  plainObject(value, KEYS);
  if (typeof value.id !== 'string' || !UUID.test(value.id)) throw new InvalidContact('Invalid contact ID');
  if (typeof value.favorite !== 'boolean') throw new InvalidContact('Invalid favorite flag');
  return Object.freeze({
    id: value.id, name: field('name',value.name),
    phone: field('phone',value.phone),
    email: field('email',value.email),
    organization: field('organization',value.organization),
    favorite: value.favorite,
  });
}
export function validateCollection(value) {
  if (!Array.isArray(value) || value.length > MAX_CONTACTS) throw new InvalidContact('Too many contacts');
  const seen = new Set();
  const contacts = value.map(item => {
    const contact = validateContact(item);
    if (seen.has(contact.id)) throw new InvalidContact('Duplicate contact IDs');
    seen.add(contact.id);
    return contact;
  });
  return contacts;
}
export function parseBackup(text) {
  if (typeof text !== 'string' || encoder.encode(text).length > MAX_BUNDLE_BYTES) {
    throw new InvalidContact('Backup exceeds size limit');
  }
  let value;
  try { value = JSON.parse(text); } catch { throw new InvalidContact('Invalid backup JSON'); }
  plainObject(value, ['contacts','format']);
  if (value.format !== FORMAT) throw new InvalidContact('Unsupported backup format');
  return validateCollection(value.contacts);
}
export function makeBackup(records) {
  const contacts = validateCollection(records).sort((a,b) => a.id.localeCompare(b.id));
  const text = JSON.stringify({format: FORMAT, contacts}, null, 2) + '\n';
  if (encoder.encode(text).length > MAX_BUNDLE_BYTES) throw new InvalidContact('Backup exceeds size limit');
  return text;
}
function esc(value) { return value.replaceAll('\\','\\\\').replaceAll(';','\\;').replaceAll(',','\\,'); }
function foldedLine(line) {
  let current = '', size = 0, output = '';
  for (const symbol of line) {
    const n = encoder.encode(symbol).length;
    if (size + n > 75) { output += current + '\r\n'; current=' '; size=1; }
    current += symbol; size += n;
  }
  return output + current;
}
export function makeVCard(records) {
  const contacts = validateCollection(records);
  let lines = [];
  for (const c of contacts) {
    lines.push('BEGIN:VCARD', 'VERSION:3.0', 'N:' + esc(c.name) + ';;;;',
      'FN:' + esc(c.name));
    if (c.phone) lines.push('TEL:' + esc(c.phone));
    if (c.email) lines.push('EMAIL:' + esc(c.email));
    if (c.organization) lines.push('ORG:' + esc(c.organization));
    lines.push('END:VCARD');
  }
  const text = lines.map(foldedLine).join('\r\n') + (lines.length ? '\r\n' : '');
  if (encoder.encode(text).length > MAX_BUNDLE_BYTES) throw new InvalidContact('vCard export exceeds size limit');
  return text;
}
export function searchContacts(records, query) {
  const fold = value => value.normalize('NFKD').replace(/\p{M}/gu,'').toLowerCase();
  const needle = fold(String(query ?? '').trim());
  return validateCollection(records).filter(c => !needle ||
    [c.name,c.phone,c.email,c.organization].some(v => fold(v).includes(needle)))
    .sort((a,b) => Number(b.favorite) - Number(a.favorite) ||
      a.name.localeCompare(b.name, undefined, {sensitivity:'base'}));
}
