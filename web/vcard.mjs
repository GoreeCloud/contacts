// Restrictive vCard 3.0 import for the exact limited profile GoreeCloud Contacts exports.
// Fail closed on rich/unknown fields rather than silently dropping personal information.
import {InvalidContact, MAX_BUNDLE_BYTES, MAX_CONTACTS, validateContact, validateCollection} from './model.mjs';
const encoder = new TextEncoder();
const ALLOWED = new Set(['VERSION','N','FN','TEL','EMAIL','ORG']);

function decodeValue(value) {
  let output = '';
  for (let i=0; i<value.length; i++) {
    const c = value[i];
    if (c === '\\') {
      const next = value[++i];
      if (next !== '\\' && next !== ';' && next !== ',') {
        throw new InvalidContact('Unsupported vCard escape sequence');
      }
      output += next;
    } else if (c === ';' || c === ',') {
      throw new InvalidContact('Unescaped vCard punctuation');
    } else {
      output += c;
    }
  }
  return output;
}
function encodeValue(value) {
  return value.replaceAll('\\','\\\\').replaceAll(';','\\;').replaceAll(',','\\,');
}
function unfold(text) {
  if (text.includes('\r') && text.replaceAll('\r\n','').includes('\r')) {
    throw new InvalidContact('Unsupported vCard line endings');
  }
  const physical = text.replaceAll('\r\n','\n').split('\n');
  if (physical.at(-1) === '') physical.pop();
  const logical = [];
  for (const line of physical) {
    if (encoder.encode(line).length > 1000 || !line) {
      throw new InvalidContact('Invalid or oversized vCard line');
    }
    if (line[0] === ' ' || line[0] === '\t') {
      if (!logical.length) throw new InvalidContact('Invalid folded vCard line');
      const value = logical.at(-1) + line.slice(1);
      if (encoder.encode(value).length > 2000) {
        throw new InvalidContact('Oversized unfolded vCard field');
      }
      logical[logical.length - 1] = value;
    } else {
      logical.push(line);
    }
  }
  return logical;
}

export function parseVCard(text, newId = () => crypto.randomUUID()) {
  if (typeof text !== 'string' || !text.length || encoder.encode(text).length > MAX_BUNDLE_BYTES) {
    throw new InvalidContact('Invalid or oversized vCard file');
  }
  const lines = unfold(text.startsWith('\uFEFF') ? text.slice(1) : text);
  let card = null, contacts = [];
  for (const line of lines) {
    if (line === 'BEGIN:VCARD') {
      if (card !== null) throw new InvalidContact('Nested vCard not supported');
      card = Object.create(null);
      continue;
    }
    if (card === null) throw new InvalidContact('vCard content outside a record');
    if (line === 'END:VCARD') {
      if (card.VERSION !== '3.0' || typeof card.FN !== 'string' || typeof card.N !== 'string') {
        throw new InvalidContact('Missing or unsupported vCard identity');
      }
      const name = decodeValue(card.FN);
      if (card.N !== encodeValue(name) + ';;;;') {
        throw new InvalidContact('Structured name cannot be imported without data loss');
      }
      const contact = validateContact({
        id: newId(), name,
        phone: decodeValue(card.TEL ?? ''),
        email: decodeValue(card.EMAIL ?? ''),
        organization: decodeValue(card.ORG ?? ''),
        favorite: false,
      });
      contacts.push(contact);
      if (contacts.length > MAX_CONTACTS) throw new InvalidContact('Too many vCards');
      card = null;
      continue;
    }
    const at = line.indexOf(':');
    if (at <= 0) throw new InvalidContact('Invalid vCard property');
    const key = line.slice(0,at);
    if (!ALLOWED.has(key) || Object.hasOwn(card,key)) {
      throw new InvalidContact('Unsupported or duplicate vCard property');
    }
    card[key] = line.slice(at+1);
  }
  if (card !== null || contacts.length === 0) throw new InvalidContact('Incomplete or empty vCard file');
  return validateCollection(contacts);
}

// Names, phones, emails and organizations are the fields retained by this importer.
// Used only for duplicate detection: no contact record is overwritten.
export function visibleIdentity(contact) {
  const c = validateContact(contact);
  return JSON.stringify([c.name.toLocaleLowerCase(),c.phone,c.email.toLocaleLowerCase(),
    c.organization.toLocaleLowerCase()]);
}
