"""Native GTK4/libadwaita GoreeCloud Contacts interface.

Private SQLite and user-confirmed file transfers. No outbound network calls.
UI colors use gc-ui main's verified semantic light/dark token roles.
"""
from __future__ import annotations

import sys
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, Gtk, Pango

from .core import (
    ContactError, ContactStore, MAX_BUNDLE_BYTES, make_backup,
    make_vcards, new_contact, read_backup_file, validate, write_new_file
)
from .vcard import read_vcards_file, visible_identity

GC_LIGHT = {
    "canvas":"#F6F7FB","surface":"#FFFFFF","tonal":"#EEF0F7",
    "text":"#1B2030","muted":"#505B70","brand":"#5146C8",
    "brand_container":"#E8E5FF","on_container":"#30266F",
    "outline":"#CED3DF",
}
GC_DARK = {
    "canvas":"#0D121D","surface":"#171D2A","tonal":"#252D3D",
    "text":"#F2F4FB","muted":"#CED5E5","brand":"#BFB8FF",
    "brand_container":"#413974","on_container":"#E8E5FF",
    "outline":"#505B70",
}

def _label(text: str, css: str = "", *, xalign: float = 0.0, wrap: bool = False):
    label = Gtk.Label(label=text)
    label.set_xalign(xalign)
    label.set_wrap(wrap)
    if css:
        label.add_css_class(css)
    return label


