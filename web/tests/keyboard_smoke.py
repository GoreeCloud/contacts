#!/usr/bin/env python3
"""Synthetic real Chrome keyboard focus, dialog and compact layout acceptance.

This is not screen reader certification. It checks browser-native keyboard
events and actual DOM focus, without reading real contact data or using any
persistent browser profile, external package, account or network endpoint.
"""
from __future__ import annotations

from pathlib import Path
import os
import subprocess
import tempfile
import threading
import time

from browser_smoke import WebDriver, driver_binary, port_free, static


def key(driver: WebDriver, value: str):
    driver.call("POST",f"/session/{driver.session}/actions",{
        "actions":[{"type":"key","id":"keyboard","actions":[
            {"type":"keyDown","value":value},
            {"type":"keyUp","value":value},
        ]}]
    })


def smoke():
    binary=driver_binary()
    with tempfile.TemporaryDirectory(prefix="gc-contacts-keyboard-") as scratch:
        directory=Path(scratch)
        http=static.ThreadingHTTPServer(("127.0.0.1",0),static.ContactsHandler)
        thread=threading.Thread(target=http.serve_forever,daemon=True)
        thread.start()
        driver_port=port_free()
        process=subprocess.Popen(
            [binary,"--port="+str(driver_port),"--allowed-ips=127.0.0.1"],
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,close_fds=True)
        browser=WebDriver(driver_port)
        try:
            status=False
            for _ in range(85):
                if process.poll() is not None:
                    raise RuntimeError("ChromeDriver exited before keyboard test started")
                try:
                    state=browser.call("GET","/status")
                    if state and state.get("ready"):
                        status=True
                        break
                except (OSError, RuntimeError):
                    time.sleep(0.1)
            if not status:
                raise RuntimeError("ChromeDriver failed to initialize")
            browser.open_session(directory/"disposable-profile")
            browser.navigate(f"http://127.0.0.1:{http.server_port}/")
            browser.wait("return !!document.getElementById('newContact') && "
                         "!document.getElementById('newContact').disabled",True)
            labels=browser.execute("""
                const field=document.getElementById('contactName');
                const live=document.getElementById('formError');
                const dialogs=[...document.querySelectorAll('dialog')];
                return {
                    lang:document.documentElement.lang,
                    nameLabel:field.closest('label')?.innerText?.trim(),
                    liveRole:live.getAttribute('role'),
                    dialogsLabeled:dialogs.every(d=>
                        !!document.getElementById(d.getAttribute('aria-labelledby'))),
                    pressed:document.getElementById('favoritesFilter').getAttribute('aria-pressed')
                };
            """)
            assert labels["lang"]=="en"
            assert labels["nameLabel"].startswith("Full name")
            assert labels["liveRole"]=="alert" and labels["dialogsLabeled"]
            assert labels["pressed"]=="false"

            # Real Tab from first keyboard-focusable brand link must reach New.
            browser.execute("document.querySelector('a.brand').focus();")
            key(browser,"\ue004")  # W3C WebDriver Tab
            browser.wait("return document.activeElement?.id","newContact")
            assert browser.execute(
                "return document.activeElement.matches(':focus-visible')"
            ), "Keyboard-focused primary action lacks a visible focus state"
            key(browser,"\ue007")  # Enter opens the native modal dialog
            browser.wait("return document.getElementById('editorDialog').open",True)
            browser.wait("return document.activeElement.id","contactName")

            # Native Escape should restore focus to its keyboard invoker.
            key(browser,"\ue00c")
            browser.wait("return document.getElementById('editorDialog').open",False)
            browser.wait("return document.activeElement?.id","newContact")

            # Invalid keyboard form submission must announce its error and
            # must not create a contact (real JS validation, not a mocked form).
            key(browser,"\ue007")
            browser.wait("return document.getElementById('editorDialog').open",True)
            browser.execute("document.getElementById('saveContact').focus();")
            key(browser,"\ue007")
            browser.wait("return !document.getElementById('formError').hidden",True)
            assert browser.execute(
                "return document.getElementById('formError').getAttribute('role')"
            )=="alert"
            key(browser,"\ue00c")
            browser.wait("return document.getElementById('editorDialog').open",False)
            browser.wait("return document.getElementById('countLabel').textContent",
                         "0 contacts saved locally")

            # Toggle filters with native keyboard Enter and semantic aria-pressed.
            browser.execute("document.getElementById('favoritesFilter').focus();")
            key(browser,"\ue007")
            browser.wait("return document.getElementById('favoritesFilter').getAttribute('aria-pressed')","true")
            browser.wait("return document.getElementById('allFilter').getAttribute('aria-pressed')","false")
            browser.execute("document.getElementById('allFilter').focus();")
            key(browser,"\ue007")
            browser.wait("return document.getElementById('allFilter').getAttribute('aria-pressed')","true")

            # At smallest common mobile viewport, controls must not extend off-screen.
            browser.call("POST",f"/session/{browser.session}/window/rect",
                         {"width":320,"height":700})
            assert browser.execute(
                "return document.documentElement.scrollWidth<=window.innerWidth+3"
            ), "Horizontal overflow at 320 px (keyboard access may be obstructed)"
            print("GOREECLOUD_CONTACTS_REAL_CHROME_KEYBOARD_DIALOG_FOCUS_320PX_PASS")
        finally:
            browser.close()
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            http.shutdown()
            http.server_close()
            thread.join(timeout=3)


if __name__=="__main__":
    smoke()
