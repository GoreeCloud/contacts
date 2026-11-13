#!/usr/bin/env python3
"""Real Chrome opt-in scoped export acceptance, using only synthetic contacts.

Chrome and ChromeDriver are provided by the official GitHub runner. No
external package, personal browser profile, remote service or user contact is
accessed. Files are downloaded into a temporary test-only directory.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import threading
import time

from browser_smoke import WebDriver, driver_binary, port_free, static


def smoke():
    binary = driver_binary()
    with tempfile.TemporaryDirectory(prefix="gc-contacts-export-scope-") as scratch:
        home = Path(scratch)
        server = static.ThreadingHTTPServer(("127.0.0.1",0),static.ContactsHandler)
        server_thread = threading.Thread(target=server.serve_forever,daemon=True)
        server_thread.start()
        chrome_port=port_free()
        driver_proc=subprocess.Popen(
            [binary,"--port="+str(chrome_port),"--allowed-ips=127.0.0.1"],
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,close_fds=True)
        browser=WebDriver(chrome_port)
        try:
            for attempt in range(85):
                if driver_proc.poll() is not None:
                    raise RuntimeError("ChromeDriver exited before scoped export test")
                try:
                    if browser.call("GET","/status").get("ready"):
                        break
                except (OSError,RuntimeError):
                    pass
                time.sleep(0.1)
            else:
                raise RuntimeError("ChromeDriver did not start")
            browser.open_session(home/"disposable-profile")
            url=f"http://127.0.0.1:{server.server_port}/"
            browser.navigate(url)
            browser.wait(
                "return !!document.getElementById('newContact') && "
                "!document.getElementById('newContact').disabled",True)
            assert browser.execute("return document.getElementById('exportScope').value")=="all"

            def create(name: str, email: str, favorite: bool, count: int):
                # Actual editor submission, not mocked database data.
                browser.execute("""
                    document.getElementById('newContact').click();
                    const form=document.getElementById('editorForm');
                    form.elements.namedItem('name').value="""+json.dumps(name)+""";
                    form.elements.namedItem('email').value="""+json.dumps(email)+""";
                    form.elements.namedItem('favorite').checked="""+json.dumps(favorite)+""";
                    form.requestSubmit();
                """)
                browser.wait("return document.getElementById('countLabel').textContent",
                             f"{count} contacts saved locally")

            create("Synthetic Favorite","favorite@example.invalid",True,1)
            create("Synthetic Private","private@example.invalid",False,2)
            assert browser.execute("return document.querySelectorAll('button.is-favorite').length")==1
            browser.execute("document.getElementById('exportScope').value='favorites'")
            assert browser.execute("return document.getElementById('exportScope').value")=="favorites"

            def click_and_confirm(button: str, fragment: str):
                try:
                    browser.execute("document.getElementById("+json.dumps(button)+").click()")
                except RuntimeError as error:
                    if "unexpected alert open" not in str(error).lower():
                        raise
                browser.accept_confirm(fragment)

            def downloaded(filename: str) -> Path:
                path=home/"synthetic-downloads"/filename
                until=time.monotonic()+15
                while time.monotonic()<until and not path.is_file():
                    time.sleep(0.1)
                if not path.is_file():
                    raise AssertionError("Synthetic scoped export file not created")
                return path

            click_and_confirm("exportBackup","Export scope: Favorites only (1 contact)")
            backup=json.loads(downloaded("goreecloud-contacts-backup.json").read_text(encoding="utf8"))
            assert backup["format"]=="goreecloud.contacts.v1"
            assert len(backup["contacts"])==1
            assert backup["contacts"][0]["name"]=="Synthetic Favorite"
            assert backup["contacts"][0]["favorite"] is True
            assert "private@example.invalid" not in json.dumps(backup)
            click_and_confirm("exportCard","Export scope: Favorites only (1 contact)")
            vcard=downloaded("goreecloud-contacts.vcf").read_text(encoding="utf8")
            assert vcard.count("BEGIN:VCARD")==1
            assert "favorite@example.invalid" in vcard
            assert "private@example.invalid" not in vcard

            # Selecting all must surface the larger count for consent before
            # any second file is produced. Dismiss, never silently export.
            browser.execute("document.getElementById('exportScope').value='all'")
            try:
                browser.execute("document.getElementById('exportBackup').click()")
            except RuntimeError as error:
                if "unexpected alert open" not in str(error).lower():
                    raise
            message=browser.call("GET",f"/session/{browser.session}/alert/text")
            assert "Export scope: All contacts (2 contacts)" in message
            browser.call("POST",f"/session/{browser.session}/alert/dismiss",{})
            assert len(list((home/"synthetic-downloads").glob("*.json")))==1

            # Favorites-only with none selected refuses a misleading empty export.
            browser.execute("""
                document.querySelector('button.is-favorite').click();
            """)
            browser.wait("return document.querySelectorAll('button.is-favorite').length",0)
            browser.execute("document.getElementById('exportScope').value='favorites'")
            browser.execute("document.getElementById('exportBackup').click()")
            browser.wait("return document.getElementById('announcer').textContent",
                         "No favorites available for export")
            assert len(list((home/"synthetic-downloads").glob("*.json")))==1

            browser.call("POST",f"/session/{browser.session}/window/rect",
                         {"width":320,"height":700})
            assert browser.execute(
                "return document.documentElement.scrollWidth<=window.innerWidth+3"
            ), "New export scope control caused narrow-screen horizontal overflow"
            assert browser.execute(
                "return performance.getEntriesByType('resource').every(e=>"
                "e.name.startsWith(location.origin+'/'))"
            ), "Unexpected third-party browser network resource"
            print("GOREECLOUD_CONTACTS_REAL_CHROME_FAVORITES_SCOPE_PRIVACY_PASS")
        finally:
            browser.close()
            driver_proc.terminate()
            try:
                driver_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                driver_proc.kill()
                driver_proc.wait(timeout=5)
            server.shutdown()
            server.server_close()
            server_thread.join(timeout=3)


if __name__ == "__main__":
    smoke()