class ContactsWindow(Adw.ApplicationWindow):
    def __init__(self, application, store: ContactStore):
        super().__init__(application=application, title="GoreeCloud Contacts")
        self.store = store
        self.set_default_size(960, 680)
        self._css_provider = Gtk.CssProvider()
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display, self._css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        self._style_manager = Adw.StyleManager.get_default()
        self._style_manager.connect("notify::dark", self._apply_gc_ui)
        self._apply_gc_ui()
        self._make_layout()
        self.refresh()
        self.connect("close-request", self._close)

    def _apply_gc_ui(self, *args):
        t = GC_DARK if self._style_manager.get_dark() else GC_LIGHT
        css = """
        .gc-canvas { background: %(canvas)s; color: %(text)s; }
        .gc-surface { background: %(surface)s; border-radius: 18px; border: 1px solid %(outline)s; }
        .gc-contact-row { padding: 10px 12px; }
        .gc-avatar { background: %(brand_container)s; color: %(on_container)s; border-radius: 14px; padding: 12px; font-weight: 700; min-width: 50px; }
        .gc-muted { color: %(muted)s; }
        .gc-eyebrow { color: %(brand)s; font-weight: 700; }
        .gc-title { color: %(text)s; font-size: 26px; font-weight: 750; }
        .gc-secondary { background: %(tonal)s; border-radius: 12px; padding: 12px; }
        .gc-space { padding: 18px; }
        .gc-error { color: #B3261E; }
        """ % t
        self._css_provider.load_from_data(css.encode("utf-8"))

    def _make_layout(self):
        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle.new("Contacts", "Private on this Linux computer"))
        toolbar.add_top_bar(header)
        self.new_button = Gtk.Button(label="＋ New contact")
        self.new_button.add_css_class("suggested-action")
        self.new_button.connect("clicked", lambda *_: self.open_editor())
        header.pack_end(self.new_button)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        root.add_css_class("gc-canvas")
        root.add_css_class("gc-space")
        root.set_hexpand(True)
        root.set_vexpand(True)
        root.append(_label("YOUR DIRECTORY  ·  GOREECLOUD CONTACTS", "gc-eyebrow"))
        root.append(_label("People, beautifully organized.", "gc-title"))
        root.append(_label("Offline-only · contacts live in a private local database. No hidden sync.", "gc-muted",wrap=True))

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.search = Gtk.SearchEntry()
        self.search.set_hexpand(True)
        self.search.set_placeholder_text("Search names, phone numbers, email, organizations")
        self.search.connect("search-changed",lambda *_: self.refresh())
        controls.append(self.search)
        self.favorites = Gtk.ToggleButton(label="Favorites")
        self.favorites.connect("toggled",lambda *_: self.refresh())
        controls.append(self.favorites)
        root.append(controls)

        transfers = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for label, handler in (
            ("Import backup",self._import_backup),
            ("Import limited vCard",self._import_vcard),
            ("Back up contacts",self._export_backup),
            ("Export vCard",self._export_vcard),
        ):
            control = Gtk.Button(label=label)
            control.connect("clicked", lambda _,f=handler: f())
            transfers.append(control)
        root.append(transfers)
        self.count = _label("Loading contacts…","gc-muted")
        root.append(self.count)
        self.empty = _label("No contacts yet. Select New contact to get started.","gc-muted",wrap=True)
        root.append(self.empty)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        scroller.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        self.people = Gtk.ListBox()
        self.people.add_css_class("gc-surface")
        self.people.set_selection_mode(Gtk.SelectionMode.NONE)
        scroller.set_child(self.people)
        root.append(scroller)
        root.append(_label("Development preview · Your backup files are not encrypted. "
                           "No CardDAV or Mesh integration is active.", "gc-muted",wrap=True))
        self.toasts = Adw.ToastOverlay()
        self.toasts.set_child(root)
        toolbar.set_content(self.toasts)
        self.set_content(toolbar)

    def refresh(self):
        entries = self.store.filtered(self.search.get_text(),self.favorites.get_active())
        while self.people.get_first_child() is not None:
            self.people.remove(self.people.get_first_child())
        self.count.set_text(f"{len(self.store.list())} contacts saved locally")
        self.empty.set_visible(len(entries)==0)
        for c in entries:
            row = Gtk.ListBoxRow()
            bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=14)
            bar.add_css_class("gc-contact-row")
            bar.append(_label(c["name"][0].upper(),"gc-avatar"))
            summary = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=4)
            summary.set_hexpand(True)
            title = _label(c["name"])
            title.set_ellipsize(Pango.EllipsizeMode.END)
            summary.append(title)
            details = _label(c["organization"] or c["email"] or c["phone"] or "Personal contact","gc-muted")
            details.set_ellipsize(Pango.EllipsizeMode.END)
            summary.append(details)
            bar.append(summary)
            for label, callback in (
                ("★" if c["favorite"] else "☆", lambda item=c: self._toggle_favorite(item)),
                ("Edit",lambda item=c: self.open_editor(item)),
                ("Delete",lambda item=c: self._delete_confirm(item)),
            ):
                b = Gtk.Button(label=label)
                b.set_tooltip_text((("Remove " if c["favorite"] else "Add ") +
                    c["name"] + " favorites") if label in ("★","☆") else label + " " + c["name"])
                b.connect("clicked",lambda _,f=callback: f())
                bar.append(b)
            row.set_child(bar)
            self.people.append(row)

    def _toast(self, message: str):
        self.toasts.add_toast(Adw.Toast.new(message))

    def _message(self, title: str, detail: str):
        dialog=Adw.MessageDialog.new(self,title,detail)
        dialog.add_response("ok","OK")
        dialog.present()

    def _confirm(self, title: str, detail: str, action: str, on_confirm, *, destructive=False):
        dialog=Adw.MessageDialog.new(self,title,detail)
        dialog.add_response("cancel","Cancel")
        dialog.add_response("confirm",action)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        if destructive:
            dialog.set_response_appearance("confirm",Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.connect("response",lambda _,r: on_confirm() if r=="confirm" else None)
        dialog.present()

    def open_editor(self, existing: dict | None = None):
        dialog=Gtk.Window(title="Edit contact" if existing else "New contact",
                          transient_for=self,modal=True,default_width=450)
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=13)
        box.set_margin_start(22);box.set_margin_end(22)
        box.set_margin_top(22);box.set_margin_bottom(22)
        inputs={}
        for key,caption in (("name","Full name"),("phone","Phone"),
                            ("email","Email"),("organization","Organization")):
            label=_label(caption)
            entry=Gtk.Entry()
            entry.set_text(existing[key] if existing else "")
            label.set_mnemonic_widget(entry)
            box.append(label);box.append(entry)
            inputs[key]=entry
        favorite=Gtk.CheckButton(label="Keep in Favorites")
        favorite.set_active(existing["favorite"] if existing else False)
        box.append(favorite)
        error=_label("","gc-error",wrap=True)
        error.set_visible(False)
        box.append(error)
        actions=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=10)
        actions.set_halign(Gtk.Align.END)
        cancel=Gtk.Button(label="Cancel")
        cancel.connect("clicked",lambda *_: dialog.close())
        save=Gtk.Button(label="Save contact")
        save.add_css_class("suggested-action")
        def commit(*args):
            try:
                values={key:entry.get_text() for key,entry in inputs.items()}
                if existing:
                    raw=validate(dict(existing,**values,favorite=favorite.get_active()))
                    self.store.save(raw,is_new=False,expected=existing)
                else:
                    raw=new_contact(**values,favorite=favorite.get_active())
                    self.store.save(raw,is_new=True)
                self.refresh()
                dialog.close()
                self._toast("Contact saved locally")
            except ContactError as failure:
                error.set_text(str(failure))
                error.set_visible(True)
        save.connect("clicked",commit)
        actions.append(cancel);actions.append(save);box.append(actions)
        dialog.set_child(box)
        dialog.present()
        inputs["name"].grab_focus()
        return dialog  # Exposed only to synthetic native UI tests.

    def _toggle_favorite(self, contact):
        try:
            self.store.save(dict(contact,favorite=not contact["favorite"]),is_new=False,expected=contact)
            self.refresh()
        except ContactError as error:
            self._message("Unable to update favorite",str(error))

    def _delete_confirm(self, contact):
        def delete():
            try:
                self.store.delete(contact["id"],expected=contact)
                self.refresh()
                self._toast("Contact deleted")
            except ContactError as error:
                self._message("Unable to delete contact",str(error))
        self._confirm("Delete " + contact["name"] + "?",
                      "This permanently removes the local record. Use a backup to recover it.",
                      "Delete",delete,destructive=True)

    def _choose_file(self, title: str, action, on_path, *, filename=None):
        chooser = Gtk.FileChooserNative.new(title,self,action,
             "Open" if action==Gtk.FileChooserAction.OPEN else "Save", "Cancel")
        if filename:
            chooser.set_current_name(filename)
        def selected(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                selected_file=dialog.get_file()
                path=selected_file.get_path() if selected_file else None
                if path:
                    on_path(path)
                else:
                    self._message("Local file required","Choose a file on this computer, not a remote URI.")
            dialog.destroy()
        chooser.connect("response",selected)
        chooser.show()

    def _import_backup(self):
        def picked(path):
            try:
                records=read_backup_file(path)
                known={c["id"] for c in self.store.list()}
                if any(c["id"] in known for c in records):
                    raise ContactError("Import refused: matching contact IDs already exist")
            except ContactError as error:
                self._message("Backup not imported",str(error))
                return
            def apply():
                try:
                    count=self.store.import_new(records)
                    self.refresh()
                    self._toast(f"{count} contacts imported")
                except ContactError as error:
                    self._message("Backup not imported",str(error))
            self._confirm("Import " + str(len(records)) + " contacts?",
                "Only the displayed portable fields are stored. "
                "Existing contacts will not be replaced.", "Import",apply)
        self._choose_file("Select GoreeCloud Contacts JSON backup",
                          Gtk.FileChooserAction.OPEN,picked)

    def _import_vcard(self):
        def picked(path):
            try:
                incoming=read_vcards_file(path)
                known={visible_identity(c) for c in self.store.list()}
                staged=set()
                for item in incoming:
                    key=visible_identity(item)
                    if key in known or key in staged:
                        raise ContactError("Duplicate visible contact details; no import performed")
                    staged.add(key)
            except ContactError as error:
                self._message("vCard not imported",str(error))
                return
            preview=", ".join(c["name"] for c in incoming[:3])
            if len(incoming)>3:
                preview+=" …"
            def apply():
                try:
                    count=self.store.import_new(incoming,reject_visible_duplicates=True)
                    self.refresh()
                    self._toast(f"{count} limited vCards imported locally")
                except ContactError as error:
                    self._message("vCard not imported",str(error))
            self._confirm("Import " + str(len(incoming)) + " limited vCards?",
                "Preview: " + preview + "\nOnly name, one phone, one email, and "
                "organization are supported. Rich fields and favorites will not "
                "be restored. Existing contacts are never overwritten.",
                "Import",apply)
        self._choose_file("Select a limited Contacts vCard",
                          Gtk.FileChooserAction.OPEN,picked)

    def _export_backup(self):
        self._confirm("Export an unencrypted backup?",
            "The JSON backup includes names and contact details. "
            "Choose trusted private storage; an existing file will never be overwritten.",
            "Choose file",lambda: self._choose_file(
                "Save Contacts backup",Gtk.FileChooserAction.SAVE,
                lambda path: self._save_file(path,make_backup(self.store.list())),
                filename="goreecloud-contacts-backup.json"))

    def _export_vcard(self):
        self._confirm("Export a limited vCard?",
            "Only names, phones, emails and organizations are exported. "
            "Favorite markers are not included. Choose trusted private storage.",
            "Choose file",lambda: self._choose_file(
                "Save vCard",Gtk.FileChooserAction.SAVE,
                lambda path: self._save_file(path,make_vcards(self.store.list())),
                filename="goreecloud-contacts.vcf"))

    def _save_file(self, path, content):
        try:
            write_new_file(path,content)
            self._toast("Export saved to selected private file")
        except ContactError as error:
            self._message("Export not saved",str(error))

    def _close(self, *args):
        if not getattr(self,"_closed",False):
            self.store.close()
            self._closed=True
        app=self.get_application()
        if app is not None and getattr(app,"window",None) is self:
            app.window=None
        return False


class ContactsApplication(Adw.Application):
    def __init__(self, data_path=None):
        super().__init__(application_id="com.goreecloud.Contacts",
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.data_path=data_path
        self.window=None

    def do_activate(self):
        if self.window is None:
            try:
                store=ContactStore(self.data_path)
                self.window=ContactsWindow(self,store)
            except (ContactError, OSError) as error:
                print("GoreeCloud Contacts cannot open private data store: " + str(error),
                      file=sys.stderr)
                self.quit()
                return
        self.window.present()


def main(argv=None):
    return ContactsApplication().run(argv if argv is not None else sys.argv)

if __name__ == "__main__":
    raise SystemExit(main())
