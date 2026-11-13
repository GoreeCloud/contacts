# GoreeCloud Contacts — browser keyboard acceptance (development)

The web app uses native HTML `dialog` elements, semantic label associations, keyboard-operable buttons, `role="alert"` for form errors, `aria-pressed` for filters, and a visible `:focus-visible` outline. Its existing CSS also respects `prefers-reduced-motion`.

An independent **real Chrome** test lives in `web/tests/keyboard_smoke.py` and runs under `.github/workflows/web-keyboard.yml`. It uses ChromeDriver's actual W3C keyboard actions rather than synthetic click events to check that Tab reaches New contact, Enter opens a native editor, the name field receives focus, Escape restores focus, invalid form submission announces an error, and Enter toggles semantic filters. It also checks horizontal overflow at 320 px. The test runs with a disposable Chrome profile and a first-party loopback HTTP server, no personal contacts and no third-party npm/pip dependency.

To run the smoke where Google Chrome and ChromeDriver are installed: `python3 web/tests/keyboard_smoke.py`. A CI pass is limited **keyboard/runtime evidence**, not a certification of screen-reader announcements, WCAG conformance, VoiceOver/NVDA behavior, color contrast across all modes, or interaction on actual phones and tablets.

**Still open:** real assistive-technology testing, high-contrast/forced-colors visual inspection, touch and zoom behavior, error recovery, non-Chromium browsers, and founder approval of the final GoreeCloud UI implementation. No public hosted service, account login, CardDAV sync or encryption is added by this test.
