"""Disposable real GTK4/libadwaita smoke, never reads a person's contacts."""
import os
from pathlib import Path
import tempfile

from goreecloud_contacts.app import ContactsApplication, ContactsWindow, Gtk, Adw
from goreecloud_contacts.core import ContactStore, new_contact

def main():
    with tempfile.TemporaryDirectory(prefix="gc-contacts-gtk-") as directory:
        path=Path(directory)/"data"
        path.mkdir(mode=0o700)
        db_path=path/"db.sqlite3"
        app=ContactsApplication(data_path=db_path)
        assert app.register(None), "GTK application registration failed"
        db=ContactStore(db_path)
        window=ContactsWindow(app,db)
        assert isinstance(window,Adw.ApplicationWindow)
        assert isinstance(window.search,Gtk.SearchEntry)
        assert isinstance(window.people,Gtk.ListBox)
        assert window.count.get_text()=="0 contacts saved locally"
        assert window.empty.get_visible()
        def widgets(widget):
            yield widget
            child=widget.get_first_child()
            while child:
                yield from widgets(child)
                child=child.get_next_sibling()
        transfer_buttons=[v.get_label() for v in widgets(window) if isinstance(v,Gtk.Button)]
        assert "Import limited vCard" in transfer_buttons
        editor=window.open_editor()
        fields=[v for v in widgets(editor) if isinstance(v,Gtk.Entry)]
        assert len(fields)==4, "Expected native name, phone, email, organization editors"
        fields[0].set_text("Synthetic GTK Contact")
        fields[1].set_text("555-0100")
        favorites=[v for v in widgets(editor) if isinstance(v,Gtk.CheckButton)]
        assert len(favorites)==1
        favorites[0].set_active(True)
        save=[v for v in widgets(editor) if isinstance(v,Gtk.Button) and v.get_label()=="Save contact"]
        assert len(save)==1
        save[0].emit("clicked")
        assert len(db.list())==1, "Native editor did not save synthetic contact"
        assert db.list()[0]["phone"]=="555-0100"
        window.refresh()
        assert window.count.get_text()=="1 contacts saved locally"
        assert window.people.get_first_child() is not None
        assert not window.empty.get_visible()
        window.search.set_text("no matching contact")
        window.refresh()
        assert window.empty.get_visible()
        window.search.set_text("")
        window.favorites.set_active(True)
        window.refresh()
        assert window.people.get_first_child() is not None
        from gi.repository import GLib
        app.window=window
        window.present()
        context=GLib.MainContext.default()
        for _ in range(15):
            while context.pending():
                context.iteration(False)
        window.close()  # Native close-request must release DB and clear app state.
        for _ in range(15):
            while context.pending():
                context.iteration(False)
        assert app.window is None, "A closed window must not be reused on next activation"
    print("GOREECLOUD_CONTACTS_NATIVE_GTK4_LIBADWAITA_SMOKE_PASS")

if __name__=="__main__":
    main()
