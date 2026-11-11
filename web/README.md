# GoreeCloud Contacts — web application

This is a browser-native, locally persistent Contacts app with no external JS packages, CDN, remote fonts, telemetry or network APIs. It includes GoreeCloud UI tokens and the verified official GoreeCloud umbrella logo.

Run from repository root: python3 web/server.py --port 8765. Visit http://127.0.0.1:8765/. This loopback-only static development server is not an authenticated contact-hosting or public production service.

Implemented in source: create/edit/delete, favorites, accent-insensitive search, accessible dialogs and controls, responsive light/dark design, atomic no-overwrite import of strict JSON v1, user-confirmed unencrypted JSON backup and limited vCard 3.0 export. Contacts persist only in the current browser profile's IndexedDB.

Caution: Browser-profile data is not encrypted by this app. Clearing browser data can delete it, and anyone who controls the same unlocked profile can access it. The app never automatically syncs contacts with Linux, Android or a server. Exports create sensitive plaintext files.

Tests: node --test web/tests/*.test.mjs; python3 -m unittest discover -s web/tests -p test_*.py. Native browser visual and assistive-technology acceptance remain open. See docs/PLATFORMS.md in the parent repository.
