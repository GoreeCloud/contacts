#!/usr/bin/env python3
"""Real Chrome/ChromeDriver smoke of the Contacts browser app (synthetic-only).

Uses only Python's standard library and the Chrome/ChromeDriver binaries already
present on official GitHub Ubuntu hosted runners. No pip/npm downloads. Both
servers bind to 127.0.0.1. Browser data lives in a disposable profile; no user
browser profile, personal contacts, real accounts, telemetry or network backend.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, ProxyHandler, build_opener

WEB_DIR = Path(__file__).resolve().parents[1]
SERVER_MODULE = WEB_DIR / "server.py"
spec = importlib.util.spec_from_file_location("goreecloud_contacts_static", SERVER_MODULE)
static = importlib.util.module_from_spec(spec)
spec.loader.exec_module(static)
HTTP = build_opener(ProxyHandler({}))  # Never use any ambient HTTP proxy for loopback.


def driver_binary() -> str:
    direct = shutil.which("chromedriver")
    fallback = Path(os.environ.get("CHROMEWEBDRIVER", "/usr/local/share/chromedriver-linux64")) / "chromedriver"
    found = direct or (str(fallback) if fallback.is_file() else None)
    if not found:
        raise RuntimeError("ChromeDriver missing; real browser gate cannot be skipped")
    if not shutil.which("google-chrome") and not shutil.which("google-chrome-stable"):
        raise RuntimeError("Google Chrome missing; real browser gate cannot be skipped")
    return found


def port_free() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class WebDriver:
    def __init__(self, port: int):
        self.base = f"http://127.0.0.1:{port}"
        self.session = None

    def call(self, method: str, path: str, body=None):
        payload = json.dumps(body).encode("utf8") if body is not None else None
        request = Request(self.base + path, data=payload, method=method,
                          headers={"Content-Type": "application/json"})
        try:
            with HTTP.open(request, timeout=15) as response:
                obj = json.loads(response.read())
        except HTTPError as error:
            detail = error.read(1000).decode("utf8", errors="replace")
            raise RuntimeError(f"ChromeDriver HTTP {error.code}: {detail[:700]}") from error
        value = obj.get("value")
        if isinstance(value, dict) and value.get("error"):
            raise RuntimeError("ChromeDriver command failed: " + str(value.get("error")))
        return value

    def open_session(self, profile: Path):
        args = [
            "--headless=new", "--window-size=1200,850",
            "--disable-background-networking", "--disable-sync",
            "--disable-extensions", "--no-first-run", "--no-default-browser-check",
            "--disable-default-apps", "--disable-features=MediaRouter",
            "--user-data-dir=" + str(profile),
        ]
        value = self.call("POST", "/session", {"capabilities": {"alwaysMatch": {
            "browserName": "chrome",
            "acceptInsecureCerts": False,
            "goog:chromeOptions": {"args": args},
        }}})
        self.session = value["sessionId"]

    def navigate(self, url: str):
        return self.call("POST", f"/session/{self.session}/url", {"url": url})

    def execute(self, script: str):
        return self.call("POST", f"/session/{self.session}/execute/sync",
                         {"script": script, "args": []})

    def wait(self, script: str, expected, timeout: float = 12):
        until = time.monotonic() + timeout
        last = None
        while time.monotonic() < until:
            last = self.execute(script)
            if last == expected:
                return
            time.sleep(0.1)
        raise AssertionError("Real browser UI condition was not met: " + repr(last))

    def accept_confirm(self, contains: str, timeout: float = 10):
        until=time.monotonic()+timeout
        while time.monotonic()<until:
            try:
                message=self.call("GET",f"/session/{self.session}/alert/text")
            except RuntimeError as error:
                if "no such alert" in str(error).lower():
                    time.sleep(0.1)
                    continue
                raise
            if contains not in message:
                raise AssertionError("Unexpected browser confirmation prompt")
            self.call("POST",f"/session/{self.session}/alert/accept",{})
            return
        raise AssertionError("Expected import confirmation was not displayed")

    def close(self):
        if self.session is not None:
            try:
                self.call("DELETE", f"/session/{self.session}")
            finally:
                self.session = None


def smoke() -> None:
    binary = driver_binary()  # Fail if native real-browser dependency is missing.
    with tempfile.TemporaryDirectory(prefix="gc-contacts-browser-") as scratch:
        home = Path(scratch)
        chrome_profile = home / "disposable-chrome-profile"
        server = static.ThreadingHTTPServer(("127.0.0.1", 0), static.ContactsHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        driver_port = port_free()
        driver_process = subprocess.Popen(
            [binary, "--port=" + str(driver_port), "--allowed-ips=127.0.0.1"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        webdriver = WebDriver(driver_port)
        try:
            ready = False
            for _ in range(80):
                if driver_process.poll() is not None:
                    raise RuntimeError("ChromeDriver exited before its local status endpoint was ready")
                try:
                    state = webdriver.call("GET", "/status")
                    if state and state.get("ready"):
                        ready = True
                        break
                except (URLError, TimeoutError, RuntimeError):
                    time.sleep(0.1)
            if not ready:
                raise RuntimeError("ChromeDriver did not become ready on loopback")
            webdriver.open_session(chrome_profile)
            webdriver.navigate(f"http://127.0.0.1:{server.server_port}/")
            webdriver.wait(
                "return !!document.getElementById('newContact') && !document.getElementById('newContact').disabled",
                True)
            webdriver.wait("return document.getElementById('countLabel').textContent",
                           "0 contacts saved locally")
            assert webdriver.execute(
                "return performance.getEntriesByType('resource').every(r=>r.name.startsWith(location.origin+'/'))"
            ), "Unexpected off-origin application resource"

            # Exercise the real window editor and IndexedDB transaction, not a mocked model.
            webdriver.execute("""
                document.getElementById('newContact').click();
                const form=document.getElementById('editorForm');
                if(!document.getElementById('editorDialog').open) throw Error('Editor did not open');
                form.elements.namedItem('name').value='Synthetic Browser Person';
                form.elements.namedItem('phone').value='+1 555 0100';
                form.elements.namedItem('email').value='person@example.invalid';
                form.elements.namedItem('organization').value='GoreeCloud';
                form.requestSubmit();
            """)
            webdriver.wait("return document.getElementById('countLabel').textContent",
                           "1 contact saved locally")
            webdriver.wait("return document.querySelector('.person-name')?.textContent",
                           "Synthetic Browser Person")

            # Live favorites and local directory filter, including an empty-state transition.
            webdriver.execute("""
                const add=document.querySelector('button[title="Add Synthetic Browser Person to favorites"]');
                if(!add) throw Error('Favorite action missing');
                add.click();
            """)
            webdriver.wait("return !!document.querySelector('button.is-favorite')", True)
            webdriver.execute("document.getElementById('favoritesFilter').click();")
            webdriver.wait("return document.getElementById('contactList').childElementCount", 1)
            webdriver.execute("""
                const input=document.getElementById('searchInput');
                input.value='not-a-match';
                input.dispatchEvent(new Event('input',{bubbles:true}));
            """)
            webdriver.wait("return !document.getElementById('emptyState').hidden", True)
            webdriver.execute("""
                const input=document.getElementById('searchInput');
                input.value=''; input.dispatchEvent(new Event('input',{bubbles:true}));
            """)
            webdriver.wait("return document.getElementById('contactList').childElementCount", 1)

            # Actual browser reload must load the same private IndexedDB profile.
            webdriver.navigate(f"http://127.0.0.1:{server.server_port}/")
            webdriver.wait("return document.getElementById('countLabel').textContent",
                           "1 contact saved locally")
            webdriver.wait("return !!document.querySelector('button.is-favorite')", True)

            # Confirm cancel preserves data, then confirmed deletion is persisted.
            webdriver.execute("""
                document.querySelector('button[title="Delete Synthetic Browser Person"]').click();
                if(!document.getElementById('deleteDialog').open) throw Error('Delete dialog missing');
                document.getElementById('cancelDelete').click();
            """)
            assert webdriver.execute("return document.getElementById('contactList').childElementCount") == 1
            webdriver.execute("""
                document.querySelector('button[title="Delete Synthetic Browser Person"]').click();
                document.getElementById('confirmDelete').click();
            """)
            webdriver.wait("return document.getElementById('countLabel').textContent",
                           "0 contacts saved locally")
            webdriver.navigate(f"http://127.0.0.1:{server.server_port}/")
            webdriver.wait("return document.getElementById('countLabel').textContent",
                           "0 contacts saved locally")

            # Exercise the actual new limited vCard upload + browser-native
            # consent alert, not merely the shared parser in a Node test.
            webdriver.wait(
                "return !!document.getElementById('importCard') && !document.getElementById('importCard').disabled",
                True)
            limited_vcard=(
                "BEGIN:VCARD\r\nVERSION:3.0\r\n"
                "N:Synthetic Imported Contact;;;;\r\n"
                "FN:Synthetic Imported Contact\r\n"
                "TEL:+1 555 0101\r\n"
                "EMAIL:import@example.invalid\r\n"
                "ORG:GoreeCloud\r\nEND:VCARD\r\n"
            )
            def offer_vcard(source):
                script=(
                    "const input=document.getElementById('importCardFile');"
                    "const value=new File([" + json.dumps(source) +
                    "],'synthetic.vcf',{type:'text/vcard'});"
                    "const transfer=new DataTransfer();transfer.items.add(value);"
                    "input.files=transfer.files;"
                    "input.dispatchEvent(new Event('change',{bubbles:true}));"
                )
                try:
                    webdriver.execute(script)
                except RuntimeError as error:
                    if "unexpected alert open" not in str(error).lower():
                        raise
            offer_vcard(limited_vcard)
            webdriver.accept_confirm("Import 1 limited vCards")
            webdriver.wait("return document.getElementById('countLabel').textContent",
                           "1 contact saved locally")
            webdriver.wait("return document.querySelector('.person-name')?.textContent",
                           "Synthetic Imported Contact")
            # Duplicate imported visible details must not create an extra record.
            offer_vcard(limited_vcard)
            webdriver.wait(
                "return document.getElementById('announcer').textContent",
                "Duplicate visible contact details; no import performed")
            assert webdriver.execute(
                "return document.getElementById('contactList').childElementCount"
            )==1
            # Rich vCards are rejected, never quietly truncated into six fields.
            offer_vcard(limited_vcard.replace("END:VCARD",
                                              "NOTE:private info must not be lost\r\nEND:VCARD"))
            webdriver.wait(
                "return document.getElementById('announcer').textContent",
                "Unsupported or duplicate vCard property")
            assert webdriver.execute(
                "return document.getElementById('contactList').childElementCount"
            )==1

            # Basic small-screen horizontal overflow regression.
            webdriver.call("POST", f"/session/{webdriver.session}/window/rect",
                           {"width": 390, "height": 800})
            assert webdriver.execute(
                "return document.documentElement.scrollWidth <= window.innerWidth + 3"
            ), "Unexpected horizontal overflow in compact browser layout"
            print("GOREECLOUD_CONTACTS_REAL_CHROME_INDEXEDDB_VCARD_EDITOR_FAVORITES_SEARCH_DELETE_PASS")
        finally:
            webdriver.close()
            driver_process.terminate()
            try:
                driver_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                driver_process.kill()
                driver_process.wait(timeout=5)
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    smoke()
