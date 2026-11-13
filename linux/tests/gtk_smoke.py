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
        # Exercise real GTK row buttons (not a fake callback): both states
        # must rebind after persistence and expose readable accessible text.
        def row_button(label):
            found=[v for v in widgets(window.people) if isinstance(v,Gtk.Button)
                   and v.get_label()==label]
            assert len(found)==1, "Missing native favorite action: "+label
            return found[0]
        row_button("★ Favorite").emit("clicked")
        assert not db.list()[0]["favorite"], "Native star failed to remove favorite"
        assert row_button("☆ Add favorite").get_tooltip_text().startswith("Add Synthetic")
        row_button("☆ Add favorite").emit("clicked")
        assert db.list()[0]["favorite"], "Native star failed to restore favorite"
        assert row_button("★ Favorite").get_tooltip_text().startswith("Remove Synthetic")
        assert not window.empty.get_visible()
        # Native export scope is independent of the visible Favorites filter.
        assert isinstance(window.export_favorites,Gtk.CheckButton)
        assert not window.export_favorites.get_active()
        other=new_contact("Synthetic Private","555-0123",
                          "private@example.invalid",favorite=False)
        db.save(other,is_new=True)
        window.refresh()
        confirmed=[]
        exported=[]
        errors=[]
        original_confirm=window._confirm
        original_file=window._choose_file
        original_message=window._message
        try:
            def confirm(title,detail,action,callback,**kwargs):
                confirmed.append((title,detail))
                callback()
            def choose(title,action,on_path,**kwargs):
                suffix=".vcf" if "vCard" in title else ".json"
                target=path/("scoped-"+str(len(exported))+suffix)
                exported.append(target)
                on_path(target)
            window._confirm=confirm
            window._choose_file=choose
            window._message=lambda title,detail: errors.append((title,detail))
            window.export_favorites.set_active(True)
            window._export_backup()
            assert confirmed[-1][0]=="Export 1 contact (favorites only)?"
            from goreecloud_contacts.core import read_backup_file
            assert read_backup_file(exported[-1])[0]["name"]=="Synthetic GTK Contact"
            assert other["name"] not in exported[-1].read_text(encoding="utf8")
            assert (exported[-1].stat().st_mode & 0o077)==0
            window._export_vcard()
            assert "favorites only" in confirmed[-1][0]
            text=exported[-1].read_text(encoding="utf8")
            assert text.count("BEGIN:VCARD")==1
            assert "Synthetic GTK Contact" in text and other["name"] not in text
            window.export_favorites.set_active(False)
            window._export_backup()
            assert "2 contacts (all contacts)" in confirmed[-1][0]
            assert len(read_backup_file(exported[-1]))==2
            saved=next(c for c in db.list() if c["favorite"])
            db.save(dict(saved,favorite=False),is_new=False,expected=saved)
            prior_count=len(exported)
            window.export_favorites.set_active(True)
            window._export_backup()
            assert len(exported)==prior_count, "Empty favorites attempted file creation"
            assert errors[-1][0]=="Backup not exported"
        finally:
            window._confirm=original_confirm
            window._choose_file=original_file
            window._message=original_message
            window.export_favorites.set_active(False)
        # Restore the synthetic favorite used by the pre-existing view-filter
        # smoke, after verifying that a zero-favorites export was refused.
        reloaded=next(c for c in db.list() if c["id"]==saved["id"])
        db.save(dict(reloaded,favorite=True),is_new=False,expected=reloaded)
        window.refresh()
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
