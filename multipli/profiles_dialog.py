"""
Dialogue Adwaita pour gérer les profils des enfants (création, changement, suppression).
"""

from typing import Callable
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from multipli.i18n import _
from multipli.models import StorageManager


class ProfilesDialog(Adw.PreferencesWindow):
    def __init__(self, parent_window: Gtk.Window, on_profile_changed_cb: Callable[[], None]):
        super().__init__()
        self.set_transient_for(parent_window)
        self.set_modal(True)
        self.set_title(_("profiles_manage"))
        self.set_default_size(480, 520)

        self.on_profile_changed = on_profile_changed_cb
        self.avatars = ["🦊", "🐼", "🦉", "🐱", "🦁", "🦄", "🚀", "⭐"]
        self.selected_avatar = "🦊"
        self.avatar_btns = []

        self._build_ui()

    def _build_ui(self):
        page = Adw.PreferencesPage()
        self.add(page)

        # Groupe 1 : Profils existants
        self.group_profiles = Adw.PreferencesGroup(title=_("profiles_manage"))
        page.add(self.group_profiles)
        self._populate_profiles()

        # Groupe 2 : Créer un nouveau profil
        group_new = Adw.PreferencesGroup(title=_("btn_add_player"))
        page.add(group_new)

        self.entry_name = Adw.EntryRow(title=_("profile_name"))
        group_new.add(self.entry_name)

        # Choix de l'avatar
        avatar_row = Adw.ActionRow(title=_("profile_avatar"))
        avatar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        avatar_box.set_valign(Gtk.Align.CENTER)

        self.avatar_btns = []
        for av in self.avatars:
            b = Gtk.ToggleButton(label=av)
            b.add_css_class("flat")
            if av == self.selected_avatar:
                b.set_active(True)
            self.avatar_btns.append(b)

            def make_handler(chosen, btn):
                return lambda _: self._select_avatar(chosen, btn)

            b.connect("clicked", make_handler(av, b))
            avatar_box.append(b)

        avatar_row.add_suffix(avatar_box)
        group_new.add(avatar_row)

        # Bouton Ajouter
        add_btn_row = Adw.ActionRow()
        btn_add = Gtk.Button(label=_("profile_create"))
        btn_add.add_css_class("suggested-action")
        btn_add.add_css_class("pill")
        btn_add.connect("clicked", self._on_add_profile)
        add_btn_row.add_suffix(btn_add)
        group_new.add(add_btn_row)

    def _populate_profiles(self):
        storage = StorageManager.get_instance()
        active_id = storage.active_profile_id

        for profile in storage.profiles:
            row = Adw.ActionRow()
            row.set_title(f"{profile.avatar}  {profile.name}")
            total_stars = sum(profile.stars.values())
            row.set_subtitle(f"{total_stars} ⭐ • Record chrono : {profile.chrono_best} pts")

            is_active = (profile.id == active_id)

            if is_active:
                check_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
                check_icon.add_css_class("accent")
                row.add_suffix(check_icon)
            else:
                btn_select = Gtk.Button(label="Choisir")
                btn_select.add_css_class("pill")
                btn_select.add_css_class("flat")

                def make_select_handler(p_id):
                    return lambda _: self._on_select_profile(p_id)

                btn_select.connect("clicked", make_select_handler(profile.id))
                row.add_suffix(btn_select)

            # Bouton supprimer si plus d'un profil
            if len(storage.profiles) > 1 and not is_active:
                btn_del = Gtk.Button.new_from_icon_name("user-trash-symbolic")
                btn_del.add_css_class("flat")
                btn_del.add_css_class("destructive-action")

                def make_del_handler(p_id):
                    return lambda _: self._on_delete_profile(p_id)

                btn_del.connect("clicked", make_del_handler(profile.id))
                row.add_suffix(btn_del)

            self.group_profiles.add(row)

    def _select_avatar(self, chosen: str, active_btn: Gtk.ToggleButton):
        self.selected_avatar = chosen
        for b in self.avatar_btns:
            if b != active_btn:
                b.set_active(False)
        active_btn.set_active(True)

    def _on_select_profile(self, profile_id: str):
        StorageManager.get_instance().set_active_profile(profile_id)
        self.on_profile_changed()
        self.close()

    def _on_delete_profile(self, profile_id: str):
        StorageManager.get_instance().delete_profile(profile_id)
        self.on_profile_changed()
        self.close()

    def _on_add_profile(self, btn):
        name = self.entry_name.get_text().strip()
        if not name:
            name = "Élève"

        StorageManager.get_instance().add_profile(name, self.selected_avatar)
        self.entry_name.set_text("")
        self.on_profile_changed()
        self.close()
