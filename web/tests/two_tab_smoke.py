#!/usr/bin/env python3
"""Actual two-tab IndexedDB stale edit/delete conflict safety acceptance.

Uses first-party loopback server, one disposable Chrome profile, two real
browser tabs and only invented contacts. The stale UI must never overwrite
or delete an update committed in the other tab.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import threading
import time

from browser_smoke import WebDriver, driver_binary, port_free, static


def switch(browser: WebDriver, handle: str):
    browser.call("POST",f"/session/{browser.session}/window",{"handle":handle})


def create(browser: WebDriver):
    browser.execute("""
        document.getElementById('newContact').click();
        const form=document.getElementById('editorForm');
        if(!document.getElementById('editorDialog').open) throw Error('Editor missing');
        form.elements.namedItem('name').value='Synthetic Multi-Tab Contact';
        form.elements.namedItem('email').value='tabs@example.invalid';
        form.requestSubmit();
    """)
    browser.wait("return document.getElementById('countLabel').textContent",
                 "1 contact saved locally")
    browser.wait("return document.querySelector('.person-name')?.textContent",
                 "Synthetic Multi-Tab Contact")


def start_edit(browser: WebDriver, old: str, next_name: str):
    browser.execute("""
        const title='Edit ' + """ + repr(old) + """;
        const action=[...document.querySelectorAll('button')].find(
            b=>b.getAttribute('title')===title);
        if(!action) throw Error('Expected edit action absent');
        action.click();
        if(!document.getElementById('editorDialog').open) throw Error('Editor did not open');
        document.getElementById('editorForm').elements.namedItem('name').value=
            """ + repr(next_name) + """;
    """)


def smoke():
    binary=driver_binary()
    with tempfile.TemporaryDirectory(prefix="gc-contacts-tabs-") as scratch:
        server=static.ThreadingHTTPServer(("127.0.0.1",0),static.ContactsHandler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        port=port_free()
        chrome=subprocess.Popen(
            [binary,"--port="+str(port),"--allowed-ips=127.0.0.1"],
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,close_fds=True)
        browser=WebDriver(port)
        try:
            ready=False
            for _ in range(85):
                if chrome.poll() is not None:
                    raise RuntimeError("ChromeDriver exited unexpectedly")
                try:
                    if browser.call("GET","/status").get("ready"):
                        ready=True
                        break
                except (OSError,RuntimeError):
                    time.sleep(0.1)
            if not ready:
                raise RuntimeError("ChromeDriver unavailable")
            browser.open_session(Path(scratch)/"private-browser-profile")
            url=f"http://127.0.0.1:{server.server_port}/"
            browser.navigate(url)
            browser.wait("return !!document.getElementById('newContact') && "
                         "!document.getElementById('newContact').disabled",True)
            a=browser.call("GET",f"/session/{browser.session}/window")
            create(browser)
            start_edit(browser,"Synthetic Multi-Tab Contact","Stale first-tab edit")

            # A genuine second browser tab shares IndexedDB but not the first
            # tab's form snapshot, unlike a mocked repository or JS-only test.
            new=browser.call("POST",f"/session/{browser.session}/window/new",
                             {"type":"tab"})
            b=new["handle"]
            assert b!=a
            switch(browser,b)
            browser.navigate(url)
            browser.wait("return document.getElementById('countLabel').textContent",
                         "1 contact saved locally")
            start_edit(browser,"Synthetic Multi-Tab Contact","Fresh second-tab edit")
            browser.execute("document.getElementById('editorForm').requestSubmit()")
            browser.wait("return document.querySelector('.person-name')?.textContent",
                         "Fresh second-tab edit")

            switch(browser,a)
            browser.wait("return document.getElementById('editorDialog').open",True)
            browser.execute("document.getElementById('editorForm').requestSubmit()")
            browser.wait("return document.getElementById('announcer').textContent",
                         "Unable to complete action; existing data was kept")
            assert browser.execute(
                "return document.getElementById('editorDialog').open"
            ), "Stale edit incorrectly closed its dialog"
            browser.execute("document.getElementById('cancelEditor').click()")
            switch(browser,b)
            browser.navigate(url)
            browser.wait("return document.querySelector('.person-name')?.textContent",
                         "Fresh second-tab edit")

            # A captured deletion confirmation is stale after a second-tab
            # edit. The original tab must refuse to delete the newer data.
            switch(browser,a)
            browser.wait("return document.querySelector('.person-name')?.textContent",
                         "Fresh second-tab edit")
            browser.execute("""
                const action=[...document.querySelectorAll('button')].find(
                    b=>b.title==='Delete Fresh second-tab edit');
                if(!action) throw Error('Expected delete action absent');
                action.click();
            """)
            browser.wait("return document.getElementById('deleteDialog').open",True)
            switch(browser,b)
            start_edit(browser,"Fresh second-tab edit","Final second-tab edit")
            browser.execute("document.getElementById('editorForm').requestSubmit()")
            browser.wait("return document.querySelector('.person-name')?.textContent",
                         "Final second-tab edit")

            switch(browser,a)
            browser.execute("document.getElementById('confirmDelete').click()")
            browser.wait("return document.getElementById('announcer').textContent",
                         "Unable to complete action; existing data was kept")
            switch(browser,b)
            browser.navigate(url)
            browser.wait("return document.querySelector('.person-name')?.textContent",
                         "Final second-tab edit")
            browser.wait("return document.getElementById('countLabel').textContent",
                         "1 contact saved locally")
            print("GOREECLOUD_CONTACTS_REAL_TWO_TAB_STALE_EDIT_DELETE_SAFE_PASS")
        finally:
            browser.close()
            chrome.terminate()
            try:
                chrome.wait(timeout=5)
            except subprocess.TimeoutExpired:
                chrome.kill()
                chrome.wait(timeout=5)
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__=="__main__":
    smoke()
